from app.services.wiki_service import WikiService


def test_online_search_always_uses_configured_timeout(monkeypatch, tmp_path):
    observed = []

    class Response:
        status_code = 200
        def raise_for_status(self): pass
        def json(self): return {"query": {"search": []}}

    service = WikiService.__new__(WikiService)
    service.mode = "online"
    service.search_api_url = "https://example.test/search"
    service.request_timeout = (1.0, 2.0)
    service.session = type("Session", (), {
        "get": lambda _self, *args, **kwargs: observed.append(kwargs.get("timeout")) or Response()
    })()
    assert service._search_online("query", 2) == []
    assert observed == [(1.0, 2.0)]
