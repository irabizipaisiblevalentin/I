# IMIKINO Simulation Guide

## Overview

IMIKINO provides a complete simulation framework beyond traditional game development.Use it for:
- **Robotics**: Robot modeling, kinematics, sensor simulation
- **Autonomous Vehicles**: Vehicle dynamics, traffic scenarios, ADAS
- **Smart Cities**: Urban planning, infrastructure, environment, pedestrian simulation
- **Digital Twins**: Factory simulation, production lines, supply chain
- **General Simulation**: Custom scenarios with configurable clocks, recording, replay

## Simulation Core (ikigereranyo)

### Simulator Setup

```python
from imikino import Simulator, SimulationMode, Scenario

sim = Simulator("my_sim")
sim.clock.mode = SimulationMode.REALTIME
sim.clock.time_scale = 2.0  # 2x speed
sim.set_deterministic(True, seed=42)

scenario = Scenario("test")
scenario.add_parameter("speed", 10.0, "float", 0.0, 100.0, "Movement speed")
sim.load_scenario(scenario)
```

### Running Simulations

```python
# Run for a duration
result = sim.run_for(30.0)

# Run for a specific number of steps
result = sim.run_steps(1000)

# Manual stepping
sim.start()
for _ in range(100):
    sim.step(0.016)  # 60 FPS fixed step
result = sim.stop()
```

### Recording and Replay

```python
sim.recorder.start()
sim.run_for(10.0)
sim.recorder.stop()
sim.recorder.save("simulation_log.json")

# Replay later
recorder = SimulationRecorder()
recorder.load("simulation_log.json")
recorder.replay(lambda event: print(event.type, event.data))
```

## Robotics (ibintu_nyabutatu)

### Creating a Robot

```python
from imikino import RobotModel, Joint, Link, JointType
from imikino.ibintu_nyabutatu import get_robotics

robot = RobotModel("ArmBot")
robot.add_link(Link(name="base", mass=5.0))
robot.add_joint(Joint(
    name="shoulder", joint_type=JointType.REVOLUTE,
    parent_link="base", child_link="upper_arm",
    position_lower=-3.14, position_upper=3.14,
))
robot.add_link(Link(name="upper_arm", mass=2.0))
robot.add_joint(Joint(
    name="elbow", joint_type=JointType.REVOLUTE,
    parent_link="upper_arm", child_link="forearm",
))
robot.add_link(Link(name="forearm", mass=1.0))
get_robotics().add_robot(robot)
```

### Forward Kinematics

```python
positions = {"shoulder": 0.5, "elbow": 1.0}
transforms = robot.forward_kinematics(positions)
for link_name, transform in transforms.items():
    print(f"{link_name}: {transform.position}")
```

### Sensors

```python
from imikino.ibintu_nyabutatu import LidarSensor, CameraSensor, IMUSensor

lidar = LidarSensor("main_lidar")
lidar.num_beams = 32
lidar.range_max = 50.0
lidar.noise_std = 0.05
get_robotics().add_sensor(lidar)

reading = lidar.read(sim_time=1.0, obstacles=[(Vector3(5,0,3), 0.5)])
if reading:
    print(f"Lidar points: {reading.data['num_points']}")
```

## Autonomous Vehicles (imodoka)

### Traffic Scenario

```python
from imikino import VehicleDynamics, TrafficParticipant, TrafficScenario
from imikino.imodoka import get_av_system

av = get_av_system()
scenario = av.create_scenario("highway")

# Add vehicles
for i in range(10):
    v = VehicleDynamics()
    v.position = Vector3(i * 10, 0, 0)
    participant = TrafficParticipant(
        dynamics=v,
        desired_speed=20.0 + random.uniform(-5, 5),
    )
    scenario.add_participant(participant)

# Enable ADAS
av.adas.adaptive_cruise_control = True
av.adas.lane_keep_assist = True
av.load_scenario("highway")

# Run
for _ in range(600):  # 10 seconds at 60 FPS
    av.update(1/60)
```

## Smart City (umujyi)

### City Setup

```python
from imikino import CitySimulation, Zone, ZoneType, Building, BuildingType
from imikino.umujyi import Environment, WeatherType, get_city_sim

city = get_city_sim()
zone = Zone("Downtown", ZoneType.COMMERCIAL, population=5000, capacity=10000)
city.add_zone(zone)

building = Building("Office1", BuildingType.OFFICE,
                    position=Vector3(100, 0, 200), floors=10, occupants=200)
city.add_building(building, "Downtown")

city.environment.set_weather(WeatherType.CLEAR)
city.environment.time_of_day = 8.0  # Morning

for _ in range(600):
    city.update(1/60)
```

## Digital Twin (inganda)

### Factory Simulation

```python
from imikino import FactorySimulation, ProductionLine, Machine, MachineStatus
from imikino.inganda import get_factory_sim

factory = get_factory_sim()
line = ProductionLine("Assembly", target_output=500)

m1 = Machine("Robot1", "welding", cycle_time=2.5)
m2 = Machine("Robot2", "painting", cycle_time=3.0)
m3 = Machine("Inspector", "quality", cycle_time=1.0)
line.add_machine(m1)
line.add_machine(m2)
line.add_machine(m3)
factory.add_production_line(line)
factory.start_production("Assembly")

for _ in range(1800):  # 30 minutes at 1 step/sec
    factory.update(1.0)
    alerts = factory.get_alerts()
    if alerts:
        for alert in alerts:
            print(f"ALERT: {alert.name} - {alert.value}")

print(f"Total output: {factory.total_output}")
print(f"Line OEE: {line.oee:.3f}")
```

## UBWENGE AI Integration

Simulation modules integrate with UBWENGE for:
- Intelligent NPC agents in city simulations
- Predictive maintenance in digital twins
- Sensor data analysis and anomaly detection
- Traffic flow optimization
- Robot motion planning with reinforcement learning

```python
from imikino import get_ai
from ubwenge import UbwengeEngine

ai = get_ai()
engine = UbwengeEngine()
# AI-enhanced simulation agent
tree = BehaviourTree(SelectorNode(name="smart_agent"))
tree.set_value("engine", engine)
ai.register_behaviour_tree("agent_001", tree)
```

## Best Practices

1. **Deterministic mode** for reproducible simulations (test, debug, CI/CD)
2. **Record and replay** to analyze failures and edge cases
3. **Time scaling** for accelerated or slow-motion analysis
4. **Scenario parameters** for systematic exploration
5. **Sensor noise** for realistic perception simulation
6. **OEE monitoring** for digital twin optimization
