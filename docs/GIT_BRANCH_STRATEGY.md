# SimSight — Git Branch Strategy

> As a solo developer, keep the branching model **simple but professional**.
> The goal is a clean Git history that looks impressive on GitHub and makes
> it easy to recover from mistakes.

---

## Branch Overview

```
main ──────────────────────────────────────────────────────► (production)
  │
  └── dev ──────────────────────────────────────────────────► (integration)
        │
        ├── feature/phase-1-db-setup
        ├── feature/phase-2-data-gen-engine
        ├── feature/phase-3-graph-relationships
        ├── feature/phase-3-anomaly-detection
        ├── feature/phase-4-dashboard-ui
        ├── feature/phase-4-map-view
        ├── feature/phase-4-graph-view
        └── hotfix/fix-cors-header            (branches from main, not dev)
```

---

## Branch Purposes

### `main`
- **Always deployable.** Every commit on `main` is production-ready.
- Never commit directly to `main`.
- Only merges come from `dev` (via PR) or `hotfix/*` branches.
- Protected branch: require at least one passing CI check before merge.
- Tagged with version numbers: `v0.1.0`, `v0.2.0`, etc.

### `dev`
- **Integration branch.** This is where feature branches are merged and tested together.
- You will spend most of your time here.
- Keep it reasonably stable — if something breaks `dev`, fix it before starting new work.
- Merge into `main` at the end of each completed phase (or whenever `dev` is fully stable).

### `feature/*`
- **One branch per logical unit of work** (not per phase, but per deliverable within a phase).
- Name format: `feature/<phase>-<short-description>`
  - ✅ `feature/phase-2-person-generator`
  - ✅ `feature/phase-4-cytoscape-graph`
  - ❌ `feature/stuff` (too vague)
  - ❌ `feature/phase-2` (too broad — one branch per deliverable)
- Branch from: `dev`
- Merge back into: `dev` (via PR or direct merge for solo work)

### `hotfix/*`
- **Emergency fix for a bug found on `main`** (i.e., production).
- Name format: `hotfix/<short-description>`
  - ✅ `hotfix/fix-env-secret-exposure`
  - ✅ `hotfix/patch-neo4j-connection-leak`
- Branch from: `main`
- Merge back into: **both `main` AND `dev`** (so `dev` gets the fix too)
- Tag the fixed `main` with a patch version: `v0.1.1`

---

## Commit Message Convention

Follow the **Conventional Commits** spec. This makes the history readable and enables
automatic changelog generation later.

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

### Types

| Type | When to Use |
|------|-------------|
| `feat` | A new feature |
| `fix` | A bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code change, no new feature or fix |
| `test` | Adding/updating tests |
| `chore` | Build tools, dependencies, config |
| `perf` | Performance improvement |

### Examples

```
feat(data-gen): add person generator using Faker library
fix(api): correct pagination offset in /persons endpoint
docs(readme): add local setup instructions for phase 1
test(anomaly): add unit tests for z-score detection
chore(docker): update postgres image to 15-alpine
```

---

## Workflow — Day-to-Day Solo Development

### Starting a new feature

```bash
# Make sure dev is up to date
git checkout dev
git pull origin dev

# Create your feature branch
git checkout -b feature/phase-2-person-generator

# Do your work, commit often
git add -p                    # stage hunks interactively
git commit -m "feat(data-gen): scaffold person generator"
git commit -m "feat(data-gen): add fake SSN + address generation"
git commit -m "test(data-gen): add unit tests for person generator"
```

### Finishing a feature (merging back to dev)

```bash
# Option A: Direct merge (solo project, acceptable)
git checkout dev
git merge --no-ff feature/phase-2-person-generator -m "feat: merge person generator into dev"
git push origin dev

# Option B: Open a PR on GitHub (looks better on resume, shows PR history)
git push origin feature/phase-2-person-generator
# → open PR on GitHub: feature/phase-2-person-generator → dev

# Clean up the feature branch after merge
git branch -d feature/phase-2-person-generator
git push origin --delete feature/phase-2-person-generator
```

### Releasing a phase (merging dev → main)

```bash
git checkout main
git merge --no-ff dev -m "chore: release Phase 2 — Synthetic Data Engine"
git tag -a v0.2.0 -m "Phase 2: Synthetic Data Engine complete"
git push origin main --tags
```

### Emergency hotfix

```bash
git checkout main
git checkout -b hotfix/fix-cors-header
# ... fix it ...
git commit -m "fix(cors): add missing allow-headers for Authorization"

# Merge into main
git checkout main
git merge --no-ff hotfix/fix-cors-header -m "fix: merge CORS hotfix"
git tag -a v0.1.1 -m "Hotfix: CORS header"
git push origin main --tags

# Also merge into dev so the fix isn't lost
git checkout dev
git merge --no-ff hotfix/fix-cors-header -m "fix: backport CORS hotfix to dev"
git push origin dev
git branch -d hotfix/fix-cors-header
```

---

## Version Tagging Scheme

```
v<MAJOR>.<MINOR>.<PATCH>

MAJOR = 0 during development (pre-release)
MINOR = increments at each completed phase
PATCH = increments for hotfixes
```

| Tag | Meaning |
|-----|---------|
| `v0.0.1` | Phase 0: docs and repo skeleton |
| `v0.1.0` | Phase 1: core setup complete |
| `v0.2.0` | Phase 2: data gen engine complete |
| `v0.3.0` | Phase 3: graph + anomaly detection |
| `v0.4.0` | Phase 4: full dashboard integration |
| `v0.5.0` | Phase 5: optimisation complete |
| `v0.6.0` | Phase 6: tests + hardening |
| `v0.7.0` | Phase 7: deployed to production |
| `v1.0.0` | Phase 8: fully documented, resume-ready |

---

## `.gitignore` Essentials

```gitignore
# Python
__pycache__/
*.pyc
.venv/
*.egg-info/

# Environment
.env
*.env.local

# Node
node_modules/
dist/
.vite/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Alembic
alembic/versions/*.pyc

# Test coverage
htmlcov/
.coverage
coverage.xml

# Docker
docker-compose.override.yml
```

---

*Keep Git history clean. Future you (and hiring managers viewing your GitHub) will thank you.*
