from obj.imageboards import imageboardsb


def make_imageboard(name, url, status="active", extra=None):
    base = {
        "name": name,
        "url": url,
        "status": status,
        "protocol": "https",
        "mirrors": [],
        "language": [],
        "software": [],
        "boards": [],
        "description": "",
    }
    if extra:
        base.update(extra)
    return base


def test_add_update_and_delete_imageboard(temp_env):
    manager = imageboardsb()
    manager.add_imageboard(make_imageboard("A", "https://alpha.test"))

    assert len(manager) == 1
    assert manager.get_last_id() == 1
    assert manager.get_imageboard(1)["name"] == "A"

    manager.update_imageboard(1, {"status": "offline", "description": "down"})
    updated = manager.get_imageboard(1)
    assert updated["status"] == "offline"
    assert updated["description"] == "down"

    manager.delete_imageboard(1)
    assert len(manager) == 0
    assert manager.get_last_id() == 0


def test_duplicate_detection_ignores_subdomains(temp_env):
    temp_env.write_imageboards([make_imageboard("Base", "https://example.com", "active", {"id": 1})])

    manager = imageboardsb()
    assert manager.check_if_duplicate({"url": "https://sub.example.com"}) is True
    assert manager.check_if_duplicate({"url": "https://another.test"}) is False
