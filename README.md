# Measuring and Forecasting AI Agents

A SaaS company's tenants run AI agents, and every agent run produces telemetry: the model used, tokens in and out, tool calls, latency, cost and outcome.

Product teams need trustworthy answers to questions such as "What is tenant ABC's agent success rate this week?" and "How many tokens will they use next month?"

Tenants must never see each other's raw data (Tier 0), while the company can publish anonymised cross-tenant benchmarks (Tier 1).

# Architecture

```  
Tenant agents / simulator (tenants A, B, C ...)
                 |
                 | JSON over HTTPS + tenant token
                 v
  +----------------------------+         +----------------------------+
  | Ingest gateway             |<------->| Schema Registry            |
  | validate, serialize Avro   |         | compatibility: BACKWARD    |
  | rejects -> DLQ topic       |         | (register / look up)       |
  +----------------------------+         +----------------------------+
                 |
                 | Avro: event_id, tenant_id, tier, event_time ...
                 v
  +----------------------------+
  | Kafka (Redpanda)           |
  | agent.runs.v1              |
  |   key = tenant_id          |
  | agent.runs.dlq (rejects)   |
  +----------------------------+
                 |
                 v
  +----------------------------+         +----------------------------+
  | Flink (streaming)          |         | Spark (batch)              |
  | dedup, windows, late data  |         | backfill, compaction,      |
  | Avro decode via registry   |         | forecast jobs              |
  +----------------------------+         +----------------------------+
                 |                               ^             |
                 | append                        | read        | write
                 v                               |             v
  +-------------------------------------------------------------------+
  | Lakehouse: object store + Iceberg REST catalog                    |
  |                                                                   |
  | dbt models + tests (run via Trino):  bronze --> silver --> gold   |
  |                                                                   |
  | tier0.* (tenanted) --> promotion job --> tier1.* (aggregated)     |
  |                        k >= 10, no tenant ids                     |
  +-------------------------------------------------------------------+
                                    |
                                    v
  +-------------------------------------------------------------------+
  | Trino (SQL engine)                                                |
  | row filter: tenant_id = session principal                [wall 2] |
  +-------------------------------------------------------------------+
                                    |
                                    v
  +-------------------------------------------------------------------+
  | Semantic layer: MetricFlow (compare with Cube)                    |
  | metrics defined once, compiled to SQL                             |
  +-------------------------------------------------------------------+
                                    |
                                    v
  +-------------------------------------------------------------------+
  | Metrics service: gRPC + REST (hexagonal)                          |
  | Keycloak OIDC (authN) -> OpenFGA (authZ)                 [wall 1] |
  | queries Trino as the tenant principal                             |
  +-------------------------------------------------------------------+
                 |                                      |
                 v                                      v
  +----------------------------+         +----------------------------+
  | Dashboards                 |         | MCP server                 |
  | (business metrics)         |         | -> AI agents               |
  +----------------------------+         +----------------------------+

  Cross-cutting: Git + GitHub Actions gates | OpenBao secrets/keys
                 OpenTelemetry + Grafana LGTM | k3s + Helm + Argo CD
```
Wall 1 and Wall 2 mark the two independent tenant-isolation layers one in the metrics service, one in Trino.

