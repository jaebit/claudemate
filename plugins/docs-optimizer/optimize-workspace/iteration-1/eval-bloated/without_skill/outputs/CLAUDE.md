# CLAUDE.md

## Tech Stack

- **Frontend:** React 18, TypeScript 5.3, Tailwind CSS 3.4, Vite 5
- **Backend:** Node.js 20, Express 4, Prisma ORM
- **Database:** PostgreSQL 15, Redis 7
- **Testing:** Jest 29, React Testing Library, Playwright

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

- TypeScript strict mode; avoid `any` without explicit justification
- Functional components only (no class components)
- Use `const` by default, `let` only when reassignment is needed
- Error boundaries around all route-level components
- API calls go through `services/api.ts`

## Error Handling

API error response format:
```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested resource does not exist",
    "details": {}
  }
}
```

Use try-catch around all async operations. Structured logging via Winston. Never expose stack traces in production.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| REDIS_URL | Yes | Redis connection string |
| JWT_SECRET | Yes | Secret for JWT signing |
| AWS_ACCESS_KEY_ID | Yes | AWS credentials |
| AWS_SECRET_ACCESS_KEY | Yes | AWS credentials |
| SENTRY_DSN | No | Sentry error tracking |

## Git Workflow

- Feature branches from `main`, conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- Squash merge to main; delete branch after merge; tag releases with semver
- Update CHANGELOG.md for all user-facing changes before merge

## Golden Rules

- **NEVER** commit .env files or secrets
- **ALWAYS** run `npm test` before pushing
- **ALWAYS** update types when modifying API contracts
- Database migrations must be backward-compatible (no column drops without deprecation)
