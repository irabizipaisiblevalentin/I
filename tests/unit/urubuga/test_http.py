"""Tests for urubuga HTTP request/response."""

import json
import pytest
from urubuga.http.request_response import (
    Headers, HTTPMethod, Request, Response, StatusCode,
)


class TestHeaders:
    def test_case_insensitive(self):
        h = Headers({"Content-Type": "text/html"})
        assert h.get("content-type") == "text/html"
        assert h.get("CONTENT-TYPE") == "text/html"

    def test_set_and_get(self):
        h = Headers()
        h.set("x-custom", "value")
        assert h["x-custom"] == "value"

    def test_add_multiple(self):
        h = Headers()
        h.add("accept", "text/html")
        h.add("accept", "application/json")
        assert "text/html" in h.get("accept")

    def test_delete(self):
        h = Headers({"x-test": "1"})
        assert h.delete("x-test")
        assert not h.has("x-test")

    def test_contains(self):
        h = Headers({"x-test": "1"})
        assert "x-test" in h
        assert "x-other" not in h

    def test_len(self):
        h = Headers({"a": "1", "b": "2"})
        assert len(h) == 2

    def test_items(self):
        h = Headers({"a": "1"})
        items = h.items()
        assert "a" in items

    def test_keys_values(self):
        h = Headers({"a": "1", "b": "2"})
        assert set(h.keys()) == {"a", "b"}
        assert set(h.values()) == {"1", "2"}


class TestHTTPMethod:
    def test_str(self):
        assert str(HTTPMethod.GET) == "GET"
        assert str(HTTPMethod.POST) == "POST"


class TestStatusCode:
    def test_is_success(self):
        assert StatusCode.OK.is_success
        assert StatusCode.CREATED.is_success
        assert not StatusCode.NOT_FOUND.is_success

    def test_is_redirect(self):
        assert StatusCode.FOUND.is_redirect
        assert not StatusCode.OK.is_redirect

    def test_is_client_error(self):
        assert StatusCode.NOT_FOUND.is_client_error
        assert StatusCode.BAD_REQUEST.is_client_error
        assert not StatusCode.OK.is_client_error

    def test_is_server_error(self):
        assert StatusCode.INTERNAL_SERVER_ERROR.is_server_error
        assert not StatusCode.OK.is_server_error

    def test_phrase(self):
        assert StatusCode.OK.phrase == "OK"
        assert StatusCode.NOT_FOUND.phrase == "Not Found"


class TestRequest:
    def test_create(self):
        req = Request("GET", "/test")
        assert req.method == "GET"
        assert req.path == "/test"

    def test_method_uppercased(self):
        req = Request("get", "/")
        assert req.method == "GET"

    def test_query_params(self):
        req = Request("GET", "/search", "q=hello&lang=en")
        assert req.query_param("q") == "hello"
        assert req.query_param("lang") == "en"

    def test_query_param_default(self):
        req = Request("GET", "/")
        assert req.query_param("missing", "default") == "default"

    def test_json(self):
        body = json.dumps({"name": "test"}).encode()
        req = Request("POST", "/", headers={"content-type": "application/json"},
                      body=body)
        assert req.json() == {"name": "test"}

    def test_is_json(self):
        req = Request("POST", "/",
                      headers={"content-type": "application/json"})
        assert req.is_json

    def test_is_form(self):
        req = Request("POST", "/",
                      headers={"content-type": "application/x-www-form-urlencoded"})
        assert req.is_form

    def test_cookies(self):
        req = Request("GET", "/",
                      headers={"cookie": "session=abc123; theme=dark"})
        assert req.cookie("session") == "abc123"
        assert req.cookie("theme") == "dark"

    def test_client_ip(self):
        req = Request("GET", "/", client=("127.0.0.1", 8080))
        assert req.client_ip == "127.0.0.1"

    def test_client_ip_forwarded(self):
        req = Request("GET", "/",
                      headers={"x-forwarded-for": "10.0.0.1"})
        assert req.client_ip == "10.0.0.1"

    def test_accept(self):
        req = Request("GET", "/",
                      headers={"accept": "application/json"})
        assert req.accept("application/json")
        assert not req.accept("text/html")

    def test_accept_wildcard(self):
        req = Request("GET", "/")
        assert req.accept("anything")

    def test_path_params(self):
        req = Request("GET", "/users/42")
        req._path_params = {"user_id": "42"}
        assert req.path_params["user_id"] == "42"

    def test_user(self):
        req = Request("GET", "/")
        assert req.user is None
        req.user = {"id": "1"}
        assert req.user == {"id": "1"}

    def test_state(self):
        req = Request("GET", "/")
        req.state["key"] = "value"
        assert req.state["key"] == "value"

    def test_url(self):
        req = Request("GET", "/test")
        req._scheme = "https"
        req._host = "example.com"
        assert req.url == "https://example.com/test"

    def test_repr(self):
        req = Request("GET", "/test")
        assert "GET" in repr(req)

    def test_timestamp(self):
        req = Request("GET", "/")
        assert req.timestamp > 0


class TestResponse:
    def test_json(self):
        resp = Response.json({"hello": "world"})
        assert resp.status == StatusCode.OK
        assert "application/json" in resp.headers.get("content-type")
        data = json.loads(resp.body.decode())
        assert data["hello"] == "world"

    def test_json_status(self):
        resp = Response.json({}, StatusCode.CREATED)
        assert resp.status == StatusCode.CREATED

    def test_text(self):
        resp = Response.text("hello")
        assert resp.body == b"hello"
        assert "text/plain" in resp.headers.get("content-type")

    def test_html(self):
        resp = Response.html("<h1>Hello</h1>")
        assert "text/html" in resp.headers.get("content-type")

    def test_redirect(self):
        resp = Response.redirect("https://example.com")
        assert resp.status == StatusCode.FOUND
        assert resp.headers.get("location") == "https://example.com"

    def test_no_content(self):
        resp = Response.no_content()
        assert resp.status == StatusCode.NO_CONTENT

    def test_error(self):
        resp = Response.error(404, "Not found")
        assert resp.status == StatusCode.NOT_FOUND
        data = json.loads(resp.body.decode())
        assert data["error"]["status"] == 404

    def test_set_cookie(self):
        resp = Response(StatusCode.OK)
        resp.set_cookie("session", "abc123")
        cookie_headers = resp.build_cookie_headers()
        assert len(cookie_headers) == 1
        assert "session=abc123" in cookie_headers[0]

    def test_set_header(self):
        resp = Response(StatusCode.OK)
        resp.set_header("x-custom", "value")
        assert resp.headers.get("x-custom") == "value"

    def test_repr(self):
        resp = Response(StatusCode.OK)
        assert "200" in repr(resp)
