# Website & Learning Platform Architecture

This document specifies the complete architecture of the I Programming Language website and learning platform.

## Table of Contents

- [Overview](#overview)
- [Website Architecture](#website-architecture)
- [Learning Platform](#learning-platform)
- [Interactive Playground](#interactive-playground)
- [Documentation System](#documentation-system)
- [Blog & Community](#blog--community)
- [Analytics & SEO](#analytics--seo)
- [Performance & CDN](#performance--cdn)
- [Accessibility](#accessibility)

## Overview

The I Programming Language website (ilang.dev) serves as the central hub for the ecosystem:

1. **Marketing**: Showcase the language and ecosystem
2. **Documentation**: Official language and library docs
3. **Learning**: Interactive tutorials and courses
4. **Community**: Forums, discussions, events
5. **Downloads**: Compiler and tools
6. **Blog**: News, announcements, tutorials

### URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Main Site | `https://ilang.dev` | Marketing & landing |
| Docs | `https://docs.ilang.dev` | Documentation |
| Learn | `https://learn.ilang.dev` | Learning platform |
| Playground | `https://play.ilang.dev` | Online compiler |
| Blog | `https://blog.ilang.dev` | Blog & news |
| Community | `https://community.ilang.dev` | Forums |
| Package Registry | `https://isoko.ilang.dev` | Package registry |

---

## Website Architecture

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Next.js (React) | SSR, SSG, performance |
| Styling | Tailwind CSS | Utility-first, performance |
| CMS | Sanity.io | Headless CMS, real-time |
| Hosting | Vercel | Edge functions, CDN |
| Analytics | Plausible | Privacy-first analytics |
| Search | Algolia | Fast, relevant search |

### Site Structure

```
ilang.dev/
├── pages/                # Pages
│   ├── index.tsx         # Home page
│   ├── about.tsx         # About I
│   ├── features.tsx      # Language features
│   ├── playground.tsx    # Online playground
│   ├── download.tsx      # Download compiler
│   ├── ecosystem.tsx     # Ecosystem overview
│   ├── community.tsx     # Community hub
│   ├── blog/             # Blog
│   │   ├── index.tsx     # Blog listing
│   │   └── [slug].tsx    # Blog post
│   └── docs/             # Documentation
│       ├── index.tsx     # Docs landing
│       └── [...slug].tsx # Docs pages
├── components/           # Components
│   ├── layout/           # Layout components
│   ├── ui/               # UI components
│   ├── marketing/        # Marketing components
│   └── docs/             # Documentation components
├── content/              # Content
│   ├── blog/             # Blog posts
│   ├── docs/             # Documentation
│   └── pages/            # Static pages
└── public/               # Static assets
    ├── images/           # Images
    ├── fonts/            # Fonts
    └── videos/           # Videos
```

### Pages

#### Home Page

```
+----------------------------------------------------------+
|  I Programming Language                                   |
|  *Kuvana Imana, Kubaka Icyo Turije*                      |
|  From God, Building What We Have                         |
|                                                          |
|  [Get Started] [Download] [Playground]                   |
+----------------------------------------------------------+
|                                                          |
|  Features                                                |
|  - Native Kinyarwanda syntax                             |
|  - Progressive type system                               |
|  - Modern tooling                                        |
|  - 7 official frameworks                                 |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  Code Example                                            |
|  ```                                                     |
|  shyiramo urubuga                                         |
|                                                          |
|  umurimo greet(name: string) -> string {                 |
|      subira "Muraho, " + name + "!"                      |
|  }                                                       |
|  ```                                                     |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  Ecosystem                                               |
|  [urubuga] [ibiro] [mobile] [ubwenge] [imikino]         |
|  [sisitemu] [igicu]                                      |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  Community                                               |
|  [Discord] [GitHub] [Forum]                              |
|                                                          |
+----------------------------------------------------------+
|                                                          |
|  Latest News                                             |
|  - I v0.1.0 Released (Blog Post)                        |
|  - New Framework: imikino Game Engine (Blog Post)        |
|  - Community Meeting Notes (Blog Post)                   |
|                                                          |
+----------------------------------------------------------+
|  Footer: © 2026 I Programming Language                   |
+----------------------------------------------------------+
```

#### Features Page

```
+----------------------------------------------------------+
|  Language Features                                        |
+----------------------------------------------------------+
|                                                          |
|  Kinyarwanda Syntax                                      |
|  - Native keywords                                       |
|  - Bilingual error messages                              |
|  - Cultural relevance                                    |
|                                                          |
|  Progressive Type System                                 |
|  - Optional typing                                       |
|  - Type inference                                        |
|  - Generics                                             |
|                                                          |
|  Modern Tooling                                          |
|  - Package manager (isoko)                               |
|  - Code formatter (iformat)                              |
|  - Debugger (idebug)                                     |
|  - IDE support (I Studio)                                |
|                                                          |
|  7 Frameworks                                            |
|  - urubuga (Web)                                         |
|  - ibiro (Desktop)                                       |
|  - mobile (Mobile)                                       |
|  - ubwenge (AI)                                          |
|  - imikino (Game Engine)                                 |
|  - sisitemu (Systems)                                    |
|  - igicu (Cloud)                                         |
|                                                          |
|  [View Language Specification]                           |
+----------------------------------------------------------+
```

#### Download Page

```
+----------------------------------------------------------+
|  Download I Programming Language                         |
+----------------------------------------------------------+
|                                                          |
|  Latest Version: v0.1.0                                  |
|                                                          |
|  [Windows] [macOS] [Linux]                               |
|                                                          |
|  Or install via package manager:                         |
|  ```                                                     |
|  # Windows (winget)                                      |
|  winget install ilang                                     |
|                                                          |
|  # macOS (Homebrew)                                      |
|  brew install ilang                                       |
|                                                          |
|  # Linux (apt)                                           |
|  sudo apt install ilang                                  |
|  ```                                                     |
|                                                          |
|  Development Tools:                                      |
|  [I Studio IDE] [isoko CLI] [iformat]                   |
|                                                          |
+----------------------------------------------------------+
```

---

## Learning Platform

### Course Structure

```
learn.ilang.dev/
├── courses/              # Courses
│   ├── beginner/         # Beginner track
│   ├── intermediate/     # Intermediate track
│   ├── advanced/         # Advanced track
│   └── frameworks/       # Framework courses
├── exercises/            # Exercises
│   ├── basics/           # Basic exercises
│   ├── functions/        # Function exercises
│   ├── types/            # Type exercises
│   └── projects/         # Project exercises
├── projects/             # Guided projects
│   ├── web-app/          # Build a web app
│   ├── desktop-app/      # Build a desktop app
│   ├── ai-model/         # Build an AI model
│   └── game/             # Build a game
└── assessments/          # Assessments
    ├── quizzes/          # Quizzes
    ├── challenges/       # Coding challenges
    └── certifications/   # Certifications
```

### Course Tracks

#### Beginner Track (8 weeks)

| Week | Topic | Exercises | Project |
|------|-------|-----------|---------|
| 1 | Hello World | 5 | - |
| 2 | Variables & Types | 8 | Calculator |
| 3 | Control Flow | 10 | - |
| 4 | Functions | 12 | - |
| 5 | Data Structures | 10 | Todo List |
| 6 | Error Handling | 8 | - |
| 7 | Modules | 6 | - |
| 8 | Final Project | - | Blog App |

#### Intermediate Track (8 weeks)

| Week | Topic | Exercises | Project |
|------|-------|-----------|---------|
| 1 | OOP | 8 | - |
| 2 | Generics | 10 | - |
| 3 | Concurrency | 12 | - |
| 4 | Async/Await | 10 | - |
| 5 | Web Framework | 15 | Web API |
| 6 | Database | 12 | - |
| 7 | Testing | 10 | - |
| 8 | Final Project | - | Full Stack App |

#### Advanced Track (8 weeks)

| Week | Topic | Exercises | Project |
|------|-------|-----------|---------|
| 1 | Metaprogramming | 10 | - |
| 2 | Systems Programming | 12 | - |
| 3 | AI Framework | 15 | ML Model |
| 4 | Game Engine | 12 | - |
| 5 | Cloud Architecture | 10 | - |
| 6 | Performance | 8 | - |
| 7 | Security | 10 | - |
| 8 | Final Project | - | Open Source |

### Exercise Format

```
igiceri Exercise
    id: string
    title: string
    description: string
    difficulty: Difficulty
    topics: List<string>
    
    # Starter code
    starter_code: string
    
    # Tests
    tests: List<TestCase>
    
    # Hints
    hints: List<string>
    
    # Solution
    solution: string
iherezo

igiceri TestCase
    input: string
    expected_output: string
    hidden: bool = false
iherezo
```

### Example Exercise

```
# Exercise: Hello World
difficulty: easy
topics: ["basics", "output"]

## Description
Write a program that prints "Muraho, Dunia!" (Hello World in Kinyarwanda).

## Starter Code
```
# Write your code here
```

## Tests
- Input: (none)
- Expected: "Muraho, Dunia!"

## Hints
- Use the `print()` function
- Strings are enclosed in double quotes

## Solution
```
print("Muraho, Dunia!")
```
```

### Progress Tracking

```
igiceri UserProgress
    user_id: string
    course_id: string
    completed_lessons: List<string>
    current_lesson: string
    scores: Map<string, float>
    streak: int
    points: int
    badges: List<Badge>
iherezo

igiceri Badge
    id: string
    name: string
    description: string
    icon: string
    earned_at: timestamp?
iherezo
```

### Gamification

| Points | Badge | Description |
|--------|-------|-------------|
| 100 | *Umwansi* (Beginner) | Complete first lesson |
| 500 | *Intore* (Warrior) | Complete beginner track |
| 1000 | *Umwega* (Expert) | Complete intermediate track |
| 2000 | *Umuhizi* (Master) | Complete advanced track |
| 5000 | *Umuvandimwe* (Contributor) | Contribute to ecosystem |
| 10000 | *Umuvugizi* (Ambassador) | Help others learn |

---

## Interactive Playground

### Architecture

```
play.ilang.dev/
├── frontend/            # Web interface
│   ├── editor/          # Code editor
│   ├── output/          # Output panel
│   ├── examples/        # Example programs
│   └── share/           # Share functionality
├── backend/             # Backend
│   ├── compiler/        # Compiler service
│   ├── sandbox/         # Sandboxed execution
│   └── storage/         # Example storage
└── infrastructure/      # Infrastructure
    ├── container/       # Container runtime
    ├── queue/           # Task queue
    └── cache/           # Result cache
```

### Features

1. **Code Editor**: Monaco editor with I syntax highlighting
2. **Live Compilation**: Real-time compilation feedback
3. **Execution**: Sandboxed code execution
4. **Examples**: Pre-built example programs
5. **Sharing**: Share code via URL
6. **Export**: Export to GitHub Gist
7. **Terminal**: Integrated terminal output
8. **Debug**: Basic debugging support

### Playground Layout

```
+----------------------------------------------------------+
|  I Playground                                    [Share] |
+----------------------------------------------------------+
| Examples | [main.i]                              | Output |
|----------|--------------------------------------|---------|
| Hello    | shyiramo urubuga                       | >      |
| World    |                                        | Muraho |
| Calculator| umurimo main() -> void {              | Dunia! |
| Todo     |     print("Muraho, Dunia!")            |        |
| Web API  | }                                      |        |
|          |                                        |        |
|          |                                        |        |
|          |                                        |        |
+----------------------------------------------------------+
| [Run] [Format] [Reset] | Speed: 100ms | Memory: 10MB    |
+----------------------------------------------------------+
```

### API

```
# Compile code
POST /api/compile
{
  "code": "shyiramo urubuga\n\nprint(\"Muraho, Dunia!\")",
  "optimize": false
}

# Execute code
POST /api/execute
{
  "code": "shyiramo urubuga\n\nprint(\"Muraho, Dunia!\")",
  "input": ""
}

# Get example
GET /api/examples/:id

# Share code
POST /api/share
{
  "code": "...",
  "title": "My Example"
}

# Get shared code
GET /api/share/:id
```

---

## Documentation System

### Architecture

```
docs.ilang.dev/
├── content/             # Documentation content
│   ├── language/        # Language specification
│   ├── standard-lib/    # Standard library
│   ├── frameworks/      # Framework docs
│   ├── tools/           # Tool docs
│   ├── guides/          # Guides
│   └── examples/        # Code examples
├── components/          # Documentation components
│   ├── code/            # Code blocks
│   ├── api/             # API reference
│   ├── tutorial/        # Tutorial steps
│   └── quiz/            # Quizzes
├── search/              # Search
│   ├── index/           # Search index
│   └── engine/          # Search engine
└── versioning/          # Version management
    ├── current/         # Current version
    ├── v0.1/            # Version 0.1
    └── latest/          # Latest version
```

### Documentation Structure

```
docs/
├── getting-started/      # Getting started
│   ├── installation/
│   ├── hello-world/
│   ├── variables/
│   └── first-program/
├── language/             # Language reference
│   ├── syntax/
│   ├── types/
│   ├── functions/
│   ├── classes/
│   ├── modules/
│   └── error-handling/
├── standard-library/     # Standard library
│   ├── core/
│   ├── collections/
│   ├── io/
│   └── ...
├── frameworks/           # Frameworks
│   ├── urubuga/
│   ├── ibiro/
│   └── ...
├── tools/                # Tools
│   ├── compiler/
│   ├── package-manager/
│   └── ...
├── guides/               # Guides
│   ├── web-development/
│   ├── desktop-development/
│   └── ...
└── examples/             # Examples
    ├── hello-world/
    ├── calculator/
    ├── web-api/
    └── ...
```

### Code Examples

All documentation includes runnable code examples:

```
# Example: Variables
shyiramo urubuga

# Variable declaration
shyira name: string = "I Language"
shyira version: float = 0.1

# Type inference
shyira greeting = "Muraho"  # Inferred as string

# Constants
gusangiza PI = 3.14159

# Output
print(name)           # I Language
print(version)        # 0.1
print(greeting)       # Muraho
print(PI)             # 3.14159
```

### Search

Documentation search powered by Algolia:

1. **Full-text search**: Search in all documentation
2. **Autocomplete**: Search as you type
3. **Faceted search**: Filter by category, version
4. **Popular searches**: Show trending searches
5. **Recent searches**: Remember user searches

---

## Blog & Community

### Blog

```
blog.ilang.dev/
├── posts/               # Blog posts
│   ├── announcements/   # Product announcements
│   ├── tutorials/       # Tutorials
│   ├── community/       # Community posts
│   └── technical/       # Technical deep dives
├── authors/             # Authors
│   └── [slug].tsx       # Author page
└── tags/                # Tags
    └── [tag].tsx        # Tag page
```

### Blog Post Types

1. **Announcements**: New releases, features
2. **Tutorials**: Step-by-step guides
3. **Community**: Community highlights, events
4. **Technical**: Deep dives, architecture
5. **News**: Industry news, updates

### Community Features

1. **Discord**: Real-time chat
2. **Forum**: Discussion boards
3. **GitHub**: Code collaboration
4. **Events**: Meetups, conferences
5. **Contributing**: Contribution guidelines

### Community Hub

```
community.ilang.dev/
├── forum/               # Discussion forum
│   ├── categories/      # Forum categories
│   ├── topics/          # Discussion topics
│   └── users/           # User profiles
├── events/              # Events
│   ├── meetups/         # Local meetups
│   ├── conferences/     # Conferences
│   └── workshops/       # Workshops
├── contribute/          # Contributing
│   ├── guidelines/      # Contribution guide
│   ├── roadmap/         # Project roadmap
│   └── governance/      # Governance
└── showcase/            # User projects
    ├── projects/        # Project showcase
    └── stories/         # User stories
```

---

## Analytics & SEO

### Analytics

| Tool | Purpose | Privacy |
|------|---------|---------|
| Plausible | Page views, visitors | Privacy-first |
| Algolia | Search analytics | - |
| Sentry | Error tracking | - |
| Vercel | Performance | - |

### SEO Strategy

1. **Metadata**: Complete Open Graph, Twitter cards
2. **Structured data**: JSON-LD schema
3. **Sitemap**: Auto-generated sitemap
4. **Robots.txt**: Search engine directives
5. **Performance**: Fast loading, Core Web Vitals
6. **Mobile**: Mobile-first design
7. **Accessibility**: WCAG compliance

### Meta Tags

```html
<title>I Programming Language - Native Kinyarwanda Programming</title>
<meta name="description" content="I is a modern programming language with native Kinyarwanda syntax..." />
<meta property="og:title" content="I Programming Language" />
<meta property="og:description" content="Native Kinyarwanda programming language..." />
<meta property="og:image" content="https://ilang.dev/og.png" />
<meta name="twitter:card" content="summary_large_image" />
```

---

## Performance & CDN

### Performance Targets

| Metric | Target |
|--------|--------|
| First Contentful Paint | < 1.0s |
| Largest Contentful Paint | < 2.5s |
| Time to Interactive | < 3.0s |
| Cumulative Layout Shift | < 0.1 |
| First Input Delay | < 100ms |

### Optimization Strategies

1. **Static Generation**: Pre-render pages at build time
2. **Incremental Static Regeneration**: Update static pages
3. **Edge Functions**: Server-side logic at edge
4. **Image Optimization**: Automatic image optimization
5. **Font Optimization**: Font subsetting, preload
6. **Code Splitting**: Automatic code splitting
7. **Lazy Loading**: Load components on demand
8. **Caching**: Aggressive caching strategy

### CDN Configuration

```
# Vercel Configuration
{
  "regions": ["iad1", "sfo1", "lhr1", "nrt1"],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "DENY"},
        {"key": "X-XSS-Protection", "value": "1; mode=block"}
      ]
    }
  ],
  "redirects": [
    {"source": "/docs", "destination": "/docs/getting-started", "permanent": true}
  ]
}
```

---

## Accessibility

### WCAG Compliance

| Level | Status | Notes |
|-------|--------|-------|
| A | ✅ | Full compliance |
| AA | ✅ | Full compliance |
| AAA | 🔄 | Partial compliance |

### Accessibility Features

1. **Keyboard Navigation**: Full keyboard support
2. **Screen Reader**: ARIA labels, semantic HTML
3. **Color Contrast**: WCAG AA contrast ratios
4. **Text Scaling**: Responsive to text size
5. **Focus Indicators**: Visible focus states
6. **Alt Text**: Images have alt text
7. **Captions**: Videos have captions
8. **Transcripts**: Audio has transcripts

### Testing

Automated accessibility testing:

1. **axe-core**: Automated accessibility testing
2. **Lighthouse**: Performance and accessibility audits
3. **WAVE**: Web accessibility evaluation
4. **Manual Testing**: Regular manual audits

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
