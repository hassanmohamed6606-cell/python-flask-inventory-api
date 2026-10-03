from cli import call_api


class FakeResponse:
    status_code = 200
    text = ""
    def json(self):
        return {"message": "ok"}


def test_call_api(monkeypatch):
    def fake_request(method, url, json=None, timeout=None):
        assert method == "GET"
        assert url.endswith("/inventory")
        return FakeResponse()
    monkeypatch.setattr("cli.requests.request", fake_request)
    status, body = call_api("GET", "/inventory")
    assert status == 200
    assert body == {"message": "ok"}


def test_call_api_connection_error(monkeypatch):
    import requests
    def fail(*args, **kwargs):
        raise requests.ConnectionError("offline")
    monkeypatch.setattr("cli.requests.request", fail)
    status, body = call_api("GET", "/inventory")
    assert status == 0
    assert "Could not connect" in body["error"]
