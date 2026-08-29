""" Module: Protonabu Lightweight Configuration
    - Intent: Standalone JSON-based configuration provider for Protonabu
    - Author: Avner Ben
        - Created: 28-Aug-2026
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Generated: 28-Aug-2026
"""

import json
import os
from pathlib import Path
import platform
import shutil
from typing import Any, Optional


class ProtonabuConfigurator:
    """ Protonabu Configurator
        - Intent: to load and query lightweight JSON configuration
        - Stereotype: Singleton
    """

    def __init__(self, configPath: Optional[Path | str] = None):
        """ to INITIALIZE Protonabu Configurator
            - Exported
            - Input [Opt "None"]: config Path
        """
        self._data: dict[str, dict[str, Any]] = {}
        # [Alt]: to load explicit config path
        if configPath:
            # [Msg]: to load configuration from JSON file
            self.load(configPath)
        # [Alt]: to discover and load configuration file
        else:
            self._discoverAndLoad()

    def _discoverAndLoad(self):
        """ to discover and load configuration file
        """
        # to get environment configuration path
        env_path = os.environ.get('PROTONABU_CONFIG')
        # [Opt]: to load configuration from environment
        if env_path and os.path.exists(env_path):
            # [Msg]: to load configuration from JSON file
            self.load(env_path)
            return

        # to get local configuration path
        local_path = Path.cwd() / 'protonabu.json'
        # [Opt]: to load configuration from current directory
        if local_path.exists():
            # [Msg]: to load configuration from JSON file
            self.load(local_path)
            return

        # to get user configuration path
        user_path = Path.home() / '.config' / 'protonabu' / 'config.json'
        # [Opt]: to load configuration from user home directory
        if user_path.exists():
            # [Msg]: to load configuration from JSON file
            self.load(user_path)
            return

    def load(self, filePath: Path | str) -> bool:
        """ to load configuration from JSON file
            - Exported
            - Input: file path
            - Output: success indicator
        """
        # to get configuration path
        path = Path(filePath)
        # [Esc Done]: file not found
        if not path.exists():
            return False
        # [Guard]: to load JSON configuration
        try:
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # [Opt]: to store loaded configuration
                if isinstance(loaded, dict):
                    self._data = loaded
                    return True
        # [Esc Error]: to handle invalid JSON file
        except Exception:
            return False
        return False

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """ to get configuration value
            - Exported
            - Input: section
            - Input: key
            - Input [Opt "None"]: default value
            - Output: value or default
        """
        # [Esc Done]: section not present
        if section not in self._data:
            return default
        sec = self._data[section]
        # [Esc Done]: section is not a dictionary
        if not isinstance(sec, dict):
            return default
        return sec.get(key, default)

    def set(self, section: str, key: str, value: Any):
        """ to set configuration value
            - Exported
            - Input: section
            - Input: key
            - Input: value
        """
        # [Opt]: to create section if missing
        if section not in self._data or not isinstance(self._data[section], dict):
            self._data[section] = {}
        self._data[section][key] = value

    def getChromiumPath(self) -> Optional[str]:
        """ to get Chrome or Chromium executable path
            - Exported
            - Output [Opt "None"]: executable path
        """
        # [Opt]: to get configured chromium path
        configured = self.get('thirdparty', 'chromium')
        # [Esc Done]: configured and exists
        if configured and os.path.exists(configured):
            return str(configured)

        # to get chromium path from environment
        env_path = os.environ.get('PROTONABU_CHROMIUM') or os.environ.get('CHROME_BIN')
        # [Esc Done]: environment path exists
        if env_path and os.path.exists(env_path):
            return env_path

        # [Msg]: to discover Chrome or Chromium executable
        discovered = self._discoverChromium()
        # [Opt]: to store discovered chromium path
        if discovered:
            self.set('thirdparty', 'chromium', discovered)
        return discovered

    def _discoverChromium(self) -> Optional[str]:
        """ to discover Chrome or Chromium executable
            - Output [Opt "None"]: executable path
        """
        names = ['google-chrome', 'chrome', 'chromium', 'chromium-browser', 'google-chrome-stable', 'msedge']
        # [Opt]: to add Windows executable names
        if platform.system() == 'Windows':
            names += ['chrome.exe', 'msedge.exe']
        # [Scan]: to find executable in system path
        for name in names:
            found = shutil.which(name)
            # [Esc Done]: executable found in path
            if found:
                return found

        sys_name = platform.system()
        candidates: list[str] = []
        # [Alt]: to set macOS candidate paths
        if sys_name == 'Darwin':
            candidates = [
                '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                '/Applications/Chromium.app/Contents/MacOS/Chromium',
                '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
            ]
        # [Alt]: to set Windows candidate paths
        elif sys_name == 'Windows':
            prog_files = os.environ.get('PROGRAMFILES', r'C:\Program Files')
            prog_files_x86 = os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')
            local_appdata = os.environ.get('LOCALAPPDATA', '')
            candidates = [
                os.path.join(prog_files, r'Google\Chrome\Application\chrome.exe'),
                os.path.join(prog_files_x86, r'Google\Chrome\Application\chrome.exe'),
                os.path.join(local_appdata, r'Google\Chrome\Application\chrome.exe'),
                os.path.join(prog_files, r'Microsoft\Edge\Application\msedge.exe'),
                os.path.join(prog_files_x86, r'Microsoft\Edge\Application\msedge.exe'),
            ]
        # [Alt]: to set Linux candidate paths
        else:
            candidates = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium',
                '/usr/bin/chromium-browser',
                '/snap/bin/chromium',
            ]

        # [Scan]: to test candidate paths
        for path_str in candidates:
            # [Esc Done]: candidate path exists
            if path_str and Path(path_str).exists():
                return path_str

        # [Esc Exhausted]: no executable found
        return None


# [Msg]: to INITIALIZE Protonabu Configurator
config = ProtonabuConfigurator()
