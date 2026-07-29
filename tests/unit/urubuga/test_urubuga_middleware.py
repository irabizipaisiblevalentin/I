"""Tests for urubuga middleware."""

import pytest
from urubuga.http.request_response import Request, Response, StatusCode
from urubuga.middleware.builtin import (
    CORSMiddleware, RateLimitMiddleware, SecurityHeadersMiddleware,
    CSRFMiddleware, RequestLoggingMiddleware, CompressionMiddleware,
    ExceptionHandlerMiddleware, MiddlewareResult,
)


class TestMiddlewareResult:
    def test_proceed(self):
        r = MiddlewareResult.proceed()
        assert r.continue_processing

    def test_respond(self):
        resp = Response(StatusCode.OK)
        r = MiddlewareResult.respond(resp)
        assert not r.continue_processing
        assert r.response is resp


class TestCORSMiddleware:
    def test_preflight(self):
        cors = CORSMiddleware()
        req = Request("OPTIONS", "/", headers={"origin": "https://example.com"})
        result = cors(req)
        assert not result.continue_processing
        assert result.response is not None

    def test_allowed_origin(self):
        cors = CORSMiddleware(allow_origins=["https://example.com"])
        req = Request("GET", "/", headers={"origin": "https://example.com"})
        result = cors(req)
        assert result.continue_processing

    def test_disallowed_origin(self):
        cors = CORSMiddleware(allow_origins=["https://allowed.com"])
        req = Request("GET", "/", headers={"origin": "https://evil.com"})
        result = cors(req)
        assert result.continue_processing

    def test_wildcard(self):
        cors = CORSMiddleware(allow_origins=["*"])
        req = Request("GET", "/", headers={"origin": "https://any.com"})
        result = cors(req)
        assert result.continue_processing

    def test_credentials(self):
        cors = CORSMiddleware(allow_credentials=True)
        resp = Response(StatusCode.OK)
        cors.apply_response(resp, "https://example.com")
        assert resp.headers.get("access-control-allow-credentials") == "true"


class TestRateLimitMiddleware:
    def test_within_limit(self):
        rl = RateLimitMiddleware(max_requests=5, window_sec=60)
        req = Request("GET", "/", client=("1.2.3.4", 80))
        for _ in range(4):
            result = rl(req)
            assert result.continue_processing

    def test_exceeds_limit(self):
        rl = RateLimitMiddleware(max_requests=2, window_sec=60)
        req = Request("GET", "/", client=("1.2.3.4", 80))
        rl(req)
        rl(req)
        result = rl(req)
        assert not result.continue_processing
        assert result.response.status == StatusCode.TOO_MANY_REQUESTS

    def test_different_ips(self):
        rl = RateLimitMiddleware(max_requests=1, window_sec=60)
        req1 = Request("GET", "/", client=("1.1.1.1", 80))
        req2 = Request("GET", "/", client=("2.2.2.2", 80))
        r1 = rl(req1)
        r2 = rl(req2)
        assert r1.continue_processing
        assert r2.continue_processing

    def test_remaining(self):
        rl = RateLimitMiddleware(max_requests=10, window_sec=60)
        assert rl.remaining("key1") == 10


class TestSecurityHeadersMiddleware:
    def test_apply(self):
        sh = SecurityHeadersMiddleware()
        resp = Response(StatusCode.OK)
        sh.apply(resp)
        assert resp.headers.has("content-security-policy")
        assert resp.headers.has("strict-transport-security")
        assert resp.headers.has("x-frame-options")
        assert resp.headers.has("x-content-type-options")
        assert resp.headers.has("x-xss-protection")
        assert resp.headers.has("referrer-policy")

    def test_custom_csp(self):
        sh = SecurityHeadersMiddleware(csp="default-src 'none'")
        resp = Response(StatusCode.OK)
        sh.apply(resp)
        assert resp.headers.get("content-security-policy") == "default-src 'none'"

    def test_permissions_policy(self):
        sh = SecurityHeadersMiddleware(
            permissions_policy={"camera": "none", "microphone": "none"})
        resp = Response(StatusCode.OK)
        sh.apply(resp)
        pp = resp.headers.get("permissions-policy")
        assert "camera" in pp
        assert "microphone" in pp


class TestCSRFMiddleware:
    def test_safe_method(self):
        csrf = CSRFMiddleware(secret="test")
        req = Request("GET", "/")
        result = csrf(req)
        assert result.continue_processing

    def test_invalid_token(self):
        csrf = CSRFMiddleware(secret="test")
        req = Request("POST", "/",
                      headers={"x-csrf-token": "invalid"})
        result = csrf(req)
        assert not result.continue_processing
        assert result.response.status == StatusCode.FORBIDDEN

    def test_valid_token(self):
        csrf = CSRFMiddleware(secret="test")
        token = csrf.generate_token()
        req = Request("POST", "/",
                      headers={"x-csrf-token": token})
        result = csrf(req)
        assert result.continue_processing


class TestRequestLoggingMiddleware:
    def test_logs_requests(self):
        log_entries = []
        def log_fn(method, path, elapsed_ms):
            log_entries.append((method, path))

        rl = RequestLoggingMiddleware(log_fn)
        req = Request("GET", "/test")
        rl(req)
        assert len(log_entries) == 1
        assert log_entries[0] == ("GET", "/test")

    def test_request_count(self):
        rl = RequestLoggingMiddleware()
        req = Request("GET", "/")
        rl(req)
        rl(req)
        assert rl.request_count == 2


class TestCompressionMiddleware:
    def test_compression(self):
        cm = CompressionMiddleware(min_size=10)
        req = Request("GET", "/",
                      headers={"accept-encoding": "gzip, deflate"})
        result = cm(req)
        assert result.continue_processing

    def test_no_compression_small(self):
        cm = CompressionMiddleware(min_size=1000)
        req = Request("GET", "/",
                      headers={"accept-encoding": "gzip"})
        result = cm(req)
        assert result.continue_processing


class TestExceptionHandlerMiddleware:
    def test_catches_exception(self):
        eh = ExceptionHandlerMiddleware()
        req = Request("GET", "/")

        def bad_handler(r):
            raise ValueError("test error")

        result = eh.invoke(req, bad_handler)
        assert isinstance(result, Response)
        assert result.status == StatusCode.INTERNAL_SERVER_ERROR

    def test_error_log(self):
        eh = ExceptionHandlerMiddleware()
        req = Request("GET", "/test")

        def bad_handler(r):
            raise ValueError("err")

        eh.invoke(req, bad_handler)
        assert eh.error_count == 1
        assert eh.error_log[0]["path"] == "/test"
