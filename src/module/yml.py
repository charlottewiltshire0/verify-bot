import yaml
from pprint import pprint


class Yml:
    def __init__(self, src):
        self.src = src

    def load(self):
        with open(self.src) as f:
            return yaml.safe_load(f)

    def read(self):
        with open(self.src, 'r') as f:
            return yaml.safe_load(f)

    def write(self, data):
        with open(self.src, 'w') as f:
            yaml.dump(data, f)