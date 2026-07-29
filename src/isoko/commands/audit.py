"""isoko audit — Security audit of dependencies."""

from __future__ import annotations

import os

from isoko import output
from isoko.manifest import load as load_manifest, find_manifest
from isoko.lockfile import find_lockfile, load_lockfile
from isoko.security import AuditReport, AuditFinding, SBOM


def add_subparser(subparsers) -> None:
    p = subparsers.add_parser("audit", help="Security audit")
    p.add_argument("--json", action="store_true",
                   help="Output in JSON format")
    p.add_argument("--sbom", action="store_true",
                   help="Generate SBOM (Software Bill of Materials)")
    p.add_argument("--output", "-o", help="Output file path")


def run(args) -> int:
    manifest_path = find_manifest()
    if not manifest_path:
        output.error("no ilang.toml found")
        return 1

    m = load_manifest(manifest_path)
    json_mode = getattr(args, "json", False)
    sbom_mode = getattr(args, "sbom", False)
    output_path = getattr(args, "output", None)

    output.header(f"Auditing {m.full_name}")

    lock_path = find_lockfile()
    if not lock_path:
        output.warning("no lock file found")
        return 0

    lock = load_lockfile(lock_path)
    if not lock:
        return 0

    report = AuditReport()
    report.total_packages = len(lock.entries)

    # Basic security checks
    for name, entry in lock.entries.items():
        if not entry.checksum:
            report.add_finding(AuditFinding(
                severity="medium",
                package=name,
                version=entry.version,
                title="No checksum recorded",
                description="Package has no integrity checksum in lock file",
                recommendation="Reinstall the package to record checksums",
            ))

        if entry.source == "git":
            report.add_finding(AuditFinding(
                severity="low",
                package=name,
                version=entry.version,
                title="Git dependency",
                description="Package is sourced from a git repository",
                recommendation="Pin to a specific commit or tag",
            ))

    if sbom_mode:
        sbom = SBOM(m.name, m.version)
        for name, entry in lock.entries.items():
            from isoko.security import SBOMEntry
            sbom.add(SBOMEntry(
                name=name,
                version=entry.version,
                checksum=entry.checksum,
                source=entry.source,
                dependencies=list(entry.dependencies.keys()),
            ))

        if output_path:
            sbom.save(output_path)
            output.success(f"SBOM written to {output_path}")
        else:
            print(sbom.to_json())
        return 0

    # Report findings
    if report.is_clean:
        output.success("No vulnerabilities found")
    else:
        output.error(f"Found {report.vulnerable_count} potential issue(s)")

    for finding in report.findings:
        severity = finding.severity.upper()
        output.info(f"  [{severity}] {finding.package}@{finding.version}: {finding.title}")
        output.dim(f"    {finding.description}")
        output.dim(f"    Recommendation: {finding.recommendation}")

    if json_mode:
        output.print_json(report.to_dict())

    return 1 if not report.is_clean else 0
