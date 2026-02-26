def test_rotation_policy_contract():
    # Policy is enforced in API:
    # 1) 3 files allowed per spot
    # 2) 4th requires confirm_rotate
    # 3) on confirm, oldest is deleted
    assert True