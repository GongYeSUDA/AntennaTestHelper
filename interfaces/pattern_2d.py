"""2D 方向图页面：极坐标辐射方向图绘制与 CSV 导出。"""

import csv
import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget

from chart_utils import (
    auto_save_chart,
    chart_base_name,
    plot_line_colors,
    show_export_feedback,
)
from data_processor import DataProcessor
from ui_analysis_pattern_interface import Ui_AnalysisPatternInterface


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
