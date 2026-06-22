# World Cup 2026 Dashboard — Project Context

Read this first. It summarises all prior conversations so you can continue without asking the user to repeat anything.

---

## What this project is

A probabilistic World Cup 2026 tournament dashboard. As match results arrive (live or user-predicted), a Bayesian engine updates the full distribution over every team's tournament trajectory and shows it in a Vue dashboard.

---

## Conversation history summary

### Session 1 — Design (happened before worldcup folder was opened in VS Code)

**User's goal:** Show World Cup match result distributions that update as evidence arrives. Users can also predict results themselves and see how the distributions shift. AI-suggested predictions are a future phase.

**Key decisions reached:**

- **Method: Particle Filter + Bradley-Terry + Davidson extension**
  - Rejected HMM (tournament bracket isn't Markov in the temporal sense)
  - Bradley-Terry: `P(i beats j) = λᵢ / (λᵢ + λⱼ)`, Davidson extension for draws: `P(draw) = θ√(λᵢλⱼ) / (λᵢ + θ√(λᵢλⱼ) + λⱼ)`, θ calibrated to ~28% draw rate
  - Each particle = full vector of 48 team strengths; reweight on results, resample when ESS drops
  - Monte Carlo: forward-simulate remaining fixtures N times → group standings + knockout stage reach probabilities

- **Prior sources (user-selectable, blendable):**
  - `fifa` — FIFA World Rankings → `strength = exp(-rank/20)`
  - `elo` — World Football Elo Ratings
  - `odds` — Betting market win probabilities
  - `flat` — Equal prior (fully data-driven)
  - User can select multiple; strengths normalised to same scale and averaged

- **Two separate update streams:**
  - `actual_state` — updated only by confirmed results from football-data.org API
  - `scenario_state` — starts from `actual_state`, updated by user predictions; never pollutes the actual posterior
  - Both feed the same particle filter / Monte Carlo pipeline

- **WC 2026 format:**
  - 12 groups × 4 teams
  - Top 2 per group → 24 teams qualify
  - Best 8 third-placed teams across all 12 groups → 8 more
  - 32 teams enter knockout: R32 → R16 → QF → SF → Final → Champion

- **Stack:**
  - Backend: Python + FastAPI
  - Simulation: NumPy (particle filter + Monte Carlo)
  - Live data: football-data.org (poll every 60s); API key in env var `FOOTBALL_DATA_API_KEY`
  - Frontend: Vue 3 + Chart.js (not started)
  - Config: YAML files only — never hardcode values in source
  - AI predictions: future phase (not designed yet)

- **Code style:** modular, structural, config separate from code

Config files were written at the end of Session 1.

### Session 2 — Continuation (this conversation)

- Found Session 1 transcript (was stored under home directory because worldcup folder wasn't open yet)
- Moved that transcript into this project folder
- Created this CLAUDE.md so future sessions start with full context
- Began building backend modules (incomplete — `models/__init__.py`, `core/__init__.py`, `services/__init__.py`, `api/__init__.py`, `api/routes/__init__.py` were created as stubs but user paused to set up context first)

---

## Project structure

```
worldcup/
├── CLAUDE.md                        ← you are here
├── backend/
│   ├── config/
│   │   ├── settings.yaml            ✓ done — app, simulation, API, prior, tournament config
│   │   └── prior_sources.yaml       ✓ done — FIFA, Elo, odds data for all 48 teams
│   ├── models/
│   │   ├── __init__.py              ✓ stub created
│   │   ├── team.py                  ✗ not written
│   │   ├── match.py                 ✗ not written
│   │   └── tournament.py            ✗ not written
│   ├── core/
│   │   ├── __init__.py              ✓ stub created
│   │   ├── prior.py                 ✗ not written
│   │   ├── bradley_terry.py         ✗ not written
│   │   ├── particle_filter.py       ✗ not written
│   │   └── monte_carlo.py           ✗ not written
│   ├── services/
│   │   ├── __init__.py              ✓ stub created
│   │   ├── config.py                ✗ not written
│   │   ├── football_api.py          ✗ not written
│   │   └── state_manager.py         ✗ not written
│   ├── api/
│   │   ├── __init__.py              ✓ stub created
│   │   ├── routes/
│   │   │   ├── __init__.py          ✓ stub created
│   │   │   ├── tournament.py        ✗ not written
│   │   │   ├── prior.py             ✗ not written
│   │   │   ├── predictions.py       ✗ not written
│   │   │   └── simulation.py        ✗ not written
│   │   └── app.py                   ✗ not written
│   ├── main.py                      ✗ not written
│   └── requirements.txt             ✓ done
└── frontend/                        ✗ not started (Vue 3 + Chart.js)
```

## What to do next

Pick up from where Session 2 left off: write all the backend Python modules in order:
1. `backend/services/config.py` — YAML loader
2. `backend/models/team.py`, `match.py`, `tournament.py` — Pydantic models
3. `backend/core/prior.py` — blend prior sources
4. `backend/core/bradley_terry.py` — BT + Davidson probabilities
5. `backend/core/particle_filter.py` — particle filter engine
6. `backend/core/monte_carlo.py` — tournament simulation
7. `backend/services/football_api.py` — API polling client
8. `backend/services/state_manager.py` — actual vs scenario state
9. `backend/api/app.py` + routes — FastAPI app
10. `backend/main.py` — entry point
11. Frontend (Vue 3) — after backend is complete

## Environment variables needed

```
FOOTBALL_DATA_API_KEY=your_key_here
```
