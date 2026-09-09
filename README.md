# EQ Agent Kit (showcase excerpt)

A Python SDK for building LLM-backed conversational agents, extracted from a larger private agent
platform I designed and built. This repo shows the **infrastructure and integration layers** — how
the SDK talks to LLM providers, structures agent output, tracks operational metrics, and stays
extensible via plugins — as a demonstration of engineering style and system design.

This is a curated excerpt, not the full package: some modules import internals that live in the
private codebase, so this repo is for reading, not running.

## What's included here

- **`llm/`** — a provider-agnostic LLM client abstraction (`base.py`, `registry.py`) with an
  OpenAI-compatible implementation, so the agent runtime can swap model providers without touching
  call sites.
- **`plugins/`** — a plugin system (`base.py`, `manager.py`, `registry.py`) for extending agent
  behavior without modifying core code.
- **`metrics/`** — collection and aggregation of runtime/system metrics (`collector.py`,
  `aggregator.py`, `system_metrics.py`) for observability into a running agent.
- **`parsers/structured_output_parser.py`** — parsing and validating structured (JSON-schema-shaped)
  output from LLM responses.
- **`cli/`** — the CLI layer for setup and interactive use (setup wizard, interactive session runner).

## What was built but isn't shown here

The full private SDK includes several subsystems that are the actual product differentiator and are
intentionally withheld from this showcase:

- A **synthetic intelligence framework** — a consciousness/motivation model with curiosity-driven
  exploration, implemented as a distinct reasoning layer above the base LLM calls.
- A **GraphRAG-based long-term memory system** — hierarchical memory with graph-backed retrieval,
  not a simple vector store.
- An **emotional intelligence layer** — arousal modeling, "wonder"/novelty scoring, and breakthrough
  detection that shapes agent responses in real time.
- **Belief and goal modeling** — agents that track and update internal beliefs and goals across a
  conversation, not just a fixed system prompt.
- **Core orchestration** (personality composition, mode switching, multi-agent coordination) tying
  all of the above together.

I'm happy to walk through the design of any of these in conversation — they're just not published
as code.

## Stack

Python, structured around a plugin architecture, LLM-provider abstraction, and a CLI-driven setup
flow.
