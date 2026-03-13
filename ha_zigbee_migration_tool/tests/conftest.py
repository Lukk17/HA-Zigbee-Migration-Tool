from deepdiff import DeepDiff


def pytest_assertrepr_compare(op, left, right):
    """
    Provides a clean, readable diff output for DeepDiff objects in pytest assertions.
    This hook is triggered when an assertion like 'assert diff == {}' fails.
    """
    if op == "==" and isinstance(left, DeepDiff) and right == {}:
        # The assertion was `assert diff == {}`, and it failed.
        return [
            "Migration output does not match expected output:",
            left.pretty(),
        ]
    if op == "==" and isinstance(right, DeepDiff) and left == {}:
        # The assertion was `assert {} == diff`, and it failed.
        return [
            "Migration output does not match expected output:",
            right.pretty(),
        ]
