# 🌉 Flavor Bridge Engine

A discovery engine that finds **"chemical cousins"** between ingredients using AI embeddings and vector similarity search.

> *"I had to figure out how to represent 'Umami' as a mathematical vector so an AI could understand that miso and parmesan share similar chemical properties."*

## 🎯 The Problem

Why do Miso and Parmesan taste similar? Both are fermented foods rich in **glutamic acid** — the compound responsible for umami. Traditional search matches keywords. This engine discovers ingredients that share **flavor chemistry**, even when they seem unrelated.

| Query | Chemical Cousins | Why? |
|-------|------------------|------|
| Miso | Parmesan, Soy Sauce | High glutamate |
| Dark Chocolate | Coffee, Raspberry | Maillard compounds |
| Truffle | Cauliflower, Butternut | Earthy aromatics |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge                          │
├─────────────────────────────────────────────────────────────┤
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │   Workers   │───▶│  Workers AI │───▶│  Vectorize  │    │
│   │   (Python)  │    │ (Embeddings)│    │  (Vector DB)│    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

**How it works:**
1. Each ingredient description → 384-dimensional vector
2. Query vectors compared using cosine similarity  
3. LLM explains *why* ingredients are related

## 🚀 Live Demo

| | URL |
|---|-----|
| **API** | https://flavor-bridge-engine.fabiodiceglie.workers.dev |
| **Docs** | https://flavor-bridge-engine.fabiodiceglie.workers.dev/docs |

## 🛠️ Tech Stack

- **Runtime**: Cloudflare Workers (Python)
- **AI**: Workers AI (bge-small-en-v1.5 + llama-3.1-8b)
- **Vector DB**: Cloudflare Vectorize
- **Caching**: Cloudflare KV (search: 1h TTL, explain: 24h TTL)
- **Rate Limiting**: Cloudflare KV (10 req/min per IP)
- **CI/CD**: GitHub Actions (staging → tests → production)

## 📁 Project Structure

```
backend/
├── src/
│   ├── routes/           # HTTP handlers
│   ├── services/         # AI, Vectorize, Cache logic
│   ├── prompts/          # LLM prompts
│   ├── utils/            # Rate limiting
│   └── data/             # 200 ingredients
├── tests/e2e/            # Integration tests
└── wrangler.toml         # Cloudflare config
```

## 🧪 Quick Start

```bash
cd backend
npm install -g wrangler
wrangler login
npx wrangler dev          # http://localhost:8787
```

## 🚢 CI/CD Pipeline

Push to `main` triggers an automated deployment flow:

```
                         push to main
                              │
                              ▼
                 ┌────────────────────────┐
                 │   🚧 Deploy Staging    │
                 │   (isolated env)       │
                 └───────────┬────────────┘
                             │
                             ▼
                ┌────────────────────────┐
                │   🧪 E2E Tests         │
                │   • Health check       │
                │   • Search API         │
                │   • Cache (X-Cache)    │
                │   • AI Explanations    │
                │   • Rate Limiting      │
                └───────────┬────────────┘
                             │
                      ✅ all pass?
                             │
                             ▼
                 ┌────────────────────────┐
                 │   🚀 Deploy Production │
                 │   (live traffic)       │
                 └────────────────────────┘
```

**Zero-downtime**: Production only updates if staging tests pass.

## ⚡ Performance

Responses are cached in Cloudflare KV to reduce latency and AI costs:

| Endpoint | Cache TTL | Typical Response |
|----------|-----------|------------------|
| `/search` | 1 hour | MISS: ~200ms, HIT: ~10ms |
| `/explain` | 24 hours | MISS: ~2s, HIT: ~10ms |

Cache status is returned via `X-Cache: HIT` or `X-Cache: MISS` header.

---

Built with ☕ and 🧀 (they're chemical cousins, after all)
