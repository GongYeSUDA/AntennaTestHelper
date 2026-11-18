"""绘图与文件工具：线条颜色、配色、图片导出及 InfoBar 反馈。"""

import os

import matplotlib.pyplot as plt
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from qfluentwidgets import InfoBar, InfoBarPosition

from app_config import DEFAULT_OUTPUT_DIR, cfg
from data_processor import DataProcessor


def blend_color(color: QColor, target: QColor, ratio: float) -> QColor:
    """按比例把 color 混向 target"""
    ratio = min(max(ratio, 0.0), 1.0)
    return QColor(
        round(color.red() * (1 - ratio) + target.red() * ratio),
        round(color.green() * (1 - ratio) + target.green() * ratio),
        round(color.blue() * (1 - ratio) + target.blue() * ratio),
    )


def plot_line_colors():
    """读取设置中的线条颜色，返回 (水平, 垂直, 总增益) 三种颜色"""
    base = QColor(cfg.plotColor.value)
    if not base.isValid():
        base = QColor(0, 0, 255)

    base.setAlpha(255)
    horizontal = base.name()
    vertical = blend_color(base, QColor(255, 255, 255), 0.4).name()
    total = blend_color(base, QColor(0, 0, 0), 0.25).name()
    return horizontal, vertical, total


def plot_colormap():
    """3D 曲面固定使用内置 managua 反转配色，不受设置影响"""
    return plt.get_cmap("managua_r")


def resolve_output_dir() -> str:
    """获取图片输出目录，不存在时自动创建"""
    path = cfg.outputPath.value or DEFAULT_OUTPUT_DIR
    path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)
    return path


def chart_base_name(processor: DataProcessor, suffix: str) -> str:
    """根据数据文件名与图表后缀生成图片文件名"""
    if processor.file_path:
        stem = os.path.splitext(os.path.basename(processor.file_path))[0]
    else:
        stem = "Antenna"

    return f"{stem}_{suffix}"


def save_figure(figure, base_name: str):
    """按设置的多选格式把图表保存到输出路径，返回已保存的文件列表"""
    output_dir = resolve_output_dir()
    saved_paths = []

    for fmt in cfg.outputFormats.value:
        path = os.path.join(output_dir, f"{base_name}.{fmt.lower()}")
        # JPG 不支持透明背景，统一使用不透明底色
        figure.savefig(path, dpi=300, bbox_inches="tight", transparent=False)
        saved_paths.append(path)

    return saved_paths


def show_export_feedback(
    widget, saved_paths=None, error=None, warning=None, title="图表保存失败"
):
    """在界面上提示图片保存结果，也可用于弹出其他错误提示"""
    old_bar = getattr(widget, "_exportBar", None)
    if old_bar is not None:
        try:
            old_bar.close()
        except RuntimeError:
            pass

    if error is not None:
        bar = InfoBar.error(
            title,
            str(error),
            orient=Qt.Vertical,
            isClosable=True,
            duration=6000,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=widget,
        )
    elif warning is not None:
        bar = InfoBar.warning(
            "已跳过导出",
            str(warning),
            orient=Qt.Vertical,
            isClosable=True,
            duration=4000,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=widget,
        )
    else:
        output_dir = resolve_output_dir()
        formats = "、".join(
            os.path.splitext(path)[1].lstrip(".").upper() for path in saved_paths
        )
        bar = InfoBar.success(
            "图表已保存",
            f"{formats} 已导出至 {output_dir}",
            orient=Qt.Vertical,
            isClosable=False,
            duration=2600,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=widget,
        )

    widget._exportBar = bar


def auto_save_chart(widget, figure, base_name: str):
    """绘制完成后自动把图表导出到输出路径"""
    # 设置中未勾选任何图片格式时，跳过导出并提示
    if not cfg.outputFormats.value:
        show_export_feedback(widget, warning="未勾选任何图片格式，请在设置中勾选后重试")
        return []

    try:
        saved_paths = save_figure(figure, base_name)
    except Exception as e:  # noqa: BLE001 保存失败不应影响绘图结果
        print(f"保存图表失败: {e}")
        show_export_feedback(widget, error=e)
        return []

    print(f"图表已保存: {' '.join(saved_paths)}")
    show_export_feedback(widget, saved_paths)
    return saved_paths
