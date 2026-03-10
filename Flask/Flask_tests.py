import unittest
import json

from app.modules.Flask.controller import FlaskController


def test_index():
    Flask_controller = FlaskController()
    result = Flask_controller.index()
    assert result == {'message': 'Hello, World!'}
