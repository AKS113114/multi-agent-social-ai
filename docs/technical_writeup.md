# Technical Writeup: Multi-Agent Social Media AI Company

## Executive Summary
This project implements an autonomous, local multi-agent social media agency system designed to operate **100% locally** using Ollama with model `gemma3:4b`. The system features 8 specialized agents, a 3-channel mock social platform with hidden engagement signals, automated audience comment generation, closed-loop analytics recommendations, and strict human approval and compliance gates.

---

## 1. System Architecture & Agent Roles

```
                           +---------------------------+
                           |  Human Brief / Operator   |
                           +-------------+-------------+
                                         |
                                         v
                           +-------------+-------------+
                           |    Orchestrator Agent     |
                           +-------------+-------------+
                                         |
               +-------------------------+-------------------------+
               |                         |                         |
               v                         v                         v
     +---------+-------+       +---------+-------+       +---------+-------+
     | Strategy Agent  | ----> |  Content Agent  | ----> | Creative Agent  |
     +-----------------+       +---------+-------+       +---------+-------+
                                         |                         |
                                         +------------+------------+
                                                      |
                                                      v
                                           +----------+----------+
                                           |  Compliance Agent   |
                                           +----------+----------+
                                                      |
                                             (Auto Rejection /
                                              Max 3 Retries)
                                                      |
                                                      v
                                           +----------+----------+
                                           | Human Approval Gate |
                                           +----------+----------+
                                                      |
                                                      v
                                           +----------+----------+
                                           |   Scheduler Agent   |
                                           +----------+----------+
                                                      |
                                                      v
                                           +----------+----------+
                                           | Mock Social Platform|
                                           | (Pulse, Forum,      |
                                           |  ProNet + Signals)  |
                                           +----------+----------+
                                                      |
                                         +------------+------------+
                                         |                         |
                                         v                         v
                               +---------+-------+       +---------+-------+
                               |    Community    |       | Analytics Agent |
                               |  Manager Agent  |       +---------+-------+
                               +-----------------+                 |
                                                                   | (Week 1 Recs)
                                                                   v
                                                         +---------+-------+
                                                         | Strategy Agent  |
                                                         |    (Week 2)     |
                                                         +-----------------+
```

### Agent Roles & Specifications:
1. **Orchestrator Agent**: Chief of Staff governing campaign lifecycle, state transitions (`DRAFT` → `AGENT_REVIEW` → `COMPLIANCE` → `HUMAN_REVIEW` → `APPROVED` → `SCHEDULED` → `PUBLISHED` → `ANALYZING` → `IMPROVEMENT`), and message routing.
2. **Strategy Agent**: Translates natural language human briefs into target demographics, content pillars, channel selections, 3-post demo weekly publishing cadences, KPIs, and strategic hypotheses.
3. **Content Agent**: Writes platform-tailored post copy for `Pulse` (short video captions <60w), `Forum` (conversational Q&A), and `ProNet` (polished B2B insights).
4. **Creative Agent**: Produces visual graphic concepts, scene compositions, on-screen text, and brand direction notes.
5. **Compliance Agent**: Pre-audits copy against legal, false-claim ("100% guarantee"), and brand safety guidelines. Auto-rejects violations and enforces a maximum 3-attempt revision cap before escalating to `ESCALATED_HUMAN`.
6. **Scheduler Agent**: Maps optimized posting timestamps per channel (`Pulse`: 18:00, `Forum`: 14:00, `ProNet`: 09:00).
7. **Community Manager Agent**: Scans audience comments, classifies sentiment (`positive`, `question`, `complaint`, `sensitive`), drafts public replies, and escalates sensitive safety/legal issues.
8. **Analytics Agent**: Evaluates campaign performance metrics, identifies top/bottom post drivers, and outputs structured evidence-backed recommendations (`observation`, `evidence`, `hypothesis`, `confidence`, `recommendation`) using strict metric alignment and within-channel comparisons.

---

## 2. Deterministic Engagement Simulator (7 Hidden Signals)

The simulator evaluates published posts using 7 deterministic mathematical formulas + controlled 5% uniform noise ($\epsilon \sim [-0.05, 0.05]$):

1. **Channel Peak Window Boost**: $+35\%$ boost if post scheduled hour aligns with channel peak hours.
2. **Question CTA Boost**: $+25\%$ comment rate boost on `Forum` if copy ends with `?`.
3. **Pulse Length Penalty**: $-30\%$ reach penalty on `Pulse` if word count $> 60$ words.
4. **Tone Alignment**: $+20\%$ boost if post tone matches channel target style.
5. **Hashtag Non-Linear Scaling**: Peak multiplier at 3 hashtags ($1.25\times$), penalty if $> 4$ hashtags ($0.7\times$).
6. **Format Novelty Decay**: $1.0\times$ for post 1, $0.85\times$ for post 2, $0.70\times$ for post 3+.
7. **Pillar-Audience Fit**: $+15\%$ engagement boost if pillar matches audience preference.

---

## 3. Closed-Loop Feedback Engine (Week 1 → Week 2)

```
[Week 1 Execution] ---> [Week 1 Analytics Report]
                                |
                                v
               [Structured 5-Field Recommendations]
                (observation, evidence, hypothesis,
                 confidence, recommendation)
                                |
                                v
                   [Strategy Agent (Week 2)]
                                |
                                v
               [Revised Week 2 Strategy & Cadence]
                                |
                                v
                 [Week 2 Content & Simulation]
                                |
                                v
              [Week 1 vs Week 2 Metric Comparison]
```

---

## 4. Local Execution & Zero Hosted LLM Guarantee
- **Model**: `gemma3:4b` running on local Ollama server at `http://localhost:11434`.
- **Zero External APIs**: Audited repository contains **zero** dependencies on OpenAI, Anthropic, Gemini, Groq, or any other hosted API.
- **Pydantic Validation**: Uses native Ollama JSON mode + automatic schema validation and repair retries via `parse_and_validate`.
