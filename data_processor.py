import scipy.io
import numpy as np
import os


class DataProcessor:
    def __init__(self):
        self.raw_data = {}
        self.file_path = ""
        self.data_mea_amp = None
        self.data_mea_phase = None
        self.freq = None
        self.theta = None
        self.phi = None
        self.polar = None

    def load_mat(self, file_path):
        """加载 .mat 文件并返回基本信息列表"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        self.file_path = file_path
        # 加载数据
        self.raw_data = scipy.io.loadmat(file_path)

        info = []
        for key, value in self.raw_data.items():
            if not key.startswith("__"):
                shape = str(value.shape) if hasattr(value, "shape") else "N/A"
                info.append({"name": key, "shape": shape})

        self.data_mea_amp = np.array(self.raw_data["Data_Mea_Amp"])
        self.data_mea_phase = np.array(self.raw_data["Data_Mea_Phase"])
        self.freq = np.array(self.raw_data["Freq"]).flatten().astype(int)
        self.theta = np.array(self.raw_data["Theta"]).flatten().astype(int)
        self.phi = np.array(self.raw_data["Phi"]).flatten().astype(int)
        self.polar = np.array(self.raw_data["polar"]).flatten().astype(str)

        return info
