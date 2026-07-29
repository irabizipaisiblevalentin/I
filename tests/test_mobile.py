"""Tests for MOBILE platform."""

from __future__ import annotations

import pytest

from mobile.porogaramu import MobileApplication
from mobile.ikiganiro import ActivityState, Ikiganiro
from mobile.ubugenzuzi import (
    NavigationEvent,
    NavigationRoute,
    Ubugenzuzi,
)
from mobile.ibikoresho.buto import Buto, ButoSize, ButoVariant
from mobile.ibikoresho.ikimenyetso import (
    FontWeight,
    Ibara,
    Ikimenyetso,
    TextTransform,
    Umutwe,
)
from mobile.ibikoresho.ikoresho import Ikoresho
from mobile.ibikoresho.ifishi import Ifishi
from mobile.ibikoresho.ikarita import Ikarita
from mobile.ibikoresho.ishusho import Ishusho
from mobile.ibikoresho.ikadiri import Ikadiri
from mobile.ibikoresho.ikubaza import Ikubaza
from mobile.ibikoresho.umubare import Umubare
from mobile.ibikoresho.urutonde import Urutonde
from mobile.imiterere.inkingi import Alignment, Inkingi
from mobile.imiterere.umurongo import Umurongo
from mobile.imiterere.urusobete import Urusobete
from mobile.imiterere.itemba import Itemba
from mobile.imiterere.ikinyabiziga import Ikinyabiziga
from mobile.kamere.imiterere import Imiterere
from mobile.kamere.ibonwa import Ibonwa, IbonwaOrutonde, IbonwaInzuzi


# ---------------------------------------------------------------------------
# TestMobileApplication
# ---------------------------------------------------------------------------


class TestMobileApplication:
    def test_create_default(self):
        app = MobileApplication()
        assert app.name == "i-mobile-app"
        assert app.version == "0.1.0"
        assert app.debug is False
        assert app.activities == []
        assert app.current_activity is None
        assert app.navigator is not None

    def test_create_custom(self):
        app = MobileApplication("MyApp", "2.0.0", debug=True)
        assert app.name == "MyApp"
        assert app.version == "2.0.0"
        assert app.debug is True

    def test_debug_property(self):
        app = MobileApplication()
        assert app.debug is False
        app.debug = True
        assert app.debug is True

    def test_lifecycle_run(self):
        app = MobileApplication()
        app.register_activity(Ikiganiro("test"))
        app.run()
        assert app.current_activity is not None

    def test_lifecycle_stop(self):
        app = MobileApplication()
        app.run()
        app.stop()
        assert app.current_activity is None

    def test_register_activity(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.register_activity(act)
        assert act in app.activities
        assert len(app.activities) == 1

    def test_register_activity_duplicate(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.register_activity(act)
        app.register_activity(act)
        assert len(app.activities) == 1

    def test_start_activity(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.start_activity(act)
        assert app.current_activity is act
        assert act.state == ActivityState.KIGEZWEHO

    def test_start_activity_with_params(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.start_activity(act, {"key": "value"})
        assert act.params.get("key") == "value"

    def test_start_activity_auto_registers(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.start_activity(act)
        assert act in app.activities

    def test_finish_activity(self):
        app = MobileApplication()
        act1 = Ikiganiro("act1")
        act2 = Ikiganiro("act2")
        app.start_activity(act1)
        app.start_activity(act2)
        app.finish_activity(act2)
        assert app.current_activity is act1
        assert act2.state == ActivityState.KURASENZWE

    def test_finish_activity_none(self):
        app = MobileApplication()
        app.finish_activity()
        assert app.current_activity is None

    def test_on_save_and_restore_state(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.register_activity(act)
        saved = app.on_save_state()
        assert "activity_stack" in saved
        assert "activity_states" in saved
        assert "nav_history" in saved

        app2 = MobileApplication()
        app2.register_activity(Ikiganiro("act1"))
        app2.on_restore_state(saved)
        assert app2.navigator.history == saved["nav_history"]

    def test_on_back_pressed(self):
        app = MobileApplication()
        act1 = Ikiganiro("act1")
        act2 = Ikiganiro("act2")
        app.start_activity(act1)
        app.start_activity(act2)
        result = app.on_back_pressed()
        assert result is True
        assert app.current_activity is act1

    def test_on_back_pressed_no_stack(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.start_activity(act)
        app.on_back_pressed()
        result = app.on_back_pressed()
        assert result is False

    def test_on_low_memory(self):
        app = MobileApplication()
        act = Ikiganiro("act1")
        app.start_activity(act)
        app.on_low_memory()
        assert act.state == ActivityState.KURASENZWE

    def test_on_create_callback(self):
        app = MobileApplication()
        app.on_create()

    def test_on_start_callback(self):
        app = MobileApplication()
        app.on_start()

    def test_on_resume_callback(self):
        app = MobileApplication()
        app.on_resume()

    def test_on_pause_callback(self):
        app = MobileApplication()
        app.on_pause()

    def test_on_stop_callback(self):
        app = MobileApplication()
        app.on_stop()

    def test_on_destroy_callback(self):
        app = MobileApplication()
        app.on_destroy()

    def test_load_config_valid(self, tmp_path):
        app = MobileApplication()
        cfg = tmp_path / "config.json"
        cfg.write_text('{"debug": true}')
        assert app.load_config(str(cfg)) is True
        assert app.debug is True

    def test_load_config_missing(self):
        app = MobileApplication()
        assert app.load_config("nonexistent.json") is False

    def test_load_config_invalid_json(self, tmp_path):
        app = MobileApplication()
        cfg = tmp_path / "bad.json"
        cfg.write_text("not json")
        assert app.load_config(str(cfg)) is False

    def test_managers_exist(self):
        app = MobileApplication()
        assert app.state_manager is not None
        assert app.security is not None
        assert app.database is not None
        assert app.network is not None
        assert app.media is not None
        assert app.device is not None
        assert app.ai is not None
        assert app.perf is not None

    def test_activity_stack_order(self):
        app = MobileApplication()
        a1 = Ikiganiro("a1")
        a2 = Ikiganiro("a2")
        a3 = Ikiganiro("a3")
        app.start_activity(a1)
        app.start_activity(a2)
        app.start_activity(a3)
        assert app.current_activity is a3
        app.finish_activity(a3)
        assert app.current_activity is a2
        app.finish_activity(a2)
        assert app.current_activity is a1

    def test_property_types(self):
        app = MobileApplication()
        assert isinstance(app.activities, list)
        assert isinstance(app.navigator, Ubugenzuzi)
        assert isinstance(app.debug, bool)


# ---------------------------------------------------------------------------
# TestIkiganiro
# ---------------------------------------------------------------------------


class TestIkiganiro:
    def test_create(self):
        act = Ikiganiro("test-activity", "Test Title")
        assert act.id == "test-activity"
        assert act.title == "Test Title"
        assert act.state == ActivityState.KUREMWE
        assert act.params == {}
        assert act.children == []
        assert act.parent is None

    def test_create_minimal(self):
        act = Ikiganiro("minimal")
        assert act.id == "minimal"
        assert act.title == ""

    def test_state_transitions(self):
        act = Ikiganiro("lifecycle")
        assert act.state == ActivityState.KUREMWE
        act.on_create()
        assert act.state == ActivityState.KUREMWE
        act.on_start()
        assert act.state == ActivityState.KURAMUKA
        act.on_resume()
        assert act.state == ActivityState.KIGEZWEHO
        act.on_pause()
        assert act.state == ActivityState.KURAHAGURIKA
        act.on_stop()
        assert act.state == ActivityState.KURAHAGARARA
        act.on_destroy()
        assert act.state == ActivityState.KURASENZWE

    def test_title_setter(self):
        act = Ikiganiro("test")
        act.title = "New Title"
        assert act.title == "New Title"

    def test_params_setter(self):
        act = Ikiganiro("test")
        act.params = {"a": 1, "b": 2}
        assert act.params == {"a": 1, "b": 2}

    def test_set_content(self):
        act = Ikiganiro("test")
        obj = object()
        act.set_content(obj)
        assert act._content is obj

    def test_find_view_by_id(self):
        act = Ikiganiro("test")
        view = object()
        act._views["my_view"] = view
        assert act.find_view_by_id("my_view") is view
        assert act.find_view_by_id("missing") is None

    def test_save_state(self):
        act = Ikiganiro("test", "Title")
        act.params = {"key": "value"}
        state = act.save_state()
        assert state["id"] == "test"
        assert state["title"] == "Title"
        assert state["params"]["key"] == "value"
        assert state["state"] == "created"

    def test_restore_state(self):
        act = Ikiganiro("test")
        saved = {
            "id": "test",
            "title": "Restored",
            "params": {"x": 10},
            "state": "resumed",
        }
        act.restore_state(saved)
        assert act.title == "Restored"
        assert act.params.get("x") == 10
        assert act.state == ActivityState.KIGEZWEHO

    def test_add_child(self):
        parent = Ikiganiro("parent")
        child = Ikiganiro("child")
        parent.add_child(child)
        assert child in parent.children
        assert child.parent is parent

    def test_remove_child(self):
        parent = Ikiganiro("parent")
        child = Ikiganiro("child")
        parent.add_child(child)
        parent.remove_child(child)
        assert child not in parent.children
        assert child.parent is None

    def test_repr(self):
        act = Ikiganiro("test", "Title")
        r = repr(act)
        assert "Ikiganiro" in r
        assert "test" in r
        assert "Title" in r

    def test_on_destroy_clears_views(self):
        act = Ikiganiro("test")
        act._views["v1"] = object()
        act._children.append(Ikiganiro("child"))
        act._content = object()
        act.on_destroy()
        assert act._views == {}
        assert act._children == []
        assert act._content is None

    def test_multiple_children(self):
        parent = Ikiganiro("parent")
        c1 = Ikiganiro("c1")
        c2 = Ikiganiro("c2")
        c3 = Ikiganiro("c3")
        parent.add_child(c1)
        parent.add_child(c2)
        parent.add_child(c3)
        assert len(parent.children) == 3
        parent.remove_child(c2)
        assert len(parent.children) == 2
        assert c2.parent is None


# ---------------------------------------------------------------------------
# TestUbugenzuzi
# ---------------------------------------------------------------------------


class TestUbugenzuzi:
    def test_create(self):
        nav = Ubugenzuzi()
        assert nav.stack == []
        assert nav.history == []
        assert nav.routes == {}
        assert nav.current_route is None
        assert nav.can_go_back is False

    def test_register_route(self):
        nav = Ubugenzuzi()
        route = NavigationRoute("/home", "home")
        nav.register_route(route)
        assert nav.routes["home"] is route
        assert nav.current_route is None

    def test_register_routes(self):
        nav = Ubugenzuzi()
        r1 = NavigationRoute("/a", "a")
        r2 = NavigationRoute("/b", "b")
        nav.register_routes([r1, r2])
        assert len(nav.routes) == 2

    def test_push(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/home", "home"))
        nav.push("home")
        assert nav.current_route is not None
        assert nav.current_route.name == "home"

    def test_push_with_params(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/user/:id", "user"))
        nav.push("user", {"id": "42"})
        assert nav.current_route.name == "user"

    def test_push_unknown_route(self):
        nav = Ubugenzuzi()
        with pytest.raises(ValueError, match="Unknown route"):
            nav.push("nonexistent")

    def test_pop(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.register_route(NavigationRoute("/b", "b"))
        nav.push("a")
        nav.push("b")
        entry = nav.pop()
        assert entry is not None
        assert entry.route.name == "b"
        assert nav.current_route.name == "a"

    def test_pop_empty(self):
        nav = Ubugenzuzi()
        assert nav.pop() is None

    def test_replace(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.register_route(NavigationRoute("/b", "b"))
        nav.push("a")
        nav.replace("b")
        assert nav.current_route.name == "b"
        assert len(nav.stack) == 1

    def test_clear(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.push("a")
        nav.clear()
        assert nav.stack == []

    def test_go_back(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.register_route(NavigationRoute("/b", "b"))
        nav.push("a")
        nav.push("b")
        assert nav.go_back() is True
        assert nav.current_route.name == "a"

    def test_go_back_fails_when_single(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.push("a")
        assert nav.go_back() is False

    def test_can_go_back(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.register_route(NavigationRoute("/b", "b"))
        assert nav.can_go_back is False
        nav.push("a")
        assert nav.can_go_back is False
        nav.push("b")
        assert nav.can_go_back is True

    def test_navigate_by_name(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/home", "home"))
        nav.navigate("home")
        assert nav.current_route.name == "home"

    def test_navigate_by_path(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/user/:id", "user"))
        nav.navigate("/user/99")
        assert nav.current_route.name == "user"

    def test_navigate_unknown(self):
        nav = Ubugenzuzi()
        with pytest.raises(ValueError, match="Route not found"):
            nav.navigate("/unknown")

    def test_deep_link(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/profile", "profile", deep_link="i-app://profile"))
        assert nav.handle_deep_link("i-app://profile") is True
        assert nav.current_route.name == "profile"

    def test_deep_link_unhandled(self):
        nav = Ubugenzuzi()
        assert nav.handle_deep_link("unknown://link") is False

    def test_universal_link(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/profile", "profile"))
        assert nav.handle_universal_link("https://example.com/profile") is True
        assert nav.current_route.name == "profile"

    def test_universal_link_unhandled(self):
        nav = Ubugenzuzi()
        assert nav.handle_universal_link("https://example.com/unknown") is False

    def test_tab_route(self):
        nav = Ubugenzuzi()
        nav.register_tab_route("main", NavigationRoute("/home", "home"))
        nav.register_tab_route("main", NavigationRoute("/settings", "settings"))
        nav.switch_tab("main", "home")
        assert nav.current_route.name == "home"

    def test_switch_tab_unknown_route(self):
        nav = Ubugenzuzi()
        nav.register_tab_route("main", NavigationRoute("/home", "home"))
        with pytest.raises(ValueError, match="Route"):
            nav.switch_tab("main", "nope")

    def test_drawer_routes(self):
        nav = Ubugenzuzi()
        r1 = NavigationRoute("/drawer1", "d1")
        r2 = NavigationRoute("/drawer2", "d2")
        nav.register_drawer_route(r1)
        nav.register_drawer_route(r2)
        assert len(nav.drawer_routes) == 2

    def test_nested_navigator(self):
        nav = Ubugenzuzi()
        nested = Ubugenzuzi()
        nav.register_nested_navigator("parent", nested)
        assert nav.get_nested_navigator("parent") is nested
        assert nav.get_nested_navigator("missing") is None

    def test_add_listener(self):
        nav = Ubugenzuzi()
        events = []
        def listener(event, entry):
            events.append((event, entry))
        nav.add_listener(listener)
        nav.register_route(NavigationRoute("/test", "test"))
        nav.push("test")
        assert len(events) == 1
        assert events[0][0] == NavigationEvent.PUSH

    def test_remove_listener(self):
        nav = Ubugenzuzi()
        events = []
        def listener(event, entry):
            events.append(1)
        nav.add_listener(listener)
        nav.remove_listener(listener)
        nav.register_route(NavigationRoute("/test", "test"))
        nav.push("test")
        assert len(events) == 0

    def test_on_navigate(self):
        nav = Ubugenzuzi()
        events = []
        def callback(event, entry):
            events.append(event)
        nav.on_navigate(callback)
        nav.register_route(NavigationRoute("/test", "test"))
        nav.push("test")
        assert NavigationEvent.PUSH in events

    def test_route_match(self):
        route = NavigationRoute("/user/:id/post/:post_id", "post")
        match = route.match("/user/5/post/hello")
        assert match is not None
        assert match["id"] == "5"
        assert match["post_id"] == "hello"

    def test_route_no_match(self):
        route = NavigationRoute("/home", "home")
        assert route.match("/other") is None

    def test_route_to_dict(self):
        route = NavigationRoute("/test", "test", params={"a": 1}, animation="fade", deep_link="i-app://test")
        d = route.to_dict()
        assert d["path"] == "/test"
        assert d["name"] == "test"
        assert d["params"]["a"] == 1
        assert d["animation"] == "fade"
        assert d["deep_link"] == "i-app://test"

    def test_route_from_dict(self):
        d = {"path": "/test", "name": "test", "params": {"a": 1}, "animation": "fade", "deep_link": "i-app://test"}
        route = NavigationRoute.from_dict(d)
        assert route.path == "/test"
        assert route.name == "test"
        assert route.params["a"] == 1

    def test_restore_state(self):
        nav = Ubugenzuzi()
        nav.register_route(NavigationRoute("/a", "a"))
        nav.push("a")
        saved = nav.history
        nav2 = Ubugenzuzi()
        nav2.register_route(NavigationRoute("/a", "a"))
        nav2.restore_state(saved)
        assert len(nav2.stack) == 1


# ---------------------------------------------------------------------------
# TestIbikoresho
# ---------------------------------------------------------------------------


class TestIbikoresho:
    def test_buto_create_default(self):
        b = Buto()
        assert b.text == ""
        assert b.enabled is True
        assert b.loading is False
        assert b.size == ButoSize.MEDIUM
        assert b.variant == ButoVariant.PRIMARY
        assert b.visible is True

    def test_buto_create_custom(self):
        b = Buto("Click", color="#ff0000", size=ButoSize.LARGE, variant=ButoVariant.OUTLINE)
        assert b.text == "Click"
        assert b.color == "#ff0000"
        assert b.size == ButoSize.LARGE
        assert b.variant == ButoVariant.OUTLINE

    def test_buto_press(self):
        result = []
        def callback():
            result.append("pressed")
        b = Buto("Press", on_press=callback)
        b.press()
        assert result == ["pressed"]

    def test_buto_press_disabled(self):
        result = []
        def callback():
            result.append("pressed")
        b = Buto("Press", on_press=callback, enabled=False)
        b.press()
        assert result == []

    def test_buto_press_loading(self):
        result = []
        def callback():
            result.append("pressed")
        b = Buto("Press", on_press=callback, loading=True)
        b.press()
        assert result == []

    def test_buto_setters(self):
        b = Buto()
        b.text = "New"
        assert b.text == "New"
        b.enabled = False
        assert b.enabled is False
        b.loading = True
        assert b.loading is True
        b.color = "#00ff00"
        assert b.color == "#00ff00"
        b.text_color = "#fff"
        assert b.text_color == "#fff"
        b.border_radius = 8
        assert b.border_radius == 8
        b.padding = 16
        assert b.padding == 16
        b.icon = "star"
        assert b.icon == "star"
        b.size = ButoSize.SMALL
        assert b.size == ButoSize.SMALL
        b.variant = ButoVariant.TEXT
        assert b.variant == ButoVariant.TEXT

    def test_buto_render(self):
        b = Buto("OK", color="#333", size=ButoSize.SMALL)
        r = b.render()
        assert r["type"] == "Buto"
        assert r["text"] == "OK"
        assert r["color"] == "#333"
        assert r["size"] == "small"

    def test_ikimenyetso_create(self):
        t = Ikimenyetso("Hello", font_size=18, color="red")
        assert t.text == "Hello"
        assert t.font_size == 18
        assert t.color == "red"
        assert t.font_weight == FontWeight.NORMAL

    def test_ikimenyetso_text_transform_upper(self):
        t = Ikimenyetso("hello", text_transform=TextTransform.UPPERCASE)
        assert t._apply_transform() == "HELLO"

    def test_ikimenyetso_text_transform_lower(self):
        t = Ikimenyetso("HELLO", text_transform=TextTransform.LOWERCASE)
        assert t._apply_transform() == "hello"

    def test_ikimenyetso_text_transform_capitalize(self):
        t = Ikimenyetso("hello", text_transform=TextTransform.CAPITALIZE)
        assert t._apply_transform() == "Hello"

    def test_ikimenyetso_setters(self):
        t = Ikimenyetso("test")
        t.text = "changed"
        assert t.text == "changed"
        t.font_size = 20
        assert t.font_size == 20
        t.font_weight = FontWeight.BOLD
        assert t.font_weight == FontWeight.BOLD
        t.color = "blue"
        assert t.color == "blue"
        t.text_align = "center"
        assert t.text_align == "center"
        t.line_height = 1.5
        assert t.line_height == 1.5
        t.max_lines = 2
        assert t.max_lines == 2
        t.overflow = "ellipsis"
        assert t.overflow == "ellipsis"
        t.text_transform = TextTransform.UPPERCASE
        assert t.text_transform == TextTransform.UPPERCASE

    def test_ikimenyetso_measure(self):
        t = Ikimenyetso("Hello", font_size=14)
        w, h = t.measure()
        assert w > 0
        assert h > 0

    def test_ikimenyetso_render(self):
        t = Ikimenyetso("Hi", font_weight=FontWeight.BOLD)
        r = t.render()
        assert r["type"] == "Ikimenyetso"
        assert r["font_weight"] == "bold"

    def test_umutwe_create(self):
        h = Umutwe("Title", level=2)
        assert h.text == "Title"
        assert h.level == 2
        assert h.font_size == 28

    def test_umutwe_level_setter(self):
        h = Umutwe("Title", level=1)
        h.level = 4
        assert h.level == 4
        assert h.font_size == 20

    def test_umutwe_level_clamping(self):
        h = Umutwe("Title", level=1)
        h.level = 99
        assert h.level == 6
        h.level = -5
        assert h.level == 1

    def test_umutwe_render(self):
        h = Umutwe("Heading", level=3)
        r = h.render()
        assert r["type"] == "Umutwe"
        assert r["level"] == 3

    def test_ibara_create(self):
        p = Ibara("Body text")
        assert p.text == "Body text"
        assert p.font_size == 16
        assert p.line_height == 1.5

    def test_ibara_render(self):
        p = Ibara("Paragraph")
        r = p.render()
        assert r["type"] == "Ibara"

    def test_ifishi_create(self):
        f = Ifishi(placeholder="Enter name")
        assert f.placeholder == "Enter name"

    def test_ikarita_create(self):
        c = Ikarita(title="Card Title")
        assert c.title == "Card Title"

    def test_ishusho_create(self):
        img = Ishusho(source="https://example.com/img.png")
        assert img.source == "https://example.com/img.png"

    def test_ikadiri_create(self):
        d = Ikadiri(title="Dialog")
        assert d.title == "Dialog"

    def test_ikubaza_create(self):
        bs = Ikubaza()
        assert bs is not None

    def test_umubare_create(self):
        badge = Umubare(value=5)
        assert badge.value == 5

    def test_urutonde_create(self):
        lst = Urutonde()
        assert lst is not None

    def test_ikoresho_base(self):
        ik = Ikoresho()
        assert ik.enabled is True
        assert ik.visible is True


# ---------------------------------------------------------------------------
# TestImiterere (Layouts)
# ---------------------------------------------------------------------------


class TestImiterere:
    def test_inkingi_create(self):
        col = Inkingi(spacing=8, padding=16)
        assert col.spacing == 8
        assert col.padding == 16
        assert col.children == []
        assert col.alignment == Alignment.START

    def test_inkingi_add_child(self):
        col = Inkingi()
        col.add("child1")
        col.add("child2")
        assert len(col.children) == 2
        assert col.children[0] == "child1"

    def test_inkingi_add_at_index(self):
        col = Inkingi(children=["a", "c"])
        col.add("b", index=1)
        assert col.children == ["a", "b", "c"]

    def test_inkingi_remove_child(self):
        col = Inkingi(children=["a", "b"])
        assert col.remove("a") is True
        assert col.children == ["b"]
        assert col.remove("x") is False

    def test_inkingi_clear(self):
        col = Inkingi(children=["a", "b"])
        col.clear()
        assert col.children == []

    def test_inkingi_get_child(self):
        col = Inkingi(children=["x", "y"])
        assert col.get_child(1) == "y"

    def test_inkingi_get_child_index_error(self):
        col = Inkingi(children=[])
        with pytest.raises(IndexError):
            col.get_child(0)

    def test_inkingi_setters(self):
        col = Inkingi()
        col.spacing = 12
        assert col.spacing == 12
        col.padding = 24
        assert col.padding == 24
        col.alignment = Alignment.CENTER
        assert col.alignment == Alignment.CENTER
        col.cross_alignment = Alignment.END
        assert col.cross_alignment == Alignment.END
        col.width = 300
        assert col.width == 300
        col.height = 400
        assert col.height == 400
        col.scrollable = True
        assert col.scrollable is True

    def test_umurongo_create(self):
        row = Umurongo(spacing=8, wrap=True)
        assert row.spacing == 8
        assert row.wrap is True

    def test_umurongo_add_remove(self):
        row = Umurongo()
        row.add("a")
        row.add("b")
        assert len(row.children) == 2
        row.remove("a")
        assert len(row.children) == 1

    def test_umurongo_setters(self):
        row = Umurongo()
        row.wrap = False
        assert row.wrap is False
        row.spacing = 10
        assert row.spacing == 10

    def test_urusobete_create(self):
        grid = Urusobete(columns=3, spacing=4)
        assert grid.columns == 3
        assert grid.spacing == 4
        assert grid.row_count == 0

    def test_urusobete_invalid_columns(self):
        with pytest.raises(ValueError, match="columns must be at least 1"):
            Urusobete(columns=0)

    def test_urusobete_columns_setter(self):
        grid = Urusobete(columns=2)
        grid.columns = 4
        assert grid.columns == 4
        with pytest.raises(ValueError):
            grid.columns = 0

    def test_urusobete_row_count(self):
        grid = Urusobete(columns=3)
        grid.add("a")
        grid.add("b")
        grid.add("c")
        grid.add("d")
        assert grid.row_count == 2

    def test_urusobete_get_item_position(self):
        grid = Urusobete(columns=2)
        grid.add("a")
        grid.add("b")
        grid.add("c")
        pos = grid.get_item_position(2)
        assert pos == (1, 0)

    def test_urusobete_get_item_position_index_error(self):
        grid = Urusobete(columns=2)
        with pytest.raises(IndexError):
            grid.get_item_position(5)

    def test_urusobete_add_remove(self):
        grid = Urusobete(columns=2)
        grid.add("x")
        grid.add("y")
        grid.remove("x")
        assert len(grid.children) == 1

    def test_urusobete_clear(self):
        grid = Urusobete(columns=2, children=["a", "b"])
        grid.clear()
        assert grid.children == []

    def test_itemba_create(self):
        table = Itemba()
        assert table is not None

    def test_ikinyabiziga_create(self):
        scroll = Ikinyabiziga()
        assert scroll is not None


# ---------------------------------------------------------------------------
# TestKamere (State Management)
# ---------------------------------------------------------------------------


class TestKamere:
    def test_imiterere_create(self):
        s = Imiterere(0)
        assert s.value == 0
        assert s.previous_value == 0
        assert s.changed is False

    def test_imiterere_set(self):
        s = Imiterere(0)
        s.set(5)
        assert s.value == 5
        assert s.previous_value == 0
        assert s.changed is True

    def test_imiterere_get(self):
        s = Imiterere("hello")
        assert s.get() == "hello"

    def test_imiterere_reset(self):
        s = Imiterere(10)
        s.set(20)
        s.reset()
        assert s.value == 10

    def test_imiterere_observe(self):
        s = Imiterere(0)
        observed = []
        def cb(old, new):
            observed.append((old, new))
        s.observe(cb)
        s.set(1)
        s.set(2)
        assert observed == [(0, 1), (1, 2)]

    def test_imiterere_unobserve(self):
        s = Imiterere(0)
        def cb(old, new):
            pass
        oid = s.observe(cb)
        assert s.unobserve(oid) is True
        assert s.unobserve(999) is False

    def test_imiterere_set_same_value(self):
        s = Imiterere("a")
        observed = []
        def cb(old, new):
            observed.append((old, new))
        s.observe(cb)
        s.set("a")
        assert observed == []

    def test_imiterere_value_property(self):
        s = Imiterere(0)
        s.value = 42
        assert s.value == 42

    def test_ibonwa_create(self):
        obs = Ibonwa(0)
        assert obs.value == 0
        assert obs.lazy is True

    def test_ibonwa_subscribe(self):
        obs = Ibonwa("start")
        events = []
        def cb(old, new):
            events.append(new)
        obs.subscribe(cb)
        obs.set("end")
        assert events == ["end"]

    def test_ibonwa_unsubscribe(self):
        obs = Ibonwa(0)
        def cb(o, n):
            pass
        sid = obs.subscribe(cb)
        assert obs.unsubscribe(sid) is True

    def test_ibonwa_compute(self):
        a = Imiterere(2)
        b = Imiterere(3)
        obs = Ibonwa(0, dependencies=[a, b])
        obs.compute(lambda x, y: x + y)
        assert obs.value == 5

    def test_ibonwa_when(self):
        obs = Ibonwa(0)
        triggered = []
        cancel = obs.when(lambda v: v > 5, lambda v: triggered.append(v))
        obs.set(3)
        assert triggered == []
        obs.set(10)
        assert triggered == [10]
        cancel()
        obs.set(20)
        assert triggered == [10]

    def test_ibonwa_when_cancel(self):
        obs = Ibonwa(0)
        triggered = []
        cancel = obs.when(lambda v: v > 0, lambda v: triggered.append(v))
        cancel()
        obs.set(1)
        assert triggered == []

    def test_ibonwa_orutonde(self):
        lst = IbonwaOrutonde([1, 2, 3])
        assert len(lst) == 3
        assert lst[0] == 1

    def test_ibonwa_orutonde_append(self):
        lst = IbonwaOrutonde([1])
        lst.append(2)
        assert list(lst) == [1, 2]

    def test_ibonwa_orutonde_insert(self):
        lst = IbonwaOrutonde(["a", "c"])
        lst.insert(1, "b")
        assert list(lst) == ["a", "b", "c"]

    def test_ibonwa_orutonde_remove(self):
        lst = IbonwaOrutonde([1, 2, 3])
        assert lst.remove(2) is True
        assert list(lst) == [1, 3]
        assert lst.remove(99) is False

    def test_ibonwa_orutonde_pop(self):
        lst = IbonwaOrutonde([1, 2, 3])
        val = lst.pop()
        assert val == 3
        assert list(lst) == [1, 2]

    def test_ibonwa_orutonde_clear(self):
        lst = IbonwaOrutonde([1, 2])
        lst.clear()
        assert list(lst) == []

    def test_ibonwa_orutonde_extend(self):
        lst = IbonwaOrutonde([1])
        lst.extend([2, 3])
        assert list(lst) == [1, 2, 3]

    def test_ibonwa_orutonde_sort(self):
        lst = IbonwaOrutonde([3, 1, 2])
        lst.sort()
        assert list(lst) == [1, 2, 3]

    def test_ibonwa_orutonde_filter(self):
        lst = IbonwaOrutonde([1, 2, 3, 4])
        filtered = lst.filter(lambda x: x % 2 == 0)
        assert list(filtered) == [2, 4]

    def test_ibonwa_orutonde_map(self):
        lst = IbonwaOrutonde([1, 2, 3])
        mapped = lst.map(lambda x: x * 2)
        assert list(mapped) == [2, 4, 6]

    def test_ibonwa_inzuzi(self):
        d = IbonwaInzuzi({"a": 1})
        assert len(d) == 1
        assert d["a"] == 1

    def test_ibonwa_inzuzi_set_item(self):
        d = IbonwaInzuzi()
        d.set_item("key", "value")
        assert d.get_item("key") == "value"

    def test_ibonwa_inzuzi_remove_item(self):
        d = IbonwaInzuzi({"x": 10})
        assert d.remove_item("x") is True
        assert "x" not in d
        assert d.remove_item("nope") is False

    def test_ibonwa_inzuzi_clear(self):
        d = IbonwaInzuzi({"a": 1, "b": 2})
        d.clear()
        assert len(d) == 0

    def test_ibonwa_inzuzi_update(self):
        d = IbonwaInzuzi({"a": 1})
        d.update({"b": 2, "c": 3})
        assert dict(d) == {"a": 1, "b": 2, "c": 3}

    def test_ibonwa_inzuzi_keys_values(self):
        d = IbonwaInzuzi({"x": 1, "y": 2})
        assert "x" in d.keys()
        assert "y" in d.keys()
        assert 1 in d.values()
        assert 2 in d.values()

    def test_ibonwa_inzuzi_bracket_ops(self):
        d = IbonwaInzuzi({"a": 1})
        d["b"] = 2
        assert d["b"] == 2
        del d["a"]
        assert "a" not in d
