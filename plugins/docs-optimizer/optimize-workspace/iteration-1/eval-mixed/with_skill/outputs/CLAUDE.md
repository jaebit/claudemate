# CLAUDE.md

## Build & Test

```bash
# Build
cargo build --release
cargo build --features experimental

# Test
cargo test                    # All tests
cargo test --lib              # Unit tests only
cargo test integration_       # Integration tests
RUST_LOG=debug cargo test     # With debug logging

# Lint
cargo clippy -- -D warnings
cargo fmt --check
```

## Constraints

- Maximum event processing latency: 50ms p99
- Batch size for ClickHouse: 10,000 events or 5 seconds
- S3 files must be partitioned by date: `s3://bucket/year=YYYY/month=MM/day=DD/`
- All public API types must derive `Serialize`, `Deserialize`, `Debug`, `Clone`
- No unwrap() in production code paths — use proper error handling with `thiserror`

## CI/CD

Pipeline runs on every PR:
1. `cargo fmt --check`
2. `cargo clippy -- -D warnings`
3. `cargo test`
4. `cargo build --release`
5. Docker image build + push (main branch only)
6. Deploy to staging (main branch only)

## Architecture

Rust event processing pipeline: Ingestion (HTTP + Kafka) -> Validation -> Transform -> Sink (ClickHouse + S3).

## Dependencies

See `Cargo.toml` for full dependency list.

## Monitoring

- Prometheus metrics at `/metrics`
- Grafana dashboard: `https://grafana.internal/d/pipeline-overview`
