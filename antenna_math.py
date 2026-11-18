"""天线后处理纯函数：立体角权重与 Gain / Directivity / Efficiency。

不依赖任何界面对象；调用方需把数据数组、角度轴和 S1P 数据显式传入。
"""

import numpy as np


def solid_angle_weights(theta, phi):
    """离散球面的立体角权重 w_ij（完整球面时 Σw ≈ 4π）。

    兼容三种常见角度约定：
    1. 极角 θ∈[0,180°]、方位角 φ∈[0,360°)；
    2. 有符号极角 θ∈[-180°,180°]、φ∈[0,180°]（ EMT 数据，
       θ<0 时方位角折叠到 φ+180°，两个半圈合起来覆盖整圈）；
    3. 仰角 θ∈[-90°,90°]、φ∈[0,360°)（极角 = 90°−θ）。
    """
    theta = np.deg2rad(np.asarray(theta, dtype=float))
    phi = np.deg2rad(np.asarray(phi, dtype=float))

    theta_min, theta_max = np.min(theta), np.max(theta)
    signed_full = theta_min < -1e-9 and theta_max >= np.pi - 1e-6
    if signed_full:
        polar = np.abs(theta)  # 有符号极角 → 取绝对值
    elif theta_min < -1e-9:
        polar = np.pi / 2 - theta  # 仰角约定
    else:
        polar = theta  # 标准极角

    if theta.size > 1:
        theta_edges = np.empty(theta.size + 1)
        theta_edges[1:-1] = (polar[:-1] + polar[1:]) / 2.0
        theta_edges[0] = polar[0] + (polar[0] - polar[1]) / 2.0
        theta_edges[-1] = polar[-1] + (polar[-1] - polar[-2]) / 2.0
        theta_edges = np.clip(theta_edges, 0.0, np.pi)
        # 取绝对值以兼容极角递增/递减两种排列
        w_theta = np.abs(np.cos(theta_edges[:-1]) - np.cos(theta_edges[1:]))
    else:
        w_theta = np.array([2.0])

    if phi.size > 1:
        step = np.median(np.diff(phi))
        span = phi[-1] - phi[0]
        if np.isclose(span, 2 * np.pi) or (signed_full and np.isclose(span, np.pi)):
            # 端点重复（0° 与 360°，或有符号约定下的 0° 与 180°）：末列权重置零
            w_phi = np.zeros(phi.size)
            w_phi[:-1] = step
        elif span >= 2 * np.pi - 1.5 * step:
            # 周期整圆（如 0~350°）：每个方位单元等宽
            w_phi = np.full(phi.size, step)
        else:
            phi_edges = np.empty(phi.size + 1)
            phi_edges[1:-1] = (phi[:-1] + phi[1:]) / 2.0
            phi_edges[0] = phi[0] - step / 2.0
            phi_edges[-1] = phi[-1] + step / 2.0
            w_phi = np.diff(phi_edges)
    else:
        w_phi = np.array([2 * np.pi])

    return np.outer(w_theta, w_phi)


def compute_metrics(
    data, theta, phi, freq, s1p_freq=None, s1p_gamma2=None, no_s1p=False
):
    """返回 (freqs, gain_dBi, directivity_dBi, efficiency, used_s1p)。

    data 形状为 [antenna, polar, freq, theta, phi]。
    G_re = max(r), D = 4π·max(r)/Σw·r,
    G = G_re/(1-|Γ|²), η_rad = G/D = Σw·r / (4π(1-|Γ|²))。
    no_s1p 为真时取 |Γ|=0，此时 G=G_re、η=总效率。
    """
    h = data[0, 0]
    v = data[0, 1]
    r = 10 ** (h / 10.0) + 10 ** (v / 10.0)  # 双极化按功率相加
    r_max = np.max(r, axis=(1, 2))
    s = np.sum(r * solid_angle_weights(theta, phi)[np.newaxis, :, :], axis=(1, 2))

    no_s1p = bool(no_s1p)
    used_s1p = (not no_s1p) and (s1p_freq is not None)
    if used_s1p:
        gamma2 = np.interp(freq, s1p_freq, s1p_gamma2)
        mismatch = np.clip(1.0 - gamma2, 1e-12, 1.0)
    else:
        mismatch = np.ones_like(r_max)

    with np.errstate(divide="ignore", invalid="ignore"):
        gain_db = 10 * np.log10(r_max / mismatch)
        directivity_db = 10 * np.log10(4 * np.pi * r_max / s)
        efficiency = s / (4 * np.pi * mismatch)  # 辐射效率（0~1）

    return freq, gain_db, directivity_db, efficiency, used_s1p
