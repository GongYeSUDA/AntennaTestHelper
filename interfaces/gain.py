"""增益分析页面：RealizedGain 随频率变化的曲线绘制与 CSV 导出。"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from chart_utils import auto_save_chart, chart_base_name, plot_line_colors
from data_processor import DataProcessor
from ui_analysis_gain_interface import Ui_AnalysisGainInterface


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
