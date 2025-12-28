import threading
from types import SimpleNamespace

from butils import sauron


def test_check_imageboard_handles_status_codes(monkeypatch):
    success_response = SimpleNamespace(status_code=200)
    failure_response = SimpleNamespace(status_code=500)

    monkeypatch.setattr(sauron.requests, "get", lambda url, headers, timeout: success_response)
    assert sauron.check_imageboard({"url": "https://ok.test"}) is True

    monkeypatch.setattr(sauron.requests, "get", lambda url, headers, timeout: failure_response)
    assert sauron.check_imageboard({"url": "https://fail.test"}) is False


def test_check_imageboards_updates_status(monkeypatch):
    updates = []

    class FakeImageboards(list):
        def __init__(self):
            super().__init__(
                [
                    {"id": 1, "url": "https://active.test", "status": "active", "protocol": "https"},
                    {"id": 2, "url": "https://pending.test", "status": "pending", "protocol": "https"},
                ]
            )

        def set_status(self, imageboard_id, status):
            updates.append(("status", imageboard_id, status))

        def set_sauron_status(self, imageboard_id, status):
            updates.append(("sauron_status", imageboard_id, status))

    fake_boards = FakeImageboards()
    monkeypatch.setattr(sauron, "imageboardsb", lambda: fake_boards)
    monkeypatch.setattr(sauron, "check_if_dns_resolves", lambda url: True)
    monkeypatch.setattr(sauron, "check_imageboard", lambda ib: ib["id"] == 1)

    state_changes = {}

    def record_state(key, value):
        state_changes[key] = value

    def record_date(key):
        state_changes[key] = "set"

    monkeypatch.setattr(sauron, "set_var", record_state)
    monkeypatch.setattr(sauron, "set_date", record_date)

    event = threading.Event()
    event.set()

    sauron.check_imageboards(event)

    assert state_changes.get("sauron_state") == "idle"
    assert ("sauron_status", 1, "active") in updates
    # Pending boards are skipped for status updates.
    assert all(update[1] != 2 for update in updates)
