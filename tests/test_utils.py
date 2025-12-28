from types import SimpleNamespace

from butils import utils


def test_time_elapsed_str_formats_units(monkeypatch):
    monkeypatch.setattr(utils.time, "time", lambda: 4000)
    assert utils.time_elapsed_str(3985) == "15 seconds ago"
    assert utils.time_elapsed_str(3940) == "1 minutes ago"
    assert utils.time_elapsed_str(1000) == "50 minutes ago"

    monkeypatch.setattr(utils.time, "time", lambda: 8000)
    assert utils.time_elapsed_str(0) == "2 hours ago"


def test_timestamp_to_humane():
    assert utils.timestamp_to_humane(0, "%d %B %Y") == "01 January 1970"


def test_verify_hcaptcha(monkeypatch, temp_env):
    success_response = SimpleNamespace(status_code=200, json=lambda: {"success": True})
    monkeypatch.setattr(utils.requests, "post", lambda url, data: success_response)
    assert utils.verify_hcaptcha("token-value") is True

    failure_response = SimpleNamespace(status_code=500, json=lambda: {"success": False})
    monkeypatch.setattr(utils.requests, "post", lambda url, data: failure_response)
    assert utils.verify_hcaptcha("token-value") is False

    malformed_response = SimpleNamespace(status_code=200, json=lambda: {})
    monkeypatch.setattr(utils.requests, "post", lambda url, data: malformed_response)
    assert utils.verify_hcaptcha("token-value") is False


def test_check_claimed_imageboard(monkeypatch, temp_env):
    temp_env.write_imageboards(
        [
            {
                "id": 1,
                "name": "TestBoard",
                "url": "https://claimed.test",
                "status": "active",
                "protocol": "https",
                "mirrors": [],
                "language": [],
                "software": [],
                "boards": [],
                "description": "",
            }
        ]
    )

    monkeypatch.setattr(utils, "query_txt_records", lambda domain: ["ibclaim-user-uuid"])
    assert utils.check_claimed_imageboard("user-uuid", 1) is True

    monkeypatch.setattr(utils, "query_txt_records", lambda domain: False)
    assert utils.check_claimed_imageboard("user-uuid", 1) is False


def test_get_board_name(temp_env):
    temp_env.write_imageboards(
        [
            {
                "id": 2,
                "name": "BoardName",
                "url": "https://board.test",
                "status": "active",
                "protocol": "https",
                "mirrors": [],
                "language": [],
                "software": [],
                "boards": [],
                "description": "",
            }
        ]
    )

    assert utils.get_board_name(2) == "BoardName"
    assert utils.get_board_name(3) is None
