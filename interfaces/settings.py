"""设置页面：绘图颜色/归一化、输出路径与多图片格式选择。"""

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QWidget
from qfluentwidgets import (
    CheckBox,
    ColorSettingCard,
    ExpandLayout,
    PushSettingCard,
    ScrollArea,
    SettingCard,
    SettingCardGroup,
    SwitchSettingCard,
    qconfig,
)
from qfluentwidgets import FluentIcon as FIF

from app_config import DEFAULT_OUTPUT_DIR, IMAGE_FORMATS, cfg


class MultiSelectSettingCard(SettingCard):
    """支持多选的设置卡片"""

    valueChanged = Signal(list)

    def __init__(
        self,
        configItem,
        icon,
        title,
        content=None,
        options=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.options = list(options or IMAGE_FORMATS)
        self.checkBoxes = []

        for option in self.options:
            checkBox = CheckBox(option, self)
            checkBox.setChecked(option in (qconfig.get(configItem) or []))
            checkBox.stateChanged.connect(self.__onStateChanged)
            self.hBoxLayout.addSpacing(16)
            self.hBoxLayout.addWidget(checkBox, 0, Qt.AlignRight)
            self.checkBoxes.append(checkBox)

        self.hBoxLayout.addSpacing(16)
        configItem.valueChanged.connect(self.setValue)

    def checkedItems(self):
        """按选项顺序返回当前勾选的值"""
        return [checkBox.text() for checkBox in self.checkBoxes if checkBox.isChecked()]

    def __onStateChanged(self, state):
        values = self.checkedItems()

        # 允许全部不勾选：绘制图表时将跳过图片导出
        if qconfig.get(self.configItem) != values:
            qconfig.set(self.configItem, values)

        self.valueChanged.emit(values)

    def setValue(self, values):
        """根据配置值同步勾选状态"""
        values = list(values or [])
        for checkBox in self.checkBoxes:
            checkBox.blockSignals(True)
            checkBox.setChecked(checkBox.text() in values)
            checkBox.blockSignals(False)


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
            "选择目录", FIF.FOLDER, "输出路径", self._path_text(), self.outputGroup
        )

        self.formatCard = MultiSelectSettingCard(
            cfg.outputFormats,
            FIF.PHOTO,
            "图片格式",
            "可同时选择多种格式，绘制图表时自动导出",
            IMAGE_FORMATS,
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

    def _path_text(self):
        """输出路径卡片的说明文字"""
        path = cfg.outputPath.value
        if not path:
            return f"当前路径: {os.path.abspath(DEFAULT_OUTPUT_DIR)}（默认）"
        return f"当前路径: {path}"

    def on_select_path(self):
        path = QFileDialog.getExistingDirectory(
            self, "选择输出文件夹", cfg.outputPath.value or ""
        )
        if path:
            qconfig.set(cfg.outputPath, path)
            self.pathCard.setContent(self._path_text())
