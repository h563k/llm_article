import os
from functionals.system_config import ModelConfig


def ensure_output_dir():
    """确保输出目录存在"""
    config = ModelConfig()
    output_dir = os.path.join(config.file_path, 'plot', 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def get_output_path(filename):
    """获取输出文件的完整路径"""
    output_dir = ensure_output_dir()
    return os.path.join(output_dir, filename)
