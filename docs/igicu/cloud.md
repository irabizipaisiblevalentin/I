# IGICU Cloud Guide

## Overview

IGICU is the cloud computing platform for the I Programming Language. This guide
covers the core concepts and usage patterns for building cloud-native applications.

## Core Concepts

### Projects
An IGICU project is a directory containing infrastructure definitions, function code,
and deployment configurations. Create one with `isoko igicu new my-project`.

### Clusters
A cluster is a group of nodes that run your workloads. Clusters provide:
- Resource isolation via namespaces
- Node management (add, remove, cordon, drain)
- Health monitoring and auto-recovery

### Deployments
Deployments manage replicated applications with:
- Declarative updates (rolling, blue/green, canary)
- Health checking and auto-healing
- Horizontal and vertical scaling

### Services
Services provide stable endpoints for your applications:
- Service discovery via DNS or registry
- Load balancing across instances
- Health-based routing

## Getting Started

```bash
# Install IGICU
isoko install igicu

# Create a project
isoko igicu new my-first-cloud-app --type project
cd my-first-cloud-app

# Create a cluster
isoko igicu cluster create dev --nodes 3

# Deploy an application
isoko igicu deploy web-app --image nginx:latest --replicas 3 --port 80

# Monitor your deployment
isoko igicu monitor --type all
```

## Architecture Patterns

### Microservices
Deploy independent services that communicate via the service mesh:

```bash
isoko igicu deploy auth-service --image auth:latest --replicas 2
isoko igicu deploy api-gateway --image gateway:latest --replicas 3
isoko igicu deploy user-service --image users:latest --replicas 2
```

### Event-Driven
Use messaging topics to decouple services:

```bash
isoko igicu messaging topic orders --partitions 3
isoko igicu messaging topic payments --partitions 2
```

### Serverless
Deploy functions for event-driven workloads:

```bash
isoko igicu function create process-order --runtime i_lang --memory 256
isoko igicu function invoke process-order --data '{"id": "123"}'
```
