# 🌍 Global Sustainability Dashboard

An interactive fullstack dashboard providing real-time environmental insights using global datasets from authoritative sources like **Our World in Data** and **World Bank Open Data APIs**.

Built as part of a fullstack home assignment to demonstrate end-to-end capabilities, this dashboard tracks **CO₂ emissions**, **renewable energy adoption**, and **environmental trends** across 50+ countries between 2010–2023.

---

## 🚀 Features

- 📊 **Live environmental insights**: CO₂ emissions, renewable energy percentages, and top/bottom performers.
- 🌐 **Global coverage**: Over 50 countries with real-time data refresh every 30 seconds.
- 📈 **Visual analytics**: Line and bar charts, comparisons across years, performance breakdowns.
- ⚙️ **Auto-updating backend**: Background scheduler pulls the latest data from public APIs.
- 🧠 **Intelligent insights**: Summarized KPIs and highlights like “Best Performer” for CO₂ per capita.

---

## 🧰 Tech Stack

### 🔙 Backend (Python - FastAPI)
- Data collection from:
    - [`ourworldindata.org`](https://ourworldindata.org)
    - [`data.worldbank.org`](https://data.worldbank.org)
- Scheduled updates with `APScheduler`
- RESTful API with endpoints for stats, charts, and comparisons
- Dockerized via `Dockerfile` and orchestrated with `docker-compose`

### 🔜 Frontend (React + TypeScript + TailwindCSS)
- Built with Vite for optimal performance
- Rich data visualizations via `Recharts`
- Modular and themed UI with reusable components
- Responsive design for desktop & mobile

## ▶️ Getting Started

> **Requirements**: Docker installed on your machine.

1. Clone the repo:
   ```bash
   git clone https://github.com/yochaiak/global-sustainability-dashboard.git
   cd global-sustainability-dashboard
   ```

2. Start the project:
   ```bash
   ./start.sh
   ```

3. Access the dashboard at:  
   `http://localhost:5173`

---

## 🔁 Data Updating Mechanism

- The backend includes a **scheduler** (`scheduler.py`) that fetches updated environmental metrics every X minutes.
- The frontend auto-refreshes every **30 seconds** using `setInterval()` to fetch updated data and reflect changes in charts and stats.
- You can also manually refresh data with the **Refresh** button.

## Why this approach?
I chose to implement long polling and periodic background updates for several reasons:

- Simplicity & Reliability: Long polling (via setInterval) offers a straightforward and robust way to keep the frontend updated without adding complexity like WebSockets or Server-Sent Events, which are often unnecessary for dashboards with low-to-medium update frequency.

- Data Nature: The sustainability metrics used (CO₂ emissions, renewable energy) are updated periodically from public sources and do not change every second. A refresh interval of 30 seconds strikes a good balance between data freshness and performance.

- Backend Efficiency: By using a background scheduler (scheduler.py) to periodically fetch and store new data in the database, I reduce repeated API calls on every frontend request, avoiding rate-limiting issues and improving scalability.

- User Control: Including a manual refresh button gives users the flexibility to trigger immediate updates if needed, without waiting for the next automatic refresh.

This hybrid approach ensures consistent, timely, and resource-efficient updates, while keeping the overall architecture simple and maintainable.

---

## 🧪 Testing Approach (not implemented due to time constraints)

If expanded, testing would be approached as follows:

- **Backend**
    - `pytest` for unit tests around services and endpoints
    - Mock external API calls to test fallback/error logic
    - Integration tests for `/dashboard`, `/health`, etc.

- **Frontend**
    - `Jest` + `React Testing Library` for component-level tests
    - Snapshot tests for visual consistency
    - E2E testing (if scaled up) using `Cypress`

---

## 📊 Monitoring Strategy (if in production)

For a production-grade app, monitoring would include:

- **Backend**
    - Logging with `structlog` or `loguru`
    - Metrics with `Prometheus + Grafana`
    - Error tracking via `Sentry`

- **Frontend**
    - Performance tracking with `Lighthouse`
    - Error capture with `Sentry SDK`
    - UX analytics using `PostHog` or `Plausible`

---

## 💡 Future Improvements

With more time, I’d consider adding:

- 🗺️ Interactive map-based visualization
- 🌱 Country-level sustainability score
- 📦 Caching layers (Redis) to reduce API calls
- 🔐 Authentication for custom views
- 📥 Export options (CSV, PDF reports)
- 🌍 Support for more data sources (e.g., UN, Eurostat)