# Multi-Agent Social Media AI Agency Architecture

## System Overview & Agent Organization

The application implements a discrete multi-agent architecture where specialized AI agents cooperate, review work, enforce compliance guardrails, and execute closed-loop analytics improvement.

```
                              ┌─────────────────────────────────────────┐
                              │            HUMAN OPERATOR               │
                              │    (Campaign Brief & Approval Gate)     │
                              └────────────────────┬────────────────────┘
                                                   │ Human Brief
                                                   ▼
                              ┌─────────────────────────────────────────┐
                              │         ORCHESTRATOR AGENT              │
                              │  (Decomposes work, manages state/bus)   │
                              └───────┬─────────────────────────▲───────┘
                                      │                         │ Recommendations
                                      ▼                         │
                             ┌──────────────────┐               │
                             │  STRATEGY AGENT  ├───────────────┤ (Week 2 Loop)
                             └────────┬─────────┘               │
                                      │ Strategy                │
                                      ▼                         │
┌──────────────────┐         ┌──────────────────┐       ┌───────┴──────────┐
│  CREATIVE AGENT  │◄────────┤  CONTENT AGENT   ├──────►│ ANALYTICS AGENT  │
└────────┬─────────┘ Visuals └────────┬─────────┘ Copy  └───────▲──────────┘
         │                            │                         │
         └─────────────┬──────────────┘                         │ Metrics & Comments
                       ▼                                        │
             ┌──────────────────┐                               │
             │ COMPLIANCE AGENT │ (Rejection loop max 3x)       │
             └────────┬─────────┘                               │
                      │ Approved Posts                          │
                      ▼                                         │
             ┌──────────────────┐                               │
             │ HUMAN APPROVAL   │ (Mandatory Gate)              │
             └────────┬─────────┘                               │
                      │ Approved                                │
                      ▼                                         │
             ┌──────────────────┐       ┌──────────────────┐    │
             │ SCHEDULER AGENT  ├──────►│  MOCK PLATFORM   ├────┘
             └──────────────────┘ Posts │    SIMULATOR     │
                                        └────────┬─────────┘
                                                 │ Comments
                                                 ▼
                                        ┌──────────────────┐
                                        │COMMUNITY MANAGER │
                                        └──────────────────┘
```

## Agent Responsibilities & Contracts

1. **Orchestrator Agent / Chief of Staff**: Parses human brief, decomposes tasks, manages state transitions, enforces maximum 3-strike compliance revision loops, and routes Week 1 analytics recommendations to Strategy for Week 2.
2. **Strategy Agent**: Formulates target audience persona, channel mix, posting cadence, content pillars, KPIs, and strategic hypotheses.
3. **Content Writer Agent**: Writes platform-tailored post copy for Pulse, Forum, and ProNet.
4. **Creative Agent**: Produces visual and creative briefs (scene composition, visual hook, asset type, on-screen text).
5. **Brand & Compliance Agent**: Audits copy & visuals for brand tone, prohibited guarantee claims, over-promising, and legal safety.
6. **Scheduler / Publisher Agent**: Arranges approved posts into optimal channel time slots.
7. **Community Manager Agent**: Scans comments, classifies sentiment, drafts replies, and escalates sensitive safety/legal inquiries.
8. **Analytics Agent**: Evaluates simulated post metrics at week-end, discovers hidden patterns, and outputs evidence-backed recommendations for Week 2.

## Local Model Layer

- **LLM Runtime**: Ollama running locally at `http://localhost:11434`.
- **Target Model**: `gemma3:4b` (Parameter size: 4.3B, Quantization: Q4_K_M).
- **Zero Hosted APIs**: Absolutely no external LLM APIs (OpenAI, Anthropic, Gemini, Groq) are used.
- **Validation & Retries**: `generate_json` uses Pydantic schema validation + prompt repair retries (up to 3 attempts) on malformed output.
