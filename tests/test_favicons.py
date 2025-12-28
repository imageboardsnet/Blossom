from types import SimpleNamespace

from butils import favicons


def test_download_favicons_respects_only_new(monkeypatch, temp_env):
    created_files = []

    class FakeImageboards:
        def __init__(self):
            self.imageboards = [
                {"id": 1, "url": "https://new.test", "status": "active"},
                {"id": 2, "url": "https://existing.test", "status": "active"},
            ]

    def fake_get(url, timeout):
        return SimpleNamespace(status_code=200, content=b"ico-bytes")

    monkeypatch.setattr(favicons, "imageboardsb", FakeImageboards)
    monkeypatch.setattr(favicons.requests, "get", fake_get)

    existing_favicon = temp_env.favicons_dir / "2.ico"
    existing_favicon.write_bytes(b"old")

    favicons.download_favicons(onlynew=True)

    assert (temp_env.favicons_dir / "1.ico").exists()
    assert (temp_env.favicons_dir / "2.ico").read_bytes() == b"old"
