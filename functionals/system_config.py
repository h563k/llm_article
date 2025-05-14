import os
import yaml


class ModelConfig:
    def __init__(self) -> None:
        self.file_path = os.path.abspath(__file__)
        self.file_path = os.path.dirname(os.path.dirname(self.file_path))
        self.configs = self.config_read()
        self.OpenAI = self.configs['OpenAI']
        self.WorkSpace = self.configs['WorkSpace']

    def config_read(self):
        file_path = os.path.join(self.file_path, 'config/setting.yaml')
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        return config


