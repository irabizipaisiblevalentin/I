"""IMIKINO Quickstart — Complete game engine example."""
import sys
sys.path.insert(0, 'src')

from imikino import (
    get_engine, Scene, Layer,
    Vector3, Transform, Color,
    get_rendering, Mesh, Material, RenderComponent, CameraComponent,
    get_physics, RigidBodyComponent, PhysicsBodyType,
    get_audio, AudioClip,
    get_animation, AnimationClip, AnimatorComponent,
    get_input, InputSystem,
    get_network, NetworkMessage, NetworkRole,
    get_editor, Editor, EditorTool,
    ScriptComponent,
    get_ai, BehaviourTree, SelectorNode, ActionNode,
    Entity,
)

print("=== IMIKINO Quickstart ===\n")

# 1. Engine
print("--- Engine ---")
engine = get_engine()
print(f"Engine: {engine.config.title}\n")

# 2. ECS
print("--- ECS ---")
scene = Scene(name="MainScene")
entity = scene.create_entity("Player")
transform = scene.get_transform(entity)
print(f"Entity: {entity.name} [{entity.id[:8]}...]\n")

# 3. Rendering
print("--- Rendering ---")
mesh = Mesh(name="Cube")
mesh.add_cube(size=2.0)
mat = Material(name="Default", albedo=Color.blue(), metallic=0.3)
rc = RenderComponent(mesh=mesh, material=mat)
entity.add(rc)
camera = CameraComponent(fov=70)
rs = get_rendering()
rs.add_renderable(rc, transform)
rs.set_camera(camera)
print(f"Mesh: {mesh.name} ({len(mesh.vertices)} verts, {len(mesh.indices)} indices)\n")

# 4. Physics
print("--- Physics ---")
body = RigidBodyComponent(body_type=PhysicsBodyType.DYNAMIC, mass=1.0)
entity.add(body)
phys = get_physics()
phys.add_body(entity.id, body)
phys.add_force(entity.id, Vector3(0, 10, 0))
hit = phys.raycast(Vector3(0, 0, 0), Vector3(0, -1, 0))
print(f"Raycast hit: {hit is not None}\n")

# 5. Audio
print("--- Audio ---")
audio = get_audio()
clip = audio.load_clip("sounds/test.wav")
src = audio.play(clip.name)
print(f"Audio playing: {clip.name}\n")

# 6. Animation
print("--- Animation ---")
anim = get_animation()
clip = anim.create_clip("idle", duration=2.0)
animator = AnimatorComponent()
animator.add_state("idle", clip)
anim.register_animator(animator)
animator.play("idle")
anim.update(0.016)
print(f"Animation: {animator.current_state}\n")

# 7. Input
print("--- Input ---")
input_sys = get_input()
input_sys.press_key("space")
print(f"Space down: {input_sys.is_key_down('space')}")
print(f"Space pressed: {input_sys.is_key_pressed('space')}\n")

# 8. Networking
print("--- Networking ---")
net = get_network()
net.start_server(port=7777)
net.broadcast(NetworkMessage(msg_type="hello", data={"msg": "Server ready"}))
msg = NetworkMessage(msg_type="chat", data={"text": "Hello!"})
net.send("player_1", msg)
print(f"Network role: {net.role.value}\n")

# 9. Scripting
print("--- Scripting ---")
script = ScriptComponent(module_path="scripts/player.py", class_name="PlayerController")
entity.add(script)
print(f"Script: {script.class_name}\n")

# 10. AI
print("--- AI ---")
ai = get_ai()
root = SelectorNode(name="Root")
root.children.append(ActionNode(name="Idle", action_fn=lambda e, dt: "success"))
tree = BehaviourTree(root=root)
ai.register_behaviour_tree(entity.id, tree)
result = tree.execute(entity, 0.016)
print(f"AI behaviour tree: {result}\n")

# 11. Editor
print("--- Editor ---")
editor = get_editor()
editor.select_entity(entity.id)
editor.active_tool = EditorTool.MOVE
print(f"Selected: {editor.selection.entity_ids}\n")

# 12. Summary
print("--- Engine Summary ---")
summary = engine.summary()
for k, v in summary.items():
    print(f"  {k}: {v}")

print("\n=== IMIKINO Quickstart Complete ===")
