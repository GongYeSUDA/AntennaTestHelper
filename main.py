import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from qfluentwidgets import FluentWindow, FluentIcon as FIF
# 如果你的子页面内容写在 ui_mainwindow.py 中，可以导入；
# 但通常使用 FluentWindow 时，我们会为每个页面创建独立的类。
# from ui_mainwindow import Ui_MainWindow


class Window(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Antenna Test Helper")

        # 1. 创建子页面
        # 在实际项目中，建议将这些页面定义为独立的 QWidget 类
        self.homeInterface = QWidget()
        self.homeInterface.setObjectName("homeInterface")
        self.set_up_dummy_page(self.homeInterface, "首页内容")

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
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
