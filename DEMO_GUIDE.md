# CivicAI – 5-Minute Competition Demonstration Guide

This guide provides a minute-by-minute presentation script and click-through walkthrough tailored for hackathon judges and competition evaluators.

---

## ⏱️ At-A-Glance Schedule

| Time | Segment | URL / Screen | Key Focus |
|---|---|---|---|
| **0:00 – 1:00** | Introduction & Citizen Submission | `/` $\rightarrow$ `/submit` | Modern UI, Live KPIs, GPS Auto-Detection & Live Vision Scan |
| **1:00 – 2:00** | Explainable AI Triage | `/submit` | Categorization, 0–100 Priority Scoring & Bullet Justifications |
| **2:00 – 3:00** | Map & Hotspot Radar | `/map` | Leaflet.js Pins, 400m Hotspot Rings & Spatial Deduplication |
| **3:00 – 4:00** | Executive Admin Dashboard | `/admin` | Real Dynamic KPIs, Chart.js Visualizations & Hotspot Radar |
| **4:00 – 5:00** | Full Lifecycle & Citizen Tracking | `/manage` $\rightarrow$ `/track` | Department Assignment, Status Updates, 5-Stage Timeline & 5-Star Rating |

---

## 🎬 Minute-by-Minute Walkthrough Script

### 📍 Minute 0:00 – 1:00: Platform Introduction & Citizen Submission

#### 1. Start on the Home Page (`http://127.0.0.1:5000/`)
* **What to Show**:
  - Point out the dark navy (`#080E1A`) and teal design with glowing accents.
  - Highlight the **4 dynamic statistics cards**: Total Complaints, Pending, Resolved, and Urgent. Mention that these are calculated dynamically from SQLite.
  - Scroll briefly down to show the 4-step workflow explainer and the real-time public complaints feed.
* **What to Say**:
  > *"Judges, this is CivicAI – a full-stack municipal incident triage platform. In standard municipal portals, complaints disappear into a black-box queue without transparent priorities or tracking. CivicAI uses transparent, explainable AI to categorize issues, calculate urgency, eliminate duplicate reports, and provide an accountable 5-stage lifecycle."*

#### 2. Click "Report a Problem" or Navigate to `/submit`
* **What to Show**:
  - The submission form: Citizen Name, Contact, Title, Description, Category, Location, and Image Upload.
  - Click the **GPS Auto-Detect Location** button or select a location preset chip (e.g., `Koramangala 80 Feet Road`).
  - Select one of the sample hazard photo presets or drag-and-drop an image.
  - Point to the **Real-Time AI Vision & Priority Scan** card on the right updating live as you type.
* **What to Say**:
  > *"When a citizen reports an issue, our client-side AI assistant immediately extracts physical hazard features and provides a live preview of the estimated urgency before submission."*

---

### 📍 Minute 1:00 – 2:00: Explainable AI Triage & The Flood Test Case

#### 1. Demonstrate the Specific Test Case
* **What to Enter**:
  - **Citizen Name**: `Ananya Roy`
  - **Citizen Contact**: `ananya@example.com`
  - **Complaint Title**: `Severe road flooding inundating homes`
  - **Complaint Description**: `Water is entering houses because of road flooding.`
  - **Category**: Leave as `Auto-Detect` or select `Waterlogging`
  - **Location**: `Koramangala 4th Block`
* **Click**: `File Incident Report` button.
* **What to Show**:
  - Watch the button show the loading spinner: `<i class="fas fa-circle-notch fa-spin"></i> Submitting & Triaging...`.
  - The **Digital Submission Receipt Modal** pops up instantly with:
    - **Unique Tracking ID**: e.g., `CV-2026-1041` (with 1-click clipboard copy).
    - **Assigned Category**: `Waterlogging` (Confidence: 98.5%).
    - **Assigned Priority**: `High` (Score: 61/100, Target SLA: 24 Hours).
    - **Auto-Routed Department**: `Water Supply & Sewerage Board (BWSSB)`.
    - **Triage Justifications** (clearly listed):
      - *Risk to residential properties.*
      - *Potential safety hazard.*
      - *Immediate attention required.*
* **What to Say**:
  > *"Notice that CivicAI does not use opaque black-box AI. It provides transparent, explainable justifications. When a citizen reports that water is entering homes, our engine detects property risk and pedestrian hazards, elevating it to High priority with a 24-hour SLA."*

---

### 📍 Minute 2:00 – 3:00: Interactive City Pulse Map & Hotspot Radar

#### 1. Navigate to `/map` (Click "City Pulse" in Top Navigation)
* **What to Show**:
  - The interactive Leaflet.js map with OpenStreetMap tiles.
  - **Priority Marker Pins**:
    - **Red Pins** (High/Critical) with a glowing, pulsing beacon.
    - **Amber Pins** (Medium).
    - **Green Pins** (Low).
    - **Teal Pins** (Resolved).
  - Click any red marker pin on the map to open the interactive popup showing:
    - Complaint Title, Tracking ID, and AI Category.
    - AI Executive Summary.
    - Priority Justifications list.
    - Direct "Track" and "Manage" action buttons.

#### 2. Highlight Automated Hotspot Detection & Duplicate Radar
* **What to Show**:
  - Point to the **Active Hotspots** sidebar on the left and the glowing circular boundary rings on the map.
  - Click on the `80 Feet Road (Waterlogging Hotspot)` item in the sidebar — the map smoothly pans and zooms to the cluster.
  - Explain the 400-meter clustering radius: 7 complaints in this immediate perimeter have been aggregated into a single operational zone.
  - Demonstrate the **Category Filter** dropdown: select `Drainage` or `Road Damage` to show markers filtering instantly.
* **What to Say**:
  > *"During civic emergencies like monsoon storms, dozens of citizens report the exact same flooded intersection. CivicAI's spatial deduplication detects nearby reports using Haversine geodesic distance, while our Hotspot Radar clusters reports within 400 meters into geographic hotspots so emergency crews can deploy bulk resources instead of chasing isolated tickets."*

---

### 📍 Minute 3:00 – 4:00: Executive Admin Command Center

#### 1. Navigate to `/admin` (Click "Dashboard" in Top Navigation)
* **What to Show**:
  - **4 Dynamic KPI Cards**: Total Complaints, Pending, Resolved, and Urgent (calculated dynamically from SQLite).
  - **Interactive Chart.js Visualizations**:
    - *Complaints by Category* (Doughnut chart with 6 classes).
    - *Priority Distribution* (Bar chart: High, Medium, Low).
  - **AI Hotspot Radar Panel**: Active multi-complaint clusters with complaint counts, primary categories, and 1-click "View on Map" shortcuts.
  - **Department Resolution Performance Table**: Shows active work orders, completed jobs, and average SLA hours for PWD, BWSSB, BESCOM, and SWM.
  - **Emergency Triage Queue**: High-priority incidents awaiting municipal assignment.
* **What to Say**:
  > *"For municipal commissioners, the Admin Dashboard provides instant operational visibility. Every statistic is live from SQLite, giving leadership real-time oversight of department resolution velocity and SLA compliance."*

---

### 📍 Minute 4:00 – 5:00: Full Lifecycle Management & Citizen Tracking

#### 1. Navigate to `/manage` (Click "Management" in Top Navigation)
* **What to Show**:
  - The comprehensive complaints management table.
  - Search for `CV-2026-1041` (the complaint filed in Minute 1) or filter by `Waterlogging`.
  - Click the **Update** button on the row to open the status modal.
* **Perform Status Update 1**:
  - Change Status to `In Progress`.
  - Assign Department: `Water Supply & Sewerage Board (BWSSB)`.
  - Assign Officer: `S. Patil (Stormwater Engineer)`.
  - Remediation Notes: `Dewatering high-capacity pump deployed to 4th Block cross. Catch-basin silt clearing in progress.`
  - Click **Save Changes**. Show the instant toast notification.
* **Perform Status Update 2**:
  - Open the modal again and change Status to `Resolved`.
  - Remediation Notes: `Standing stormwater drained completely. Catch-basin cleared of 1.4 tons of silt. Road reopened.`
  - Click **Save Changes**.

#### 2. Switch to Citizen Tracking View (`/track?id=CV-2026-1041`)
* **What to Show**:
  - The **5-Stage Interactive Progression Timeline**:
    1. `Submitted` (Green checkmark with initial timestamp).
    2. `Under Review` (Green checkmark).
    3. `Assigned` (Green checkmark, BWSSB).
    4. `In Progress` (Green checkmark, S. Patil).
    5. `Resolved` (Highlighted teal badge).
  - Point to the **Official Remediation Notes** displaying the engineer's deployment report.
  - Demonstrate the **Citizen 5-Star Resolution Verification**:
    - Click **5 Stars**.
    - Type feedback: *"Water drained within 4 hours. Excellent response from the municipal team!"*
    - Click **Submit Feedback** and show the confirmation badge.
* **What to Say**:
  > *"This closes the civic feedback loop. Every status change is immutably logged in SQLite with timestamp and actor tracking. Citizens can track progress at every stage and provide verified satisfaction ratings before a ticket is closed."*

---

## 🎯 Winning Closing Pitch (15 Seconds)

> *"In summary, CivicAI delivers an end-to-end, full-stack municipal management system. It requires no heavy external frameworks, runs completely offline, uses 100% explainable AI with zero hallucination risk, and provides cities with actionable geospatial intelligence to save lives and protect urban infrastructure. Thank you!"*

