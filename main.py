import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QTableWidgetItem,
    QHeaderView,
)
from qfluentwidgets import FluentWindow, FluentIcon as FIF
from ui_home_interface import Ui_HomeInterface
from data_processor import DataProcessor


class HomeInterface(QWidget, Ui_HomeInterface):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.processor = DataProcessor()

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
            if file_path.endswith(".mat"):
                self.process_file(file_path)


class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antenna Test Helper")

        # 1. 创建子页面
        self.homeInterface = HomeInterface(self)
        self.homeInterface.setObjectName("homeInterface")

        self.settingInterface = QWidget()
        self.settingInterface.setObjectName("settingInterface")
        self.set_up_dummy_page(self.settingInterface, "设置页面")

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
