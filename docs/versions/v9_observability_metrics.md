# V9 - Observability + Metrics

## Version Goal
V9 adds the observability layer for InsightAgent.

The target flow is:
- trace each API request with a request id
- carry useful context through agent and tool flows
- log endpoint, status, latency, session id, tool usage, token/cost metadata where available
- categorize errors
- summarize runtime logs into metrics
- document the request lifecycle and observability proof

## Current Progress

Status: started.

This first V9 chunk creates the version boundary and documentation scaffold. Runtime tracing and metrics behavior will be implemented in small follow-up chunks.

## Planned Scope

From the V9 checklist, the version should cover:
- request tracing across API -> agent -> tool
- request id logging everywhere practical
- endpoint and status tracking
- session id tracking where available
- tool used and tool status tracking
- latency tracking
- token/cost tracking where available
- tool usage frequency and success/failure tracking
- error categorization
- metrics summary script
- log format documentation
- request lifecycle trace example
- README observability section

## Initial Version Boundary

Updated:
- app version default to `v9`
- `.env.example` to `APP_VERSION=v9`
- health endpoint test expectation to `v9`
- README current version and V9 docs link

## Deferred To Follow-Up Chunks

Not implemented in this scaffold chunk:
- runtime request tracing changes
- structured log schema updates
- metrics summary script
- observability README proof
- request lifecycle trace examples

## Testing Status

The scaffold will be verified through:
- focused health endpoint test
- full test suite

## Interview Explanation
In V9, I started the observability layer by creating the version boundary and documentation scaffold. This prepares the project to add request-level tracing, structured runtime logs, tool and error metrics, token/cost visibility, and a metrics summary workflow without mixing observability work into the completed V8 evaluation layer.
