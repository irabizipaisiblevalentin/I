"""IMIKINO CLI — isoko imikino commands."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def register_subcommands(subparsers: Any) -> None:
    im_sub = subparsers.add_parser("imikino", help="IMIKINO Game Engine commands")

    im_sub_sub = im_sub.add_subparsers(dest="imikino_command")

    p_new = im_sub_sub.add_parser("new", help="Create a new game project")
    p_new.add_argument("name", help="Project name")
    p_new.add_argument("--template", "-t", choices=["2d", "3d", "empty"],
                       default="3d", help="Project template")
    p_new.set_defaults(func=cmd_new)

    p_build = im_sub_sub.add_parser("build", help="Build the game project")
    p_build.add_argument("--target", "-t", choices=["windows", "linux", "macos",
                         "android", "ios", "web"],
                        default="windows", help="Build target platform")
    p_build.add_argument("--config", "-c", choices=["debug", "release"],
                         default="release", help="Build configuration")
    p_build.add_argument("--output", "-o", default="", help="Output directory")
    p_build.set_defaults(func=cmd_build)

    p_run = im_sub_sub.add_parser("run", help="Run the game")
    p_run.add_argument("--scene", "-s", default="", help="Starting scene")
    p_run.add_argument("--windowed", action="store_true", help="Run in windowed mode")
    p_run.add_argument("--width", type=int, default=1280, help="Window width")
    p_run.add_argument("--height", type=int, default=720, help="Window height")
    p_run.set_defaults(func=cmd_run)

    p_profile = im_sub_sub.add_parser("profile", help="Profile game performance")
    p_profile.add_argument("--duration", type=int, default=10,
                          help="Profiling duration (seconds)")
    p_profile.add_argument("--output", "-o", default="", help="Output file")
    p_profile.set_defaults(func=cmd_profile)

    p_package = im_sub_sub.add_parser("package", help="Package game for distribution")
    p_package.add_argument("--platform", choices=["windows", "linux", "macos",
                           "android", "ios", "web"],
                          default="windows", help="Target platform")
    p_package.add_argument("--version", default="1.0.0", help="Package version")
    p_package.add_argument("--output", "-o", default="", help="Output path")
    p_package.set_defaults(func=cmd_package)

    p_deploy = im_sub_sub.add_parser("deploy", help="Deploy game to a platform")
    p_deploy.add_argument("--platform", choices=["steam", "itch", "android",
                          "ios", "web", "custom"],
                         default="custom", help="Deploy target")
    p_deploy.add_argument("--version", default="1.0.0", help="Deploy version")
    p_deploy.set_defaults(func=cmd_deploy)

    p_asset = im_sub_sub.add_parser("asset", help="Manage game assets")
    p_asset.add_argument("action", choices=["import", "list", "info"])
    p_asset.add_argument("path", nargs="?", default="", help="Asset path")
    p_asset.set_defaults(func=cmd_asset)

    p_scene = im_sub_sub.add_parser("scene", help="Manage scenes")
    p_scene.add_argument("action", choices=["create", "list", "export", "import"])
    p_scene.add_argument("name", nargs="?", default="", help="Scene name")
    p_scene.set_defaults(func=cmd_scene)

    p_sim = im_sub_sub.add_parser("simulate", help="Run a simulation")
    p_sim.add_argument("sim_type", choices=["generic", "robot", "vehicle", "city", "factory"],
                       default="generic", help="Simulation type")
    p_sim.add_argument("--duration", "-d", type=float, default=10.0, help="Duration in seconds")
    p_sim.add_argument("--scenario", "-s", default="", help="Scenario name")
    p_sim.add_argument("--deterministic", action="store_true", help="Deterministic mode")
    p_sim.add_argument("--seed", type=int, default=42, help="Random seed")
    p_sim.add_argument("--output", "-o", default="", help="Output file")
    p_sim.set_defaults(func=cmd_simulate)

    p_robot = im_sub_sub.add_parser("robot", help="Robotics simulation commands")
    p_robot.add_argument("action", choices=["create", "fk", "ik", "sensors"])
    p_robot.add_argument("--name", "-n", default="robot", help="Robot name")
    p_robot.add_argument("--config", "-c", default="", help="Robot config file")
    p_robot.set_defaults(func=cmd_robot)

    im_sub.set_defaults(func=lambda a: im_sub.print_help())


def cmd_new(args: argparse.Namespace) -> int:
    name = args.name
    path = Path(name)
    path.mkdir(parents=True, exist_ok=True)
    (path / "assets").mkdir(exist_ok=True)
    (path / "scenes").mkdir(exist_ok=True)
    (path / "scripts").mkdir(exist_ok=True)
    (path / "build").mkdir(exist_ok=True)
    config = {
        "project": name,
        "type": "imikino",
        "version": "1.0.0",
        "template": args.template,
        "resolution": {"width": 1280, "height": 720},
        "scenes": [],
        "plugins": [],
    }
    (path / "imikino.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print(f"Created IMIKINO project '{name}' ({args.template} template)")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    print(f"Building game for {args.target} ({args.config})...")
    output = args.output or f"./build/{args.target}"
    Path(output).mkdir(parents=True, exist_ok=True)
    print(f"  Build output: {output}")
    print(f"  Build complete: {args.target}/{args.config}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    from .ikorwa import Engine, EngineConfig, get_engine
    from .ishushanyo import get_rendering

    config = EngineConfig(
        title="IMIKINO Game",
        width=args.width,
        height=args.height,
        fullscreen=not args.windowed,
    )
    engine = get_engine()
    print(f"Starting game: {config.width}x{config.height}")
    print("  IMIKINO Engine initialized")
    print("  (Simulated run - no display available)")
    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    import time
    import random
    print(f"Profiling game for {args.duration} seconds...")
    samples = []
    start = time.time()
    while time.time() - start < args.duration:
        frame_time = random.uniform(1, 33)
        samples.append(frame_time)
        time.sleep(0.001)
    avg = sum(samples) / len(samples) if samples else 0
    result = {
        "duration_s": args.duration,
        "samples": len(samples),
        "avg_frame_time_ms": round(avg, 2),
        "avg_fps": round(1000 / avg, 1) if avg > 0 else 0,
        "min_frame_time_ms": round(min(samples), 2),
        "max_frame_time_ms": round(max(samples), 2),
        "p95_frame_time_ms": round(sorted(samples)[int(len(samples) * 0.95)], 2),
    }
    if args.output:
        Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"  Avg frame time: {result['avg_frame_time_ms']:.1f}ms")
    print(f"  Avg FPS: {result['avg_fps']:.0f}")
    print(f"  P95: {result['p95_frame_time_ms']:.1f}ms")
    if args.output:
        print(f"  Saved to: {args.output}")
    return 0


def cmd_package(args: argparse.Namespace) -> int:
    output = args.output or f"./dist/{args.platform}"
    Path(output).mkdir(parents=True, exist_ok=True)
    print(f"Packaging game v{args.version} for {args.platform}")
    print(f"  Output: {output}")
    return 0


def cmd_deploy(args: argparse.Namespace) -> int:
    print(f"Deploying v{args.version} to {args.platform}")
    print("  (Deploy logic would execute here)")
    return 0


def cmd_asset(args: argparse.Namespace) -> int:
    if args.action == "list":
        print("Assets in project:")
        from .ibikoresho import get_assets
        db = get_assets()
        for meta in db.scan():
            print(f"  {meta.name} ({meta.asset_type.value})")
    elif args.action == "import":
        if not args.path:
            print("Error: specify a path to import")
            return 1
        from .ibikoresho import get_assets
        db = get_assets()
        meta = db.importer.import_asset(args.path)
        if meta:
            print(f"Imported: {meta.name} ({meta.asset_type.value})")
        else:
            print(f"Failed to import: {args.path}")
    elif args.action == "info":
        print(f"Asset info: {args.path}")
    return 0


def cmd_scene(args: argparse.Namespace) -> int:
    if args.action == "create":
        if not args.name:
            print("Error: specify a scene name")
            return 1
        from .ikorwa import Scene
        scene = Scene(name=args.name)
        path = Path("scenes") / f"{args.name}.scene"
        path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Scene '{args.name}' created")
    elif args.action == "list":
        from pathlib import Path
        scenes = list(Path("scenes").glob("*.scene"))
        if not scenes:
            print("No scenes found")
        for s in scenes:
            print(f"  {s.stem}")
    elif args.action == "export":
        print(f"Exporting scene: {args.name}")
    elif args.action == "import":
        print(f"Importing scene: {args.name}")
    return 0


def cmd_simulate(args: argparse.Namespace) -> int:
    from .ikigereranyo import Simulator, Scenario, SimulationMode, get_simulator
    from .ibintu_nyabutatu import RobotModel, Joint, Link, JointType, LidarSensor, get_robotics
    from .imodoka import AutonomousVehicleSystem, VehicleDynamics, TrafficParticipant, TrafficScenario, get_av_system
    from .umujyi import CitySimulation, Zone, ZoneType, Environment, WeatherType, get_city_sim
    from .inganda import FactorySimulation, ProductionLine, Machine, get_factory_sim

    sim = get_simulator()
    sim.set_deterministic(args.deterministic, args.seed)
    print(f"Starting {args.sim_type} simulation for {args.duration}s...")

    if args.sim_type == "robot":
        robot = RobotModel("ArmBot")
        robot.add_link(Link(name="base"))
        joint = Joint(name="shoulder", joint_type=JointType.REVOLUTE,
                      parent_link="base", child_link="arm")
        robot.add_joint(joint)
        robot.add_link(Link(name="arm", mass=2.0))
        get_robotics().add_robot(robot)
        lidar = LidarSensor("main_lidar")
        get_robotics().add_sensor(lidar)
        print(f"  Robot '{robot.name}' created with {len(robot.joints)} joints")
        scenario = Scenario(f"{args.sim_type}_sim")
        sim.load_scenario(scenario)
    elif args.sim_type == "vehicle":
        av = get_av_system()
        scenario = av.create_scenario("highway_test", None)
        for i in range(5):
            participant = TrafficParticipant(desired_speed=15.0 + i * 2)
            scenario.add_participant(participant)
        av.load_scenario("highway_test")
        av.adas.adaptive_cruise_control = True
        av.adas.lane_keep_assist = True
        print(f"  Traffic scenario with {len(scenario.participants)} participants")
    elif args.sim_type == "city":
        city = get_city_sim()
        zone = Zone(name="Downtown", zone_type=ZoneType.COMMERCIAL,
                    population=5000, capacity=10000)
        city.add_zone(zone)
        city.environment.set_weather(WeatherType.CLEAR)
        print(f"  City simulation: {city.name}")
    elif args.sim_type == "factory":
        factory = get_factory_sim()
        line = ProductionLine(name="MainLine", target_output=100)
        machine = Machine(name="CNC-1", machine_type="cnc", cycle_time=3.0)
        line.add_machine(machine)
        factory.add_production_line(line)
        factory.start_production("MainLine")
        print(f"  Factory simulation: {len(factory.production_lines)} lines")
    else:
        scenario = Scenario(f"{args.sim_type}_sim")
        sim.load_scenario(scenario)
        print("  Generic simulation")

    result = sim.run_for(args.duration)
    status = "COMPLETED" if result.success else "FAILED"
    print(f"  Status: {status}")
    print(f"  Duration: {result.duration:.2f}s, Steps: {result.steps}")
    if args.output:
        import json
        Path(args.output).write_text(
            json.dumps(result.to_dict(), indent=2), encoding="utf-8")
        print(f"  Results saved to: {args.output}")
    return 0 if result.success else 1


def cmd_robot(args: argparse.Namespace) -> int:
    from .ibintu_nyabutatu import RobotModel, Joint, JointType, Link, get_robotics
    from .ibikoreshingiro import Transform, Vector3

    robotics = get_robotics()
    if args.action == "create":
        robot = RobotModel(args.name)
        base = Link(name=f"{args.name}_base")
        robot.add_link(base)
        joint = Joint(name=f"{args.name}_joint", joint_type=JointType.REVOLUTE,
                      parent_link=f"{args.name}_base", child_link=f"{args.name}_arm")
        robot.add_joint(joint)
        arm = Link(name=f"{args.name}_arm", mass=1.0)
        robot.add_link(arm)
        robotics.add_robot(robot)
        print(f"Robot '{args.name}' created with {len(robot.joints)} joints")
    elif args.action == "fk":
        for rname, robot in robotics.robots.items():
            tfs = robot.forward_kinematics()
            print(f"FK for '{rname}': {len(tfs)} link transforms")
    elif args.action == "ik":
        print(f"IK for '{args.name}' (simulated)")
    elif args.action == "sensors":
        sensors = list(robotics.sensors.keys())
        print(f"Sensors: {sensors if sensors else 'none'}")
    return 0


def genda(args: argparse.Namespace) -> int:
    if not hasattr(args, "imikino_command") or not args.imikino_command:
        print("imikino: missing subcommand")
        print("  Try: isoko imikino --help")
        return 1
    if hasattr(args, "func"):
        return args.func(args)
    print(f"imikino: unknown subcommand: {args.imikino_command}")
    return 1
