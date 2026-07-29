"""Integration tests for urubuga Application."""

import json
import pytest
from urubuga.app import UrubugaApplication
from urubuga.http.request_response import Request, Response, StatusCode
from urubuga.auth.authentication import Role, Policy, User
from urubuga.validation import Schema, Field


class TestUrubugaApplication:
    def test_create(self):
        app = UrubugaApplication("test", "1.0.0")
        assert app.name == "test"

    def test_route(self):
        app = UrubugaApplication()
        @app.get("/")
        def index(req):
            return {"message": "ok"}
        assert app.route_count() == 1

    def test_handle_request(self):
        app = UrubugaApplication()
        @app.get("/hello")
        def hello(req):
            return {"greeting": "hello"}
        resp = app.handle_request("GET", "/hello")
        assert resp.status == StatusCode.OK
        data = json.loads(resp.body.decode())
        assert data["greeting"] == "hello"

    def test_not_found(self):
        app = UrubugaApplication()
        resp = app.handle_request("GET", "/nonexistent")
        assert resp.status == StatusCode.NOT_FOUND

    def test_method_not_allowed(self):
        app = UrubugaApplication()
        @app.get("/test")
        def test(req):
            return "ok"
        resp = app.handle_request("POST", "/test")
        assert resp.status == StatusCode.METHOD_NOT_ALLOWED

    def test_dynamic_route(self):
        app = UrubugaApplication()
        @app.get("/users/{user_id}")
        def get_user(req):
            return {"id": req.path_params["user_id"]}
        resp = app.handle_request("GET", "/users/42")
        data = json.loads(resp.body.decode())
        assert data["id"] == "42"

    def test_post_json(self):
        app = UrubugaApplication()
        @app.post("/items")
        def create_item(req):
            return Response.json(req.json(), StatusCode.CREATED)
        body = json.dumps({"name": "test"}).encode()
        resp = app.handle_request("POST", "/items",
                                  headers={"content-type": "application/json"},
                                  body=body)
        assert resp.status == StatusCode.CREATED
        data = json.loads(resp.body.decode())
        assert data["name"] == "test"

    def test_group(self):
        app = UrubugaApplication()
        g = app.group("/api/v1")
        g.get("/users")(lambda req: {"users": []})
        g.get("/items")(lambda req: {"items": []})
        assert app.route_count() == 2
        resp = app.handle_request("GET", "/api/v1/users")
        assert resp.status == StatusCode.OK

    def test_url_for(self):
        app = UrubugaApplication()
        @app.get("/users/{user_id}", name="user")
        def get_user(req):
            return {}
        url = app.url_for("user", user_id="42")
        assert url == "/users/42"

    def test_configure_cors(self):
        app = UrubugaApplication()
        app.configure_cors(allow_origins=["https://example.com"])
        resp = app.handle_request("OPTIONS", "/",
                                  headers={"origin": "https://example.com"})
        assert resp.status == StatusCode.NO_CONTENT

    def test_configure_rate_limiting(self):
        app = UrubugaApplication()
        app.configure_rate_limiting(max_requests=2, window_sec=60)
        @app.get("/test")
        def test(req):
            return "ok"
        resp1 = app.handle_request("GET", "/test")
        resp2 = app.handle_request("GET", "/test")
        resp3 = app.handle_request("GET", "/test")
        assert resp3.status == StatusCode.TOO_MANY_REQUESTS

    def test_error_handler(self):
        app = UrubugaApplication()
        @app.error_handler(ValueError)
        def handle_value_error(req, err):
            return Response.error(400, str(err))
        @app.get("/test")
        def test(req):
            raise ValueError("bad input")
        resp = app.handle_request("GET", "/test")
        assert resp.status == StatusCode.BAD_REQUEST

    def test_json_response(self):
        app = UrubugaApplication()
        resp = app.json_response({"key": "value"})
        assert resp.status == StatusCode.OK
        data = json.loads(resp.body.decode())
        assert data["key"] == "value"

    def test_text_response(self):
        app = UrubugaApplication()
        resp = app.text_response("hello")
        assert resp.body == b"hello"

    def test_html_response(self):
        app = UrubugaApplication()
        resp = app.html_response("<h1>Hi</h1>")
        assert b"<h1>" in resp.body

    def test_redirect(self):
        app = UrubugaApplication()
        resp = app.redirect("/new-location")
        assert resp.status == StatusCode.FOUND
        assert resp.headers.get("location") == "/new-location"

    def test_middleware(self):
        app = UrubugaApplication()
        results = []
        def my_middleware(req):
            results.append("called")
            return MiddlewareResult.proceed()
        app.use(my_middleware)
        @app.get("/test")
        def test(req):
            return "ok"
        resp = app.handle_request("GET", "/test")
        assert "called" in results

    def test_add_role(self):
        app = UrubugaApplication()
        app.add_role(Role("admin", permissions=["read", "write"]))
        assert app.authorization.role_count() == 1

    def test_add_policy(self):
        app = UrubugaApplication()
        app.add_policy(Policy("owner", lambda u, r, a: True))
        assert app.authorization.policy_count() == 1

    def test_authenticate_jwt(self):
        app = UrubugaApplication()
        @app.get("/protected")
        @app.authenticate_jwt
        def protected(req):
            return {"user": req.user.id}
        user = User(id="1", username="alice")
        token = app.jwt.create_token(user)
        resp = app.handle_request("GET", "/protected",
                                  headers={"authorization": f"Bearer {token}"})
        data = json.loads(resp.body.decode())
        assert data["user"] == "1"

    def test_authenticate_jwt_no_token(self):
        app = UrubugaApplication()
        @app.get("/protected")
        @app.authenticate_jwt
        def protected(req):
            return "secret"
        resp = app.handle_request("GET", "/protected")
        assert resp.status == StatusCode.UNAUTHORIZED

    def test_authorize(self):
        app = UrubugaApplication()
        app.add_role(Role("admin", permissions=["read", "write"]))
        @app.get("/admin")
        @app.authenticate_jwt
        @app.authorize("read")
        def admin_endpoint(req):
            return "admin"
        user = User(id="1", roles=["admin"])
        token = app.jwt.create_token(user)
        resp = app.handle_request("GET", "/admin",
                                  headers={"authorization": f"Bearer {token}"})
        assert resp.status == StatusCode.OK

    def test_authorize_forbidden(self):
        app = UrubugaApplication()
        app.add_role(Role("viewer", permissions=["read"]))
        @app.delete("/items/{id}")
        @app.authenticate_jwt
        @app.authorize("delete")
        def delete_item(req):
            return "deleted"
        user = User(id="1", roles=["viewer"])
        token = app.jwt.create_token(user)
        resp = app.handle_request("DELETE", "/items/1",
                                  headers={"authorization": f"Bearer {token}"})
        assert resp.status == StatusCode.FORBIDDEN

    def test_validate(self):
        app = UrubugaApplication()
        schema = Schema("create", [
            Field("name", required=True, min_length=1),
            Field("age", field_type="integer", min_value=0),
        ])
        @app.post("/users")
        @app.validate(schema)
        def create_user(req):
            return req.state["validated"]
        body = json.dumps({"name": "Alice", "age": 25}).encode()
        resp = app.handle_request("POST", "/users",
                                  headers={"content-type": "application/json"},
                                  body=body)
        assert resp.status == StatusCode.OK

    def test_validate_fails(self):
        app = UrubugaApplication()
        schema = Schema("create", [
            Field("name", required=True),
        ])
        @app.post("/users")
        @app.validate(schema)
        def create_user(req):
            return "created"
        resp = app.handle_request("POST", "/users",
                                  headers={"content-type": "application/json"},
                                  body=b"{}")
        assert resp.status == StatusCode.UNPROCESSABLE_ENTITY

    def test_middleware_count(self):
        app = UrubugaApplication()
        assert app.middleware_count() >= 5  # builtins

    def test_openapi(self):
        app = UrubugaApplication()
        @app.get("/users")
        def list_users(req):
            return []
        spec = app.openapi()
        assert spec["openapi"] == "3.0.0"
        assert "/users" in spec["paths"]

    def test_head_method(self):
        app = UrubugaApplication()
        @app.head("/test")
        def test_head(req):
            return Response(StatusCode.OK, headers={"x-test": "1"})
        resp = app.handle_request("HEAD", "/test")
        assert resp.status == StatusCode.OK

    def test_multiple_methods(self):
        app = UrubugaApplication()
        @app.get("/resource")
        def get_res(req):
            return "get"
        @app.post("/resource")
        def post_res(req):
            return "post"
        resp1 = app.handle_request("GET", "/resource")
        resp2 = app.handle_request("POST", "/resource")
        assert resp1.status == StatusCode.OK
        assert resp2.status == StatusCode.OK

    def test_debug_mode(self):
        app = UrubugaApplication(debug=True)
        assert app.debug

    def test_session_auth(self):
        app = UrubugaApplication()
        user = User(id="1", username="alice")
        session_id = app.sessions.create(user)
        @app.get("/profile")
        @app.authenticate_session
        def profile(req):
            return {"user": req.user.username}
        resp = app.handle_request("GET", "/profile",
                                  headers={"cookie": f"session_id={session_id}"})
        data = json.loads(resp.body.decode())
        assert data["user"] == "alice"

    def test_api_key_auth(self):
        app = UrubugaApplication()
        key = app.api_keys.create_key("user1", name="test")
        @app.get("/data")
        @app.authenticate_api_key
        def get_data(req):
            return {"user": req.user.id}
        resp = app.handle_request("GET", "/data",
                                  headers={"x-api-key": key})
        data = json.loads(resp.body.decode())
        assert data["user"] == "user1"

    def test_api_key_invalid(self):
        app = UrubugaApplication()
        @app.get("/data")
        @app.authenticate_api_key
        def get_data(req):
            return "data"
        resp = app.handle_request("GET", "/data",
                                  headers={"x-api-key": "invalid"})
        assert resp.status == StatusCode.UNAUTHORIZED

    def test_empty_response(self):
        app = UrubugaApplication()
        @app.delete("/items/{id}")
        def delete(req):
            return None
        resp = app.handle_request("DELETE", "/items/1")
        assert resp.status == StatusCode.NO_CONTENT


from urubuga.middleware.builtin import MiddlewareResult
