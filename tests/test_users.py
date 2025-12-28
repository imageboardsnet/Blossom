from obj.users import ph, usersb


def test_add_and_check_user(temp_env):
    manager = usersb()
    manager.add_user("alice", "password", "admin", [], [])

    user_id = manager.check_user("alice", "password")
    assert user_id == 1
    assert manager.get_user(user_id)["role"] == "admin"
    assert manager.check_user("alice", "wrong-password") is False

    manager.set_password(user_id, "new-password")
    assert manager.check_user("alice", "new-password") == user_id


def test_manage_imageboards_and_claims(temp_env):
    temp_env.write_users(
        [
            {
                "id": 1,
                "username": "bob",
                "password": ph.hash("secret"),
                "role": "user",
                "imageboards": [],
                "claim": [],
                "uuid": "uuid-1",
                "creation_date": 0,
            }
        ]
    )

    manager = usersb()
    manager.add_imageboard(1, "10")
    assert manager.get_user(1)["imageboards"] == ["10"]

    manager.add_claim(1, "20")
    assert manager.get_user(1)["claim"] == ["20"]

    manager.remove_claim(1, "20")
    assert manager.get_user(1)["claim"] == []

    manager.remove_imageboard(1, 10)
    assert manager.get_user(1)["imageboards"] == []

    manager.remove_user(1)
    assert manager.get_user(1) is False
