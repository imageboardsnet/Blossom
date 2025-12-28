import builtins
import json
import os
import sys
import time
from pathlib import Path

import pytest

# Ensure project root is on path for module resolution when running tests from repo root.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import butils.config as config_module
import butils.endpoints as endpoints_module
import butils.favicons as favicons_module
import butils.sauron as sauron_module
import butils.utils as utils_module
import obj.imageboards as imageboards_module
import obj.users as users_module


class TempEnv:
    """Utility container for temporary data files used during tests."""

    def __init__(self, root):
        self.root = root
        self.data_dir = root / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.endpoints_dir = root / "endpoints"
        self.endpoints_dir.mkdir(parents=True, exist_ok=True)
        self.favicons_dir = self.data_dir / "favicons"
        self.favicons_dir.mkdir(parents=True, exist_ok=True)
        self.users_file = self.data_dir / "users.json"
        self.imageboards_file = self.data_dir / "imageboards.json"
        self.config_file = self.data_dir / "config.json"

    def write_users(self, users):
        self.users_file.write_text(json.dumps(users))

    def write_imageboards(self, imageboards):
        self.imageboards_file.write_text(json.dumps(imageboards))

    def write_config(self, overrides=None):
        base_config = {
            "app_secret_key": "test-secret",
            "hcaptcha_sitekey": "sitekey",
            "hcaptcha_secret_key": "secret-key",
            "favicon_download_date": 0,
            "endpoint_build_date": 0,
            "sauron_last_check": 0,
            "sauron_state": "idle",
        }
        if overrides:
            base_config.update(overrides)
        self.config_file.write_text(json.dumps(base_config))

    def read_config(self):
        return json.loads(self.config_file.read_text())


@pytest.fixture
def temp_env(tmp_path, monkeypatch):
    """Prepare isolated data/config paths and patch modules to use them."""
    env = TempEnv(tmp_path)
    env.write_users([])
    env.write_imageboards([])
    env.write_config()

    monkeypatch.setattr(users_module, "users_path", str(env.users_file))
    monkeypatch.setattr(imageboards_module, "imageboards_path", str(env.imageboards_file))

    # Config helpers used across modules
    def fake_get_var(var):
        return env.read_config().get(var)

    def fake_set_var(var, value):
        config = env.read_config()
        config[var] = value
        env.config_file.write_text(json.dumps(config))

    def fake_set_date(var):
        fake_set_var(var, int(time.time()))

    monkeypatch.setattr(config_module, "get_var", fake_get_var)
    monkeypatch.setattr(config_module, "set_var", fake_set_var)
    monkeypatch.setattr(config_module, "set_date", fake_set_date)

    # Ensure modules holding direct imports also use the fake config writers.
    monkeypatch.setattr(utils_module, "get_var", fake_get_var)
    monkeypatch.setattr(sauron_module, "set_var", fake_set_var)
    monkeypatch.setattr(sauron_module, "set_date", fake_set_date)
    monkeypatch.setattr(endpoints_module, "set_date", fake_set_date)
    monkeypatch.setattr(favicons_module, "set_date", fake_set_date)

    # Redirect endpoint and favicon file writes into the temporary workspace.
    real_open = builtins.open

    def endpoints_open(path, mode="r", *args, **kwargs):
        if isinstance(path, str) and path.startswith("endpoints/"):
            path = env.root / path
            path.parent.mkdir(parents=True, exist_ok=True)
        return real_open(path, mode, *args, **kwargs)

    def favicons_open(path, mode="r", *args, **kwargs):
        if isinstance(path, str) and path.startswith("data/favicons/"):
            path = env.root / path
            path.parent.mkdir(parents=True, exist_ok=True)
        return real_open(path, mode, *args, **kwargs)

    # Allow creating new attributes on modules if not present.
    monkeypatch.setattr(endpoints_module, "open", endpoints_open, raising=False)
    monkeypatch.setattr(favicons_module, "open", favicons_open, raising=False)

    real_exists = os.path.exists

    def favicons_exists(path):
        if isinstance(path, str) and path.startswith("data/favicons/"):
            return (env.root / path).exists()
        return real_exists(path)

    monkeypatch.setattr(favicons_module.os.path, "exists", favicons_exists)

    return env
