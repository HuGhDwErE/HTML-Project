import json

class TestMain():
    def test_index(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Ultimate Elite Skyrim Item Tracker' in response.data
