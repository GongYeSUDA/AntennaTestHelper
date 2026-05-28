import sys
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    # QLabel,
    QFileDialog,
    QTableWidgetItem,
    QHeaderView,
    QButtonGroup,
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from qfluentwidgets import (
    ScrollArea,
    SettingCardGroup,
    SwitchSettingCard,
    ComboBoxSettingCard,
    PushSettingCard,
    ExpandLayout,
    FluentIcon as FIF,
    ColorSettingCard,
    FluentWindow,
    setTheme,
    Theme,
    QConfig,
    ConfigItem,
    OptionsConfigItem,
    ColorConfigItem,
    OptionsValidator,
    # ImageLabel,
)
from PySide6.QtGui import QColor
from ui_home_interface import Ui_HomeInterface
from ui_analysis_gain_interface import Ui_AnalysisGainInterface  # 导入新生成的 UI
from ui_analysis_pattern_interface import Ui_AnalysisPatternInterface
from ui_analysis_3dpattern_interface import Ui_Analysis3DPatternInterface
from data_processor import DataProcessor


class AppConfig(QConfig):
    """应用配置类"""

    # 绘图颜色
    plotColor = ColorConfigItem("Plot", "Color", QColor(0, 0, 255))
    # 归一化
    isNormalization = ConfigItem("Plot", "IsNormalization", False)
    # 输出格式
    outputFormat = OptionsConfigItem(
        "Output", "Format", "PNG", OptionsValidator(["PNG", "JPG", "PDF", "SVG"])
    )


cfg = AppConfig()


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

        # 获取选中的索引
        phi_idx = self.phiComboBox.currentIndex()
        theta_idx = self.thetaComboBox.currentIndex()
        freqs = self.processor.freq

        self.ax.clear()
        has_plot = False

        # 1. 绘制水平极化 (Horizontal/Theta)
        if self.checkBoxHori.isChecked():
            gain_h = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
            self.ax.plot(freqs, gain_h, label="RealizedGainHorizontal")
            has_plot = True

        # 2. 绘制垂直极化 (Vertical/Phi)
        if self.checkBoxVert.isChecked():
            # 假设极化索引 1 是垂直极化
            gain_v = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
            self.ax.plot(freqs, gain_v, label="RealizedGainVertical")
            has_plot = True

        # 3. 绘制总增益 (Total Gain)
        if self.checkBoxTotal.isChecked():
            # 自动计算 Total = 10*log10(10^(H/10) + 10^(V/10))
            h_db = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
            v_db = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
            gain_total = 10 * np.log10(10 ** (h_db / 10) + 10 ** (v_db / 10))

            self.ax.plot(
                freqs,
                gain_total,
                label="RealizedGainTotal",
                linewidth=2,
                linestyle="--",
            )
            has_plot = True

        if has_plot:
            self.ax.legend()

        self.ax.set_title(
            f"RealizedGain vs Frequency (Phi={self.phiComboBox.currentText()}, Theta={self.thetaComboBox.currentText()})"
        )
        self.ax.set_xlim([freqs[0], freqs[-1]])
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.set_ylabel("RealizedGain (dB)")
        self.ax.grid(True)
        self.canvas.draw()


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
        plane_idx = self.planeComboBox.currentIndex()

        self.ax.clear()
        has_plot = False

        # 根据选中的平面确定角度和数据索引
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

        # 绘制
        if self.checkBoxHori.isChecked():
            self.ax.plot(angles, d_h, label=f"RealizedGainH {label_suffix}")
            has_plot = True

        if self.checkBoxVert.isChecked():
            self.ax.plot(angles, d_v, label=f"RealizedGainV {label_suffix}")
            has_plot = True

        if self.checkBoxTotal.isChecked():
            gain_total = 10 * np.log10(10 ** (d_h / 10) + 10 ** (d_v / 10))
            self.ax.plot(
                angles,
                gain_total,
                label=f"RealizedGainTotal {label_suffix}",
                linewidth=2,
                linestyle="--",
            )
            has_plot = True

        if has_plot:
            self.ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))

        self.ax.set_theta_zero_location("N")  # 0度向上
        self.ax.set_theta_direction(-1)  # 顺时针
        self.ax.set_title(f"Radiation Pattern at {self.freqComboBox.currentText()} MHz")
        self.canvas.draw()

    def update_schematic(self, path):
        """更新 ImageLabel 的图片"""
        # ImageLabel 会自动处理圆角和缩放
        self.schematicLabel.setImage(path)
        # 如果需要固定大小不拉伸，可以设置
        self.schematicLabel.setFixedSize(150, 150)


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
        self.ax = self.figure.add_subplot(111, projection="3d")
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
        self.ax.clear()

        # 获取数据 [antenna, polar, freq, theta, phi]
        if self.checkBoxHori.isChecked():
            data = self.processor.data_mea_amp[0, 0, freq_idx, :, :]
            label = "RealizedGainHorizontal"
        elif self.checkBoxVert.isChecked():
            data = self.processor.data_mea_amp[0, 1, freq_idx, :, :]
            label = "RealizedGainVertical"
        else:  # checkBoxTotal
            d_h = self.processor.data_mea_amp[0, 0, freq_idx, :, :]
            d_v = self.processor.data_mea_amp[0, 1, freq_idx, :, :]
            data = 10 * np.log10(10 ** (d_h / 10) + 10 ** (d_v / 10))
            label = "RealizedGainTotal"

        # 准备网格数据 (theta是行, phi是列)
        phi_grid, theta_grid = np.meshgrid(
            np.radians(self.processor.phi), np.radians(self.processor.theta)
        )

        # 转换坐标: R 需要为正值，这里使用 (data - min) 或者直接用线性增益
        # 为了保留方向性，通常将 dB 映射到大于0的范围
        r = data - np.min(data)

        X = r * np.sin(theta_grid) * np.cos(phi_grid)
        Y = r * np.sin(theta_grid) * np.sin(phi_grid)
        Z = r * np.cos(theta_grid)

        # 移除旧的 colorbar
        if self.colorbar:
            self.colorbar.remove()
            self.colorbar = None

        # 归一化数据用于颜色映射（使用原始 dB 数据）
        norm = plt.Normalize(vmin=np.min(data), vmax=np.max(data))
        mappable = plt.cm.ScalarMappable(norm=norm, cmap="jet")
        # 将数据映射到颜色
        colors = mappable.to_rgba(data)

        # 绘制表面，增加采样率使更平滑，并根据 Gain 值着色
        surf = self.ax.plot_surface(
            X,
            Y,
            Z,
            facecolors=colors,
            antialiased=True,
            rcount=100,  # 提高采样密度，使图形更平滑
            ccount=100,
            edgecolor="none",
            shade=True,  # 开启阴影以增强立体感
        )

        # 添加颜色条，展示数值对应关系
        self.colorbar = self.figure.colorbar(
            mappable, ax=self.ax, shrink=0.6, aspect=15, pad=0.1
        )
        self.colorbar.set_label("Gain (dB)")

        self.ax.set_title(
            f"3D Radiation Pattern ({label}) at {self.freqComboBox.currentText()} MHz"
        )
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")
        self.canvas.draw()


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
            "选择目录", FIF.FOLDER, "输出路径", "当前路径: ./output", self.outputGroup
        )

        # 传入 cfg.outputFormat
        self.formatCard = ComboBoxSettingCard(
            cfg.outputFormat,
            FIF.PHOTO,
            "图片格式",
            "选择保存图片的后缀名",
            ["PNG", "JPG", "PDF", "SVG"],
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

    def on_select_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if path:
            self.pathCard.setContent(f"当前路径: {path}")


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

        self.settingInterface = SettingInterface(self)

        self.homeInterface.fileLoaded.connect(self.gainInterface.refresh_comboboxes)
        self.homeInterface.fileLoaded.connect(self.patternInterface.refresh_comboboxes)
        self.homeInterface.fileLoaded.connect(self.p3dInterface.refresh_comboboxes)

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
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置")

        # 你还可以添加带有路由键的页面（如果需要像之前代码那样使用 routeKey）
        # self.addSubInterface(self.homeInterface, FIF.HOME, "首页", routeKey="home")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置主题：Light（亮色）, DARK（深色）, AUTO（跟随系统）
    setTheme(Theme.LIGHT)

    window = Window()
    window.show()
    sys.exit(app.exec())
