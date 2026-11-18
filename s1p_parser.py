"""Touchstone .s1p 文件解析（基于 scikit-rf）。"""

import numpy as np
import skrf as rf


def parse_s1p(file_path):
    """解析 Touchstone .s1p 文件，返回 (频率 MHz, |Γ|²)。

    选项行中的频率单位（Hz/kHz/MHz/GHz）与数据格式（RI/MA/DB）由
    scikit-rf 负责解析；这里统一把频率换算为 MHz，并取 S11 的功率 |Γ|²。
    """
    network = rf.Network(file_path)
    freq_mhz = np.asarray(network.f, dtype=float) / 1e6
    s11 = np.asarray(network.s[:, 0, 0], dtype=complex)
    gamma_sq = np.abs(s11) ** 2

    if freq_mhz.size == 0:
        raise ValueError("S1P 文件中没有找到有效数据")

    return freq_mhz, gamma_sq
