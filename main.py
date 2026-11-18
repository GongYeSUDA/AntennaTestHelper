import os
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    # QLabel,
    QFileDialog,
    QHeaderView,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import (
    CheckBox,
    ColorConfigItem,
    ColorSettingCard,
    ConfigItem,
    ConfigValidator,
    ExpandLayout,
    FluentWindow,
    InfoBar,
    InfoBarPosition,
    # ImageLabel,
    PushSettingCard,
    QConfig,
    ScrollArea,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
    Theme,
    qconfig,
    setTheme,
)
from qfluentwidgets import (
    FluentIcon as FIF,
)
from scipy.interpolate import RectBivariateSpline

from data_processor import DataProcessor
from ui_analysis_3dpattern_interface import Ui_Analysis3DPatternInterface
from ui_analysis_gain_interface import Ui_AnalysisGainInterface  # 导入新生成的 UI
from ui_analysis_pattern_interface import Ui_AnalysisPatternInterface
from ui_home_interface import Ui_HomeInterface
from ui_post_processing_interface import Ui_PostProcessingInterface

# 可导出/保存的图片格式
IMAGE_FORMATS = ["PNG", "JPG", "PDF", "SVG"]
# 未指定输出路径时使用的默认目录
DEFAULT_OUTPUT_DIR = "output"


class MultiOptionsValidator(ConfigValidator):
    """多选选项校验器"""

    def __init__(self, options):
        self.options = list(options)

    def validate(self, value):
        # 允许空列表（未勾选任何格式时跳过导出）
        return isinstance(value, (list, tuple)) and all(
            v in self.options for v in value
        )

    def correct(self, value):
        if isinstance(value, str):
            value = [value]

        if not isinstance(value, (list, tuple)):
            return [self.options[0]]

        # 去重并按选项顺序排列，避免传入非法值
        return [option for option in self.options if option in value]


class OutputFolderValidator(ConfigValidator):
    """输出目录校验器，允许为空（为空时使用默认目录）"""

    def validate(self, value):
        return isinstance(value, str)

    def correct(self, value):
        if not value:
            return ""

        path = Path(value)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            return ""

        return str(path.absolute()).replace("\\", "/")


class AppConfig(QConfig):
    """应用配置类"""

    # 绘图颜色
    plotColor = ColorConfigItem("Plot", "Color", QColor(0, 0, 255))
    # 归一化
    isNormalization = ConfigItem("Plot", "IsNormalization", False)
    # 图片输出路径
    outputPath = ConfigItem("Output", "Path", "", OutputFolderValidator())
    # 图片输出格式（多选）
    outputFormats = ConfigItem(
        "Output", "Formats", [IMAGE_FORMATS[0]], MultiOptionsValidator(IMAGE_FORMATS)
    )


cfg = AppConfig()


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


def parse_s1p(file_path):
    """解析 Touchstone .s1p 文件，返回 (频率 MHz, |Γ|²)。

    支持选项行中的 Hz/kHz/MHz/GHz 与 RI/MA/DB 三种数据格式。
    """
    freqs = []
    gamma_sq = []
    freq_scale = 1e-6  # 默认按 Hz 处理
    data_format = "RI"

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("!"):
                continue
            if line.startswith("#"):
                tokens = line[1:].split()
                upper = [token.upper() for token in tokens]
                if upper:
                    freq_scale = {
                        "HZ": 1e-6,
                        "KHZ": 1e-3,
                        "MHZ": 1.0,
                        "GHZ": 1e3,
                    }.get(upper[0], 1e-6)
                for candidate in ("RI", "MA", "DB"):
                    if candidate in upper:
                        data_format = candidate
                        break
                continue

            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                f_val = float(parts[0])
                a_val = float(parts[1])
                b_val = float(parts[2])
            except ValueError:
                continue

            if data_format == "RI":
                gamma2 = a_val * a_val + b_val * b_val
            elif data_format == "MA":
                gamma2 = a_val * a_val
            else:  # DB: S11(dB) = 20log10(|Γ|)
                gamma2 = (10 ** (a_val / 20.0)) ** 2

            freqs.append(f_val * freq_scale)
            gamma_sq.append(gamma2)

    if not freqs:
        raise ValueError("S1P 文件中没有找到有效数据")

    return np.asarray(freqs, dtype=float), np.asarray(gamma_sq, dtype=float)


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


class HomeInterface(QWidget, Ui_HomeInterface):
    fileLoaded = Signal()

    def __init__(self, processor: DataProcessor, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.processor = processor

        # 启用拖拽
        self.setAcceptDrops(True)

        # 初始化表格
        self.infoTable.setColumnCount(2)
        self.infoTable.setHorizontalHeaderLabels(["变量名", "矩阵形状"])
        self.infoTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 连接信号
        self.openFileButton.clicked.connect(self.on_open_file)

    def on_open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择数据文件",
            "",
            "EMT 文件 (*.emt);;Matlab 文件 (*.mat);;All Files (*)",
        )
        if file_path:
            self.process_file(file_path)

    def process_file(self, file_path):
        """核心处理逻辑：读取文件并更新 UI"""
        self.filePathLineEdit.setText(file_path)
        try:
            info = self.processor.load_mat(file_path)

            # 清空并填充表格
            self.infoTable.setRowCount(0)
            for item in info:
                row = self.infoTable.rowCount()
                self.infoTable.insertRow(row)
                self.infoTable.setItem(row, 0, QTableWidgetItem(item["name"]))
                self.infoTable.setItem(row, 1, QTableWidgetItem(item["shape"]))

            # 发射信号通知其他页面文件已加载
            self.fileLoaded.emit()
        except Exception as e:
            print(f"读取文件失败: {e}")
            self.infoTable.setRowCount(0)
            row = self.infoTable.rowCount()
            self.infoTable.insertRow(row)
            self.infoTable.setItem(row, 0, QTableWidgetItem(f"读取文件失败: {e}"))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.lower().endswith(".mat") or file_path.lower().endswith(".emt"):
                self.process_file(file_path)


class AnalysisGainInterface(QWidget, Ui_AnalysisGainInterface):
    def __init__(self, processor: DataProcessor, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.processor = processor

        # 默认勾选 checkBoxTotal
        self.checkBoxTotal.setChecked(True)

        # 布局 Matplotlib

        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.chartContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        # 初始状态下禁用绘制按钮
        self.plotButton.setEnabled(False)
        self.plotButton.clicked.connect(self.update_plot)
        self.chartContainer.setEnabled(False)
        self.csvButton.setEnabled(False)
        self.csvButton.clicked.connect(self.export_csv)

        # 连接 checkBoxMax 信号
        self.checkBoxMax.stateChanged.connect(self.on_max_checkbox_changed)

    def on_max_checkbox_changed(self, state):
        is_checked = state == Qt.Checked.value or state == Qt.Checked
        self.phiComboBox.setDisabled(is_checked)
        self.thetaComboBox.setDisabled(is_checked)

    def refresh_comboboxes(self):
        """当文件加载后，更新下拉列表并启用按钮"""
        if self.processor.phi is not None:
            self.phiComboBox.clear()
            self.phiComboBox.addItems([str(a) for a in self.processor.phi])
            self.thetaComboBox.clear()
            self.thetaComboBox.addItems([str(a) for a in self.processor.theta])

            # 启用绘制按钮
            self.plotButton.setEnabled(True)

    def update_plot(self):
        if self.processor.data_mea_amp is None:
            return

        is_max = self.checkBoxMax.isChecked()
        freqs = self.processor.freq

        if not is_max:
            # 获取选中的索引
            phi_idx = self.phiComboBox.currentIndex()
            theta_idx = self.thetaComboBox.currentIndex()
            if phi_idx < 0 or theta_idx < 0:
                # 下拉框为空（如数据未加载或被清空），中止绘制
                return
            title_suffix = f"(Phi={self.phiComboBox.currentText()}, Theta={self.thetaComboBox.currentText()})"
        else:
            title_suffix = "(Max Gain over all directions)"

        self.ax.clear()
        has_plot = False
        # 读取设置中的线条颜色
        horizontal_color, vertical_color, total_color = plot_line_colors()

        # 1. 绘制水平极化 (Horizontal/Theta)
        if self.checkBoxHori.isChecked():
            if is_max:
                # data_mea_amp shape: [antenna, polar, freq, theta, phi]
                gain_h = np.max(self.processor.data_mea_amp[0, 0, :, :, :], axis=(1, 2))
            else:
                gain_h = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
            self.ax.plot(
                freqs,
                gain_h,
                label="RealizedGainHorizontal",
                color=horizontal_color,
                linewidth=1.5,
            )
            has_plot = True

        # 2. 绘制垂直极化 (Vertical/Phi)
        if self.checkBoxVert.isChecked():
            if is_max:
                gain_v = np.max(self.processor.data_mea_amp[0, 1, :, :, :], axis=(1, 2))
            else:
                gain_v = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
            self.ax.plot(
                freqs,
                gain_v,
                label="RealizedGainVertical",
                color=vertical_color,
                linewidth=1.5,
                linestyle="-.",
            )
            has_plot = True

        # 3. 绘制总增益 (Total Gain)
        if self.checkBoxTotal.isChecked():
            # 自动计算 Total = 10*log10(10^(H/10) + 10^(V/10))
            if is_max:
                h_db = self.processor.data_mea_amp[0, 0, :, :, :]
                v_db = self.processor.data_mea_amp[0, 1, :, :, :]
                gain_all_dirs = 10 * np.log10(10 ** (h_db / 10) + 10 ** (v_db / 10))
                gain_total = np.max(gain_all_dirs, axis=(1, 2))
            else:
                h_db = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
                v_db = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
                gain_total = 10 * np.log10(10 ** (h_db / 10) + 10 ** (v_db / 10))

            self.ax.plot(
                freqs,
                gain_total,
                label="RealizedGainTotal",
                color=total_color,
                linewidth=2.5,
                linestyle="--",
            )
            has_plot = True

        if has_plot:
            self.ax.legend()
            self.chartContainer.setEnabled(True)
            self.csvButton.setEnabled(True)
        else:
            self.chartContainer.setEnabled(False)
            self.csvButton.setEnabled(False)

        self.ax.set_title(f"RealizedGain vs Frequency {title_suffix}")
        self.ax.set_xlim([freqs[0], freqs[-1]])
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.set_ylabel("RealizedGain (dBi)")
        self.ax.grid(True)
        self.canvas.draw()

        # 按下“绘制图表”后自动导出图片
        if has_plot:
            if is_max:
                name_suffix = "RealizedGain_Max"
            else:
                name_suffix = (
                    f"RealizedGain_Phi{self.phiComboBox.currentText()}"
                    f"_Theta{self.thetaComboBox.currentText()}"
                )

            series = "".join(
                tag
                for tag, checked in (
                    ("H", self.checkBoxHori.isChecked()),
                    ("V", self.checkBoxVert.isChecked()),
                    ("Tot", self.checkBoxTotal.isChecked()),
                )
                if checked
            )
            auto_save_chart(
                self,
                self.figure,
                chart_base_name(self.processor, f"{name_suffix}_{series}"),
            )

    def export_csv(self):
        if self.processor.data_mea_amp is None:
            return

        is_max = self.checkBoxMax.isChecked()
        freqs = self.processor.freq

        import os

        base_name = ""
        if self.processor.file_path:
            base_name = (
                os.path.splitext(os.path.basename(self.processor.file_path))[0] + "_"
            )

        default_name = f"{base_name}RealizedGain"

        if not is_max:
            phi_idx = self.phiComboBox.currentIndex()
            theta_idx = self.thetaComboBox.currentIndex()
            if phi_idx < 0 or theta_idx < 0:
                # 下拉框为空（如数据未加载或被清空），中止导出
                return
            default_name += f"_Phi{self.phiComboBox.currentText()}_Theta{self.thetaComboBox.currentText()}"
        else:
            default_name += "_Max"

        data_dict = {"Frequency(MHz)": freqs}

        if self.checkBoxHori.isChecked():
            if is_max:
                gain_h = np.max(self.processor.data_mea_amp[0, 0, :, :, :], axis=(1, 2))
            else:
                gain_h = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
            data_dict["RealizedGainHorizontal(dBi)"] = gain_h
            default_name += "_H"

        if self.checkBoxVert.isChecked():
            if is_max:
                gain_v = np.max(self.processor.data_mea_amp[0, 1, :, :, :], axis=(1, 2))
            else:
                gain_v = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
            data_dict["RealizedGainVertical(dBi)"] = gain_v
            default_name += "_V"

        if self.checkBoxTotal.isChecked():
            if is_max:
                h_db = self.processor.data_mea_amp[0, 0, :, :, :]
                v_db = self.processor.data_mea_amp[0, 1, :, :, :]
                gain_all_dirs = 10 * np.log10(10 ** (h_db / 10) + 10 ** (v_db / 10))
                gain_total = np.max(gain_all_dirs, axis=(1, 2))
            else:
                h_db = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
                v_db = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
                gain_total = 10 * np.log10(10 ** (h_db / 10) + 10 ** (v_db / 10))
            data_dict["RealizedGainTotal(dBi)"] = gain_total
            default_name += "_Tot"

        default_name += ".csv"

        import csv
        import os

        base_dir = (
            os.path.dirname(self.processor.file_path)
            if self.processor.file_path
            else ""
        )
        default_path = os.path.join(base_dir, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", default_path, "CSV Files (*.csv)"
        )
        if file_path:
            keys = list(data_dict.keys())
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(keys)
                for i in range(len(freqs)):
                    row = [data_dict[k][i] for k in keys]
                    writer.writerow(row)


class AnalysisPatternInterface(QWidget, Ui_AnalysisPatternInterface):
    def __init__(self, processor: DataProcessor, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.processor = processor

        # 1. 初始化 ComboBox 选项
        self.planeComboBox.addItems(
            [
                "Phi = 0°",
                "Phi = 90°",
                "Theta = 90°",
            ]
        )

        # 2. 连接切换信号
        self.planeComboBox.currentIndexChanged.connect(self.on_plane_changed)

        # 3. 设置默认图片
        self.update_schematic("assets/phi0.png")

        # 默认勾选 checkBoxTotal
        self.checkBoxTotal.setChecked(True)

        # 布局 Matplotlib (极坐标)
        self.figure = plt.figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111, projection="polar")
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.chartContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # 初始状态下禁用绘制按钮
        self.plotButton.setEnabled(False)
        self.plotButton.clicked.connect(self.update_plot)
        self.chartContainer.setEnabled(False)
        self.csvButton.setEnabled(False)
        self.csvButton.clicked.connect(self.export_csv)

    def refresh_comboboxes(self):
        """当文件加载后，更新下拉列表并启用按钮"""
        if self.processor.freq is not None:
            self.freqComboBox.clear()
            self.freqComboBox.addItems([str(f) for f in self.processor.freq])
            # 启用绘制按钮
            self.plotButton.setEnabled(True)

    def on_plane_changed(self, index):
        """根据索引切换图片"""
        mapping = {
            0: "assets/phi0.png",
            1: "assets/phi90.png",
            2: "assets/theta90.png",
        }
        image_path = mapping.get(index)
        if image_path:
            self.update_schematic(image_path)

    def update_plot(self):
        if self.processor.data_mea_amp is None:
            return

        freq_idx = self.freqComboBox.currentIndex()
        if freq_idx < 0:
            return
        plane_idx = self.planeComboBox.currentIndex()

        self.ax.clear()
        has_plot = False
        # 读取设置中的线条颜色
        horizontal_color, vertical_color, total_color = plot_line_colors()

        # 根据选中的平面确定角度和数据索引
        plane_name = self.planeComboBox.currentText()
        try:
            if plane_idx == 0:  # Phi = 0
                angles = np.radians(self.processor.theta)
                phi_idx = np.where(self.processor.phi == 0)[0][0]
                label_suffix = "(Phi=0)"
                d_h = self.processor.data_mea_amp[0, 0, freq_idx, :, phi_idx]
                d_v = self.processor.data_mea_amp[0, 1, freq_idx, :, phi_idx]
            elif plane_idx == 1:  # Phi = 90
                angles = np.radians(self.processor.theta)
                phi_idx = np.where(self.processor.phi == 90)[0][0]
                label_suffix = "(Phi=90)"
                d_h = self.processor.data_mea_amp[0, 0, freq_idx, :, phi_idx]
                d_v = self.processor.data_mea_amp[0, 1, freq_idx, :, phi_idx]
            else:  # Theta = 90
                angles = np.radians(self.processor.phi)
                theta_idx = np.where(self.processor.theta == 90)[0][0]
                label_suffix = "(Theta=90)"
                d_h = self.processor.data_mea_amp[0, 0, freq_idx, theta_idx, :]
                d_v = self.processor.data_mea_amp[0, 1, freq_idx, theta_idx, :]
        except IndexError:
            # 数据中不存在所选切面（如 phi 中没有 0/90 或 theta 中没有 90），
            # 弹出与导出失败同样的提示并中止绘制
            show_export_feedback(
                self,
                error=f"数据中不存在切面 {plane_name}，无法绘制",
                title="方向图绘制失败",
            )
            self.canvas.draw()  # ax 已被 clear，重绘以刷新画布
            return

        # 绘制
        if self.checkBoxHori.isChecked():
            self.ax.plot(
                angles,
                d_h,
                label=f"RealizedGainH {label_suffix}",
                color=horizontal_color,
                linewidth=1.5,
            )
            has_plot = True

        if self.checkBoxVert.isChecked():
            self.ax.plot(
                angles,
                d_v,
                label=f"RealizedGainV {label_suffix}",
                color=vertical_color,
                linewidth=1.5,
                linestyle="-.",
            )
            has_plot = True

        if self.checkBoxTotal.isChecked():
            gain_total = 10 * np.log10(10 ** (d_h / 10) + 10 ** (d_v / 10))
            self.ax.plot(
                angles,
                gain_total,
                label=f"RealizedGainTotal {label_suffix}",
                color=total_color,
                linewidth=2.5,
                linestyle="--",
            )
            has_plot = True

        if has_plot:
            self.ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
            self.chartContainer.setEnabled(True)
            self.csvButton.setEnabled(True)
        else:
            self.chartContainer.setEnabled(False)
            self.csvButton.setEnabled(False)

        self.ax.set_theta_zero_location("N")  # 0度向上
        self.ax.set_theta_direction(-1)  # 顺时针
        self.ax.set_title(f"Radiation Pattern at {self.freqComboBox.currentText()} MHz")
        self.canvas.draw()

        # 按下“绘制图表”后自动导出图片
        if has_plot:
            freq = self.processor.freq[freq_idx]
            plane_tag = ("Phi0", "Phi90", "Theta90")[plane_idx]
            series = "".join(
                tag
                for tag, checked in (
                    ("H", self.checkBoxHori.isChecked()),
                    ("V", self.checkBoxVert.isChecked()),
                    ("Tot", self.checkBoxTotal.isChecked()),
                )
                if checked
            )
            auto_save_chart(
                self,
                self.figure,
                chart_base_name(
                    self.processor, f"Pattern_{freq}MHz_{plane_tag}_{series}"
                ),
            )

    def update_schematic(self, path):
        """更新 ImageLabel 的图片"""
        # ImageLabel 会自动处理圆角和缩放
        self.schematicLabel.setImage(path)
        # 如果需要固定大小不拉伸，可以设置
        self.schematicLabel.setFixedSize(150, 150)

    def export_csv(self):
        if self.processor.data_mea_amp is None:
            return

        freq_idx = self.freqComboBox.currentIndex()
        if freq_idx < 0:
            return
        freq = self.processor.freq[freq_idx]
        plane_idx = self.planeComboBox.currentIndex()

        import os

        base_name = ""
        if self.processor.file_path:
            base_name = (
                os.path.splitext(os.path.basename(self.processor.file_path))[0] + "_"
            )

        default_name = f"{base_name}Pattern_{freq}MHz"

        plane_name = self.planeComboBox.currentText()
        try:
            if plane_idx == 0:
                default_name += "_Phi0"
                angles_deg = self.processor.theta
                phi_idx = np.where(self.processor.phi == 0)[0][0]
                d_h = self.processor.data_mea_amp[0, 0, freq_idx, :, phi_idx]
                d_v = self.processor.data_mea_amp[0, 1, freq_idx, :, phi_idx]
                angle_col = "Theta(deg)"
            elif plane_idx == 1:
                default_name += "_Phi90"
                angles_deg = self.processor.theta
                phi_idx = np.where(self.processor.phi == 90)[0][0]
                d_h = self.processor.data_mea_amp[0, 0, freq_idx, :, phi_idx]
                d_v = self.processor.data_mea_amp[0, 1, freq_idx, :, phi_idx]
                angle_col = "Theta(deg)"
            else:
                default_name += "_Theta90"
                angles_deg = self.processor.phi
                theta_idx = np.where(self.processor.theta == 90)[0][0]
                d_h = self.processor.data_mea_amp[0, 0, freq_idx, theta_idx, :]
                d_v = self.processor.data_mea_amp[0, 1, freq_idx, theta_idx, :]
                angle_col = "Phi(deg)"
        except IndexError:
            # 数据中不存在所选切面，弹出与导出失败同样的提示并中止导出
            show_export_feedback(
                self,
                error=f"数据中不存在切面 {plane_name}，无法导出",
                title="方向图导出失败",
            )
            return

        data_dict = {angle_col: angles_deg}

        if self.checkBoxHori.isChecked():
            default_name += "_H"
            data_dict["RealizedGainHorizontal(dBi)"] = d_h
        if self.checkBoxVert.isChecked():
            default_name += "_V"
            data_dict["RealizedGainVertical(dBi)"] = d_v
        if self.checkBoxTotal.isChecked():
            default_name += "_Tot"
            gain_total = 10 * np.log10(10 ** (d_h / 10) + 10 ** (d_v / 10))
            data_dict["RealizedGainTotal(dBi)"] = gain_total

        default_name += ".csv"

        import csv
        import os

        base_dir = (
            os.path.dirname(self.processor.file_path)
            if self.processor.file_path
            else ""
        )
        default_path = os.path.join(base_dir, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", default_path, "CSV Files (*.csv)"
        )
        if file_path:
            keys = list(data_dict.keys())
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(keys)
                for i in range(len(angles_deg)):
                    row = [data_dict[k][i] for k in keys]
                    writer.writerow(row)


class Analysis3DPatternInterface(QWidget, Ui_Analysis3DPatternInterface):
    def __init__(self, processor: DataProcessor, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.processor = processor

        # 设置复选框互斥
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.checkBoxHori)
        self.buttonGroup.addButton(self.checkBoxVert)
        self.buttonGroup.addButton(self.checkBoxTotal)
        self.buttonGroup.setExclusive(True)

        # 默认勾选 checkBoxTotal
        self.checkBoxTotal.setChecked(True)

        # 布局 Matplotlib (3D)
        self.figure = plt.figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(projection="3d")
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.chartContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.colorbar = None

        # 初始状态下禁用绘制按钮
        self.plotButton.setEnabled(False)
        self.plotButton.clicked.connect(self.update_plot)

    def refresh_comboboxes(self):
        """当文件加载后，更新下拉列表并启用按钮"""
        if self.processor.freq is not None:
            self.freqComboBox.clear()
            self.freqComboBox.addItems([str(f) for f in self.processor.freq])
            # 启用绘制按钮
            self.plotButton.setEnabled(True)

    def update_plot(self):
        if self.processor.data_mea_amp is None:
            return

        freq_idx = self.freqComboBox.currentIndex()
        if freq_idx < 0:
            return

        self.figure.clear()
        self.ax = self.figure.add_subplot(111, projection="3d")

        try:
            self._plot_3d_pattern(freq_idx)
        except Exception as e:  # noqa: BLE001 绘图失败不应导致程序崩溃
            print(f"3D方向图绘制失败: {e}")
            show_export_feedback(
                self,
                error=e,
                title="3D方向图绘制失败",
            )
            self.canvas.draw()
            return

        # 按下“绘制图表”后自动导出图片
        if self.checkBoxHori.isChecked():
            series = "H"
        elif self.checkBoxVert.isChecked():
            series = "V"
        else:
            series = "Tot"
        freq = self.processor.freq[freq_idx]
        auto_save_chart(
            self,
            self.figure,
            chart_base_name(self.processor, f"3DPattern_{freq}MHz_{series}"),
        )

    def _plot_3d_pattern(self, freq_idx):
        """根据当前选中系列绘制 3D 方向图，数据不满足插值条件时抛出异常"""
        # 1. 获取原始数据 (theta是行, phi是列)
        if self.checkBoxHori.isChecked():
            data = self.processor.data_mea_amp[0, 0, freq_idx, :, :]
            label = "RealizedGainHorizontal"
        elif self.checkBoxVert.isChecked():
            data = self.processor.data_mea_amp[0, 1, freq_idx, :, :]
            label = "RealizedGainVertical"
        else:
            d_h = self.processor.data_mea_amp[0, 0, freq_idx, :, :]
            d_v = self.processor.data_mea_amp[0, 1, freq_idx, :, :]
            data = 10 * np.log10(10 ** (d_h / 10) + 10 ** (d_v / 10))
            label = "RealizedGainTotal"

        # 2. 插值处理：创建密集的经纬度网格 (例如 1度一个点)
        theta_orig = self.processor.theta
        phi_orig = self.processor.phi

        if len(theta_orig) < 4 or len(phi_orig) < 4:
            # 双三次样条插值要求每个方向至少 4 个网格点
            raise ValueError(
                f"网格点数不足：theta={len(theta_orig)}, phi={len(phi_orig)}，"
                "3D 插值需要每个方向至少 4 个点"
            )

        # 定义新的高密度坐标
        theta_new = np.linspace(
            theta_orig.min(), theta_orig.max(), theta_orig.max() - theta_orig.min() + 1
        )
        phi_new = np.linspace(
            phi_orig.min(), phi_orig.max(), phi_orig.max() - phi_orig.min() + 1
        )

        # 执行双三次样条插值
        interp_spline = RectBivariateSpline(theta_orig, phi_orig, data)
        data_interp = interp_spline(theta_new, phi_new)

        # 3. 准备绘图网格
        phi_grid, theta_grid = np.meshgrid(np.radians(phi_new), np.radians(theta_new))

        # 4. 坐标转换 (使用插值后的数据)
        r = data_interp - np.min(data_interp)
        X = r * np.sin(theta_grid) * np.cos(phi_grid)
        Y = r * np.sin(theta_grid) * np.sin(phi_grid)
        Z = r * np.cos(theta_grid)

        # 5. 颜色映射（固定 managua 反转配色）
        norm = plt.Normalize(vmin=np.min(data_interp), vmax=np.max(data_interp))
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=plot_colormap())
        colors = mappable.to_rgba(data_interp)

        # 6. 绘图
        self.ax.plot_surface(
            X,
            Y,
            Z,
            facecolors=colors,
            antialiased=False,
            shade=True,
            edgecolor="none",
            rcount=80,
            ccount=80,
        )

        # 添加颜色条，展示数值对应关系
        self.colorbar = self.figure.colorbar(
            mappable, ax=self.ax, shrink=0.6, aspect=15, pad=0.1
        )
        self.colorbar.set_label("RealizedGain (dBi)")

        self.ax.set_title(
            f"3D Radiation Pattern ({label}) at {self.freqComboBox.currentText()} MHz"
        )
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.canvas.draw()


class PostProcessingInterface(QWidget, Ui_PostProcessingInterface):
    """由离散 3D RealizedGain 与 S1P 求解 Gain / Directivity / Efficiency"""

    def __init__(self, processor: DataProcessor, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.processor = processor

        # 三个结果互斥，默认显示 MaxGain
        self.buttonGroup = QButtonGroup(self)
        self.buttonGroup.addButton(self.checkBoxGain)
        self.buttonGroup.addButton(self.checkBoxDirectivity)
        self.buttonGroup.addButton(self.checkBoxEffeciency)
        self.buttonGroup.setExclusive(True)
        self.checkBoxGain.setChecked(True)

        # 布局 Matplotlib
        self.figure, self.ax = plt.subplots(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout(self.chartContainer)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        # S1P 数据缓存（频率为 MHz，gamma2 = |Γ|²）
        self.s1p_freq = None
        self.s1p_gamma2 = None

        # 初始状态下禁用绘制相关控件
        self.plotButton.setEnabled(False)
        self.csvButton.setEnabled(False)
        self.chartContainer.setEnabled(False)

        # 连接信号
        self.plotButton.clicked.connect(self.update_plot)
        self.csvButton.clicked.connect(self.export_csv)
        self.openS1PButton.clicked.connect(self.on_open_s1p)
        self.S1PPathLineEdit.editingFinished.connect(self.on_s1p_path_edited)
        self.checkBoxNoS1P.stateChanged.connect(self.on_no_s1p_changed)

    def on_no_s1p_changed(self, state):
        """勾选“视RealizedGain为Gain”后，S1P 文本框与浏览按钮失效"""
        is_checked = state == Qt.Checked.value or state == Qt.Checked
        self.S1PPathLineEdit.setDisabled(is_checked)
        self.openS1PButton.setDisabled(is_checked)

    def on_data_loaded(self):
        """主数据加载完成后启用绘制按钮"""
        if self.processor.data_mea_amp is not None:
            self.plotButton.setEnabled(True)

    def on_open_s1p(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 S1P 文件", "", "Touchstone 文件 (*.s1p);;All Files (*)"
        )
        if path:
            self.load_s1p(path)

    def on_s1p_path_edited(self):
        path = self.S1PPathLineEdit.text().strip()
        if path and os.path.isfile(path) and path.lower().endswith(".s1p"):
            self.load_s1p(path)

    def load_s1p(self, path):
        try:
            freqs, gamma2 = parse_s1p(path)
        except Exception as e:  # noqa: BLE001 解析失败仅提示，不影响其他页面
            self.s1p_freq = None
            self.s1p_gamma2 = None
            show_export_feedback(self, error=e, title="S1P 读取失败")
            return

        self.S1PPathLineEdit.setText(path)
        self.s1p_freq = freqs
        self.s1p_gamma2 = gamma2
        print(f"S1P 已加载: {path} ({len(freqs)} 个频点)")

    def solid_angle_weights(self):
        """离散球面的立体角权重 w_ij（完整球面时 Σw ≈ 4π）。

        兼容三种常见角度约定：
        1. 极角 θ∈[0,180°]、方位角 φ∈[0,360°)；
        2. 有符号极角 θ∈[-180°,180°]、φ∈[0,180°]（ EMT 数据，
           θ<0 时方位角折叠到 φ+180°，两个半圈合起来覆盖整圈）；
        3. 仰角 θ∈[-90°,90°]、φ∈[0,360°)（极角 = 90°−θ）。
        """
        theta = np.deg2rad(np.asarray(self.processor.theta, dtype=float))
        phi = np.deg2rad(np.asarray(self.processor.phi, dtype=float))

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
            if np.isclose(span, 2 * np.pi) or (
                signed_full and np.isclose(span, np.pi)
            ):
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

    def compute_metrics(self):
        """返回 (freqs, gain_dBi, directivity_dBi, efficiency, used_s1p)。

        G_re = max(r), D = 4π·max(r)/Σw·r,
        G = G_re/(1-|Γ|²), η_rad = G/D = Σw·r / (4π(1-|Γ|²))。
        勾选“视RealizedGain为Gain”时取 |Γ|=0，此时 G=G_re、η=总效率。
        """
        data = self.processor.data_mea_amp
        # data_mea_amp: [antenna, polar, freq, theta, phi]
        h = data[0, 0]
        v = data[0, 1]
        r = 10 ** (h / 10.0) + 10 ** (v / 10.0)  # 双极化按功率相加
        r_max = np.max(r, axis=(1, 2))
        s = np.sum(r * self.solid_angle_weights()[np.newaxis, :, :], axis=(1, 2))

        no_s1p = self.checkBoxNoS1P.isChecked()
        used_s1p = (not no_s1p) and (self.s1p_freq is not None)
        if used_s1p:
            gamma2 = np.interp(self.processor.freq, self.s1p_freq, self.s1p_gamma2)
            mismatch = np.clip(1.0 - gamma2, 1e-12, 1.0)
        else:
            mismatch = np.ones_like(r_max)

        with np.errstate(divide="ignore", invalid="ignore"):
            gain_db = 10 * np.log10(r_max / mismatch)
            directivity_db = 10 * np.log10(4 * np.pi * r_max / s)
            efficiency = s / (4 * np.pi * mismatch)  # 辐射效率（0~1）

        return self.processor.freq, gain_db, directivity_db, efficiency, used_s1p

    def update_plot(self):
        if self.processor.data_mea_amp is None:
            return

        try:
            freqs, gain_db, directivity_db, efficiency, used_s1p = (
                self.compute_metrics()
            )
        except Exception as e:  # noqa: BLE001 计算失败不应导致程序崩溃
            show_export_feedback(self, error=e, title="后处理计算失败")
            return

        if not used_s1p:
            print("提示: 未使用 S1P（按 |Γ|=0 处理）")

        self.ax.clear()
        horizontal_color, vertical_color, total_color = plot_line_colors()

        if self.checkBoxGain.isChecked():
            self.ax.plot(
                freqs, gain_db, label="Gain", color=total_color, linewidth=2.5
            )
            self.ax.set_ylabel("Gain (dBi)")
            self.ax.set_title("Max Gain vs Frequency")
            tag = "MaxGain"
        elif self.checkBoxDirectivity.isChecked():
            self.ax.plot(
                freqs,
                directivity_db,
                label="Directivity",
                color=horizontal_color,
                linewidth=1.5,
            )
            self.ax.set_ylabel("Directivity (dBi)")
            self.ax.set_title("Max Directivity vs Frequency")
            tag = "MaxDirectivity"
        else:
            self.ax.plot(
                freqs,
                efficiency * 100,
                label="Efficiency",
                color=vertical_color,
                linewidth=1.5,
            )
            self.ax.set_ylabel("Efficiency (%)")
            self.ax.set_title("Efficiency vs Frequency")
            tag = "Efficiency"

        self.ax.set_xlim([freqs[0], freqs[-1]])
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.grid(True)
        self.ax.legend()
        self.canvas.draw()

        self.chartContainer.setEnabled(True)
        self.csvButton.setEnabled(True)

        auto_save_chart(self, self.figure, chart_base_name(self.processor, tag))

    def export_csv(self):
        if self.processor.data_mea_amp is None:
            return

        try:
            freqs, gain_db, directivity_db, efficiency, _ = self.compute_metrics()
        except Exception as e:  # noqa: BLE001
            show_export_feedback(self, error=e, title="数据计算失败")
            return

        import csv

        base_name = ""
        if self.processor.file_path:
            base_name = (
                os.path.splitext(os.path.basename(self.processor.file_path))[0] + "_"
            )

        if self.checkBoxGain.isChecked():
            default_name = f"{base_name}MaxGain.csv"
            data_dict = {"Frequency(MHz)": freqs, "MaxGain(dBi)": gain_db}
        elif self.checkBoxDirectivity.isChecked():
            default_name = f"{base_name}MaxDirectivity.csv"
            data_dict = {
                "Frequency(MHz)": freqs,
                "MaxDirectivity(dBi)": directivity_db,
            }
        else:
            default_name = f"{base_name}Efficiency.csv"
            data_dict = {"Frequency(MHz)": freqs, "Efficiency(%)": efficiency * 100}

        base_dir = (
            os.path.dirname(self.processor.file_path)
            if self.processor.file_path
            else ""
        )
        default_path = os.path.join(base_dir, default_name)

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export CSV", default_path, "CSV Files (*.csv)"
        )
        if file_path:
            keys = list(data_dict.keys())
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(keys)
                for i in range(len(freqs)):
                    writer.writerow([data_dict[k][i] for k in keys])


class MultiSelectSettingCard(SettingCard):
    """支持多选的设置卡片"""

    valueChanged = Signal(list)

    def __init__(
        self,
        configItem,
        icon,
        title,
        content=None,
        options=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.options = list(options or IMAGE_FORMATS)
        self.checkBoxes = []

        for option in self.options:
            checkBox = CheckBox(option, self)
            checkBox.setChecked(option in (qconfig.get(configItem) or []))
            checkBox.stateChanged.connect(self.__onStateChanged)
            self.hBoxLayout.addSpacing(16)
            self.hBoxLayout.addWidget(checkBox, 0, Qt.AlignRight)
            self.checkBoxes.append(checkBox)

        self.hBoxLayout.addSpacing(16)
        configItem.valueChanged.connect(self.setValue)

    def checkedItems(self):
        """按选项顺序返回当前勾选的值"""
        return [checkBox.text() for checkBox in self.checkBoxes if checkBox.isChecked()]

    def __onStateChanged(self, state):
        values = self.checkedItems()

        # 允许全部不勾选：绘制图表时将跳过图片导出
        if qconfig.get(self.configItem) != values:
            qconfig.set(self.configItem, values)

        self.valueChanged.emit(values)

    def setValue(self, values):
        """根据配置值同步勾选状态"""
        values = list(values or [])
        for checkBox in self.checkBoxes:
            checkBox.blockSignals(True)
            checkBox.setChecked(checkBox.text() in values)
            checkBox.blockSignals(False)


class SettingInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 使用垂直布局放置滚动区域
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        # 将原本继承的 ScrollArea 提取为成员变量
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 启用背景透明，使底层的 QWidget 主题白/黑背景可以透出来
        self.scrollArea.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }"
        )
        # self.scrollArea.viewport().setStyleSheet("background-color: transparent;")
        self.vBoxLayout.addWidget(self.scrollArea)

        self.scrollWidget = QWidget()
        self.scrollWidget.setStyleSheet("QWidget { background-color: transparent; }")

        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 1. 绘图设置组
        self.plotGroup = SettingCardGroup("绘图配置", self.scrollWidget)

        # 传入 cfg.plotColor 而不是直接传颜色
        self.colorCard = ColorSettingCard(
            cfg.plotColor,
            FIF.PALETTE,
            "线条颜色",
            "设置默认绘图线条的颜色",
            self.plotGroup,
        )

        # 传入 cfg.isNormalization
        self.normCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            "数据归一化",
            "绘图前是否对数据进行归一化处理",
            configItem=cfg.isNormalization,
            parent=self.plotGroup,
        )
        self.plotGroup.addSettingCard(self.colorCard)
        self.plotGroup.addSettingCard(self.normCard)

        # 2. 输出设置组
        self.outputGroup = SettingCardGroup("导出选项", self.scrollWidget)

        self.pathCard = PushSettingCard(
            "选择目录", FIF.FOLDER, "输出路径", self._path_text(), self.outputGroup
        )

        self.formatCard = MultiSelectSettingCard(
            cfg.outputFormats,
            FIF.PHOTO,
            "图片格式",
            "可同时选择多种格式，绘制图表时自动导出",
            IMAGE_FORMATS,
            self.outputGroup,
        )
        self.outputGroup.addSettingCard(self.pathCard)
        self.outputGroup.addSettingCard(self.formatCard)

        # 将组添加到布局
        self.expandLayout.addWidget(self.plotGroup)
        self.expandLayout.addWidget(self.outputGroup)

        self.scrollArea.setWidget(self.scrollWidget)
        self.setObjectName("settingInterface")

        # 连接信号
        self.pathCard.clicked.connect(self.on_select_path)

    def _path_text(self):
        """输出路径卡片的说明文字"""
        path = cfg.outputPath.value
        if not path:
            return f"当前路径: {os.path.abspath(DEFAULT_OUTPUT_DIR)}（默认）"
        return f"当前路径: {path}"

    def on_select_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "选择输出文件夹", cfg.outputPath.value or ""
        )
        if path:
            qconfig.set(cfg.outputPath, path)
            self.pathCard.setContent(self._path_text())


class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.processor = DataProcessor()  # 公用一个处理器
        self.setWindowTitle("Antenna Test Helper")

        # 1. 创建子页面
        self.homeInterface = HomeInterface(self.processor, self)
        self.gainInterface = AnalysisGainInterface(self.processor, self)
        self.patternInterface = AnalysisPatternInterface(self.processor, self)
        self.p3dInterface = Analysis3DPatternInterface(self.processor, self)
        self.postInterface = PostProcessingInterface(self.processor, self)

        self.settingInterface = SettingInterface(self)

        self.homeInterface.fileLoaded.connect(self.gainInterface.refresh_comboboxes)
        self.homeInterface.fileLoaded.connect(self.patternInterface.refresh_comboboxes)
        self.homeInterface.fileLoaded.connect(self.p3dInterface.refresh_comboboxes)
        self.homeInterface.fileLoaded.connect(self.postInterface.on_data_loaded)

        # 2. 初始化导航栏
        self.init_navigation()

        # 3. 设置窗口大小
        self.resize(900, 700)

    def init_navigation(self):
        # 使用 addSubInterface 将页面添加到侧边导航栏
        # FIF 是 FluentIcon 的缩写，提供了大量的 Fluent 设计风格图标
        self.addSubInterface(self.homeInterface, FIF.HOME, "首页")
        self.addSubInterface(
            self.gainInterface, FIF.CHEVRON_RIGHT_MED, "增益分析"
        )  # 添加到导航
        self.addSubInterface(
            self.patternInterface, FIF.FILTER, "2D方向图"
        )  # 添加到导航
        self.addSubInterface(self.p3dInterface, FIF.FILTER, "3D方向图")  # 添加到导航
        self.addSubInterface(self.postInterface, FIF.DEVELOPER_TOOLS, "后处理")
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置")

        # 你还可以添加带有路由键的页面（如果需要像之前代码那样使用 routeKey）
        # self.addSubInterface(self.homeInterface, FIF.HOME, "首页", routeKey="home")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 读取配置文件，恢复线条颜色、输出路径、图片格式等设置
    qconfig.load("config/config.json", cfg)

    # 设置主题：Light（亮色）, DARK（深色）, AUTO（跟随系统）
    setTheme(Theme.AUTO)

    window = Window()
    window.show()
    sys.exit(app.exec())
