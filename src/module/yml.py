import yaml
from pprint import pprint

class Yml:
    def __init__(self, src):
        self.src = src

    def load(self, src):
        with open(src) as f:
            templates = yaml.safe_load(f)
