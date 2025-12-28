from butils.endpoints import build_endpoints, get_endpoints


def test_build_endpoints_filters_and_shapes_output(temp_env):
    active_ib = {
        "id": 1,
        "name": "ActiveBoard",
        "url": "https://active.test",
        "status": "active",
        "protocol": "https",
        "mirrors": [],
        "language": ["en"],
        "software": ["custom"],
        "boards": ["news"],
        "description": "running",
        "favicon": "path.ico",
    }
    pending_ib = {**active_ib, "id": 2, "name": "Pending", "status": "pending"}
    temp_env.write_imageboards([active_ib, pending_ib])

    build_endpoints()

    standard = get_endpoints()
    legacy = get_endpoints(legacy=True)

    assert standard == [active_ib]
    assert legacy == [
        {
            "name": "ActiveBoard",
            "url": "https://active.test",
            "protocol": "https",
            "mirrors": [],
            "language": ["en"],
            "software": ["custom"],
        }
    ]
