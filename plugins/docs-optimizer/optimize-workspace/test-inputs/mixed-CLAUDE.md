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

## Architecture

This is a Rust-based event processing pipeline. Events flow through:

1. **Ingestion** (src/ingest/) - HTTP + Kafka consumers
2. **Validation** (src/validate/) - Schema validation + dedup
3. **Transform** (src/transform/) - Enrichment + normalization
4. **Sink** (src/sink/) - ClickHouse + S3 output

## Project Context

This project was originally written in Python but migrated to Rust for performance. The Python version is archived at `legacy/python-pipeline/`. Some team members are still learning Rust, so keep code idiomatic but not overly clever.

## Key Files

- `src/ingest/kafka.rs` - Kafka consumer with backpressure handling
- `src/ingest/http.rs` - HTTP endpoint for direct event submission
- `src/validate/schema.rs` - JSON Schema validation engine
- `src/transform/enricher.rs` - GeoIP and user-agent enrichment
- `src/sink/clickhouse.rs` - ClickHouse batch writer
- `src/sink/s3.rs` - S3 parquet file writer
- `src/config.rs` - Configuration loading from env/file
- `src/metrics.rs` - Prometheus metrics exposition

## Constraints

- Maximum event processing latency: 50ms p99
- Batch size for ClickHouse: 10,000 events or 5 seconds
- S3 files must be partitioned by date: `s3://bucket/year=YYYY/month=MM/day=DD/`
- All public API types must derive `Serialize`, `Deserialize`, `Debug`, `Clone`
- No unwrap() in production code paths — use proper error handling with `thiserror`

## Dependencies

- `tokio` 1.35 - Async runtime
- `rdkafka` 0.36 - Kafka client
- `clickhouse` 0.11 - ClickHouse client
- `axum` 0.7 - HTTP framework
- `serde` 1.0 - Serialization
- `tracing` 0.1 - Structured logging

## REST API Conventions

All endpoints follow standard REST patterns:
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes
- Use JSON for request/response bodies
- Include pagination for list endpoints
- Use query parameters for filtering

## CI/CD

Pipeline runs on every PR:
1. `cargo fmt --check`
2. `cargo clippy -- -D warnings`
3. `cargo test`
4. `cargo build --release`
5. Docker image build + push (main branch only)
6. Deploy to staging (main branch only)

## Monitoring

- Prometheus metrics at `/metrics`
- Grafana dashboard: `https://grafana.internal/d/pipeline-overview`
- PagerDuty integration for critical alerts
- Log aggregation in Datadog
