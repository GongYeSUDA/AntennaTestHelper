"""3D 方向图页面：插值后的三维辐射曲面绘制与图片导出。"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QButtonGroup, QVBoxLayout, QWidget
from scipy.interpolate import RectBivariateSpline

from chart_utils import (
    auto_save_chart,
    chart_base_name,
    plot_colormap,
    show_export_feedback,
)
from data_processor import DataProcessor
from ui_analysis_3dpattern_interface import Ui_Analysis3DPatternInterface


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
