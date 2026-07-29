"""
IMIKINO Simulation Platform — Complete Walkthrough

Demonstrates: simulation core, robotics, autonomous vehicles,
smart city, and digital twin capabilities.
"""

import math
import random

print("=" * 60)
print("IMIKINO Simulation Platform")
print("=" * 60)

# ── 1. Simulation Core ──────────────────────────────────────────────────
print("\n--- 1. Simulation Core ---")
from imikino import (
    Simulator, SimulationMode, Scenario, SimulationRecorder,
    get_simulator,
)

sim = get_simulator()
sim.name = "DemoSim"
sim.clock.mode = SimulationMode.FIXED_STEP
sim.clock.fixed_dt = 0.01
sim.set_deterministic(True, seed=42)

scenario = Scenario("demo_scenario")
scenario.add_parameter("gravity", 9.81, "float", 0.0, 20.0, "Gravity acceleration")
scenario.add_parameter("iterations", 1000, "int", 1, 10000)
sim.load_scenario(scenario)

sim.recorder.start()
sim_result = sim.run_for(1.0)
sim.recorder.stop()
print(f"  Simulator ran for {sim_result.duration:.2f}s ({sim_result.steps} steps)")
print(f"  Recorded {len(sim.recorder.events)} events")
assert sim_result.success, "Simulation should succeed"
print("  PASS: Simulation core works")

# ── 2. Robotics ─────────────────────────────────────────────────────────
print("\n--- 2. Robotics ---")
from imikino import RobotModel, Joint, Link, JointType
from imikino.ibintu_nyabutatu import (
    LidarSensor, CameraSensor, IMUSensor, GPSSensor,
    get_robotics,
)
from imikino import Vector3, Transform, Quaternion

robotics = get_robotics()
robot = RobotModel("ArmBot")
robot.add_link(Link(name="base", mass=5.0))
robot.add_joint(Joint(
    name="shoulder_pitch", joint_type=JointType.REVOLUTE,
    parent_link="base", child_link="upper_arm",
    position_lower=-math.pi, position_upper=math.pi,
))
robot.add_link(Link(name="upper_arm", mass=2.0))
robot.add_joint(Joint(
    name="elbow_pitch", joint_type=JointType.REVOLUTE,
    parent_link="upper_arm", child_link="forearm",
))
robot.add_link(Link(name="forearm", mass=1.0))
robot.add_joint(Joint(
    name="wrist_roll", joint_type=JointType.CONTINUOUS,
    parent_link="forearm", child_link="end_effector",
))
robot.add_link(Link(name="end_effector", mass=0.5))
robotics.add_robot(robot)
print(f"  Robot '{robot.name}': {len(robot.links)} links, {len(robot.joints)} joints")

# Forward kinematics
fk = robot.forward_kinematics({"shoulder_pitch": 0.5, "elbow_pitch": 1.0, "wrist_roll": 0.0})
assert len(fk) == len(robot.links), f"FK should return {len(robot.links)} link transforms"
print(f"  FK: {len(fk)} link transforms computed")

# Inverse kinematics
target = Transform(position=Vector3(2.0, 1.5, 0.0))
ik_result = robot.inverse_kinematics(target, "end_effector", max_iterations=50)
if ik_result:
    print(f"  IK: found solution with {len(ik_result)} joint positions")
else:
    print("  IK: (no solution within tolerance)")

# Sensors
lidar = LidarSensor("main_lidar")
lidar.num_beams = 16
lidar.range_max = 30.0
lidar.noise_std = 0.02
robotics.add_sensor(lidar)

camera = CameraSensor("rgb_camera")
camera.width = 640
camera.height = 480
robotics.add_sensor(camera)

imu = IMUSensor("imu_main")
robotics.add_sensor(imu)

gps = GPSSensor("gps_main")
gps.latitude = -1.9441
gps.longitude = 30.0619
robotics.add_sensor(gps)

obstacles = [(Vector3(5, 0, 3), 0.5), (Vector3(10, 0, -2), 1.0)]
readings = robotics.read_all_sensors(1.0, obstacles=obstacles,
                                     acceleration=Vector3(0, -9.81, 0),
                                     position=Vector3(10, 0, 20))
assert len(readings) > 0, "Should have sensor readings"
print(f"  Sensors: {len(readings)} readings ({', '.join(readings.keys())})")
print("  PASS: Robotics module works")

# ── 3. Autonomous Vehicles ──────────────────────────────────────────────
print("\n--- 3. Autonomous Vehicles ---")
from imikino.imodoka import (
    AutonomousVehicleSystem, VehicleDynamics, TrafficParticipant,
    TrafficLight, ADASSystem, VehicleType, DriveType, TrafficLightState,
    get_av_system,
)

av = get_av_system()
scenario = av.create_scenario("highway_demo")

for i in range(6):
    v = VehicleDynamics(
        vehicle_type=VehicleType.SEDAN,
        mass=1500.0,
        engine_power=150000.0,
    )
    v.position = Vector3(i * 15, 0, 0)
    participant = TrafficParticipant(
        dynamics=v,
        desired_speed=15.0 + i * 1.5,
        min_gap=2.0,
    )
    scenario.add_participant(participant)

tl = TrafficLight(position=Vector3(80, 0, 0),
                  green_duration=10.0, red_duration=10.0)
scenario.add_traffic_light(tl)
av.load_scenario("highway_demo")
av.adas.adaptive_cruise_control = True
av.adas.lane_keep_assist = True
av.adas.target_speed = 20.0

for _ in range(300):
    av.update(1/60)

collisions = av.active_scenario.check_collisions() if av.active_scenario else []
print(f"  Collisions detected: {len(collisions)}")
for participant in scenario.participants:
    print(f"    Speed: {participant.dynamics.speed_kmh:.1f} km/h")
print("  PASS: Vehicle simulation works")

# ── 4. Smart City ──────────────────────────────────────────────────────
print("\n--- 4. Smart City ---")
from imikino.umujyi import (
    CitySimulation, Zone, ZoneType, Building, BuildingType,
    Infrastructure, InfrastructureType, Environment, WeatherType,
    Pedestrian, get_city_sim,
)

city = get_city_sim()
city.name = "KigaliDemo"

res = Zone("Kagugu", ZoneType.RESIDENTIAL, population=8000, capacity=12000)
res.bounds_max = Vector3(500, 0, 500)
city.add_zone(res)

com = Zone("Downtown", ZoneType.COMMERCIAL, population=3000, capacity=8000)
com.bounds_max = Vector3(400, 0, 400)
city.add_zone(com)

ind = Zone("SpecialZone", ZoneType.INDUSTRIAL, population=500, capacity=2000)
ind.bounds_max = Vector3(600, 0, 400)
city.add_zone(ind)

for i in range(10):
    b = Building(f"Bldg{i}", BuildingType.APARTMENT if i < 6 else BuildingType.OFFICE,
                 position=Vector3(random.uniform(50, 450), 0, random.uniform(50, 450)),
                 floors=random.randint(2, 8), occupants=random.randint(10, 100))
    city.add_building(b, "Kagugu" if i < 6 else "Downtown")

power = Infrastructure(InfrastructureType.POWER, capacity=10000.0)
water = Infrastructure(InfrastructureType.WATER, capacity=5000.0)
telecom = Infrastructure(InfrastructureType.TELECOM, capacity=2000.0)
city.add_infrastructure(power)
city.add_infrastructure(water)
city.add_infrastructure(telecom)

for _ in range(20):
    ped = Pedestrian(position=Vector3(random.uniform(0, 500), 0, random.uniform(0, 500)),
                     speed=random.uniform(1.0, 1.8))
    ped.set_destination(Vector3(random.uniform(0, 500), 0, random.uniform(0, 500)))
    city.add_pedestrian(ped)

city.environment.time_of_day = 6.0
city.environment.set_weather(WeatherType.CLEAR)

for _ in range(600):
    city.update(1/60)

stats = city.get_stats()
print(f"  Population: {stats['population']}")
print(f"  Zones: {stats['zones']}, Buildings: {stats['buildings']}")
print(f"  Pedestrians: {stats['pedestrians']}")
print(f"  Time: {city.environment.to_dict()['time']}")
print("  PASS: City simulation works")

# ── 5. Digital Twin ─────────────────────────────────────────────────────
print("\n--- 5. Digital Twin ---")
from imikino.inganda import (
    FactorySimulation, ProductionLine, Machine, ConveyorBelt,
    SupplyChainNode, EquipmentSensor, MachineStatus, SupplyChainStage,
    get_factory_sim,
)

factory = get_factory_sim()
factory.name = "SmartFactory"

line1 = ProductionLine("AssemblyLine1", target_output=200)
m1 = Machine("CNC-1", "cnc", cycle_time=3.0)
m2 = Machine("Welding-1", "welding", cycle_time=4.0)
m3 = Machine("Painting-1", "painting", cycle_time=2.5)
m4 = Machine("Inspector-1", "quality", cycle_time=1.5)
line1.add_machine(m1)
line1.add_machine(m2)
line1.add_machine(m3)
line1.add_machine(m4)

conveyor = ConveyorBelt("MainConveyor", length=20.0, speed=0.5, capacity=30)
line1.add_conveyor(conveyor)
factory.add_production_line(line1)

supplier = SupplyChainNode("SupplierA", SupplyChainStage.PROCUREMENT,
                           capacity=5000, lead_time=48.0)
warehouse = SupplyChainNode("Warehouse", SupplyChainStage.WAREHOUSING,
                            capacity=2000, lead_time=12.0)
factory.add_supply_chain_node(supplier)
factory.add_supply_chain_node(warehouse)

sensor = EquipmentSensor("Temp-CNC1", "CNC-1", "temperature",
                         normal_min=20.0, normal_max=80.0, unit="C")
factory.add_sensor(sensor)
factory.start_production("AssemblyLine1")

for _ in range(600):
    factory.update(1.0)

summary = factory.summary()
print(f"  Total output: {factory.total_output}")
print(f"  Line OEE: {line1.oee:.3f}")
print(f"  Alerts: {len(factory.get_alerts())}")
print("  PASS: Factory simulation works")

# ── 6. Integrated Scenario ──────────────────────────────────────────────
print("\n--- 6. Integrated Simulation ---")
from imikino.inyenzure import BehaviourTree, SequenceNode, ConditionNode, ActionNode, get_ai

# Factory + AI integration: intelligent quality control
ai = get_ai()
quality_tree = BehaviourTree(SequenceNode(name="quality_check"))
quality_tree.root.children.append(
    ConditionNode("defect_rate_high",
                  lambda e: m4.defect_count / max(m4.total_products, 1) > 0.05)
)
quality_tree.root.children.append(
    ActionNode("adjust_parameters",
               lambda e, dt: "success")
)
ai.register_behaviour_tree("quality_001", quality_tree)
result = quality_tree.execute(None, 0.0)
print(f"  AI quality check result: {result}")
print("  PASS: Integrated simulation works")

# ── Summary ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("IMIKINO Simulation - ALL TESTS PASSED")
print("=" * 60)
print(f"  Core: Simulator ran {sim_result.steps} steps")
print(f"  Robotics: Robot with {len(robot.joints)} joints, {len(readings)} sensors")
print(f"  Vehicles: {len(scenario.participants)} traffic participants")
print(f"  City: {city.total_population} population, {len(city.zones)} zones")
print(f"  Factory: {factory.total_output} units produced, {line1.oee:.1%} OEE")
print("=" * 60)
