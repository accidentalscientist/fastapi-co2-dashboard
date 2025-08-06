# 🌿 CO₂ Dashboard – Custom Edition by Accidentalscientist

This project started as a fork of [yochaiak/global-sustainability-dashboard](https://github.com/yochaiak/global-sustainability-dashboard), which was originally built as a technical home assignment to demonstrate fullstack capabilities with FastAPI, React, and MongoDB. The original dashboard ingested live environmental data from public APIs to visualise global CO₂ emissions, renewable energy adoption, and sustainability metrics across 50+ countries.

---

## 🧭 What I'm Turning It Into

I'm reshaping this project into a focused, personal, and practical tool: a **CO₂ Dashboard**.

My goals are to:

- **Focus on key metrics**: CO₂ emissions, per capita data, and renewable energy % — with an emphasis on countries that matter to me (Australia, France, ASEAN, G20).
- **Create a public-facing environmental tool**, hosted on my Django-based website at [accidentalscientist.net](https://accidentalscientist.net).
- **Update it weekly**, not hourly, to keep it lightweight and sustainable.
- **Pair it with behavioural data**: Eventually, I’ll combine it with personal habit tracking, mindfulness data, or sustainability actions to create a dashboard that spans both *planetary* and *personal* indicators.

This dashboard is no longer just a fullstack demo — it's becoming a curated, purpose-built data storytelling tool.

---

## 🔧 Key Modifications

- 🌏 Country selection customised (e.g. Australia-centric focus)
- 📆 Update interval reduced to **weekly**
- 🎨 Planned frontend tweaks for tone, clarity, and layout
- 🧩 Backend changes to chart titles, default behaviours, and logic
- 🛠️ Future: Integration into Django site as a project module

---

## 🚀 Tech Stack

- **Frontend**: React + TypeScript + Tailwind + Recharts
- **Backend**: FastAPI + Pydantic + MongoDB + APScheduler
- **Containerised** with Docker & Docker Compose
- **Data sources**: Our World in Data & World Bank APIs

---

## 🧠 Future Ideas

- ✅ Integrate **habit and behaviour tracking** to combine personal and planetary data
- 💾 Add a **static export mode** for low-overhead or offline versions
- 🌍 Enable **public dashboard views** with auto-publishing or scheduled refreshes
- 🔢 Group countries into **clusters or scoring tiers** for sustainability comparison
- 🎓 Create dashboard variants for:
  - Educators
  - NGOs
  - Policy makers
  - Green energy professionals

---

## ✨ Author

**Thibault – [accidentalscientist](https://github.com/accidentalscientist)**  
Data analyst and developer exploring the intersection of green energy, personal analytics, and long-term thinking.  
Built this dashboard to turn raw environmental data into insight, action, and clarity.

MIT Licensed.
