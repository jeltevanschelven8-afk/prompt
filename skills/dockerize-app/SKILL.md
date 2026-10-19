---
name: dockerize-app
description: >-
  Containerise an existing application with a small, secure Dockerfile (multi-stage build, pinned base
  image, non-root user, healthcheck), a .dockerignore and a docker compose file for local development.
  Use this skill whenever the user wants to "dockerize", "containerize", "put this in Docker", "write a
  Dockerfile", "make the image smaller", "add docker compose", or asks why their image is huge or runs
  as root. Also trigger for Dutch requests like "zet mijn app in een container", "maak een Dockerfile"
  or "mijn docker image is te groot". Works for Node, Python, Go, Java and .NET projects.
license: "MIT"
metadata:
  author: "prompt"
  category: "devops"
  tags: "docker, dockerfile, compose, container, multi-stage, devops, containeriseren, image"
  version: "1.0.0"
  summary_nl: "Zet je app in een kleine, veilige Docker-container met multi-stage build, non-root gebruiker en compose voor lokaal."
---

# Dockerize app

A good container image is small (fast to pull, less to patch), runs as an unprivileged user (a
compromise stays contained), and starts the same way everywhere. This skill inspects the project and
writes a Dockerfile, a .dockerignore and a compose file that fit it, instead of pasting a generic
template.

## Workflow

### 1. Inspect the project

Find out, from files rather than assumptions:

- Language and version: `package.json` engines, `.nvmrc`, `pyproject.toml`, `go.mod`, `*.csproj`.
- Lockfile: `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `go.sum`.
- How it builds and starts: scripts in `package.json`, a `Procfile`, `main.py`, the README.
- Port, required environment variables, writable paths, and services it talks to (database, cache).

Ask about anything that cannot be found, especially the port and which environment variables are
required at runtime.

### 2. Write a multi-stage Dockerfile

Build tools and dev dependencies stay in the build stage; only the runtime artefacts are copied to the
final stage. Copy dependency manifests before source code so the dependency layer stays cached when
only code changes. Example for Node:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM deps AS build
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22-alpine AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
COPY --chown=node:node package.json ./
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

Adapt the pattern: `python:3.12-slim` with a virtualenv copied across, Go with a static binary on
`gcr.io/distroless/static` or `scratch`, .NET with the `aspnet` runtime image. Pin at least the major
and minor version of the base image so builds are reproducible; mention digest pinning for production.

Use the exec form of `CMD` (JSON array) so the process receives stop signals and shuts down cleanly.
If the app has no health endpoint, suggest adding one or use a check that fits (a TCP probe, a CLI
command) and say which.

### 3. Write the .dockerignore

It keeps the build context small and stops secrets from ending up in a layer:

```text
.git
node_modules
dist
.env
.env.*
*.log
coverage
Dockerfile*
docker-compose*.yml
```

### 4. Write compose.yaml for local development

Mount the source for hot reload, load settings from an untracked `.env`, and add the services the
app needs with a healthcheck so startup order is reliable:

```yaml
services:
  app:
    build: { context: ., target: build }
    command: npm run dev
    ports: ["3000:3000"]
    env_file: .env
    volumes: [".:/app", "/app/node_modules"]
    depends_on:
      db: { condition: service_healthy }
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: app
      POSTGRES_PASSWORD_FILE: /run/secrets/db_pw
    secrets: [db_pw]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
    volumes: [dbdata:/var/lib/postgresql/data]
secrets:
  db_pw: { file: ./db_pw.txt }
volumes:
  dbdata:
```

Keep real credentials out of the Dockerfile and compose file; reference `.env` or secret files that
are listed in `.gitignore`, and add a `.env.example` hint in the summary.

### 5. Build and check

If Docker is available, run and report the actual results:

```bash
docker build -t myapp .
docker image ls myapp            # report the size
docker run --rm -p 3000:3000 myapp
docker inspect --format '{{.State.Health.Status}}' <container>
```

If Docker is not available, say the files are untested and give the user these commands.

## Output format

1. Short summary: base image, final image size (measured or "not built yet"), user, port, healthcheck.
2. The files: `Dockerfile`, `.dockerignore`, `compose.yaml`, with one comment line per non-obvious step.
3. How to run: `docker compose up --build` for dev, `docker build` plus `docker run` for production.
4. Follow-ups worth considering, e.g. image scanning with `docker scout cves` or Trivy.

## Pitfalls

- Alpine uses musl; native Python or Node modules sometimes break. Switch to `-slim` when builds fail.
- `npm install` instead of `npm ci` makes builds non-reproducible.
- Files written at runtime need a directory owned by the non-root user.
- Do not bake `.env` files or cloud credentials into the image; they are readable in every layer.
- Ask before overwriting an existing Dockerfile; show a diff of the proposed changes instead.

## Scope

This skill is about building and running images locally. Kubernetes manifests, cloud deployment and
registry setup are out of scope; publishing images from CI fits with github-actions-ci.
