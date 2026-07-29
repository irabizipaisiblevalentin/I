"""urubuga — The official web platform of the I Programming Language.

Urubuga is a full-stack web framework written entirely in I language `.i` files.
It competes with Django, Laravel, Rails, Express.js, Next.js, and all major
web frameworks.

Architecture:
  - Framework code: urubuga/*.i (I language files)
  - Native modules: src/stdlib/httpserver.py (Python runtime support)
  - CLI commands: src/isoko/commands/urubugs.py

Features:
  - HTTP Server with routing and middleware
  - REST API with CRUD generation
  - GraphQL server with playground
  - WebSocket and Server-Sent Events
  - Database ORM with SQLite
  - JWT and Session authentication
  - RBAC authorization
  - Template engine with components
  - Server-side rendering (SSR)
  - Static site generation (SSG)
  - AI-native features (chat, embeddings, search)
  - CSS framework
  - Rate limiting, CORS, CSRF protection
  - Project templates (website, API, fullstack, blog, e-commerce, school)
  - CLI integration (isoko urubuga new/dev/build/serve)

Usage:
  isoko urubuga new my-project website
  cd my-project
  isoko urubuga dev

Framework files (.i):
  urubuga/ubatse.i              — Core framework, router, middleware
  urubuga/api.i                 — REST API platform
  urubuga/realtime.i            — WebSocket, SSE, presence
  urubuga/graphql.i             — GraphQL server
  urubuga/inyandikorumurongo.i  — Template engine, components
  urubuga/ai.i                  — AI integration
  urubuga/ssr.i                 — Server-side rendering
"""

__version__ = "0.1.0"
