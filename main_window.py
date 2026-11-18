"""主窗口：装配各功能页面、初始化导航栏并连线 fileLoaded 信号。"""

from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import FluentWindow

from data_processor import DataProcessor
from interfaces.gain import AnalysisGainInterface
from interfaces.home import HomeInterface
from interfaces.pattern_2d import AnalysisPatternInterface
from interfaces.pattern_3d import Analysis3DPatternInterface
from interfaces.post_processing import PostProcessingInterface
from interfaces.settings import SettingInterface


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
