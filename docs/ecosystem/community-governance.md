# Community Governance Architecture

This document specifies the governance model, contribution guidelines, and community structure for the I Programming Language project.

## Table of Contents

- [Overview](#overview)
- [Governance Model](#governance-model)
- [Roles & Responsibilities](#roles--responsibilities)
- [Decision Making](#decision-making)
- [Contribution Guidelines](#contribution-guidelines)
- [Code of Conduct](#code-of-conduct)
- [Communication](#communication)
- [Events & Programs](#events--programs)
- [Sponsorship & Funding](#sponsorship--funding)
- [Legal & Licensing](#legal--licensing)

## Overview

The I Programming Language is governed by a community-driven model with clear roles, transparent decision-making, and inclusive participation.

### Principles

1. **Openness**: All decisions are made publicly
2. **Transparency**: All discussions are archived
3. **Inclusivity**: Everyone is welcome to contribute
4. **Meritocracy**: Contributions earn responsibility
5. **Sustainability**: Long-term project health
6. **Cultural Respect**: Honor Rwandan heritage

### Governance Documents

| Document | Purpose |
|----------|---------|
| Charter | Project mission and values |
| Code of Conduct | Behavior expectations |
| Contribution Guide | How to contribute |
| Decision Process | How decisions are made |
| Release Process | How releases are managed |
| Security Policy | Security vulnerability handling |

---

## Governance Model

### Structure

```
+----------------------------------------------------------+
|                    Technical Steering Committee            |
|                    (5 members, elected annually)           |
+----------------------------------------------------------+
                           |
        +------------------+------------------+
        |                  |                  |
+-------v-------+  +-------v-------+  +-------v-------+
|  Core Team    |  |  Framework    |  |  Community    |
|  (10-20)      |  |  Teams        |  |  Team         |
+-------+-------+  +-------+-------+  +-------+-------+
        |                  |                  |
        +------------------+------------------+
                           |
                    +-------------------+
                    |  Contributors     |
                    |  (unlimited)      |
                    +-------------------+
                           |
                    +-------------------+
                    |  Users            |
                    |  (unlimited)      |
                    +-------------------+
```

### Teams

| Team | Focus | Size | Lead |
|------|-------|------|------|
| Core | Language, compiler, VM | 10-20 | Elected |
| urubuga | Web framework | 5-10 | Appointed |
| ibiro | Desktop framework | 5-10 | Appointed |
| mobile | Mobile framework | 5-10 | Appointed |
| ubwenge | AI framework | 5-10 | Appointed |
| imikino | Game engine | 5-10 | Appointed |
| sisitemu | Systems framework | 5-10 | Appointed |
| igicu | Cloud framework | 5-10 | Appointed |
| Tools | Developer tools | 5-10 | Appointed |
| Documentation | Documentation | 5-10 | Appointed |
| Community | Community management | 5-10 | Appointed |

---

## Roles & Responsibilities

### Technical Steering Committee (TSC)

**Responsibilities:**
1. Set project direction and roadmap
2. Approve major changes
3. Resolve disputes between teams
4. Manage project finances
5. Represent the project externally

**Composition:**
- 5 elected members
- 1-year terms
- Staggered elections (2-3 seats per year)
- Maximum 2 consecutive terms

**Election Process:**
1. Nominations open for 2 weeks
2. Candidates present platform
3. Community voting for 2 weeks
4. Results announced
5. Transition period (1 week)

### Core Team

**Responsibilities:**
1. Review and merge pull requests
2. Triage issues
3. Write technical documentation
4. Mentor contributors
5. Participate in design discussions

**Requirements:**
- 3+ months of contributions
- Strong understanding of I language
- Good communication skills
- Time commitment: 5-10 hours/week

**Becoming a Core Member:**
1. Contribute to the project for 3+ months
2. Submit an application
3. Core team review and vote
4. Invitation extended
5. Onboarding period (1 month)

### Framework Teams

**Responsibilities:**
1. Maintain framework code
2. Review framework PRs
3. Design framework features
4. Write framework documentation
5. Support framework users

**Requirements:**
- Strong expertise in framework domain
- Active contributions to framework
- Time commitment: 5-10 hours/week

### Community Team

**Responsibilities:**
1. Manage Discord and forums
2. Organize events
3. Create educational content
4. Support new contributors
5. Manage social media

---

## Decision Making

### Decision Levels

| Level | Scope | Process | Timeline |
|-------|-------|---------|----------|
| Strategic | Project direction | TSC vote | Monthly |
| Technical | Language design | RFC process | As needed |
| Tactical | Day-to-day | Team lead | Immediate |
| Community | Community events | Community team | As needed |

### RFC Process

For significant changes to the language or ecosystem:

1. **Proposal**: Author writes RFC document
2. **Discussion**: Community discusses (2 weeks)
3. **Revision**: Author revises based on feedback
4. **Vote**: Core team votes (1 week)
5. **Decision**: Accepted/Rejected/Deferred
6. **Implementation**: If accepted, implementation begins

### RFC Template

```markdown
# RFC: [Title]

## Summary
One paragraph description of the proposal.

## Motivation
Why is this change needed?

## Detailed Design
Technical details of the proposal.

## Alternatives
What alternatives were considered?

## Unresolved Questions
What questions need further discussion?

## References
Links to related discussions, issues, etc.
```

### Voting Rules

| Decision Type | Quorum | Threshold | Timeline |
|---------------|--------|-----------|----------|
| Strategic | 3/5 TSC | Simple majority | 1 month |
| Language | 5/10 Core | 2/3 majority | 2 weeks |
| Framework | Team lead | Simple majority | 1 week |
| Community | Open | Consensus | As needed |

### Conflict Resolution

1. **Discussion**: Parties discuss directly
2. **Mediation**: TSC member mediates
3. **Arbitration**: TSC decides
4. **Appeal**: Community vote (final)

---

## Contribution Guidelines

### Getting Started

1. **Read Documentation**: Start with the contributing guide
2. **Join Discord**: Introduce yourself
3. **Find Issues**: Look for "good first issue" labels
4. **Ask Questions**: Don't hesitate to ask
5. **Start Small**: Begin with documentation or tests

### Contribution Types

| Type | Description | Difficulty |
|------|-------------|------------|
| Documentation | Write/improve docs | Easy |
| Tests | Write tests | Easy |
| Bug Fixes | Fix bugs | Medium |
| Features | Add features | Medium |
| Design | Propose changes | Hard |
| Review | Review PRs | Medium |
| Mentoring | Help newcomers | Ongoing |

### Pull Request Process

1. **Fork Repository**: Fork the relevant repository
2. **Create Branch**: Create a feature branch
3. **Make Changes**: Implement your changes
4. **Write Tests**: Add tests for your changes
5. **Update Documentation**: Update relevant docs
6. **Submit PR**: Submit a pull request
7. **Code Review**: Address review feedback
8. **Merge**: Maintainer merges your PR

### PR Requirements

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)
- [ ] Commit messages follow convention

### Commit Convention

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style
- `refactor`: Refactoring
- `test`: Tests
- `chore`: Maintenance

**Examples:**
```
feat(compiler): add generics support
fix(vm): memory leak in garbage collector
docs(stdlib): update math module documentation
```

### Code Style

```
# I Code Style Guide

1. Naming Conventions
   - Variables: snake_case
   - Functions: snake_case
   - Types: PascalCase
   - Constants: UPPER_SNAKE_CASE
   - Keywords: Kinyarwanda lowercase

2. Indentation
   - 4 spaces
   - No tabs

3. Line Length
   - Maximum 100 characters

4. Imports
   - Sort alphabetically
   - Group by source

5. Comments
   - Use sparingly
   - Explain why, not what

6. Error Handling
   - Always handle errors
   - Use Result types
   - Provide bilingual messages
```

### Issue Guidelines

**Bug Reports:**
```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- I version:
- OS:
- Architecture:
```

**Feature Requests:**
```markdown
## Feature Description
Clear description of the feature.

## Motivation
Why is this feature needed?

## Proposed Solution
How should this feature work?

## Alternatives
What alternatives were considered?
```

---

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Community leaders will review and investigate all complaints, and will respond in a way that it deems appropriate to the circumstances.

**Consequences:**
1. Warning
2. Temporary ban
3. Permanent ban
4. Legal action (in severe cases)

### Reporting

Reports can be made to:
- Email: conduct@ilang.dev
- Discord: #moderation channel
- Anonymous form: https://ilang.dev/report

---

## Communication

### Channels

| Channel | Purpose | Audience |
|---------|---------|----------|
| Discord | Real-time chat | Everyone |
| Forum | Discussions | Everyone |
| GitHub | Code, issues | Contributors |
| Blog | Announcements | Everyone |
| Newsletter | Monthly updates | Subscribers |
| Twitter | Quick updates | Everyone |
| YouTube | Tutorials, talks | Everyone |

### Discord Structure

```
I Programming Language
├── General
│   ├── #general
│   ├── #introductions
│   └── #off-topic
├── Development
│   ├── #compiler
│   ├── #stdlib
│   ├── #frameworks
│   └── #tools
├── Frameworks
│   ├── #urubuga
│   ├── #ibiro
│   ├── #mobile
│   ├── #ubwenge
│   ├── #imikino
│   ├── #sisitemu
│   └── #igicu
├── Community
│   ├── #help
│   ├── #showcase
│   ├── #events
│   └── #jobs
├── Moderation
│   ├── #moderation
│   └── #announcements
└── Voice
    ├── General Voice
    ├── Development Voice
    └── Events Voice
```

### Meeting Schedule

| Meeting | Frequency | Purpose |
|---------|-----------|---------|
| TSC Meeting | Monthly | Strategic decisions |
| Core Team | Weekly | Development sync |
| Framework Leads | Bi-weekly | Framework coordination |
| Community Call | Monthly | Community updates |
| Office Hours | Weekly | Open Q&A |

### Meeting Notes

All meeting notes are public:
- TSC: https://github.com/ilang-dev/tsc/tree/main/meetings
- Core: https://github.com/ilang-dev/core/tree/main/meetings
- Community: https://community.ilang.dev/c/announcements/

---

## Events & Programs

### Annual Events

| Event | Time | Purpose |
|-------|------|---------|
| I Conf | September | Annual conference |
| I Hack | November | Month-long hackathon |
| I Learn | Ongoing | Learning bootcamp |
| I Give | December | Year-end review |

### I Conf

Annual conference with:
- Keynotes
- Technical talks
- Workshops
- Networking
- Awards

**Structure:**
- Day 1: Keynotes, talks
- Day 2: Workshops, hackathon
- Day 3: Community, awards

### I Hack

Month-long hackathon:
- Teams of 1-5 people
- Build projects using I
- Prizes for winners
- Categories: Web, Desktop, Mobile, AI, Games

### Programs

| Program | Description | Duration |
|---------|-------------|----------|
| Mentorship | 1-on-1 mentoring | 3 months |
| Internship | Summer internships | 3 months |
| Fellowship | Research fellowship | 1 year |
| Ambassador | Community ambassadors | Ongoing |

### Mentorship Program

**Structure:**
- Mentors: Core team members, experienced contributors
- Mentees: New contributors, students
- Duration: 3 months
- Meetings: Weekly 1-hour sessions
- Goals: Learn I, contribute to project, career development

**Topics:**
1. Language basics
2. Compiler internals
3. Framework development
4. Open source best practices
5. Career advice

---

## Sponsorship & Funding

### Funding Sources

| Source | Purpose | Status |
|--------|---------|--------|
| Individual donations | General funding | Active |
| Corporate sponsors | Development | Seeking |
| Grants | Research | Applying |
| Merchandise | Fundraising | Planned |

### Sponsorship Tiers

| Tier | Annual | Benefits |
|------|--------|----------|
| Bronze | $1,000 | Logo on website |
| Silver | $5,000 | Logo + mention in blog |
| Gold | $10,000 | Logo + blog + conference |
| Platinum | $25,000 | All above + advisory seat |

### Financial Transparency

All finances are public:
- Monthly reports on blog
- Annual audit
- Open books policy
- Community input on major expenses

### Budget Allocation

| Category | Percentage | Purpose |
|----------|------------|---------|
| Development | 50% | Core development |
| Infrastructure | 20% | Servers, tools |
| Events | 15% | Conferences, meetups |
| Marketing | 10% | Website, content |
| Reserve | 5% | Emergency fund |

---

## Legal & Licensing

### Licenses

| Component | License | Rationale |
|-----------|---------|-----------|
| Compiler | MIT | Maximum adoption |
| Standard Library | MIT | Maximum adoption |
| Frameworks | MIT | Maximum adoption |
| Developer Tools | MIT | Maximum adoption |
| Documentation | CC BY 4.0 | Open documentation |
| Website | MIT | Open source |
| Branding | Trademark | Brand protection |

### Trademark Policy

- I name and logo are trademarks
- Fair use permitted
- No use in product names without permission
- Community use encouraged

### CLA (Contributor License Agreement)

All contributors must sign CLA:
- Grants project right to use contributions
- Protects contributors
- Enables relicensing if needed
- Standard open source CLA

### Security Policy

**Reporting vulnerabilities:**
1. Email: security@ilang.dev
2. PGP key available
3. Response within 24 hours
4. Fix within 7 days (critical)
5. Credit in release notes

**Security releases:**
- Critical: Immediate release
- High: Next patch release
- Medium: Next minor release
- Low: Next major release

---

## Roadmap

### 2026

| Quarter | Milestone |
|---------|-----------|
| Q1 | Language specification v1.0 |
| Q2 | Compiler v0.1.0 |
| Q3 | Standard Library v0.1.0 |
| Q4 | urubuga v0.1.0 |

### 2027

| Quarter | Milestone |
|---------|-----------|
| Q1 | Developer tools v0.1.0 |
| Q2 | Package registry v1.0 |
| Q3 | Learning platform v1.0 |
| Q4 | All frameworks v0.1.0 |

### 2028

| Quarter | Milestone |
|---------|-----------|
| Q1 | I Language v1.0 |
| Q2 | Native compiler |
| Q3 | IDE v1.0 |
| Q4 | Enterprise features |

---

**I Programming Language** - *Kuvana Imana, Kubaka Icyo Turije* (From God, Building What We Have)
