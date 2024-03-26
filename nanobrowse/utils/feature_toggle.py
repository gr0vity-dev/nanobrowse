from os import environ as os_environ
from utils.logger import logger


class FeatureToggle:

    def __init__(self, prefix="FEATURE_"):
        self.prefix = prefix
        self.toggles = self._load_feature_toggles()

    def _load_feature_toggles(self):
        """Load feature toggles based on environment variables with a specific prefix."""
        toggles = {}
        for key, value in os_environ.items():
            if key.startswith(self.prefix):
                feature_name = key[len(self.prefix):].lower()
                toggles[feature_name] = str(value).lower() in [
                    "true", "1", "t"]
        return toggles

    def is_enabled(self, feature_name):
        """Check if a feature is enabled based on its name."""
        return self.toggles.get(feature_name.lower(), False)

    def log_feature_statuses(self):
        """Log the status of all feature toggles."""
        for feature, is_enabled in self.toggles.items():
            logger.info(
                f"Feature '%s': {'Enabled' if is_enabled else 'Disabled'}", feature)
