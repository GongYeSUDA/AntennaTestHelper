import sys
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QTableWidgetItem,
    QHeaderView,
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from qfluentwidgets import FluentWindow, FluentIcon as FIF
from ui_home_interface import Ui_HomeInterface
from ui_analysis_gain_interface import Ui_AnalysisGainInterface  # 导入新生成的 UI
from data_processor import DataProcessor


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
            self.ax.plot(freqs, gain_h, label="GainHorizontal")
            has_plot = True

        # 2. 绘制垂直极化 (Vertical/Phi)
        if self.checkBoxVert.isChecked():
            # 假设极化索引 1 是垂直极化
            gain_v = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
            self.ax.plot(freqs, gain_v, label="GainVertical")
            has_plot = True

        # 3. 绘制总增益 (Total Gain)
        if self.checkBoxTotal.isChecked():
            # 自动计算 Total = 10*log10(10^(H/10) + 10^(V/10))
            h_db = self.processor.data_mea_amp[0, 0, :, theta_idx, phi_idx]
            v_db = self.processor.data_mea_amp[0, 1, :, theta_idx, phi_idx]
            gain_total = 10 * np.log10(10 ** (h_db / 10) + 10 ** (v_db / 10))

            self.ax.plot(
                freqs, gain_total, label="GainTotal", linewidth=2, linestyle="--"
            )
            has_plot = True

        if has_plot:
            self.ax.legend()

        self.ax.set_title(
            f"Gain vs Frequency (Phi={self.phiComboBox.currentText()}, Theta={self.thetaComboBox.currentText()})"
        )
        self.ax.set_xlim([freqs[0], freqs[-1]])
        self.ax.set_xlabel("Frequency (MHz)")
        self.ax.set_ylabel("Gain (dB)")
        self.ax.grid(True)
        self.canvas.draw()


class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.processor = DataProcessor()  # 公用一个处理器
        self.setWindowTitle("Antenna Test Helper")

        # 1. 创建子页面
        self.homeInterface = HomeInterface(self.processor, self)
        # self.homeInterface.setObjectName("homeInterface")

        self.gainInterface = AnalysisGainInterface(self.processor, self)  # 实例化新页面
        # self.homeInterface.setObjectName("analysisgaininterface")

        self.settingInterface = QWidget()
        self.settingInterface.setObjectName("settingInterface")
        self.set_up_dummy_page(self.settingInterface, "设置页面")

        self.homeInterface.fileLoaded.connect(self.gainInterface.refresh_comboboxes)

        # 2. 初始化导航栏
        self.init_navigation()

        # 3. 设置窗口大小
        self.resize(900, 700)

    def set_up_dummy_page(self, widget, text):
        """给测试页面添加一些简单的内容"""
        layout = QVBoxLayout(widget)
        label = QLabel(text, widget)
        label.setAlignment(Qt.AlignCenter)
        # 设置一点样式
        label.setStyleSheet("font: 30px 'Microsoft YaHei';")
        layout.addWidget(label)

    def init_navigation(self):
        # 使用 addSubInterface 将页面添加到侧边导航栏
        # FIF 是 FluentIcon 的缩写，提供了大量的 Fluent 设计风格图标
        self.addSubInterface(self.homeInterface, FIF.HOME, "首页")
        self.addSubInterface(
            self.gainInterface, FIF.CHEVRON_RIGHT_MED, "增益分析"
        )  # 添加到导航
        self.addSubInterface(self.settingInterface, FIF.SETTING, "设置")

        # 你还可以添加带有路由键的页面（如果需要像之前代码那样使用 routeKey）
        # self.addSubInterface(self.homeInterface, FIF.HOME, "首页", routeKey="home")


if __name__ == "__main__":
    # 适配高分屏缩放
    # QApplication.setHighDpiScaleFactorRoundingPolicy(
    #     Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    # )
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
