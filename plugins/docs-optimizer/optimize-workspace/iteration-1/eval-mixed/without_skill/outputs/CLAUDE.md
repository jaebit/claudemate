# CLAUDE.md

## Build & Test

```bash
cargo build --release
cargo build --features experimental
cargo test                    # All tests
cargo test --lib              # Unit tests only
cargo test integration_       # Integration tests
cargo clippy -- -D warnings
cargo fmt --check
```

## Architecture

Rust-based event processing pipeline. Flow: **Ingestion** (`src/ingest/`) → **Validation** (`src/validate/`) → **Transform** (`src/transform/`) → **Sink** (`src/sink/` — ClickHouse + S3).

Key files: `src/config.rs` (env/file config), `src/metrics.rs` (Prometheus at `/metrics`).

## Constraints

- No `unwrap()` in production code — use `thiserror` for error handling
- All public API types must derive `Serialize`, `Deserialize`, `Debug`, `Clone`
- Max event processing latency: 50ms p99
- ClickHouse batch size: 10,000 events or 5 seconds
- S3 partitioning: `s3://bucket/year=YYYY/month=MM/day=DD/`
- Keep code idiomatic but not overly clever (mixed Rust experience on team)

## CI/CD

PR pipeline: `fmt --check` → `clippy` → `test` → `build --release`. Main branch additionally builds/pushes Docker image and deploys to staging.
