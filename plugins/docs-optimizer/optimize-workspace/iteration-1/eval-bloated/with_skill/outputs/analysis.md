# Optimization Analysis: bloated-CLAUDE.md

## Step 1: SCAN

- **Total lines:** 182
- **Sections:** 12

| Section | Line Range | Lines |
|---------|-----------|-------|
| Project Overview | 3-5 | 3 |
| Tech Stack | 7-13 | 7 |
| Directory Structure | 15-49 | 35 |
| API Schema | 51-79 | 29 |
| Operational Commands | 81-102 | 22 |
| Coding Conventions | 104-110 | 7 |
| Error Handling | 112-125 | 14 |
| Component Inventory | 127-143 | 17 |
| Git Workflow | 145-151 | 7 |
| Versioning & Changelog | 153-163 | 11 |
| Environment Variables | 165-175 | 11 |
| Golden Rules | 177-182 | 6 |

## Step 2: CLASSIFY

| Section | Lines | Classification | Reason |
|---------|-------|----------------|--------|
| Project Overview | 3 | NEUTRAL | README duplicate; project context discoverable from README.md |
| Tech Stack | 7 | NEUTRAL | Discoverable from package.json/tsconfig/prisma schema |
| Directory Structure | 35 | HARMFUL | Static tree goes stale; agent discovers via Glob/LS |
| API Schema | 29 | HARMFUL | Full field listings already in Prisma schema source code |
| Operational Commands | 22 | HIGH-VALUE | Exact CLI invocations the agent cannot infer |
| Coding Conventions | 7 | MIXED | Line 110 (API calls through services/api.ts) is repo-specific; rest is general patterns the LLM knows |
| Error Handling | 14 | HARMFUL | General coding pattern; error format is in source code |
| Component Inventory | 17 | HARMFUL | File-by-file descriptions; auto-discoverable via Glob |
| Git Workflow | 7 | NEUTRAL | Standard conventions; aspirational guidelines |
| Versioning & Changelog | 11 | NEUTRAL | Maintenance policy; standard semver format |
| Environment Variables | 11 | HIGH-VALUE | Repo-specific env config the agent needs for setup |
| Golden Rules | 6 | HIGH-VALUE | Immutable project constraints |

## Step 3: PLAN

| Section | Strategy | Target | Expected Lines |
|---------|----------|--------|----------------|
| Project Overview | Delete | - | 0 |
| Tech Stack | Delete | - | 0 |
| Directory Structure | Delete | - | 0 |
| API Schema | Pointer | See prisma/schema.prisma | 1 |
| Operational Commands | Keep | - | 22 |
| Coding Conventions | Merge | Fold repo-specific rule into Constraints | 0 (merged) |
| Error Handling | Delete | - | 0 |
| Component Inventory | Delete | - | 0 |
| Git Workflow | Merge | Fold into Constraints (1 unique rule: squash merge) | 0 (merged) |
| Versioning & Changelog | Delete | - | 0 |
| Environment Variables | Keep | - | 11 |
| Golden Rules | Merge | Consolidate into Constraints with Coding Conventions rules | ~10 |

**Expected final line count:** ~48 lines

## Step 5: VERIFY

- Before: 182 lines
- After: 49 lines
- Reduction: 73%
