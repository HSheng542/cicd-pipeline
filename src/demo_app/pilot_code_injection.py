"""Temporary PT 02 CodeQL training fixture. Do not merge into main."""

from flask import request


def evaluate_pilot_expression() -> object:
    """Intentionally unsafe: models execution of untrusted request input for PT 02."""
    expression = request.args["expression"]
    return eval(expression)
