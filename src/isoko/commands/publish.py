"""isoko publish — Publish a package to the registry."""

from __future__ import annotations

import json
import os
import tarfile
import time
from typing import Optional

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.registry import RegistryClient, RegistryConfig, RegistryError
from isoko import security


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("publish", help="Publish a package")
    p.add_argument("--registry", help="Registry URL")
    p.add_argument("--dry-run", action="store_true",
                   help="Show what would be published without actually publishing")
    p.add_argument("--tag", help="Release tag")
    p.add_argument("--allow-dirty", action="store_true",
                   help="Allow publishing with uncommitted changes")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    if not m.name:
        output.error("package name is required")
        return 1

    project_dir = os.path.dirname(manifest_path)
    dry_run = getattr(args, "dry_run", False)
    registry_url = getattr(args, "registry", None)

    output.header(f"Publishing {m.full_name}")

    # Pre-publish checks
    checks = _run_pre_publish_checks(m, project_dir)
    if checks["errors"]:
        for err in checks["errors"]:
            output.error(err)
        return 1
    for warn in checks["warnings"]:
        output.warning(warn)

    # Build the tarball
    output.info("Building package tarball...")
    tarball = _create_tarball(m, project_dir)
    checksum = security.sha256(tarball)
    output.info(f"Tarball size: {len(tarball)} bytes")
    output.info(f"Checksum: sha256:{checksum[:16]}...")

    if dry_run:
        output.header("Dry Run — would publish:")
        output.label_value("Name", m.name)
        output.label_value("Version", m.version)
        output.label_value("Description", m.description)
        output.label_value("Tarball size", f"{len(tarball)} bytes")
        output.label_value("Checksum", f"sha256:{checksum[:16]}...")
        return 0

    # Publish to registry
    config = RegistryConfig(url=registry_url or "https://registry.i-lang.dev")
    client = RegistryClient(config)

    output.spinner = output.Spinner("Publishing to registry...")
    output.spinner.start()

    try:
        success = client.publish(m.name, m.version, tarball, {
            "description": m.description,
            "license": m.license,
            "checksum": checksum,
        })
        output.spinner.stop()
        if success:
            output.success(f"Published {m.full_name}")
            output.dim(f"  Registry: {config.url}")
            return 0
        else:
            output.error("Publish failed")
            return 1
    except RegistryError as e:
        output.spinner.fail(f"Publish failed: {e}")
        return 1
    except Exception as e:
        output.spinner.fail(f"Publish failed: {e}")
        return 1


def _run_pre_publish_checks(m, project_dir: str) -> dict:
    result = {"errors": [], "warnings": []}

    if not m.name:
        result["errors"].append("package name is required")
    if not m.version:
        result["errors"].append("package version is required")
    if not m.description:
        result["warnings"].append("package description is recommended")

    readme = os.path.join(project_dir, "README.md")
    if not os.path.exists(readme):
        result["warnings"].append("README.md not found")

    license_file = os.path.join(project_dir, "LICENSE")
    if not os.path.exists(license_file) and m.license:
        result["warnings"].append(f"LICENSE file not found (declared license: {m.license})")

    lib_dir = os.path.join(project_dir, m.lib or "lib")
    if not os.path.exists(lib_dir):
        result["errors"].append(f"source directory not found: {m.lib or 'lib'}")

    return result


def _create_tarball(m, project_dir: str) -> bytes:
    import io
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for root, dirs, files in os.walk(project_dir):
            for f in files:
                fp = os.path.join(root, f)
                arcname = os.path.relpath(fp, project_dir)
                if arcname.startswith("build/") or arcname.startswith(".git/"):
                    continue
                if arcname.endswith(".pyc") or "__pycache__" in arcname:
                    continue
                tar.add(fp, arcname=arcname)
    return buf.getvalue()
