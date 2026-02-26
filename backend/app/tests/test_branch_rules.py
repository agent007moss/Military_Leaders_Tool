from app.domain.branch_rules import valid_components_for, validate_branch_component

def test_components_army():
    assert valid_components_for("Army") == ["Active", "Reserve", "National Guard"]

def test_invalid_combo_rejected():
    try:
        validate_branch_component("Navy", "National Guard")
        assert False, "Expected rejection"
    except ValueError:
        assert True