"""Antenna Test Helper 程序入口。"""

import sys

from PySide6.QtWidgets import QApplication
from qfluentwidgets import Theme, qconfig, setTheme

from app_config import cfg
from main_window import Window

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 读取配置文件，恢复线条颜色、输出路径、图片格式等设置
    qconfig.load("config/config.json", cfg)

    # 设置主题：Light（亮色）, DARK（深色）, AUTO（跟随系统）
    setTheme(Theme.AUTO)

    window = Window()
    window.show()
    sys.exit(app.exec())
