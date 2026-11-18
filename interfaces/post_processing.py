"""后处理页面：由离散 3D RealizedGain 与 S1P 求解 Gain / Directivity / Efficiency。"""

import csv
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QFileDialog, QVBoxLayout, QWidget

import antenna_math
from chart_utils import (
    auto_save_chart,
    chart_base_name,
    plot_line_colors,
    show_export_feedback,
)
from data_processor import DataProcessor
from s1p_parser import parse_s1p
from ui_post_processing_interface import Ui_PostProcessingInterface


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

    def compute_metrics(self):
        """把界面状态打包后交给 antenna_math 中的纯函数计算"""
        return antenna_math.compute_metrics(
            self.processor.data_mea_amp,
            self.processor.theta,
            self.processor.phi,
            self.processor.freq,
            self.s1p_freq,
            self.s1p_gamma2,
            self.checkBoxNoS1P.isChecked(),
        )

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
            self.ax.plot(freqs, gain_db, label="Gain", color=total_color, linewidth=2.5)
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
