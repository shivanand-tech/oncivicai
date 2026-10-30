# CivicAI – Smart Citizen Complaint Management System

CivicAI is a modern, responsive, full-stack municipal civic governance web application. It automates citizen hazard reporting, transparent SLA tracking, explainable AI-based incident prioritization, spatial duplicate detection, and end-to-end municipal complaint resolution workflows.

Built with **HTML5, CSS3, Vanilla JavaScript (ES6+), Python Flask, SQLite, Leaflet.js, and OpenStreetMap**.

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [System Architecture](#-system-architecture)
3. [Transparent & Explainable AI Methodology](#-transparent--explainable-ai-methodology)
4. [Platform Pages & Capabilities](#-platform-pages--capabilities)
5. [Database Schema & Synthetic Dataset](#-database-schema--synthetic-dataset)
6. [macOS (MacBook) Setup & Execution](#-macos-macbook-setup--execution)
7. [Windows & Linux Setup](#-windows--linux-setup)
8. [Automated Verification Test Suite](#-automated-verification-test-suite)
9. [Known Limitations & Ethical Considerations](#-known-limitations--ethical-considerations)
10. [5-Minute Competition Demonstration Guide](#-5-minute-competition-demonstration-guide)

---

## 🏛️ Project Overview

In traditional municipalities, citizen complaints face major bottlenecks:
- Unorganized submission channels and lack of real-time tracking.
- Subjective or manual triage causing critical hazards (e.g., live electrical wires, open sewer manholes) to languish in queues.
- Redundant duplicate reports overwhelming municipal desks during major civic events (e.g., monsoon flooding).
- Lack of transparency in why certain complaints take precedence over others.

**CivicAI** solves these challenges through:
- **Transparent AI Triage**: Categorizes issues, generates concise executive summaries, and calculates explainable priority scores (0–100) with human-readable justifications.
- **Geospatial Hotspot Radar**: Pinpoints high-density complaint clusters on an interactive Leaflet.js map with priority-colored pins and glowing risk rings.
- **Spatial & Semantic Deduplication**: Flags nearby matching complaints using Haversine distance and NLP token similarity, eliminating duplicate work orders.
- **5-Stage Complaint Lifecycle**: Tracks reports from `Submitted` → `Under Review` → `Assigned` → `In Progress` → `Resolved` with an immutable SQLite audit trail.

---

## 📐 System Architecture

CivicAI is built on a clean three-tier architecture without heavy external frameworks:

```
┌──────────────────────────────────────────────────────────────────────────┐
│                             PRESENTATION TIER                            │
│  • Modern Dark Navy (#080E1A) & Teal Accent Design System                │
│  • Responsive CSS Grid & Flexbox (Desktop, Tablet, Mobile)               │
│  • Interactive Leaflet.js + OpenStreetMap (Priority Pins & Hotspot Rings) │
│  • Chart.js Visualizations (Categories, Priority, Department SLA)        │
│  • Floating Aura AI Assistant Copilot                                   │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ HTTP / REST APIs (JSON / Multipart)
┌────────────────────────────────────▼─────────────────────────────────────┐
│                             APPLICATION TIER                             │
│  • Python Flask 3.0+ REST API Service (app.py)                           │
│  • Transparent AI & NLP Analysis Engine (ai_engine.py)                   │
│  • Safe File Upload Pipeline with SHA-256 Hashing & MIME Validation      │
│  • Dynamic SLA Calculation & Immutable Audit Trail Logging               │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ SQLite3 Transactional Interface
┌────────────────────────────────────▼─────────────────────────────────────┐
│                               DATA TIER                                  │
│  • SQLite3 Relational Database (civicai.db)                              │
│  • Tables: `complaints`, `audit_logs`, `citizens`                        │
│  • Foreign Key Integrity & WAL (Write-Ahead Logging) Mode                │
│  • 40 Pre-Seeded Synthetic Complaints with Geo-Coordinates               │
└──────────────────────────────────────────────────────────────────────────┘
```

### Folder Structure
```
civicai/
├── app.py                      # Flask backend: REST APIs & page routing
├── database.py                 # SQLite initialization & 40 synthetic complaints
├── ai_engine.py                # Explainable AI, Hotspots, Deduplication & Priority
├── generate_sample_svgs.py     # High-definition SVG graphic assets generator
├── civicai.db                  # SQLite database (auto-created & pre-seeded)
├── requirements.txt            # Python dependencies (Flask, Werkzeug)
├── README.md                   # System documentation & architectural reference
├── DEMO_GUIDE.md               # 5-minute competition demonstration walkthrough
├── tests/                      # Automated test verification suites
│   ├── test_competition_demo.py     # 12-point competition checklist test
│   ├── test_ai_engine.py            # AI categorization, priority & deduplication
│   ├── test_backend.py              # Backend REST APIs & file upload validation
│   ├── test_map_hotspots.py         # Leaflet route & hotspot clustering
│   └── test_workflow_lifecycle.py   # 5-stage lifecycle & citizen verification
├── static/
│   ├── css/
│   │   └── style.css           # Dark navy & teal design system & mobile styles
│   ├── js/
│   │   ├── main.js             # Global utilities, navigation & Aura AI Copilot
│   │   ├── home.js             # Home page KPIs & live complaints feed
│   │   ├── submit.js           # Form, GPS, live vision scan & priority scoring
│   │   ├── track.js            # Tracking lookup, 5-stage timeline & rating
│   │   ├── admin.js            # Dashboard KPIs, Chart.js charts & triage queue
│   │   └── manage.js           # Console filters, table, modals & status updates
│   ├── images/
│   │   └── samples/            # Pre-rendered municipal hazard & resolved SVGs
│   └── uploads/                # Citizen uploaded images directory
└── templates/
    ├── base.html               # Shared layout, navigation, footer & Aura widget
    ├── index.html              # 1. Home page: Hero & "Report a Problem" button
    ├── submit.html             # 2. Complaint submission form
    ├── track.html              # 3. Complaint tracking page with 5-stage timeline
    ├── admin.html              # 4. Admin dashboard with charts & Hotspot Radar
    ├── manage.html             # 5. Complaint management console with data table
    ├── map.html                # Interactive Leaflet geospatial incident map
    ├── risk_predictor.html     # Ward-level predictive risk matrix
    ├── before_after.html       # Photographic before/after resolution audits
    └── leaderboard.html        # Citizen community hero points & tiers
```

---

## 🧠 Transparent & Explainable AI Methodology

CivicAI adheres strictly to **transparent, explainable AI governance**. It uses transparent Python-based NLP rules, lexical matching, heuristic scoring, and geodesic spatial algorithms rather than opaque black-box APIs.

### 1. Automatic Categorization
Classifies citizen reports into 6 standard municipal categories using curated lexical dictionaries and weighted keyword densities:
- **Road Damage**: Potholes, asphalt cracks, cratering, broken curbs, cave-ins.
- **Waterlogging**: Standing floodwater, monsoon inundation, submerged roads, water entering properties.
- **Garbage**: Uncollected trash heaps, rotting refuse, illegal dumping, overflowing dumpsters.
- **Streetlight**: Dark intersections, non-functioning fixtures, flickering lamps, exposed wires.
- **Drainage**: Missing or collapsed sewer manhole covers, overflowing stormwater drains, blocked catch basins.
- **Other**: Fallen trees, encroachment, stray animals, park damage, civic infrastructure issues.

### 2. Executive Summary Synthesizer
Generates a concise 1–2 sentence municipal brief summarizing:
- The core infrastructure failure and severity.
- Specific impact on public safety, property, or vehicular traffic.
- The reported location.
- Tactical municipal equipment and crew dispatch required (e.g., *"Deployment of dewatering suction pumps and catch-basin silt clearance required"*).

### 3. Explainable Multi-Factor Priority Scoring (0–100)
Calculates an objective urgency score mapped to three official tiers:
- **High** (Score $\ge 60$ pts or critical life-safety hazard): SLA target = **24 Hours**.
- **Medium** (Score 30–59 pts): SLA target = **72 Hours**.
- **Low** (Score $< 30$ pts): SLA target = **168 Hours** (7 days).

The score synthesizes four weighted factors:
1. **Base Category Hazard** (up to 30 pts): Drainage (28), Waterlogging (25), Road Damage (22), Streetlight (20), Garbage (18), Other (15).
2. **Acute Hazard & Severity Keywords** (up to 40 pts): Detection of terms such as *entering houses, electrocution, collapsed, school, hospital, pedestrian injury, severe flood*.
3. **Location Vulnerability & Footfall** (up to 15 pts): High-density arteries, bus stations, school zones, hospital perimeters.
4. **Dimension & Scale** (up to 15 pts): Deep craters ($>1\text{ ft}$), widespread flooding ($>100\text{ meters}$), multi-ton waste piles.

#### Direct User Test Example:
- **Input**: *"Water is entering houses because of road flooding."*
- **Category**: `Waterlogging` (Confidence: 98.5%)
- **Priority**: `High` (Score: 61/100)
- **Explainable Reasons**:
  - `Risk to residential properties.`
  - `Potential safety hazard.`
  - `Immediate attention required.`

### 4. Spatial & NLP Duplicate Radar
Detects duplicate submissions using a hybrid spatial-textual algorithm:
- **Spatial Proximity**: Calculates exact geodesic distance using the Haversine formula:
  $$\Delta\sigma = 2 \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos\phi_1 \cos\phi_2 \sin^2\left(\frac{\Delta\lambda}{2}\right)} \right)$$
  $$d = R \cdot \Delta\sigma \quad (\text{with } R = 6,371,000\text{ meters})$$
- **Semantic Overlap**: Combines Jaccard token set intersection and bigram Dice coefficient.
- **Duplicate Flag**: Triggered if a report is within **150 meters** with $>30\%$ text similarity, or within **300 meters** with identical category and $>50\%$ text similarity.

### 5. Automated Geodesic Hotspot Clustering
The `/api/ai/hotspots` engine clusters open complaints within a **400-meter** radius. Clusters with $\ge 2$ complaints are identified as active hotspots with an area label, primary category, complaint count, and urgency rating, rendered as glowing circular boundary overlays on Leaflet.js.

---

## 🖥️ Platform Pages & Capabilities

1. **Home Page (`/`)**:
   - Hero banner with quick-action "Report a Problem" and "Track Complaint" buttons.
   - Dynamic KPI statistic cards: Total Complaints, Pending, Resolved, and Urgent.
   - 4-step civic workflow walkthrough and real-time public complaints feed.

2. **Submit Complaint Page (`/submit`)**:
   - Citizen reporting form with fields for Name, Contact, Title, Description, Category, and Location.
   - GPS Auto-Detection button and quick location preset chips.
   - Safe drag-and-drop image upload with live client preview.
   - Real-time AI Vision & Priority Scan previewing predicted category and urgency before submission.
   - Digital submission receipt modal with unique tracking ID (e.g., `CV-2026-1041`) and 1-click clipboard copy.

3. **Track Complaint Page (`/track`)**:
   - Real-time tracking ID search bar with prefill support (`/track?id=CV-2026-1001`).
   - 5-stage progression timeline extracting exact timestamps from SQLite audit logs.
   - SLA countdown indicator showing remaining hours or SLA compliance.
   - AI Priority Analysis card with transparent bullet justifications.
   - Official Remediation Notes panel displaying field engineer reports and resolution certificates.
   - Citizen 5-Star Resolution Verification rating and feedback submission.

4. **Executive Admin Dashboard (`/admin`)**:
   - Real-time KPIs calculated dynamically from SQLite database records.
   - Interactive Chart.js graphs: Complaints by Category, Priority Distribution, and Department Resolution Velocity.
   - **AI Hotspot Radar** card displaying active clusters, incident counts, and direct links to the map.
   - Emergency Triage Queue highlighting urgent unresolved complaints.

5. **Complaint Management Console (`/manage`)**:
   - Tabular control panel with live search and multi-factor filters (Category, Status, Priority, Duplicates).
   - Modal action dialog to reassign complaints to municipal departments and named officers.
   - Status transitions (`Submitted` → `Under Review` → `Assigned` → `In Progress` → `Resolved`).
   - Field remediation notes input and resolution proof photo logging.

6. **City Pulse Interactive Map (`/map`)**:
   - Fullscreen Leaflet.js map with OpenStreetMap tiles and Dark/Standard tile switcher.
   - Priority-coded marker pins: **Red** (High/Critical with pulsing animation), **Amber** (Medium), **Green** (Low), **Teal** (Resolved).
   - Rich interactive popups with AI summary, priority reasons, photo preview, and Track/Manage links.
   - Glowing circular hotspot radar overlays with real-time category and priority filters.

7. **Predictive Ward Risk Matrix (`/risk-predictor`)**:
   - Ward-level infrastructure vulnerability modeling and monsoon risk forecasts.

8. **Resolution Audits (`/before-after`)**:
   - Photographic side-by-side before-and-after proof gallery with citizen verification ratings.

9. **Community Champions Leaderboard (`/leaderboard`)**:
   - Citizen gamification rewarding civic points (+50 pts for filing verified reports, +25 pts on validated remediation) and tier badges.

---

## 🗄️ Database Schema & Synthetic Dataset

### SQLite Database (`civicai.db`)
- `complaints`: Primary record table with unique string `complaint_id` (`CV-2026-XXXX`), title, description, category, priority, priority_score, priority_reasons, status, coordinates, SLA deadlines, department assignments, and resolution notes.
- `audit_logs`: Immutable lifecycle audit trail recording event types (`SUBMITTED`, `AI_TRIAGE`, `STATUS_CHANGE`), actors, timestamps, and notes.
- `citizens`: Registered civic users and leaderboard points.

### Synthetic Demonstration Dataset (40 Records)
- Cleanly seeded with **exactly 40 synthetic smart city complaints** (`CV-2026-1001` to `CV-2026-1040`).
- **6 Deliberate Duplicate Pairs**: E.g., `CV-2026-1007` and `CV-2026-1008` (Residency Road open manholes), `CV-2026-1001` and `CV-2026-1002` (Koramangala 80 Feet Road waterlogging).
- **24 Urgent Safety Hazards**: Deep road craters, exposed electrical cables, overflowing sewage drains.
- **All 6 Categories Represented**: Road Damage (9), Waterlogging (8), Streetlight (7), Drainage (6), Garbage (6), Other (4).
- **5 Geographic Hotspots**: Clustered within 400m on Bangalore urban corridors.
- **Privacy Compliance**: 100% synthetic data. No real personal information. All citizen names labeled `[Synthetic]` with demo domains.

---

## 🍎 macOS (MacBook) Setup & Execution

Follow these exact terminal commands to run the complete website on your MacBook:

### Step 1: Open Terminal and Navigate to the Project Directory
```bash
cd /path/to/hackathon
```

### Step 2: Create and Activate a Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```
*(Only Flask and Werkzeug are required; all other libraries use Python standard library modules).*

### Step 4: (Optional) Seed / Reset the Database
```bash
python database.py
```
*(Initializes `civicai.db` with exactly 40 synthetic complaints, 6 duplicate pairs, and 5 hotspots).*

### Step 5: Start the CivicAI Flask Server
```bash
python app.py
```

### Step 6: Open the Website in Your Browser
Open Safari or Google Chrome and navigate to:
```
http://127.0.0.1:5000
```

---

## 💻 Windows & Linux Setup

### Linux (Ubuntu / Debian)
```bash
cd /path/to/hackathon
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python database.py
python app.py
```

### Windows (PowerShell)
```powershell
cd D:\hackathon
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python database.py
python app.py
```

---

## 🧪 Automated Verification Test Suite

CivicAI includes a comprehensive automated test suite covering all backend APIs, AI rules, geospatial clustering, and full workflow lifecycles.

To run all verification suites in sequence:
```bash
python tests/test_backend.py
python tests/test_ai_engine.py
python tests/test_map_hotspots.py
python tests/test_workflow_lifecycle.py
python tests/test_competition_demo.py
```

### Test Suite Summary:
1. `tests/test_backend.py`: Validates all 10 REST endpoints, image upload security, and dynamic SQLite KPI calculations.
2. `tests/test_ai_engine.py`: Verifies 6-category classification, the user's flood test case, 0–100 priority tiers, and NLP deduplication.
3. `tests/test_map_hotspots.py`: Verifies Leaflet markup, marker pins, and 400m hotspot clustering.
4. `tests/test_workflow_lifecycle.py`: Tests the full 5-stage lifecycle from submission to resolution and 5-star citizen verification.
5. `tests/test_competition_demo.py`: End-to-end 12-point competition checklist validation.

---

## ⚖️ Known Limitations & Ethical Considerations

1. **Deterministic Rule-Based NLP vs. Generative LLMs**:
   - *Advantage*: 100% deterministic, explainable, zero hallucination risk, zero external API costs, instant response (<5ms), works completely offline.
   - *Limitation*: Complex or ambiguous figurative phrasing outside municipal terminology defaults to the `Other` category.
2. **Geographic Coordinate Bounds**:
   - The synthetic dataset coordinates are mapped to urban Bangalore corridors (lat: 12.91–12.98, lng: 77.58–77.65) for visual demonstration. Real deployment requires integrating city-specific GIS layers.
3. **SQLite Concurrency**:
   - SQLite with WAL mode is robust and fast for single-server hackathon demonstrations. For large-scale enterprise deployments with thousands of concurrent field workers, migration to PostgreSQL with PostGIS is recommended.
4. **Data Privacy**:
   - All sample records are labeled `[Synthetic]` with synthetic names and email addresses. No actual citizen data is stored.

---

## 🏆 5-Minute Competition Demonstration Guide

For the complete minute-by-minute judge presentation script, see [DEMO_GUIDE.md](file:///d:/hackathon/DEMO_GUIDE.md).

### Quick Demo Summary:
- **Minute 0:00 – 1:00**: **Home & Citizen Submission** — Showcase the dark navy/teal UI, 4 live KPI cards, and submit a complaint with auto-detected GPS coordinates and AI live triage.
- **Minute 1:00 – 2:00**: **Explainable AI & Categorization** — Demonstrate *"Water is entering houses because of road flooding."* $\rightarrow$ High Priority with 3 clear bullet justifications.
- **Minute 2:00 – 3:00**: **Spatial Deduplication & City Pulse Map** — Showcase Leaflet.js map, color-coded priority pins, glowing 400m hotspot radar rings, and category filters.
- **Minute 3:00 – 4:00**: **Executive Admin Command Center** — Show real dynamic SQLite KPIs, department performance tables, and active hotspot cards.
- **Minute 4:00 – 5:00**: **Full Lifecycle & Citizen Tracking** — Update status to `In Progress` and `Resolved` with engineer notes, track using ID `CV-2026-1041`, view the 5-stage progression timeline, and submit a 5-star citizen rating.
