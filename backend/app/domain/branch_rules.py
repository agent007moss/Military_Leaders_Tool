from __future__ import annotations

from dataclasses import dataclass

BRANCHES = [
    "Army",
    "Air Force",
    "Navy",
    "Marine Corps",
    "Coast Guard",
    "Space Force",
]

@dataclass(frozen=True)
class BranchRule:
    branch: str
    valid_components: tuple[str, ...]
    guard_label: str | None  # branch-specific guard label (if any)

RULES: dict[str, BranchRule] = {
    "Army": BranchRule("Army", ("Active", "Reserve", "National Guard"), "National Guard"),
    "Air Force": BranchRule("Air Force", ("Active", "Reserve", "Air National Guard"), "Air National Guard"),
    "Navy": BranchRule("Navy", ("Active", "Reserve"), None),
    "Marine Corps": BranchRule("Marine Corps", ("Active", "Reserve"), None),
    "Coast Guard": BranchRule("Coast Guard", ("Active", "Reserve"), None),
    "Space Force": BranchRule("Space Force", ("Active",), None),
}

def valid_components_for(branch: str) -> list[str]:
    if branch not in RULES:
        raise ValueError("Unsupported branch")
    return list(RULES[branch].valid_components)

def validate_branch_component(branch: str, component: str) -> None:
    if branch not in RULES:
        raise ValueError("Unsupported branch")
    if component not in RULES[branch].valid_components:
        raise ValueError("Invalid branch/component combination")