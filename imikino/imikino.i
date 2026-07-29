/// imikino.i — The official game engine framework of the I Language
///
/// IMIKINO provides a complete game development ecosystem:
///   - Entity Component System (ECS)
///   - 2D/3D Rendering with PBR
///   - Physics engine (rigid bodies, collisions)
///   - 3D Audio system
///   - Skeletal animation with blend trees
///   - Input system (keyboard/mouse/touch/gamepad)
///   - Multiplayer networking
///   - AI integration with UBWENGE
///   - Full editor tooling

pub enum EngineAPI {
    Core2D = "2d",
    Core3D = "3d",
    Physics = "physics",
    Audio = "audio",
    Network = "network",
    AI = "ai",
    Editor = "editor",
}

pub struct Vector3 {
    x: Float,
    y: Float,
    z: Float,
}

pub struct Transform {
    position: Vector3,
    rotation: Quaternion,
    scale: Vector3,
}

pub struct Entity {
    id: String,
    name: String,
    active: Bool,
}

pub struct Scene {
    name: String,
    world: World,
    root: SceneNode,
}

pub fn create_entity(scene: Scene, name: String) -> Entity
pub fn destroy_entity(scene: Scene, entity_id: String) -> Bool
pub fn find_entity(scene: Scene, name: String) -> Entity?

pub fn add_component(entity: Entity, component: Component) -> Component
pub fn get_component(entity: Entity, type: Type) -> Component?
pub fn remove_component(entity: Entity, type: Type) -> Bool

pub enum CollisionShape {
    Sphere = "sphere",
    Box = "box",
    Capsule = "capsule",
}

pub struct RaycastHit {
    entity_id: String,
    point: Vector3,
    normal: Vector3,
    distance: Float,
}

pub fn raycast(origin: Vector3, direction: Vector3, max_distance: Float) -> RaycastHit?
pub fn load_scene(path: String) -> Scene
pub fn save_scene(scene: Scene, path: String)

pub struct NetworkMessage {
    type: String,
    data: Map<String, Any>,
    sender_id: String,
}

pub fn send_message(target: String, message: NetworkMessage)
pub fn broadcast_message(message: NetworkMessage)
pub fn start_server(port: Int) -> Bool
pub fn connect(host: String, port: Int) -> Bool

pub fn play_audio(clip: String, spatial: Bool) -> AudioSource
pub fn set_animation(animator: Animator, clip: String)
pub fn set_input_action(name: String, keys: [String])
pub fn get_action(name: String) -> Bool
pub fn create_navmesh(vertices: [Vector3], triangles: [Int]) -> NavigationMesh
pub fn set_destination(agent: NavMeshAgent, destination: Vector3)

// Simulation Core (ikigereranyo)
pub enum SimulationMode {
    Realtime = "realtime",
    Stepped = "stepped",
    Scaled = "scaled",
    FixedStep = "fixed_step",
    CatchUp = "catch_up",
}

pub struct SimulationClock {
    mode: SimulationMode,
    time_scale: Float,
    fixed_dt: Float,
    paused: Bool,
}

pub struct Scenario {
    name: String,
    parameters: Map<String, Any>,
}

pub fn create_simulator(name: String) -> Simulator
pub fn run_simulation(sim: Simulator, duration: Float)
pub fn stop_simulation(sim: Simulator) -> SimulationResult
pub fn record_simulation(sim: Simulator, path: String)
pub fn replay_simulation(path: String)

// Robotics (ibintu_nyabutatu)
pub enum JointType {
    Revolute = "revolute",
    Prismatic = "prismatic",
    Fixed = "fixed",
    Spherical = "spherical",
    Continuous = "continuous",
}

pub struct Joint {
    name: String,
    joint_type: JointType,
    parent_link: String,
    child_link: String,
    position: Float,
}

pub struct Link {
    name: String,
    mass: Float,
}

pub fn create_robot(name: String) -> RobotModel
pub fn compute_fk(robot: RobotModel, joint_positions: Map<String, Float>) -> Map<String, Transform>
pub fn compute_ik(robot: RobotModel, target: Transform, link: String) -> Map<String, Float>?
pub fn read_sensor(sensor: String) -> SensorReading?

// Autonomous Vehicles (imodoka)
pub enum VehicleType { Sedan = "sedan", SUV = "suv", Truck = "truck" }
pub enum TrafficLightState { Green, Yellow, Red }

pub struct VehicleDynamics {
    position: Vector3,
    heading: Float,
    velocity: Float,
    speed_kmh: Float,
}

pub struct TrafficLight {
    position: Vector3,
    state: TrafficLightState,
    green_duration: Float,
    red_duration: Float,
}

pub fn create_traffic_scenario(name: String) -> TrafficScenario
pub fn add_participant(scenario: TrafficScenario, vehicle: VehicleDynamics)
pub fn check_collisions(scenario: TrafficScenario) -> [(Int, Int, Float)]
pub fn set_adas(acc: Bool, lka: Bool, aeb: Bool)

// Smart City (umujyi)
pub enum ZoneType { Residential, Commercial, Industrial, Park, School, Hospital }
pub enum WeatherType { Clear, Cloudy, Rain, Storm, Snow, Fog }

pub struct Zone {
    name: String,
    zone_type: ZoneType,
    population: Int,
    capacity: Int,
}

pub struct Environment {
    time_of_day: Float,
    weather: WeatherType,
    temperature: Float,
}

pub fn create_city(name: String) -> CitySimulation
pub fn add_zone(city: CitySimulation, zone: Zone)
pub fn set_weather(weather: WeatherType)
pub fn get_city_stats(city: CitySimulation) -> Map<String, Any>

// Digital Twin (inganda)
pub enum MachineStatus { Idle, Running, Paused, Maintenance, Fault, Offline }
pub enum ProductState { Raw, InProgress, Completed, Rejected, Shipped }

pub struct Machine {
    name: String,
    status: MachineStatus,
    cycle_time: Float,
    oee: Float,
}

pub struct ProductionLine {
    name: String,
    machines: [Machine],
    throughput: Float,
}

pub fn create_factory(name: String) -> FactorySimulation
pub fn add_production_line(factory: FactorySimulation, line: ProductionLine)
pub fn start_production(line: String)
pub fn stop_production(line: String)
pub fn get_factory_alerts(factory: FactorySimulation) -> [String]
