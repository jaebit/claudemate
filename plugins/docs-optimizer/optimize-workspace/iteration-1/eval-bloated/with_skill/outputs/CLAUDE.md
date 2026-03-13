# CLAUDE.md

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

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string |
| REDIS_URL | Yes | Redis connection string |
| JWT_SECRET | Yes | Secret for JWT signing |
| AWS_ACCESS_KEY_ID | Yes | AWS credentials |
| AWS_SECRET_ACCESS_KEY | Yes | AWS credentials |
| SENTRY_DSN | No | Sentry error tracking |

## Constraints

- **NEVER** commit .env files or secrets to the repository
- **NEVER** use `any` type in TypeScript without explicit justification
- **ALWAYS** run `npm test` before pushing
- **ALWAYS** update types when modifying API contracts
- Database migrations must be backward-compatible (no column drops without deprecation)
- API calls go through `services/api.ts` client
- Squash merge to `main`; use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)

## References

- API schema: See `prisma/schema.prisma`
