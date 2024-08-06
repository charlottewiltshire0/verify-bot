import yaml
from typing import Any, Dict
from loguru import logger


class Yml:
    def __init__(self, src: str):
        self.src = src

    def load(self) -> Dict[str, Any]:
        """Load YAML data from the file."""
        return self._read_file()

    def read(self) -> Dict[str, Any]:
        """Read YAML data from the file."""
        return self._read_file()

    def write(self, data: Dict[str, Any]) -> None:
        """Write YAML data to the file."""
        self._write_file(data)

    def _read_file(self) -> Dict[str, Any]:
        """Helper method to read YAML data from the file."""
        try:
            with open(self.src, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            logger.error(f"The file {self.src} does not exist.")
            exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error reading YAML file {self.src}: {e}")
            exit(1)

    def _write_file(self, data: Dict[str, Any]) -> None:
        """Helper method to write YAML data to the file."""
        try:
            with open(self.src, 'w') as f:
                yaml.dump(data, f, default_flow_style=False)
        except IOError as e:
            logger.error(f"Error writing to YAML file {self.src}: {e}")
            exit(1)