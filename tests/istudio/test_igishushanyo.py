"""Tests for istudio.igishushanyo — Visual Designers."""

from __future__ import annotations

from src.istudio.igishushanyo import VisualDesigner, FormDesigner, UIComponent, FormField, FormLayout


def test_visual_designer_init():
    vd = VisualDesigner()
    assert vd.list_components() == []


def test_add_component():
    vd = VisualDesigner()
    c = UIComponent(id="btn1", type="button", label="Click Me", x=10, y=20)
    cid = vd.add_component(c)
    assert cid == "btn1"
    assert len(vd.list_components()) == 1


def test_get_component():
    vd = VisualDesigner()
    c = UIComponent(id="btn1", type="button")
    vd.add_component(c)
    assert vd.get_component("btn1") is c
    assert vd.get_component("nonexistent") is None


def test_remove_component():
    vd = VisualDesigner()
    vd.add_component(UIComponent(id="c1", type="label"))
    assert vd.remove_component("c1") is True
    assert vd.remove_component("c1") is False


def test_update_component():
    vd = VisualDesigner()
    vd.add_component(UIComponent(id="c1", type="button", label="old"))
    vd.update_component("c1", label="new", width=200)
    c = vd.get_component("c1")
    assert c.label == "new"
    assert c.width == 200


def test_copy_component():
    vd = VisualDesigner()
    vd.add_component(UIComponent(id="c1", type="button", label="test"))
    new_id = vd.copy_component("c1")
    assert new_id is not None
    assert new_id != "c1"
    assert vd.get_component(new_id) is not None


def test_add_remove_child():
    vd = VisualDesigner()
    parent = UIComponent(id="parent", type="container")
    child = UIComponent(id="child", type="button", label="Child")
    vd.add_component(parent)
    assert vd.add_child("parent", child) is True
    assert len(vd.get_component("parent").children) == 1
    assert vd.remove_child("parent", "child") is True
    assert len(vd.get_component("parent").children) == 0


def test_add_child_nonexistent_parent():
    vd = VisualDesigner()
    child = UIComponent(id="c", type="label")
    assert vd.add_child("nonexistent", child) is False


def test_generate_code():
    vd = VisualDesigner()
    btn = UIComponent(id="btn1", type="button", label="OK")
    vd.add_component(btn)
    code = vd.generate_code("btn1")
    assert 'button(label="OK")' in code


def test_generate_container_code():
    vd = VisualDesigner()
    container = UIComponent(id="cont", type="container")
    btn = UIComponent(id="btn", type="button", label="Go")
    vd.add_component(container)
    vd.add_child("cont", btn)
    code = vd.generate_code("cont")
    assert "container()" in code
    assert 'button(label="Go")' in code


def test_clear():
    vd = VisualDesigner()
    vd.add_component(UIComponent(id="c1", type="label"))
    vd.add_component(UIComponent(id="c2", type="button"))
    vd.clear()
    assert vd.list_components() == []


def test_generate_form_code():
    form = FormLayout(title="Login Form")
    form.fields.append(FormField(name="username", type="text", label="Username", required=True))
    form.fields.append(FormField(name="password", type="password", label="Password", required=True))
    vd = VisualDesigner()
    code = vd.generate_form_code(form)
    assert 'form_layout(title="Login Form")' in code
    assert "username" in code
    assert "password" in code


def test_form_designer():
    fd = FormDesigner()
    form = fd.create_form("login", "Login Form")
    assert form.title == "Login Form"
    fd.add_field("login", FormField(name="email", type="email", label="Email"))
    assert len(fd.get_form("login").fields) == 1
    fd.remove_field("login", "email")
    assert len(fd.get_form("login").fields) == 0


def test_form_designer_list():
    fd = FormDesigner()
    fd.create_form("a", "Form A")
    fd.create_form("b", "Form B")
    assert len(fd.list_forms()) == 2
