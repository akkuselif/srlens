# SRLens

> The science of how you learn — interactive visualizations and AI-powered tools grounded in Educational Psychology research.

**Live site:** [srlens.netlify.app](https://srlens.netlify.app)

---

## What is SRLens?

SRLens translates cutting-edge research on self-regulated learning (SRL), metacognition, and motivation into accessible interactive visualizations and AI-powered tools — no jargon, no paywalls.

Built by a PhD candidate in Teacher Education & Learning Sciences (concentration: Educational Psychology) with an MS in Data Science & AI.

---

## Features

- **Interactive visualizations** — real data from PISA 2022, KU Leuven VLE clickstream, and open learning analytics datasets
- **SRL profile assessment** — AI-powered tool that identifies your learner profile using Zimmerman's SRL model and SDT theory
- **Concept explainer** — ask anything about metacognition, motivation, cognitive load, spaced repetition, and more
- **Topic pages** — deep dives into SRL, metacognition, motivation, learning analytics, cross-cultural learning, and AI in education

---

## Project structure

```
srlens/
├── index.html              # Homepage
├── README.md               # This file
├── pages/
│   ├── srl.html            # Self-regulated learning topic page
│   ├── metacognition.html  # Metacognition topic page
│   ├── motivation.html     # Motivation & emotion topic page
│   ├── analytics.html      # Learning analytics topic page
│   ├── cross-cultural.html # Cross-cultural learning topic page
│   └── ai-learning.html    # AI & learning topic page
├── components/
│   ├── nav.html            # Shared navigation (if using includes)
│   └── footer.html         # Shared footer
├── assets/
│   ├── css/
│   │   └── style.css       # Shared styles (extracted from index.html)
│   └── js/
│       └── ai-tool.js      # AI chat tool logic
└── data/
    ├── pisa2022/           # PISA 2022 processed data (JSON)
    ├── ku-leuven/          # KU Leuven VLE summary data (JSON)
    └── README.md           # Data sources and licenses
```

---

## Data sources

| Dataset | Source | License | Used for |
|---|---|---|---|
| PISA 2022 | OECD | Public | Motivation, SRL constructs, cross-national comparisons |
| KU Leuven clickstream | [Scientific Data, 2026](https://www.nature.com/articles/s41597-026-06821-3) | CC BY 4.0 | VLE behavioral navigation patterns |
| PISA 2025 | OECD (expected late 2026) | Public | SRL process data — pipeline ready |

---

## Roadmap

- [x] Homepage with hero, topics, viz previews, AI tool, about
- [ ] Individual topic pages (SRL, metacognition, motivation)
- [ ] Full interactive visualizations (learner navigation, PISA motivation chart)
- [ ] SRL profile assessment — full question bank
- [ ] PISA 2025 analysis once data drops (late 2026)
- [ ] Custom domain (srlens.io)
- [ ] Blog / research notes section

---

## Tech stack

- Plain HTML, CSS, JavaScript — no framework needed yet
- Hosted on Netlify (free tier)
- AI tool powered by Claude API (Anthropic)
- Visualizations: Chart.js + D3.js

---

## Research background

This project is grounded in:

- **Zimmerman's SRL model** — planning, monitoring, reflection cycle
- **Self-determination theory** (Deci & Ryan) — autonomy, competence, relatedness
- **Metacognition** (Flavell) — metacognitive knowledge and regulation
- **Cognitive load theory** (Sweller) — intrinsic, extraneous, germane load
- **Learning analytics** — behavioral signals from VLE clickstream data

---

## License

Content: CC BY 4.0 — share and adapt with attribution.
Code: MIT License.

---

*Built with Educational Psychology, Data Science, and a lot of coffee.*
