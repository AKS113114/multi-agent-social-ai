# Multi-Agent Social Media AI Company

[![Live Web App](https://img.shields.io/badge/Live%20Demo-https%3A%2F%2Fmulti--agent--social--ai--1.onrender.com-brightgreen?style=for-the-badge&logo=render)](https://multi-agent-social-ai-1.onrender.com)

> 🚀 **Live Public URL**: [https://multi-agent-social-ai-1.onrender.com](https://multi-agent-social-ai-1.onrender.com)
> 
> # Demo Video

[![LIVE DEMO](https://img.shields.io/badge/LIVE%20DEMO-20C900?style=for-the-badge&logo=googlechrome&logoColor=white)](https://drive.google.com/file/d/1cvQcIwY4g7WJzck2ddPJZ3vMkIQAjCAw/view?usp=drive_link)
>
> **Prodigal AI Intern Hiring — Round 1 Task 1 Submission**
> A multi-agent AI social media company running on Ollama (`gemma4:cloud` / `gemma3:4b`), featuring 8 specialized agents, compliance guardrails, human approval gate, 3-channel mock social platform with hidden signals, community manager, and a closed-loop weekly analytics improvement engine.

---

## 🌟 Key Architecture & Highlights

- **100% Local Execution**: Runs entirely on local Ollama server (`http://localhost:11434`) using model `gemma3:4b` (4.3B parameters, Q4_K_M quantization). **No external LLM APIs (OpenAI, Gemini, Anthropic) are used anywhere.**
- **Genuinely Multi-Agent System**:
  1. **Orchestrator Agent**: Decomposes brief, routes work, manages campaign state, enforces 3-strike compliance caps, and manages the Week 1 → Week 2 analytics loop.
  2. **Strategy Agent**: Formulates audience personas, channel mix, posting cadence, pillars, KPIs, and updates strategy for Week 2.
  3. **Content Writer Agent**: Generates platform-tailored post copy for 3 distinct channels (`Pulse`, `Forum`, `ProNet`).
  4. **Creative Agent**: Generates visual/art direction briefs for each post.
  5. **Brand & Compliance Agent**: Audits post copy & creative briefs for brand safety, prohibited claims, over-promising, and tone compliance (with automated revision loop up to 3 retries).
  6. **Scheduler / Publisher Agent**: Arranges approved posts into optimal channel calendar slots.
  7. **Community Manager Agent**: Scans comments, classifies sentiment, drafts replies, and escalates sensitive safety/legal inquiries.
  8. **Analytics Agent**: Analyzes simulated performance metrics, discovers hidden patterns, and outputs evidence-backed recommendations for Week 2.
- **Mock Social Platform & Hidden Signals Engine**:
  - 3 Channels: `Pulse` (Short video), `Forum` (Community Q&A), `ProNet` (B2B).
  - 7 Ground-Truth Hidden Signals: Channel peak windows, CTA question boost, copy length suitability, tone resonance, hashtag non-linear scaling, format novelty decay, and pillar-audience fit.
- **Mandatory Human Approval Gate**: Posts cannot publish to the platform without passing Compliance AND Human Approval.
- **Week 1 vs Week 2 Improvement Loop**: Analytics recommendations feed directly back to Strategy for Week 2, producing comparative growth metrics and percentage deltas.
- **Interactive Web UI**: Modern dark-mode dashboard with real-time agent trace timeline, human review interface, mock platform feed viewer, and analytics comparison charts.

---

## 🛠️ Quick Start & Running Instructions

### 1. Prerequisites
- Python 3.11+
- Ollama installed and running locally on `http://localhost:11434`
- Local model `gemma3:4b` pulled in Ollama:
  ```bash
  ollama pull gemma3:4b
  ```

### 2. Installation
```bash
# Navigate to project directory
cd "C:\Users\Aman Kumar Singh\.gemini\antigravity\scratch\multi_agent_social_ai"

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Run Application
```bash
python run.py
```
Open your browser to: **`http://localhost:8000`**

---

## 🧪 Running Automated Tests

Run the complete test suite verifying Ollama connectivity, simulator hidden signals, compliance retry caps, human approval gates, and end-to-end campaign execution:

```bash
pytest tests/ -v
```

---

## 📁 Repository Structure

```
multi_agent_social_ai/
│
├── app/
│   ├── main.py                  # FastAPI Application & UI Routes
│   ├── config.py                # Configuration & Channel Settings
│   │
│   ├── agents/                  # 8 Specialized Agent Modules
│   │   ├── base_agent.py        # Base Agent Class & Trace Logger
│   │   ├── orchestrator.py      # Chief of Staff & Workflow Director
│   │   ├── strategy_agent.py    # Campaign Strategy Lead
│   │   ├── content_agent.py     # Senior Copywriter
│   │   ├── creative_agent.py    # Art & Creative Director
│   │   ├── compliance_agent.py   # Brand Safety & Legal Officer
│   │   ├── scheduler_agent.py   # Calendar Coordinator
│   │   ├── community_agent.py   # Community & Audience Manager
│   │   └── analytics_agent.py   # Performance Analyst
│   │
│   ├── llm/                     # Local Ollama Abstraction & Validation
│   │   ├── ollama_client.py     # Async/Sync Ollama HTTP Client
│   │   ├── schemas.py           # Pydantic Schemas for Agents
│   │   └── validators.py        # JSON Extraction & Repair Validators
│   │
│   ├── orchestration/           # State & Message Bus
│   │   ├── state.py             # MessageBus & AgentTrace Logger
│   │   ├── messages.py          # AgentMessage Data Structure
│   │   └── workflow.py          # State Machine & Week Comparison Engine
│   │
│   ├── simulator/               # Mock Platform & Engagement Engine
│   │   ├── hidden_rules.py      # 7 Planted Ground-Truth Hidden Signals
│   │   ├── engagement.py        # Metric Calculation with Controlled Noise
│   │   ├── audience.py          # Realistic Comment Generator & Sensitive Triggers
│   │   └── platform.py          # Platform Storage & API Service
│   │
│   ├── database/                # SQLite Models & Database Setup
│   │   ├── models.py            # SQLAlchemy Database Schemas
│   │   ├── database.py          # Session & Engine Manager
│   │   └── seed.py              # Demo Seed Campaign Data
│   │
│   ├── api/                     # REST API Routers
│   │   ├── campaigns.py
│   │   ├── posts.py
│   │   ├── analytics.py
│   │   ├── agents.py
│   │   └── platform_api.py
│   │
│   ├── templates/               # Jinja2 HTML Frontend Templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── campaign.html
│   │   ├── review.html
│   │   ├── platform.html
│   │   ├── analytics.html
│   │   └── trace.html
│   │
│   └── static/                  # UI CSS & JavaScript Assets
│       ├── css/style.css
│       └── js/app.js
│
├── tests/                       # Pytest Automated Test Suite
│   ├── test_ollama.py
│   ├── test_simulator.py
│   ├── test_agents.py
│   └── test_workflow.py
│
├── docs/                        # Architecture & Evaluation Write-ups
│   ├── architecture.md
│   ├── hidden_signals.md
│   └── requirement_audit.md
│
├── README.md
├── requirements.txt
└── run.py                       # Startup Entry Point
```

---

## 📄 License & Audit

See [`docs/requirement_audit.md`](docs/requirement_audit.md) for full mapping against authorial assignment requirements.
