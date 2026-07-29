# Package Registry Architecture

This document specifies the complete architecture of the I Programming Language package registry.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [API Design](#api-design)
- [Package Lifecycle](#package-lifecycle)
- [Search & Discovery](#search--discovery)
- [Security](#security)
- [CDN & Storage](#cdn--storage)
- [Web Interface](#web-interface)
- [CLI Integration](#cli-integration)
- [Governance](#governance)

## Overview

The I package registry (isoko) is a central repository for I packages. It provides:

1. **Package hosting**: Store and distribute packages
2. **Dependency resolution**: Automatic dependency management
3. **Version management**: Semantic versioning support
4. **Search & discovery**: Find packages easily
5. **Security scanning**: Vulnerability detection
6. **Documentation**: Auto-generated package docs
7. **Community features**: Ratings, reviews, discussions

### Registry URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Main Registry | `https://isoko.ilang.dev` | Package registry |
| API | `https://api.isoko.ilang.dev` | REST API |
| CDN | `https://cdn.isoko.ilang.dev` | Package downloads |
| Docs | `https://docs.isoko.ilang.dev` | Documentation |
| Web | `https://isoko.ilang.dev` | Web interface |

---

## Architecture

### High-Level Architecture

```
                    +-------------------+
                    |   Web Interface   |
                    +-------------------+
                           |
                    +-------------------+
                    |    Load Balancer  |
                    +-------------------+
                           |
        +------------------+------------------+
        |                  |                  |
+-------v-------+  +-------v-------+  +-------v-------+
|   API Server  |  |  Web Server   |  |  Auth Server  |
+-------+-------+  +-------+-------+  +-------+-------+
        |                  |                  |
        +------------------+------------------+
                           |
                    +-------------------+
                    |   Message Queue   |
                    +-------------------+
                           |
        +------------------+------------------+
        |                  |                  |
+-------v-------+  +-------v-------+  +-------v-------+
|   Database    |  |  Search Engine |  |    Cache      |
+-------+-------+  +-------+-------+  +-------+-------+
        |                  |                  |
        +------------------+------------------+
                           |
                    +-------------------+
                    |   Object Storage  |
                    +-------------------+
```

### Components

```
isoko-registry/
├── api/              # REST API
│   ├── auth/         # Authentication
│   ├── packages/     # Package management
│   ├── users/        # User management
│   ├── search/       # Search API
│   └── webhook/      # Webhooks
├── core/             # Core business logic
│   ├── package.i     # Package management
│   ├── version.i     # Version management
│   ├── dependency.i  # Dependency resolution
│   ├── user.i        # User management
│   └── security.i    # Security scanning
├── storage/          # Storage layer
│   ├── database/     # PostgreSQL
│   ├── cache/        # Redis
│   ├── search/       # Elasticsearch
│   └── object/       # S3/MinIO
├── web/              # Web interface
│   ├── frontend/     # React/Vue app
│   ├── templates/    # Server-rendered pages
│   └── static/       # Static assets
├── worker/           # Background workers
│   ├── build/        # Package building
│   ├── scan/         # Security scanning
│   ├── docs/         # Documentation generation
│   └── notify/       # Notifications
├── cdn/              # CDN
│   ├── edge/         # Edge servers
│   └── origin/       # Origin servers
└── monitor/          # Monitoring
    ├── metrics/      # Metrics collection
    ├── logging/      # Log aggregation
    └── alerting/     # Alert management
```

---

## API Design

### Authentication

```
# API Endpoints
POST   /api/auth/login          # Login
POST   /api/auth/register       # Register
POST   /api/auth/token          # Get token
POST   /api/auth/refresh        # Refresh token
DELETE /api/auth/logout          # Logout
```

### Package Endpoints

```
# Package CRUD
GET    /api/packages             # List packages
GET    /api/packages/:name       # Get package
POST   /api/packages             # Create package
PUT    /api/packages/:name       # Update package
DELETE /api/packages/:name       # Delete package

# Version management
GET    /api/packages/:name/versions           # List versions
GET    /api/packages/:name/versions/:version  # Get version
POST   /api/packages/:name/versions           # Create version
DELETE /api/packages/:name/versions/:version  # Delete version

# Downloads
GET    /api/packages/:name/download/:version  # Download package
GET    /api/packages/:name/download/latest    # Download latest

# Dependencies
GET    /api/packages/:name/dependencies       # List dependencies
GET    /api/packages/:name/dependents         # List dependents

# Documentation
GET    /api/packages/:name/docs               # Get documentation
GET    /api/packages/:name/readme             # Get README

# Search
GET    /api/search?q=:query                   # Search packages
GET    /api/search/advanced                   # Advanced search
```

### User Endpoints

```
# User profile
GET    /api/users/:username        # Get user
PUT    /api/users/:username        # Update user
GET    /api/users/:username/packages # Get user's packages

# API tokens
GET    /api/user/tokens            # List tokens
POST   /api/user/tokens            # Create token
DELETE /api/user/tokens/:id        # Delete token
```

### Webhook Endpoints

```
# Webhooks
GET    /api/webhooks               # List webhooks
POST   /api/webhooks               # Create webhook
PUT    /api/webhooks/:id           # Update webhook
DELETE /api/webhooks/:id           # Delete webhook
```

### Response Format

```json
{
  "success": true,
  "data": {
    "name": "urubuga",
    "version": "0.5.0",
    "description": "Web framework for I"
  },
  "meta": {
    "page": 1,
    "per_page": 20,
    "total": 100
  }
}
```

### Error Format

```json
{
  "success": false,
  "error": {
    "code": "PACKAGE_NOT_FOUND",
    "message": {
      "en": "Package not found",
      "rw": "Ibisohwe ntabwo byabonetse"
    },
    "details": "Package 'urubuga' does not exist"
  }
}
```

---

## Package Lifecycle

### Package States

```
enum PackageStatus
    DRAFT = "draft"           # Initial state
    PENDING = "pending"       # Under review
    PUBLISHED = "published"   # Publicly available
    DEPRECATED = "deprecated" # No longer maintained
    YANKED = "yanked"         # Removed from public
    SUSPENDED = "suspended"   # Suspended for policy violation
iherezo
```

### Version States

```
enum VersionStatus
    DRAFT = "draft"           # Not yet published
    PUBLISHED = "published"   # Available for download
    YANKED = "yanked"         # Removed (security/issues)
iherezo
```

### Publishing Workflow

```
1. User runs: isoko publish
2. Package built and tarball created
3. Tarball uploaded to registry
4. Metadata validated
5. Security scan performed
6. Dependencies verified
7. Package indexed
8. Documentation generated
9. Notification sent
10. Package available
```

### Version Resolution

When resolving dependencies, the registry follows these rules:

1. **Exact version**: `0.5.0` → exactly version 0.5.0
2. **Caret range**: `^0.5.0` → >=0.5.0, <0.6.0
3. **Tilde range**: `~0.5.0` → >=0.5.0, <0.5.1
4. **Wildcard**: `0.5.*` → >=0.5.0, <0.6.0
5. **Range**: `>=0.5.0, <1.0.0` → within range
6. **Latest**: `latest` → most recent stable version

---

## Search & Discovery

### Search Features

1. **Full-text search**: Search in name, description, keywords
2. **Tag-based search**: Filter by tags
3. **Author search**: Find packages by author
4. **Category search**: Browse by category
5. **Sort options**: Relevance, downloads, updated, newest
6. **Faceted search**: Filter by version, platform, license

### Search Index

```
igiceri PackageIndex
    id: string
    name: string
    description: string
    keywords: List<string>
    category: string
    author: string
    version: string
    downloads: int
    updated_at: timestamp
    score: float
iherezo
```

### Search API

```
GET /api/search?q=web+framework&category=frameworks&sort=downloads

Response:
{
  "results": [
    {
      "name": "urubuga",
      "description": "Web framework for I",
      "version": "0.5.0",
      "score": 0.95,
      "downloads": 15000
    }
  ],
  "total": 10,
  "facets": {
    "categories": [
      {"name": "frameworks", "count": 25},
      {"name": "libraries", "count": 150}
    ]
  }
}
```

### Categories

| Category | Description |
|----------|-------------|
| frameworks | Full-stack frameworks |
| libraries | Utility libraries |
| database | Database drivers & ORMs |
| web | Web development |
| ai | Machine learning & AI |
| game | Game development |
| mobile | Mobile development |
| desktop | Desktop applications |
| devtools | Developer tools |
| security | Security utilities |
| testing | Testing frameworks |
| documentation | Documentation tools |

### Tags

Tags are user-defined keywords that help with discovery:

```
# Popular tags
web, api, rest, graphql, database, postgres, mysql
machine-learning, deep-learning, llm, nlp, computer-vision
game, 2d, 3d, physics, audio, rendering
mobile, android, ios, react-native
desktop, gui, native
security, crypto, authentication
testing, unit-test, integration-test
```

---

## Security

### Security Scanning

Every published package undergoes automated security scanning:

1. **Static analysis**: Code pattern analysis
2. **Dependency scanning**: Check for vulnerable dependencies
3. **License scanning**: Verify license compatibility
4. **Malware detection**: Known malware signatures
5. **Secret detection**: API keys, passwords, tokens
6. **Binary scanning**: Check for suspicious binaries

### Security Levels

```
enum SecurityLevel
    LOW = "low"           # Minor issues
    MEDIUM = "medium"     # Potential vulnerabilities
    HIGH = "high"         # Significant vulnerabilities
    CRITICAL = "critical" # Critical vulnerabilities
iherezo
```

### Vulnerability Database

The registry maintains a database of known vulnerabilities:

```
igiceri Vulnerability
    id: string
    package: string
    version_range: string
    severity: SecurityLevel
    description: string
    cve: string?
    advisory: string?
    patched_versions: List<string>
iherezo
```

### Authentication & Authorization

| Action | Auth Required | Role Required |
|--------|---------------|---------------|
| Read package | No | - |
| Publish package | Yes | Maintainer |
| Delete package | Yes | Admin |
| Yank version | Yes | Maintainer |
| Manage users | Yes | Admin |
| Manage registry | Yes | Super Admin |

### API Keys

```
# API Key format
ilang_sk_live_XXXXXXXXXXXXXXXXXXXX

# Permissions
packages:read      # Read packages
packages:write     # Publish/update packages
packages:delete    # Delete packages
users:read         # Read user info
users:write        # Update user info
webhooks:manage    # Manage webhooks
```

---

## CDN & Storage

### Storage Architecture

```
+-------------------+     +-------------------+
|   Upload Server   | --> |   Origin Storage  |
+-------------------+     +-------------------+
                               |
                        +-------------------+
                        |   CDN Distribution |
                        +-------------------+
                               |
        +----------------------+----------------------+
        |                      |                      |
+-------v-------+    +-------v-------+    +-------v-------+
|  Edge Server  |    |  Edge Server  |    |  Edge Server  |
|    (NA)       |    |    (EU)       |    |    (AS)       |
+-------+-------+    +-------+-------+    +-------+-------+
        |                      |                      |
+-------v-------+    +-------v-------+    +-------v-------+
|    Users      |    |    Users      |    |    Users      |
+---------------+    +---------------+    +---------------+
```

### Package Tarball Format

```
package-name-version.tar.gz/
├── ilang.toml          # Package manifest
├── src/                # Source code
│   └── ...
├── tests/              # Tests
│   └── ...
├── docs/               # Documentation
│   └── ...
├── README.md           # Documentation
└── CHANGELOG.md        # Changelog
```

### Caching Strategy

| Resource | Cache Duration | Strategy |
|----------|----------------|----------|
| Package metadata | 5 minutes | Stale-while-revalidate |
| Package tarball | 1 year | Immutable |
| Search results | 1 minute | Stale-while-revalidate |
| User profile | 5 minutes | Stale-while-revalidate |
| API responses | 1 minute | Stale-while-revalidate |

### CDN Configuration

```yaml
# CDN Configuration
routes:
  - pattern: "/packages/*/download/*"
    cache:
      ttl: 365d
      immutable: true
    compress: true
    
  - pattern: "/api/*"
    cache:
      ttl: 60s
      stale_ttl: 300s
    compress: true
    
  - pattern: "/*"
    cache:
      ttl: 300s
    compress: true
```

---

## Web Interface

### Pages

1. **Home**: Featured packages, recent updates
2. **Search**: Package search with filters
3. **Package**: Package details, versions, docs
4. **User**: User profile, packages
5. **Publish**: Package publishing guide
6. **Docs**: Documentation
7. **Blog**: Announcements
8. **Community**: Discussions, forums

### Package Page

```
+----------------------------------------------------------+
| urubuga                                          v0.5.0  |
| Web framework for I Programming Language                 |
|                                                          |
| [Documentation] [Repository] [Issues] [Download]        |
+----------------------------------------------------------+
|                                                          |
| Description:                                             |
| Urubuga is a modern web framework for building...        |
|                                                          |
| Keywords: web, framework, api, rest, graphql             |
| License: MIT                                              |
| Author: John Doe                                          |
|                                                          |
| Statistics:                                               |
| Downloads: 15,000 | Dependents: 50 | Stars: 200         |
|                                                          |
| Versions:                                                |
| 0.5.0 (latest) | 0.4.0 | 0.3.0 | 0.2.0 | 0.1.0        |
|                                                          |
| Dependencies:                                            |
| ilang-database@^0.3.0, ilang-http@^0.2.0               |
|                                                          |
| Dependents:                                              |
| my_web_app, urubuga_admin, urubuga_api                  |
+----------------------------------------------------------+
```

---

## CLI Integration

### isoko Commands

```
# Package management
isoko init                    # Initialize project
isoko add <package>           # Add dependency
isoko remove <package>        # Remove dependency
isoko update                  # Update dependencies
isoko install                 # Install dependencies

# Publishing
isoko publish                 # Publish package
isoko yank <version>          # Yank version
isoko unpublish               # Unpublish package

# Search
isoko search <query>          # Search packages
isoko info <package>          # Get package info

# User
isoko login                   # Login to registry
isoko logout                  # Logout
isoko whoami                  # Show current user

# Tokens
isoko token create            # Create API token
isoko token list              # List tokens
isoko token delete <id>       # Delete token
```

### Configuration

```toml
# ~/.isoko/config.toml
[registry]
url = "https://isoko.ilang.dev"
token = "ilang_sk_live_XXXX"

[auth]
method = "token"

[cache]
directory = "~/.isoko/cache"
max_size = "1GB"

[proxy]
# http_proxy = "http://proxy.example.com:8080"
```

---

## Governance

### Package Policies

1. **Naming**: Must be lowercase, alphanumeric with hyphens
2. **Description**: Must be meaningful and accurate
3. **License**: Must include valid license
4. **Dependencies**: Must not depend on deprecated packages
5. **Security**: Must pass security scan
6. **Documentation**: Must include documentation

### Prohibited Packages

1. **Malware**: Malicious software
2. **Spam**: Low-quality, promotional content
3. **Illegal**: Illegal content
4. **Trademark**: Trademark violations
5. **Adult**: Adult content

### Enforcement

| Violation | Action |
|-----------|--------|
| Malware | Immediate removal, account suspension |
| Spam | Warning, then removal |
| Security | Immediate yank, notification |
| Policy | Warning, then suspension |

### Appeals Process

1. **Review**: Community review of enforcement action
2. **Appeal**: Author can appeal decision
3. **Decision**: Governance team makes final decision
4. **Resolution**: Action taken or reversed

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
