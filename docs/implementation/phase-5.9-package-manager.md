# Phase 5.9: Package Manager (isoko) Engineering Plan

**Status:** Draft
**Version:** 1.0
**Date:** July 2026
**Author:** I Engineering Team

---

## 1. Objectives

### 1.1 Primary Objectives

Implement the `isoko` package manager for I:

1. **Dependency Resolution**: Automated dependency management
2. **Package Installation**: Download and install packages
3. **Version Management**: Semantic versioning support
4. **Package Registry**: Package repository integration
5. **Lock Files**: Deterministic builds
6. **Workspace Support**: Multi-package projects
7. **Package Publishing**: Share packages with community

### 1.2 Quality Objectives

| Objective | Target | Measurement |
|-----------|--------|-------------|
| Test Coverage | > 90% | Line coverage |
| Documentation | 100% public API | Doc comments |
| Resolution Speed | < 1s | Time for typical project |
| Download Speed | > 10MB/s | Throughput |

### 1.3 Non-Objectives

- Package hosting (Phase 5.9.2)
- Package signing (Phase 5.9.3)
- Web interface (Future)

---

## 2. Engineering Design

### 2.1 Architecture Overview

```
isoko CLI
    ↓
Package Manager Core
    ↓
    ├── Dependency Resolution
    ├── Package Installation
    ├── Version Management
    ├── Lock File Management
    └── Workspace Management
    ↓
Package Registry
    ↓
    ├── Public Registry
    ├── Private Registry
    └── Git Registry
```

### 2.2 Package Manifest

```toml
# ilang.toml
[package]
name = "my-app"
version = "0.1.0"
edition = "1.0"
authors = ["Developer <dev@example.com>"]
description = "My I application"
license = "MIT"
repository = "https://github.com/user/my-app"
keywords = ["cli", "web"]
categories = ["command-line", "web"]

[dependencies]
ilang-std = "1.0.0"
ilang-web = "1.0.0"
my-lib = { path = "../my-lib" }

[dev-dependencies]
ilang-test = "1.0.0"

[build-dependencies]
ilang-build = "1.0.0"

[[bin]]
name = "my-app"
path = "src/main.i"

[[lib]]
name = "my-lib"
path = "src/lib.i"

[workspace]
members = [
    "packages/core",
    "packages/web",
]
```

### 2.3 Dependency Resolution

```rust
// Dependency resolution algorithm
pub struct Resolver {
    registry: Box<dyn Registry>,
    lock_file: Option<LockFile>,
}

impl Resolver {
    pub fn resolve(manifest: &Manifest) -> Result<Resolution, ResolverError> {
        let mut graph = DependencyGraph::new();
        let mut queue = VecDeque::new();
        
        // Add root package
        queue.push_back(ResolutionRequest {
            name: manifest.name.clone(),
            version: manifest.version.clone(),
            source: Source::Local,
        });
        
        // BFS resolution
        while let Some(request) = queue.pop_front() {
            if graph.contains(&request.name) {
                continue;
            }
            
            let package = self.registry.get_package(&request.name, &request.version)?;
            graph.add_node(package.clone());
            
            for dependency in &package.dependencies {
                let resolved = self.resolve_version(dependency)?;
                queue.push_back(resolved);
                graph.add_edge(&package.name, &resolved.name, dependency.clone());
            }
        }
        
        // Check for conflicts
        self.check_conflicts(&graph)?;
        
        // Optimize resolution
        self.optimize_resolution(&mut graph)?;
        
        Ok(Resolution { graph })
    }
    
    fn resolve_version(&self, dep: &Dependency) -> Result<ResolutionRequest, ResolverError> {
        match &dep.version {
            VersionReq::Exact(v) => Ok(ResolutionRequest {
                name: dep.name.clone(),
                version: v.clone(),
                source: Source::Registry,
            }),
            VersionReq::Range(range) => {
                let versions = self.registry.get_versions(&dep.name)?;
                let compatible = versions.iter()
                    .filter(|v| range.satisfies(v))
                    .max()
                    .ok_or(ResolverError::NoCompatibleVersion)?;
                Ok(ResolutionRequest {
                    name: dep.name.clone(),
                    version: compatible.clone(),
                    source: Source::Registry,
                })
            },
        }
    }
}
```

### 2.4 Package Installation

```rust
// Package installation
pub struct Installer {
    cache_dir: PathBuf,
    target_dir: PathBuf,
}

impl Installer {
    pub fn install(&self, resolution: &Resolution) -> Result<(), InstallerError> {
        for package in resolution.graph.topological_sort() {
            self.install_package(&package)?;
        }
        Ok(())
    }
    
    fn install_package(&self, package: &Package) -> Result<(), InstallerError> {
        // Check cache
        if self.cache_dir.join(&package.name).exists() {
            return self.install_from_cache(package);
        }
        
        // Download package
        let archive = self.download_package(package)?;
        
        // Verify checksum
        self.verify_checksum(&archive, &package.checksum)?;
        
        // Extract package
        self.extract_package(&archive, &package)?;
        
        // Install dependencies
        self.install_dependencies(package)?;
        
        Ok(())
    }
    
    fn download_package(&self, package: &Package) -> Result<Vec<u8>, InstallerError> {
        let url = self.get_download_url(package)?;
        let response = reqwest::blocking::get(&url)?;
        Ok(response.bytes()?.to_vec())
    }
    
    fn verify_checksum(&self, data: &[u8], expected: &str) -> Result<(), InstallerError> {
        let actual = sha2::Sha256::digest(data);
        let actual_hex = hex::encode(actual);
        if actual_hex != expected {
            return Err(InstallerError::ChecksumMismatch);
        }
        Ok(())
    }
}
```

### 2.5 Lock File

```toml
# isoko.lock
version = 1

[[package]]
name = "ilang-std"
version = "1.0.0"
source = "registry+https://isoko.io"
checksum = "abc123..."

[[package]]
name = "ilang-web"
version = "1.0.0"
source = "registry+https://isoko.io"
checksum = "def456..."

[[package]]
name = "my-lib"
version = "0.1.0"
source = "path+../my-lib"
```

---

## 3. File Structure

### 3.1 Crate Structure

```
crates/
└── isoko/
    ├── Cargo.toml
    ├── src/
    │   ├── lib.rs
    │   ├── main.rs
    │   ├── manifest.rs
    │   ├── resolver.rs
    │   ├── installer.rs
    │   ├── registry.rs
    │   ├── lockfile.rs
    │   ├── workspace.rs
    │   ├── command.rs
    │   └── error.rs
    └── tests/
        ├── manifest_tests.rs
        ├── resolver_tests.rs
        ├── installer_tests.rs
        ├── registry_tests.rs
        ├── lockfile_tests.rs
        └── integration_tests.rs
```

### 3.2 Key Files

```toml
# crates/isoko/Cargo.toml
[package]
name = "isoko"
version.workspace = true
edition.workspace = true

[[bin]]
name = "isoko"
path = "src/main.rs"

[dependencies]
ilang-core = { workspace = true }
ilang-error = { workspace = true }
toml = "0.8"
serde = { version = "1.0", features = ["derive"] }
reqwest = { version = "0.11", features = ["blocking"] }
sha2 = "0.10"
hex = "0.4"
```

---

## 4. Implementation Plan

### 4.1 Implementation Order

| Step | Component | Dependencies | Estimate |
|------|-----------|--------------|----------|
| 1 | Manifest parsing | - | 2 days |
| 2 | Package registry client | manifest | 3 days |
| 3 | Dependency resolver | registry | 4 days |
| 4 | Package installer | resolver | 3 days |
| 5 | Lock file management | resolver | 2 days |
| 6 | Workspace support | all above | 3 days |
| 7 | CLI commands | all above | 3 days |
| 8 | Unit tests | all above | 4 days |
| 9 | Integration tests | all above | 3 days |
| 10 | Documentation | all above | 3 days |

**Total Estimated Duration:** 30 days (6 weeks)

### 4.2 Detailed Implementation Steps

#### Step 1: Manifest Parsing (2 days)

```rust
// crates/isoko/src/manifest.rs

#[derive(Deserialize)]
pub struct Manifest {
    pub package: PackageInfo,
    pub dependencies: HashMap<String, Dependency>,
    pub dev_dependencies: HashMap<String, Dependency>,
    pub build_dependencies: HashMap<String, Dependency>,
    pub bin: Vec<BinaryTarget>,
    pub lib: Option<LibraryTarget>,
    pub workspace: Option<Workspace>,
}

impl Manifest {
    pub fn load(path: &Path) -> Result<Self, ManifestError> {
        let content = std::fs::read_to_string(path)?;
        let manifest: Self = toml::from_str(&content)?;
        manifest.validate()?;
        Ok(manifest)
    }
    
    pub fn validate(&self) -> Result<(), ManifestError> {
        // Validate package name
        if !is_valid_package_name(&self.package.name) {
            return Err(ManifestError::InvalidPackageName);
        }
        
        // Validate version
        if semver::Version::parse(&self.package.version).is_err() {
            return Err(ManifestError::InvalidVersion);
        }
        
        // Validate dependencies
        for (name, dep) in &self.dependencies {
            if !is_valid_package_name(name) {
                return Err(ManifestError::InvalidDependencyName(name.clone()));
            }
        }
        
        Ok(())
    }
}
```

#### Step 2: Package Registry Client (3 days)

```rust
// crates/isoko/src/registry.rs

pub trait Registry {
    fn get_package(&self, name: &str, version: &str) -> Result<Package, RegistryError>;
    fn get_versions(&self, name: &str) -> Result<Vec<Version>, RegistryError>;
    fn search(&self, query: &str) -> Result<Vec<PackageSummary>, RegistryError>;
}

pub struct IsokoRegistry {
    base_url: String,
    client: reqwest::Client,
}

impl Registry for IsokoRegistry {
    fn get_package(&self, name: &str, version: &str) -> Result<Package, RegistryError> {
        let url = format!("{}/api/v1/packages/{}/{}", self.base_url, name, version);
        let response = self.client.get(&url).send()?;
        Ok(response.json()?)
    }
    
    fn get_versions(&self, name: &str) -> Result<Vec<Version>, RegistryError> {
        let url = format!("{}/api/v1/packages/{}/versions", self.base_url, name);
        let response = self.client.get(&url).send()?;
        Ok(response.json()?)
    }
    
    fn search(&self, query: &str) -> Result<Vec<PackageSummary>, RegistryError> {
        let url = format!("{}/api/v1/search?q={}", self.base_url, query);
        let response = self.client.get(&url).send()?;
        Ok(response.json()?)
    }
}
```

---

## 5. Task Breakdown

### 5.1 Task List

| ID | Task | Priority | Estimate | Dependencies |
|----|------|----------|----------|--------------|
| 5.9.1 | Implement manifest parsing | Critical | 2 days | - |
| 5.9.2 | Implement registry client | Critical | 3 days | 5.9.1 |
| 5.9.3 | Implement dependency resolver | Critical | 4 days | 5.9.2 |
| 5.9.4 | Implement package installer | Critical | 3 days | 5.9.3 |
| 5.9.5 | Implement lock file management | High | 2 days | 5.9.3 |
| 5.9.6 | Implement workspace support | High | 3 days | All above |
| 5.9.7 | Implement CLI commands | Critical | 3 days | All above |
| 5.9.8 | Write unit tests | Critical | 4 days | All above |
| 5.9.9 | Write integration tests | Critical | 3 days | All above |
| 5.9.10 | Write documentation | High | 3 days | All above |

**Total Estimated Duration:** 30 days (6 weeks)

### 5.2 Milestone Schedule

| Milestone | Date | Tasks |
|-----------|------|-------|
| M5.9.1 | Week 1-2 | 5.9.1, 5.9.2 |
| M5.9.2 | Week 3-4 | 5.9.3, 5.9.4 |
| M5.9.3 | Week 5-6 | 5.9.5, 5.9.6, 5.9.7, 5.9.8, 5.9.9, 5.9.10 |

---

## 6. CLI Commands

### 6.1 Command List

```bash
# Initialize new project
isoko init

# Add dependency
isoko add <package>[@<version>]

# Remove dependency
isoko remove <package>

# Install dependencies
isoko install

# Update dependencies
isoko update

# Search for packages
isoko search <query>

# Publish package
isoko publish

# Run package
isoko run <script>

# List dependencies
isoko list

# Check for updates
isoko check

# Clean cache
isoko clean
```

---

## 7. Testing Strategy

### 7.1 Test Types

| Type | Coverage Target | Description |
|------|-----------------|-------------|
| Unit Tests | 90% | Individual function tests |
| Integration Tests | 85% | End-to-end tests |
| Network Tests | 80% | Registry interaction tests |
| Performance Tests | 70% | Resolution speed tests |

### 7.2 Test Examples

```rust
// Manifest parsing test
#[test]
fn test_parse_manifest() {
    let content = r#"
[package]
name = "my-app"
version = "0.1.0"

[dependencies]
ilang-std = "1.0.0"
"#;
    let manifest: Manifest = toml::from_str(content).unwrap();
    assert_eq!(manifest.package.name, "my-app");
    assert_eq!(manifest.dependencies.len(), 1);
}

// Dependency resolution test
#[test]
fn test_resolve_dependencies() {
    let manifest = create_test_manifest();
    let registry = MockRegistry::new();
    let resolver = Resolver::new(Box::new(registry));
    let resolution = resolver.resolve(&manifest).unwrap();
    assert!(resolution.graph.contains("ilang-std"));
}
```

---

## 8. Security Considerations

### 8.1 Security Requirements

| Requirement | Description | Verification |
|-------------|-------------|--------------|
| Checksum Verification | Verify package integrity | SHA-256 |
| HTTPS Only | Secure downloads | Protocol check |
| Version Pinning | Prevent supply chain attacks | Lock file |
| Signature Verification | Verify author identity | Ed25519 |

---

## 9. Performance Considerations

### 9.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Resolution Speed | < 1s | Time for typical project |
| Download Speed | > 10MB/s | Throughput |
| Cache Hit Rate | > 80% | Cache effectiveness |

---

## 10. Definition of Done

### 10.1 Phase 5.9 is complete when:

- [ ] All components implemented and compiling
- [ ] Unit tests passing (> 90% coverage)
- [ ] Integration tests passing
- [ ] Manifest parsing working
- [ ] Dependency resolution working
- [ ] Package installation working
- [ ] Lock file management working
- [ ] Workspace support working
- [ ] CLI commands working
- [ ] Documentation complete
- [ ] Examples working
- [ ] Cross-platform testing passing
- [ ] Code review complete
- [ ] Changelog updated

### 10.2 Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| Build | Clean build passes | - |
| Tests | All tests pass | - |
| Coverage | > 90% | - |
| Lint | No warnings | - |
| Format | Formatted | - |
| Docs | All public API documented | - |
| Security | No vulnerabilities | - |
| Review | Code reviewed | - |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
