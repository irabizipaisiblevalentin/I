"""IMIKINO — The official game engine and interactive simulation platform of the I Programming Language.

A complete game development ecosystem: ECS, rendering, physics, audio,
animation, input, networking, AI, scripting, asset pipeline, editor,
and professional simulation (robotics, autonomous vehicles, smart cities,
digital twins).
"""

from __future__ import annotations

from .ibikoreshingiro import (
    Vector2, Vector3, Quaternion, Matrix4, Transform, Color,
    Clock, Random, generate_entity_id,
    lerp, clamp, smoothstep,
)
from .imiyoborere import (
    World, Entity, Component, System, EntityQuery,
)
from .ikorwa import (
    Engine, EngineConfig, Scene, SceneNode, Layer,
    TransformComponent, TagComponent, NameComponent,
    get_engine,
)
from .ishushanyo import (
    RenderingSystem, Mesh, Material, Vertex,
    RenderComponent, CameraComponent, LightComponent,
    SpriteComponent, TextComponent, ParticleSystemComponent,
    ShaderType, BlendMode, RenderQueue,
    get_rendering,
)
from .ubwonekano import (
    PhysicsSystem, RigidBodyComponent, ColliderComponent,
    JointComponent, CollisionShape, PhysicsBodyType,
    RaycastHit, CollisionInfo,
    get_physics,
)
from .amajwi_imikino import (
    AudioEngine, AudioClip, AudioSourceComponent,
    AudioListenerComponent, AudioMixerGroup,
    AudioEffect, ReverbEffect, EchoEffect, LowPassFilter,
    get_audio,
)
from .imikorere_animation import (
    AnimationSystem, AnimationClip, AnimationState,
    AnimatorComponent, Skeleton, Bone,
    BlendTree, BlendTreeNode, InverseKinematics,
    Timeline, TimelineTrack, Keyframe, AnimationCurve,
    AnimationWrapMode,
    get_animation,
)
from .inyandikwa import (
    InputSystem, Touch, KeyState, GamepadState,
    InputActionBinding, MouseButton, GamepadButton,
    InputAction, TouchPhase,
    get_input,
)
from .gukoreshana import (
    NetworkManager, NetworkPeer, NetworkMessage,
    ReplicatedObject, ReplicatedProperty,
    Matchmaker, NetworkRole, ConnectionState,
    get_network,
)
from .ibikoresho import (
    AssetDatabase, AssetImporter, AssetMeta,
    Texture2D, Font, Prefab, AssetType,
    get_assets,
)
from .guhindura import (
    ScriptEngine, ScriptComponent, ScriptSystem,
    Plugin, PluginManager,
    get_scripting, get_plugins,
)
from .inyenzure import (
    AISystem, AIComponent, AIState,
    NavMeshAgentComponent, NavigationMesh,
    BehaviourTree, BehaviourTreeNode,
    SelectorNode, SequenceNode, ConditionNode, ActionNode,
    DialogueSystem, DialogueNode,
    get_ai,
)
from .uguhindura import (
    Editor, EditorLayer, EditorSelection, EditorViewport,
    EditorTool, EditorWindow,
    get_editor,
)
from .ikigereranyo import (
    Simulator, SimulationClock, SimulationMode, SimulationSystem,
    SimulationComponent, Scenario, ScenarioParameter,
    SimulationRecorder, SimulationEvent, SimulationResult,
    get_simulator,
)
from .ibintu_nyabutatu import (
    RobotModel, RobotSystem, Joint, Link, JointType,
    SensorModel, LidarSensor, CameraSensor, IMUSensor, GPSSensor, SensorType, SensorReading,
    get_robotics,
)
from .imodoka import (
    AutonomousVehicleSystem, VehicleDynamics, TrafficScenario, TrafficParticipant,
    TrafficLight, ADASSystem, VehicleType, DriveType, TrafficLightState,
    get_av_system,
)
from .umujyi import (
    CitySimulation, Zone, Building, Infrastructure, Environment, Pedestrian,
    ZoneType, WeatherType, InfrastructureType, BuildingType,
    get_city_sim,
)
from .inganda import (
    FactorySimulation, ProductionLine, Machine, Product, ConveyorBelt,
    SupplyChainNode, SupplyChainStage, EquipmentSensor, MachineStatus,
    ProductState, get_factory_sim,
)
from .itegeko import register_subcommands, genda

__all__ = [
    # Core
    "Engine", "EngineConfig", "Scene", "SceneNode", "Layer",
    "get_engine",
    # Math
    "Vector2", "Vector3", "Quaternion", "Matrix4", "Transform", "Color",
    "Clock", "Random", "generate_entity_id",
    "lerp", "clamp", "smoothstep",
    # ECS
    "World", "Entity", "Component", "System", "EntityQuery",
    # Components
    "TransformComponent", "TagComponent", "NameComponent",
    "RenderComponent", "CameraComponent", "LightComponent",
    "SpriteComponent", "TextComponent", "ParticleSystemComponent",
    "RigidBodyComponent", "ColliderComponent", "JointComponent",
    "AudioSourceComponent", "AudioListenerComponent",
    "AnimatorComponent", "ScriptComponent",
    "AIComponent", "NavMeshAgentComponent",
    # Rendering
    "RenderingSystem", "Mesh", "Material", "Vertex",
    "ShaderType", "BlendMode", "RenderQueue",
    "get_rendering",
    # Physics
    "PhysicsSystem", "CollisionShape", "PhysicsBodyType",
    "RaycastHit", "CollisionInfo",
    "get_physics",
    # Audio
    "AudioEngine", "AudioClip", "AudioMixerGroup",
    "AudioEffect", "ReverbEffect", "EchoEffect", "LowPassFilter",
    "get_audio",
    # Animation
    "AnimationSystem", "AnimationClip", "AnimationState",
    "AnimatorComponent", "Skeleton", "Bone",
    "BlendTree", "BlendTreeNode", "InverseKinematics",
    "Timeline", "Keyframe", "AnimationCurve", "AnimationWrapMode",
    "get_animation",
    # Input
    "InputSystem", "Touch", "KeyState", "GamepadState",
    "InputActionBinding", "MouseButton", "GamepadButton",
    "InputAction", "TouchPhase",
    "get_input",
    # Networking
    "NetworkManager", "NetworkPeer", "NetworkMessage",
    "ReplicatedObject", "ReplicatedProperty",
    "Matchmaker", "NetworkRole", "ConnectionState",
    "get_network",
    # Assets
    "AssetDatabase", "AssetImporter", "AssetMeta",
    "Texture2D", "Font", "Prefab", "AssetType",
    "get_assets",
    # Scripting
    "ScriptEngine", "ScriptComponent", "ScriptSystem",
    "Plugin", "PluginManager",
    "get_scripting", "get_plugins",
    # AI
    "AISystem", "AIComponent", "AIState",
    "NavMeshAgentComponent", "NavigationMesh",
    "BehaviourTree", "BehaviourTreeNode",
    "SelectorNode", "SequenceNode", "ConditionNode", "ActionNode",
    "DialogueSystem", "DialogueNode",
    "get_ai",
    # Editor
    "Editor", "EditorLayer", "EditorSelection", "EditorViewport",
    "EditorTool", "EditorWindow",
    "get_editor",
    # Simulation
    "Simulator", "SimulationClock", "SimulationMode", "SimulationSystem",
    "SimulationComponent", "Scenario", "ScenarioParameter",
    "SimulationRecorder", "SimulationEvent", "SimulationResult",
    "get_simulator",
    # Robotics
    "RobotModel", "RobotSystem", "Joint", "Link", "JointType",
    "SensorModel", "LidarSensor", "CameraSensor", "IMUSensor", "GPSSensor",
    "SensorType", "SensorReading",
    "get_robotics",
    # Autonomous Vehicles
    "AutonomousVehicleSystem", "VehicleDynamics", "TrafficScenario",
    "TrafficParticipant", "TrafficLight", "ADASSystem",
    "VehicleType", "DriveType", "TrafficLightState",
    "get_av_system",
    # Smart City
    "CitySimulation", "Zone", "Building", "Infrastructure", "Environment",
    "Pedestrian", "ZoneType", "WeatherType", "InfrastructureType", "BuildingType",
    "get_city_sim",
    # Digital Twin
    "FactorySimulation", "ProductionLine", "Machine", "Product", "ConveyorBelt",
    "SupplyChainNode", "SupplyChainStage", "EquipmentSensor", "MachineStatus", "ProductState",
    "get_factory_sim",
    # CLI
    "register_subcommands", "genda",
]
