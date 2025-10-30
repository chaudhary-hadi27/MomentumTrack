import json
import os


class AppSettings:
    def __init__(self):
        self.settings_file = 'data/app_settings.json'
        self.default_settings = {
            'theme': 'Light',
            'notification_sound': 'default',
            'progress_threshold': 60,
            'reminder_interval': 30,
            'motivational_mode': True
        }
        self._ensure_settings_file()

    def _ensure_settings_file(self):
        """Create settings file if it doesn't exist"""
        os.makedirs('data', exist_ok=True)
        if not os.path.exists(self.settings_file):
            self._save_settings(self.default_settings)

    def _load_settings(self):
        """Load settings from file"""
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except:
            return self.default_settings

    def _save_settings(self, settings):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_theme(self):
        """Get current theme"""
        settings = self._load_settings()
        return settings.get('theme', 'Light')

    def save_theme(self, theme):
        """Save theme preference"""
        settings = self._load_settings()
        settings['theme'] = theme
        self._save_settings(settings)

    def get_all_settings(self):
        """Get all settings"""
        return self._load_settings()

    def update_setting(self, key, value):
        """Update a specific setting"""
        settings = self._load_settings()
        settings[key] = value
        self._save_settings(settings)