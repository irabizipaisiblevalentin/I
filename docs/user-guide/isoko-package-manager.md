# isoko — I Package Manager Guide

`isoko` (*market*) is the I language package manager and ecosystem CLI. It scaffolds
projects, builds and runs I programs, runs tests, manages dependencies, and publishes
packages to a registry.

The CLI is invoked through Python:

```bash
python -m isoko.cli --version     # isoko 1.0.0
python -m isoko.cli --help        # full command list
```

## Command Reference

| Command | Purpose |
| --- | --- |
| `new` | Create a new project from a template |
| `init` | Initialize a project in the current directory |
| `build` | Build the current project |
| `run` | Run an I program (or the current project) |
| `test` | Run tests |
| `bench` | Run benchmarks |
| `check` | Check the project for issues |
| `fmt` | Format source code |
| `lint` | Lint source code |
| `doc` | Generate documentation |
| `publish` | Publish a package to a registry |
| `install` | Install dependencies |
| `uninstall` | Remove a dependency |
| `update` | Update dependencies within their semver range |
| `upgrade` | Upgrade dependencies to the latest versions |
| `search` | Search the registry for packages |
| `info` | Show package information |
| `login` | Authenticate with the registry |
| `logout` | End the registry session |
| `cache` | Manage the package cache |
| `doctor` | Diagnose project problems |
| `clean` | Remove build artifacts |

Global flags: `--version`, `--verbose`, `--quiet`, `--color {auto,always,never}`,
`--json`.

## Creating a Project

```bash
python -m isoko.cli new my-project
```

This scaffolds a project with the default `console` template:

```
my-project/
├── ilang.toml          # package manifest
├── lib/                # source directory (imported by default)
│   └── main.i
└── tests/
    └── ...
```

To use a different template:

```bash
python -m isoko.cli new my-project -t console
python -m isoko.cli new my-webapp -t web
python -m isoko.cli new --list-templates
```

`init` does the same but in the current directory:

```bash
mkdir my-project && cd my-project
python -m isoko.cli init
```

## The Manifest (`ilang.toml`)

The manifest is the I equivalent of `package.json`. It can be written as TOML
(`ilang.toml`) or JSON (`ilang.json`).

```toml
name = "my-project"
version = "0.1.0"
description = "A small I program"
license = "MIT"
authors = [{ name = "Irabizi Paisible Valentin" }]

[dependencies]
# "name" = "1.2.3"  (semver range)

[dev_dependencies]
# "itest" = "*"
```

Key fields:

| Field | Meaning | Default |
| --- | --- | --- |
| `name` | package name | — |
| `version` | semver version | `0.1.0` |
| `description` | one-line summary | `""` |
| `license` | SPDX license id | `MIT` |
| `dependencies` | runtime dependencies (name → semver range) | `{}` |
| `dev_dependencies` | test/build-only dependencies | `{}` |
| `lib` | source directory | `"lib"` |
| `include` / `exclude` | files shipped in the package | `["lib/**"]` / `["tests/**", "benchmarks/**"]` |
| `engines` | required I toolchain version | `{}` |

## Building and Running

```bash
python -m isoko.cli build        # compile the project
python -m isoko.cli run          # run the current project
python -m isoko.cli run path/to/program.i
python -m isoko.cli run --release  # optimized build
```

Pass arguments to the program with `--args`:

```bash
python -m isoko.cli run --args --fast out.txt
```

`clean` removes build artifacts so the next build starts fresh:

```bash
python -m isoko.cli clean
```

## Testing, Formatting, Linting

```bash
python -m isoko.cli test     # run the test suite
python -m isoko.cli bench    # run benchmarks
python -m isoko.cli fmt      # format source files
python -m isoko.cli lint     # check for common issues
python -m isoko.cli check    # combined correctness check
python -m isoko.cli doctor   # diagnose environment / project issues
```

`check` is the recommended gate before committing or publishing.

## Dependencies

```bash
python -m isoko.cli install "mypkg@^1.0.0"   # add and install
python -m isoko.cli install                   # install from manifest
python -m isoko.cli uninstall mypkg
python -m isoko.cli update mypkg              # within the semver range
python -m isoko.cli upgrade mypkg             # latest version
python -m isoko.cli search "web"
python -m isoko.cli info mypkg
python -m isoko.cli cache --help              # inspect the package cache
```

Dependencies respect semantic versioning ranges (see `stdlib.package.version_satisfies`
for the range logic).

## Publishing

Publishing requires an account on the registry.

```bash
python -m isoko.cli login
# enter your username, password (or token), and registry URL
```

Publish with a dry run first:

```bash
python -m isoko.cli publish --dry-run
python -m isoko.cli publish                 # publishes the current version
python -m isoko.cli publish --tag beta      # pre-release tag
```

`--registry` overrides the registry URL for this command; `--allow-dirty` permits
publishing with uncommitted changes (use with care).

End the session when done:

```bash
python -m isoko.cli logout
```

> **Security:** the login token is stored on your machine with owner-only permissions
> (mode `0600` on POSIX). Never share a token, and do not paste it into logs.

## Publishing Checklist

1. `python -m isoko.cli test` — all tests pass
2. `python -m isoko.cli lint` and `python -m isoko.cli check` — no issues
3. `python -m isoko.cli build` — clean build
4. `python -m isoko.cli publish --dry-run` — verify the package contents
5. Bump `version` in `ilang.toml` following [semver](https://semver.org)
6. `python -m isoko.cli publish`
