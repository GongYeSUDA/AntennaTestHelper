"""应用配置：可导出格式、输出目录常量、配置校验器与全局 cfg。"""

from pathlib import Path

from PySide6.QtGui import QColor
from qfluentwidgets import ColorConfigItem, ConfigItem, ConfigValidator, QConfig

# 可导出/保存的图片格式
IMAGE_FORMATS = ["PNG", "JPG", "PDF", "SVG"]
# 未指定输出路径时使用的默认目录
DEFAULT_OUTPUT_DIR = "output"


class MultiOptionsValidator(ConfigValidator):
    """多选选项校验器"""

    def __init__(self, options):
        self.options = list(options)

    def validate(self, value):
        # 允许空列表（未勾选任何格式时跳过导出）
        return isinstance(value, (list, tuple)) and all(
            v in self.options for v in value
        )

    def correct(self, value):
        if isinstance(value, str):
            value = [value]

        if not isinstance(value, (list, tuple)):
            return [self.options[0]]

        # 去重并按选项顺序排列，避免传入非法值
        return [option for option in self.options if option in value]


class OutputFolderValidator(ConfigValidator):
    """输出目录校验器，允许为空（为空时使用默认目录）"""

    def validate(self, value):
        return isinstance(value, str)

    def correct(self, value):
        if not value:
            return ""

        path = Path(value)
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            return ""

        return str(path.absolute()).replace("\\", "/")


class AppConfig(QConfig):
    """应用配置类"""

    # 绘图颜色
    plotColor = ColorConfigItem("Plot", "Color", QColor(0, 0, 255))
    # 归一化
    isNormalization = ConfigItem("Plot", "IsNormalization", False)
    # 图片输出路径
    outputPath = ConfigItem("Output", "Path", "", OutputFolderValidator())
    # 图片输出格式（多选）
    outputFormats = ConfigItem(
        "Output", "Formats", [IMAGE_FORMATS[0]], MultiOptionsValidator(IMAGE_FORMATS)
    )


cfg = AppConfig()
