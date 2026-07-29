"""Tests for urubuga routing system."""

import pytest
from urubuga.routing.router import (
    Router, Route, RouteGroup, RouteMatch,
    RouteParam, RouteParamType, ROUTE_PARAM_PATTERNS,
)


class TestRoute:
    def test_create(self):
        r = Route("GET", "/test", lambda: None, name="test_route")
        assert r.method == "GET"
        assert r.pattern == "/test"
        assert r.name == "test_route"

    def test_method_uppercased(self):
        r = Route("get", "/", lambda: None)
        assert r.method == "GET"

    def test_full_pattern_no_version(self):
        r = Route("GET", "/users", lambda: None)
        assert r.full_pattern == "/users"

    def test_full_pattern_with_version(self):
        r = Route("GET", "/users", lambda: None, version="v1")
        assert r.full_pattern == "/v1/users"

    def test_repr(self):
        r = Route("GET", "/test", lambda: None, name="t")
        assert "GET" in repr(r)
        assert "/test" in repr(r)


class TestRouter:
    def test_static_route(self):
        router = Router()
        handler = lambda req: "ok"
        router.get("/")(handler)
        match = router.match("GET", "/")
        assert match is not None
        assert match.handler is handler

    def test_dynamic_route(self):
        router = Router()
        handler = lambda req: "ok"
        router.get("/users/{user_id}")(handler)
        match = router.match("GET", "/users/42")
        assert match is not None
        assert match.params["user_id"] == "42"

    def test_int_param(self):
        router = Router()
        handler = lambda req: "ok"
        router.get("/items/{item_id:int}")(handler)
        match = router.match("GET", "/items/123")
        assert match is not None
        assert match.params["item_id"] == "123"
        assert router.match("GET", "/items/abc") is None

    def test_method_not_allowed(self):
        router = Router()
        router.get("/")(lambda req: "ok")
        match = router.match("POST", "/")
        assert match is None

    def test_named_route(self):
        router = Router()
        router.get("/", name="home")(lambda req: "ok")
        url = router.url_for("home")
        assert url == "/"

    def test_url_for_with_params(self):
        router = Router()
        router.get("/users/{user_id}", name="user")(lambda req: "ok")
        url = router.url_for("user", user_id="42")
        assert url == "/users/42"

    def test_url_for_missing(self):
        router = Router()
        with pytest.raises(KeyError):
            router.url_for("nonexistent")

    def test_method_allowed(self):
        router = Router()
        router.get("/")(lambda req: "ok")
        router.post("/")(lambda req: "ok")
        allowed = router.method_allowed("/", "DELETE")
        assert "GET" in allowed
        assert "POST" in allowed
        assert "DELETE" not in allowed

    def test_route_count(self):
        router = Router()
        router.get("/")(lambda req: "ok")
        router.post("/")(lambda req: "ok")
        assert router.route_count() == 2

    def test_group(self):
        router = Router()
        g = router.group("/api/v1")
        g.get("/users")(lambda req: "users")
        g.get("/items")(lambda req: "items")
        assert router.route_count() == 2
        match = router.match("GET", "/api/v1/users")
        assert match is not None

    def test_group_middleware(self):
        router = Router()
        g = router.group("/api", middleware=["auth"])
        g.get("/users")(lambda req: "ok")
        route = g.routes[0]
        assert "auth" in route.middleware

    def test_clear(self):
        router = Router()
        router.get("/")(lambda req: "ok")
        router.clear()
        assert router.route_count() == 0

    def test_openapi_paths(self):
        router = Router()
        router.get("/users")(lambda req: "ok")
        router.post("/users")(lambda req: "ok")
        paths = router.openapi_paths()
        assert "/users" in paths
        assert "get" in paths["/users"]
        assert "post" in paths["/users"]

    def test_head(self):
        router = Router()
        router.head("/")(lambda req: "ok")
        match = router.match("HEAD", "/")
        assert match is not None

    def test_options(self):
        router = Router()
        router.options("/")(lambda req: "ok")
        match = router.match("OPTIONS", "/")
        assert match is not None

    def test_versioned_route(self):
        router = Router()
        router.get("/users", version="v1")(lambda req: "v1")
        router.get("/users", version="v2")(lambda req: "v2")
        m1 = router.match("GET", "/v1/users")
        m2 = router.match("GET", "/v2/users")
        assert m1 is not None
        assert m2 is not None

    def test_slug_param(self):
        router = Router()
        router.get("/posts/{slug:slug}")(lambda req: "ok")
        match = router.match("GET", "/posts/hello-world")
        assert match is not None
        assert router.match("GET", "/posts/hello world") is None

    def test_uuid_param(self):
        router = Router()
        router.get("/items/{id:uuid}")(lambda req: "ok")
        match = router.match("GET", "/items/550e8400-e29b-41d4-a716-446655440000")
        assert match is not None


class TestRouteGroup:
    def test_group_route(self):
        g = RouteGroup("/api")
        g.get("/users")(lambda req: "ok")
        assert len(g.routes) == 1
        assert g.routes[0].pattern == "/api/users"

    def test_group_post(self):
        g = RouteGroup("/api")
        g.post("/users")(lambda req: "ok")
        assert g.routes[0].method == "POST"

    def test_group_put(self):
        g = RouteGroup("/api")
        g.put("/users/{id}")(lambda req: "ok")
        assert g.routes[0].method == "PUT"

    def test_group_delete(self):
        g = RouteGroup("/api")
        g.delete("/users/{id}")(lambda req: "ok")
        assert g.routes[0].method == "DELETE"

    def test_group_version(self):
        g = RouteGroup("/users", version="v1")
        g.get("")(lambda req: "ok")
        assert g.routes[0].version == "v1"
