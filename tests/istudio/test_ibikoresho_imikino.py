"""Tests for istudio.ibikoresho_imikino — Game Tools."""

from __future__ import annotations

from src.istudio.ibikoresho_imikino import GameDesigner, GameAsset, GameScene, Animation


def test_game_designer_init():
    gd = GameDesigner()
    assert gd.list_assets() == []
    assert gd.list_scenes() == []


def test_add_asset():
    gd = GameDesigner()
    asset = GameAsset(name="player_sprite", type="sprite", path="assets/player.png", width=32, height=32)
    gd.add_asset(asset)
    assert len(gd.list_assets()) == 1
    assert gd.get_asset("player_sprite") is not None


def test_get_asset_nonexistent():
    gd = GameDesigner()
    assert gd.get_asset("nonexistent") is None


def test_remove_asset():
    gd = GameDesigner()
    gd.add_asset(GameAsset(name="bg", type="image"))
    assert gd.remove_asset("bg") is True
    assert gd.remove_asset("bg") is False


def test_create_scene():
    gd = GameDesigner()
    scene = gd.create_scene("level1", background="sky.png", physics=True)
    assert scene.name == "level1"
    assert scene.background == "sky.png"
    assert scene.physics is True


def test_get_scene():
    gd = GameDesigner()
    gd.create_scene("level1")
    scene = gd.get_scene("level1")
    assert scene is not None
    assert gd.get_scene("nonexistent") is None


def test_list_scenes():
    gd = GameDesigner()
    gd.create_scene("level1")
    gd.create_scene("level2")
    assert len(gd.list_scenes()) == 2


def test_remove_scene():
    gd = GameDesigner()
    gd.create_scene("level1")
    assert gd.remove_scene("level1") is True
    assert gd.remove_scene("level1") is False


def test_add_object_to_scene():
    gd = GameDesigner()
    gd.create_scene("level1")
    obj = {"type": "player", "x": 100, "y": 200}
    assert gd.add_object_to_scene("level1", obj) is True
    assert len(gd.get_scene("level1").objects) == 1


def test_add_object_to_nonexistent_scene():
    gd = GameDesigner()
    assert gd.add_object_to_scene("nonexistent", {}) is False


def test_create_animation():
    gd = GameDesigner()
    anim = gd.create_animation("run", ["f1.png", "f2.png", "f3.png"], frame_duration_ms=50, loop=True)
    assert anim.name == "run"
    assert len(anim.frames) == 3
    assert anim.frame_duration_ms == 50
    assert anim.loop is True


def test_get_animation():
    gd = GameDesigner()
    gd.create_animation("run", [])
    assert gd.get_animation("run") is not None
    assert gd.get_animation("nonexistent") is None


def test_generate_scene_code():
    gd = GameDesigner()
    gd.create_scene("level1", background="bg.png", physics=True)
    gd.add_object_to_scene("level1", {"type": "player"})
    code = gd.generate_scene_code("level1")
    assert 'create_scene("level1")' in code
    assert 'set_background("bg.png")' in code
    assert "enable_physics" in code


def test_generate_scene_code_nonexistent():
    gd = GameDesigner()
    assert gd.generate_scene_code("nonexistent") == ""


def test_multiple_animations():
    gd = GameDesigner()
    gd.create_animation("idle", ["idle1.png"])
    gd.create_animation("run", ["run1.png", "run2.png"])
    assert gd.get_animation("idle") is not None
    assert gd.get_animation("run") is not None
