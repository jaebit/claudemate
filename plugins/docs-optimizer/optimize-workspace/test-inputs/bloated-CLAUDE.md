# CLAUDE.md

## Project Overview

This is a modern web application built with React, TypeScript, and Node.js. It provides a comprehensive dashboard for monitoring and managing cloud infrastructure resources. The project follows clean architecture principles and uses domain-driven design patterns throughout.

## Tech Stack

- **Frontend:** React 18, TypeScript 5.3, Tailwind CSS 3.4, Vite 5
- **Backend:** Node.js 20, Express 4, Prisma ORM
- **Database:** PostgreSQL 15, Redis 7
- **Testing:** Jest 29, React Testing Library, Playwright
- **CI/CD:** GitHub Actions, Docker, AWS ECS

## Directory Structure

```
src/
├── components/
│   ├── common/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   └── Tooltip.tsx
│   ├── dashboard/
│   │   ├── MetricsPanel.tsx
│   │   ├── AlertsWidget.tsx
│   │   └── ResourceGraph.tsx
│   └── settings/
│       ├── ProfileForm.tsx
│       └── TeamSettings.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useFetch.ts
│   └── useWebSocket.ts
├── services/
│   ├── api.ts
│   ├── auth.ts
│   └── websocket.ts
├── utils/
│   ├── formatters.ts
│   ├── validators.ts
│   └── constants.ts
└── types/
    ├── api.d.ts
    ├── models.d.ts
    └── config.d.ts
```

## API Schema

### User Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| email | string | Yes | User email address |
| name | string | Yes | Display name |
| role | enum | Yes | admin, editor, viewer |
| avatar_url | string | No | Profile image URL |
| created_at | timestamp | Yes | Account creation time |
| updated_at | timestamp | Yes | Last modification time |
| last_login | timestamp | No | Most recent login |
| preferences | jsonb | No | User settings blob |

### Resource Model

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Primary key |
| name | string | Yes | Resource name |
| type | enum | Yes | ec2, rds, s3, lambda |
| region | string | Yes | AWS region |
| status | enum | Yes | running, stopped, error |
| cost_per_hour | decimal | Yes | Hourly cost in USD |
| tags | jsonb | No | Key-value tags |
| metrics | jsonb | No | Latest metrics snapshot |
| owner_id | UUID | Yes | FK to User |

## Operational Commands

```bash
# Development
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
npm run typecheck    # TypeScript type checking

# Testing
npm test             # Run unit tests
npm run test:e2e     # Run Playwright e2e tests
npm run test:cov     # Coverage report

# Database
npx prisma migrate dev    # Run migrations
npx prisma studio         # Open Prisma Studio
npx prisma db seed        # Seed development data

# Deployment
./scripts/deploy.sh staging    # Deploy to staging
./scripts/deploy.sh production # Deploy to production (requires approval)
```

## Coding Conventions

- Use TypeScript strict mode
- All components must be functional (no class components)
- Use `const` by default, `let` only when reassignment is needed
- Error boundaries around all route-level components
- API calls go through the `services/api.ts` client

## Error Handling

All API endpoints should return errors in this format:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource does not exist",
    "details": {}
  }
}
```

Use try-catch blocks around all async operations. Log errors with structured logging using Winston. Never expose stack traces in production responses.

## Component Inventory

### Common Components
- **Button** - Standard button with variants (primary, secondary, danger, ghost)
- **Card** - Content container with optional header and footer
- **Modal** - Dialog overlay with focus trapping and ESC to close
- **Table** - Data table with sorting, pagination, and row selection
- **Tooltip** - Hover tooltip with configurable placement

### Dashboard Components
- **MetricsPanel** - Displays key metrics in a grid layout with sparklines
- **AlertsWidget** - Shows recent alerts with severity indicators
- **ResourceGraph** - Interactive graph visualization of resource relationships

### Settings Components
- **ProfileForm** - User profile editing form with avatar upload
- **TeamSettings** - Team management with role assignment

## Git Workflow

- Create feature branches from `main`
- Use conventional commits: `feat:`, `fix:`, `docs:`, `chore:`
- Squash merge to main
- Delete branch after merge
- Tag releases with semver

## Versioning & Changelog

We follow semantic versioning. All user-facing changes must be documented in CHANGELOG.md before merge. Use the format:

```
## [1.2.3] - 2024-01-15
### Added
- New feature description
### Fixed
- Bug fix description
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| REDIS_URL | Yes | Redis connection string |
| JWT_SECRET | Yes | Secret for JWT signing |
| AWS_ACCESS_KEY_ID | Yes | AWS credentials |
| AWS_SECRET_ACCESS_KEY | Yes | AWS credentials |
| SENTRY_DSN | No | Sentry error tracking |

## Golden Rules

- **NEVER** commit .env files or secrets to the repository
- **NEVER** use `any` type in TypeScript without explicit justification
- **ALWAYS** run `npm test` before pushing
- **ALWAYS** update types when modifying API contracts
- Database migrations must be backward-compatible (no column drops without deprecation)
