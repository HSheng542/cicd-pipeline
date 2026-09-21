"""Intentionally unsafe training-only code; excluded from normal CodeQL scans."""


def evaluate_user_expression(expression: str) -> object:
    # DEMO ONLY: CodeQL should flag this as code injection when demo mode is used.
    return eval(expression)  # noqa: S307
