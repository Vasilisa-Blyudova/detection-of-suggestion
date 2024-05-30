"""
Settings manager.
"""
import json
from pathlib import Path

from pydantic.dataclasses import dataclass
from pydantic.tools import parse_obj_as


@dataclass
class ServiceSettingsModel:
    """
    DTO for storing sevice settings.
    """
    weights: dict
    colors: list
    threshold: float


class ServiceSettings:
    """
    Main model for working with settings.
    """
    # Labs settings
    _dto: ServiceSettingsModel

    def __init__(self, config_path: Path) -> None:
        """
        Initialize ServiceSettings.

        Args:
            config_path (Path): Path to configuration
        """
        super().__init__()
        with config_path.open(encoding='utf-8') as config_file:
            self._dto = parse_obj_as(ServiceSettingsModel, json.load(config_file))

    @property
    def weights(self) -> dict:
        """
        Property for weights.

        Returns:
            dict: Weights for features.
        """
        return self._dto.weights

    @property
    def colors(self) -> list:
        """
        Property for color.

        Returns:
            list: Colors for features.
        """
        return self._dto.colors

    @property
    def threshold(self) -> float:
        """
        Property for color.

        Returns:
            float: Threshold for suggestiveness.
        """
        return self._dto.threshold
