"""
CivicAI - Database Layer & Competition Demonstration Seed Data Generator
Manages SQLite persistence with full lifecycle tracking, audit trails, and 40 synthetic complaints.
"""

import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "civicai.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Complaints table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id TEXT UNIQUE NOT NULL,
        citizen_name TEXT NOT NULL,
        citizen_contact TEXT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        location_name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        image_url TEXT,
        priority TEXT NOT NULL,
        priority_score INTEGER NOT NULL,
        priority_explanation TEXT,
        priority_factors_json TEXT,
        status TEXT NOT NULL DEFAULT 'Submitted',
        assigned_department TEXT,
        assigned_officer TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        sla_deadline TEXT NOT NULL,
        is_duplicate INTEGER DEFAULT 0,
        merged_into_id INTEGER,
        resolution_notes TEXT,
        resolution_image_url TEXT,
        resolved_at TEXT,
        citizen_rating INTEGER,
        citizen_feedback TEXT,
        action_brief_json TEXT,
        FOREIGN KEY (merged_into_id) REFERENCES complaints(id)
    );
    """)

    # Audit timeline logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        complaint_id INTEGER NOT NULL,
        event_type TEXT NOT NULL,
        description TEXT NOT NULL,
        actor TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (complaint_id) REFERENCES complaints(id)
    );
    """)

    # Citizen leaderboard (synthetic demo data)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS citizens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT UNIQUE NOT NULL,
        points INTEGER DEFAULT 0,
        verified_reports INTEGER DEFAULT 0,
        resolved_reports INTEGER DEFAULT 0,
        badges_json TEXT,
        tier TEXT DEFAULT 'Bronze',
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()

def reseed_competition_demo_data(force=False):
    """
    Seeds exactly 40 synthetic citizen complaints for competition demonstration:
    - Clearly labelled synthetic citizen accounts
    - 6 deliberate duplicate pairs
    - Urgent safety complaints (High Priority / Critical Hazards)
    - All 6 standard categories: Road Damage, Waterlogging, Garbage, Streetlight, Drainage, Other
    - 5 geographical hotspots with clustered coordinates in Bangalore Smart City grid
    - Complete lifecycle statuses: Submitted, Under Review, Assigned, In Progress, Resolved
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    count = cursor.fetchone()[0]

    if count > 0 and not force:
        conn.close()
        return

    # Clear existing tables if force re-seeding
    cursor.execute("DELETE FROM audit_logs")
    cursor.execute("DELETE FROM complaints")
    cursor.execute("DELETE FROM citizens")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('complaints', 'audit_logs', 'citizens')")

    now = datetime.now(timezone.utc)

    # 40 Fully Labelled Synthetic Citizen Complaints
    raw_seed_data = [
        # =========================================================================
        # HOTSPOT 1: Koramangala 80ft Road (Waterlogging & Drainage - 6 Complaints)
        # =========================================================================
        {
            "complaint_id": "CV-2026-1001",
            "citizen_name": "[Synthetic] Aarav S.",
            "citizen_contact": "synthetic.aarav@civicai.demo",
            "title": "Severe road flooding inundating residential homes",
            "description": "Water is entering houses because of road flooding after torrential shower. High danger to families and property.",
            "category": "Waterlogging",
            "location_name": "80 Feet Road, 4th Block Koramangala",
            "latitude": 12.9345,
            "longitude": 77.6258,
            "image_url": "/static/images/samples/waterlogging_1.svg",
            "priority": "High",
            "priority_score": 92,
            "priority_explanation": "High priority: Standing floodwater entering residential structures. Urgent suction pumping required.",
            "status": "In Progress",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "S. Patil (Stormwater Engineer)",
            "hours_ago": 6,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1002",
            "citizen_name": "[Synthetic] Pooja H.",
            "citizen_contact": "synthetic.pooja@civicai.demo",
            "title": "Water is entering houses because of road flooding",
            "description": "Water is entering houses because of road flooding near 4th block cross road. Flood level rising fast.",
            "category": "Waterlogging",
            "location_name": "80 Feet Road near 4th Block Cross",
            "latitude": 12.9347,
            "longitude": 77.6256,
            "image_url": "/static/images/samples/waterlogging_1.svg",
            "priority": "High",
            "priority_score": 90,
            "priority_explanation": "Duplicate Radar: 95% match with CV-2026-1001 (Distance 25m).",
            "status": "Under Review",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "Unassigned",
            "hours_ago": 4,
            "sla_hours": 24,
            "is_duplicate": 1,
            "merged_into_id": 1
        },
        {
            "complaint_id": "CV-2026-1003",
            "citizen_name": "[Synthetic] Manish G.",
            "citizen_contact": "synthetic.manish@civicai.demo",
            "title": "Knee-deep standing floodwater blocking 80 Feet Road junction",
            "description": "Arterial junction submerged under 45cm water. Two cars stalled, commuter traffic completely paralyzed.",
            "category": "Waterlogging",
            "location_name": "Sony World Signal, Koramangala 80ft Road",
            "latitude": 12.9352,
            "longitude": 77.6245,
            "image_url": "/static/images/samples/waterlogging_2.svg",
            "priority": "High",
            "priority_score": 85,
            "priority_explanation": "High priority: Arterial road closure, submerged vehicles, high commuter density.",
            "status": "Assigned",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "S. Patil (Stormwater Engineer)",
            "hours_ago": 8,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1004",
            "citizen_name": "[Synthetic] Neha R.",
            "citizen_contact": "synthetic.neha@civicai.demo",
            "title": "Stormwater drain grating choked with silt causing road inundation",
            "description": "Storm drain inlet completely blocked with construction silt and plastic bottles. Water overflowing across road.",
            "category": "Waterlogging",
            "location_name": "80 Feet Road 6th Block, Koramangala",
            "latitude": 12.9348,
            "longitude": 77.6251,
            "image_url": "/static/images/samples/waterlogging_1.svg",
            "priority": "Medium",
            "priority_score": 58,
            "priority_explanation": "Medium priority: Catch-basin silt blockage requiring scheduled vacuum desilting squad.",
            "status": "In Progress",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "V. Sharma (Desilting Supervisor)",
            "hours_ago": 16,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1005",
            "citizen_name": "[Synthetic] Karthik B.",
            "citizen_contact": "synthetic.karthik@civicai.demo",
            "title": "Stagnant floodwater pool breeding mosquitoes and foul odor",
            "description": "Dirty rainwater puddle sitting for 4 days near commercial complex. Severe mosquito larvae proliferation.",
            "category": "Waterlogging",
            "location_name": "80 Feet Road 5th Block, Koramangala",
            "latitude": 12.9360,
            "longitude": 77.6265,
            "image_url": "/static/images/samples/waterlogging_2.svg",
            "priority": "Medium",
            "priority_score": 52,
            "priority_explanation": "Medium priority: Vector-borne disease risk from stagnant water pool. Spraying & drainage needed.",
            "status": "Assigned",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "Health & Vector Control Squad",
            "hours_ago": 22,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1006",
            "citizen_name": "[Synthetic] Ananya R.",
            "citizen_contact": "synthetic.ananya@civicai.demo",
            "title": "Submerged footpath near bus shelter with 1 foot rain water",
            "description": "Bus commuters forced to walk onto vehicular road due to flooded sidewalk drain.",
            "category": "Waterlogging",
            "location_name": "Koramangala 80 Feet Road Bus Stop",
            "latitude": 12.9355,
            "longitude": 77.6248,
            "image_url": "/static/images/samples/waterlogging_1.svg",
            "priority": "Medium",
            "priority_score": 48,
            "priority_explanation": "Medium priority: Pedestrian detour hazard outside high-density bus transit shelter.",
            "status": "Submitted",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "Unassigned",
            "hours_ago": 2,
            "sla_hours": 72,
            "is_duplicate": 0
        },

        # =========================================================================
        # HOTSPOT 2: Residency Road (Drainage & Open Manholes - 5 Complaints)
        # =========================================================================
        {
            "complaint_id": "CV-2026-1007",
            "citizen_name": "[Synthetic] Rohan M.",
            "citizen_contact": "synthetic.rohan@civicai.demo",
            "title": "Hazardous open sewer manhole near St. Joseph School",
            "description": "Deep open manhole without cover or warning barrier directly outside school gate. Fatal fall hazard for schoolchildren.",
            "category": "Drainage",
            "location_name": "Residency Road, Opposite St. Joseph School Gate",
            "latitude": 12.9712,
            "longitude": 77.6015,
            "image_url": "/static/images/samples/manhole_open_1.svg",
            "priority": "High",
            "priority_score": 96,
            "priority_explanation": "High priority: Open subterranean sewer chamber in primary school transit zone.",
            "status": "In Progress",
            "assigned_department": "Municipal Infrastructure & Safety",
            "assigned_officer": "R. Kulkarni (Executive Engineer)",
            "hours_ago": 5,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1008",
            "citizen_name": "[Synthetic] Tanvi J.",
            "citizen_contact": "synthetic.tanvi@civicai.demo",
            "title": "Open manhole chamber on Residency Road school footpath",
            "description": "Uncovered drainage manhole on the sidewalk near St. Joseph school. Someone could fall inside in the dark.",
            "category": "Drainage",
            "location_name": "Residency Road Footpath, near School",
            "latitude": 12.9714,
            "longitude": 77.6017,
            "image_url": "/static/images/samples/manhole_open_1.svg",
            "priority": "High",
            "priority_score": 94,
            "priority_explanation": "Duplicate Radar: 94% match with CV-2026-1007 (Distance 28m).",
            "status": "Under Review",
            "assigned_department": "Municipal Infrastructure & Safety",
            "assigned_officer": "Unassigned",
            "hours_ago": 3,
            "sla_hours": 24,
            "is_duplicate": 1,
            "merged_into_id": 7
        },
        {
            "complaint_id": "CV-2026-1009",
            "citizen_name": "[Synthetic] Vikram S.",
            "citizen_contact": "synthetic.vikram@civicai.demo",
            "title": "Missing concrete drain slab cover outside bank entrance",
            "description": "Deep 1.2m trench opening where concrete slab cracked and collapsed into drain conduit.",
            "category": "Drainage",
            "location_name": "Residency Road, State Bank Building Entrance",
            "latitude": 12.9708,
            "longitude": 77.6020,
            "image_url": "/static/images/samples/manhole_open_1.svg",
            "priority": "High",
            "priority_score": 82,
            "priority_explanation": "High priority: Broken structural slab leaving active open drop near high footfall bank entrance.",
            "status": "Assigned",
            "assigned_department": "Municipal Infrastructure & Safety",
            "assigned_officer": "R. Kulkarni (Executive Engineer)",
            "hours_ago": 12,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1010",
            "citizen_name": "[Synthetic] Deepa N.",
            "citizen_contact": "synthetic.deepa@civicai.demo",
            "title": "Overflowing sewer chamber spilling foul black water on street",
            "description": "Underground sewer line choked with solid debris. Sewage bubbling onto road causing biohazard.",
            "category": "Drainage",
            "location_name": "Residency Road 2nd Cross, Richmond Circle",
            "latitude": 12.9716,
            "longitude": 77.6012,
            "image_url": "/static/images/samples/manhole_open_1.svg",
            "priority": "High",
            "priority_score": 78,
            "priority_explanation": "High priority: Public biological contamination and acute wastewater stench.",
            "status": "In Progress",
            "assigned_department": "Municipal Infrastructure & Safety",
            "assigned_officer": "Sewer Jetting Unit 4",
            "hours_ago": 18,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1011",
            "citizen_name": "[Synthetic] Harish I.",
            "citizen_contact": "synthetic.harish@civicai.demo",
            "title": "Blocked road gutter grating causing localized sewage puddle",
            "description": "Gutter inlet filled with plastic and leaves. Water slowly backing up onto pedestrian pavement.",
            "category": "Drainage",
            "location_name": "Residency Road near Museum Road junction",
            "latitude": 12.9710,
            "longitude": 77.6025,
            "image_url": "/static/images/samples/manhole_open_1.svg",
            "priority": "Medium",
            "priority_score": 46,
            "priority_explanation": "Medium priority: Non-emergency drain grating clearing required.",
            "status": "Submitted",
            "assigned_department": "Municipal Infrastructure & Safety",
            "assigned_officer": "Unassigned",
            "hours_ago": 2,
            "sla_hours": 72,
            "is_duplicate": 0
        },

        # =========================================================================
        # HOTSPOT 3: Indiranagar 100ft Road (Road Damage & Potholes - 6 Complaints)
        # =========================================================================
        {
            "complaint_id": "CV-2026-1012",
            "citizen_name": "[Synthetic] Divya S.",
            "citizen_contact": "synthetic.divya@civicai.demo",
            "title": "Severe crater pothole causing motorcycle accidents",
            "description": "Massive deep asphalt pothole spanning 1.5m on 100 Feet Road right after 12th Main junction. Two bikes skidded last night.",
            "category": "Road Damage",
            "location_name": "100 Feet Road, Near 12th Main Indiranagar",
            "latitude": 12.9784,
            "longitude": 77.6408,
            "image_url": "/static/images/samples/pothole_crater_1.svg",
            "priority": "High",
            "priority_score": 88,
            "priority_explanation": "High priority: Deep crater on primary vehicular arterial corridor with verified accident history.",
            "status": "In Progress",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "K. Venkatesh (Road Inspector)",
            "hours_ago": 10,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1013",
            "citizen_name": "[Synthetic] Kavita R.",
            "citizen_contact": "synthetic.kavita@civicai.demo",
            "title": "Deep road crater on 100 Ft Rd Indiranagar near 12th main",
            "description": "Large hole on main road causing severe traffic slowdown and high danger for two-wheeler commuters.",
            "category": "Road Damage",
            "location_name": "100 Feet Road Indiranagar",
            "latitude": 12.9782,
            "longitude": 77.6410,
            "image_url": "/static/images/samples/pothole_crater_1.svg",
            "priority": "High",
            "priority_score": 86,
            "priority_explanation": "Duplicate Radar: 92% match with CV-2026-1012 (Distance 30m).",
            "status": "Under Review",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "Unassigned",
            "hours_ago": 7,
            "sla_hours": 24,
            "is_duplicate": 1,
            "merged_into_id": 12
        },
        {
            "complaint_id": "CV-2026-1014",
            "citizen_name": "[Synthetic] Bhavna P.",
            "citizen_contact": "synthetic.bhavna@civicai.demo",
            "title": "Asphalt collapse around underground utility trench",
            "description": "Road surface caved in following pipe trench refill. 25cm drop across the entire left lane.",
            "category": "Road Damage",
            "location_name": "100 Feet Road near CMH Road junction, Indiranagar",
            "latitude": 12.9790,
            "longitude": 77.6415,
            "image_url": "/static/images/samples/pothole_crater_1.svg",
            "priority": "High",
            "priority_score": 80,
            "priority_explanation": "High priority: Carriageway structural subsidence posing immediate vehicle undercarriage crash hazard.",
            "status": "Assigned",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "K. Venkatesh (Road Inspector)",
            "hours_ago": 14,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1015",
            "citizen_name": "[Synthetic] Suresh K.",
            "citizen_contact": "synthetic.suresh@civicai.demo",
            "title": "Series of multiple deep potholes across both lanes",
            "description": "Bitumen disintegrated over 40 meters. Cars forced to brake abruptly, causing near rear-end collisions.",
            "category": "Road Damage",
            "location_name": "100 Feet Road, Near Domlur Flyover descent",
            "latitude": 12.9788,
            "longitude": 77.6420,
            "image_url": "/static/images/samples/pothole_crater_1.svg",
            "priority": "Medium",
            "priority_score": 56,
            "priority_explanation": "Medium priority: Surface wear across corridor requiring hot-mix leveling patch order.",
            "status": "In Progress",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "Asphalt Patch Crew 2",
            "hours_ago": 26,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1016",
            "citizen_name": "[Synthetic] Tara D.",
            "citizen_contact": "synthetic.tara@civicai.demo",
            "title": "Broken uneven road surface damaging car suspensions",
            "description": "Rough road patches and exposed gravel causing wheel alignment damage and dust pollution.",
            "category": "Road Damage",
            "location_name": "100 Feet Road, Opposite Metro Station",
            "latitude": 12.9778,
            "longitude": 77.6402,
            "image_url": "/static/images/samples/pothole_crater_1.svg",
            "priority": "Medium",
            "priority_score": 44,
            "priority_explanation": "Medium priority: Road roughness index elevated. Resurfacing schedule requested.",
            "status": "Submitted",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "Unassigned",
            "hours_ago": 3,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1017",
            "citizen_name": "[Synthetic] Manoj P.",
            "citizen_contact": "synthetic.manoj@civicai.demo",
            "title": "Dislodged cobblestone curb causing two-wheeler skid",
            "description": "Concrete curbstone loose on roadside. Repaired by municipal patch crew.",
            "category": "Road Damage",
            "location_name": "100 Feet Road, 10th Main corner",
            "latitude": 12.9795,
            "longitude": 77.6425,
            "image_url": "/static/images/samples/pothole_resolved_1.svg",
            "priority": "Low",
            "priority_score": 28,
            "priority_explanation": "Low priority: Minor edge curb realignment. Remediation completed.",
            "status": "Resolved",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "K. Venkatesh (Road Inspector)",
            "hours_ago": 48,
            "resolved_hours_ago": 12,
            "sla_hours": 168,
            "is_duplicate": 0,
            "resolution_notes": "Curbstone reset in high-grade cement mortar and painted with reflective yellow stripes.",
            "resolution_image_url": "/static/images/samples/pothole_resolved_1.svg",
            "citizen_rating": 5,
            "citizen_feedback": "Fast resolution, curbstone securely anchored. Thank you!"
        },

        # =========================================================================
        # HOTSPOT 4: HSR Layout Sector 1 & 2 (Streetlight & Electrical - 5 Complaints)
        # =========================================================================
        {
            "complaint_id": "CV-2026-1018",
            "citizen_name": "[Synthetic] Nikhil T.",
            "citizen_contact": "synthetic.nikhil@civicai.demo",
            "title": "Live electric wire snapped and sparking on wet sidewalk",
            "description": "Live high-voltage electrical cable hanging down to pedestrian height, throwing sparks onto wet pavement outside park.",
            "category": "Streetlight",
            "location_name": "27th Main Road, Sector 1 HSR Layout",
            "latitude": 12.9121,
            "longitude": 77.6445,
            "image_url": "/static/images/samples/electrical_wire_1.svg",
            "priority": "High",
            "priority_score": 98,
            "priority_explanation": "High priority: Immediate lethal electrocution threat from exposed live electrical wire on public pavement.",
            "status": "In Progress",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "V. Murthy (Line Inspector)",
            "hours_ago": 2,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1019",
            "citizen_name": "[Synthetic] Priya S.",
            "citizen_contact": "synthetic.priya@civicai.demo",
            "title": "Hanging live wire from street pole near children play area",
            "description": "Broken power line cable sparking on street pole near park corner. High shock danger for pedestrians.",
            "category": "Streetlight",
            "location_name": "Sector 1 Park Perimeter, HSR Layout",
            "latitude": 12.9123,
            "longitude": 77.6447,
            "image_url": "/static/images/samples/electrical_wire_1.svg",
            "priority": "High",
            "priority_score": 96,
            "priority_explanation": "Duplicate Radar: 93% match with CV-2026-1018 (Distance 25m).",
            "status": "Under Review",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "Unassigned",
            "hours_ago": 1,
            "sla_hours": 24,
            "is_duplicate": 1,
            "merged_into_id": 18
        },
        {
            "complaint_id": "CV-2026-1020",
            "citizen_name": "[Synthetic] Sandeep V.",
            "citizen_contact": "synthetic.sandeep@civicai.demo",
            "title": "Streetlights completely dark along entire 27th Main cross road",
            "description": "Total blackout of 8 consecutive streetlights for 3 nights. Women and elderly feel unsafe walking home.",
            "category": "Streetlight",
            "location_name": "27th Main Road, Sector 2 HSR Layout",
            "latitude": 12.9135,
            "longitude": 77.6450,
            "image_url": "/static/images/samples/electrical_wire_1.svg",
            "priority": "Medium",
            "priority_score": 64,
            "priority_explanation": "Medium priority: Public safety & anti-social deterrence compromise due to multi-lamp circuit outage.",
            "status": "Assigned",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "Feeder Squad 5",
            "hours_ago": 18,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1021",
            "citizen_name": "[Synthetic] Meenakshi K.",
            "citizen_contact": "synthetic.meenakshi@civicai.demo",
            "title": "Damaged streetlight pole leaning dangerously over road",
            "description": "Heavy goods truck struck the lamp post base. Pole is tilted at 45 degrees, threatening to collapse on traffic.",
            "category": "Streetlight",
            "location_name": "19th Main Road, Sector 1 HSR Layout",
            "latitude": 12.9115,
            "longitude": 77.6438,
            "image_url": "/static/images/samples/electrical_wire_1.svg",
            "priority": "High",
            "priority_score": 84,
            "priority_explanation": "High priority: Structural tipping hazard of steel luminaire column over active carriageway.",
            "status": "Assigned",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "Crane & Pole Recovery Unit",
            "hours_ago": 8,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1022",
            "citizen_name": "[Synthetic] Amit J.",
            "citizen_contact": "synthetic.amit@civicai.demo",
            "title": "Flickering sodium vapor street light causing blackout at blind turn",
            "description": "Single lamp fixture blinking on and off intermittently on residential corner.",
            "category": "Streetlight",
            "location_name": "14th Cross, Sector 2 HSR Layout",
            "latitude": 12.9128,
            "longitude": 77.6455,
            "image_url": "/static/images/samples/electrical_wire_1.svg",
            "priority": "Low",
            "priority_score": 26,
            "priority_explanation": "Low priority: Routine LED bulb driver swap work order.",
            "status": "Submitted",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "Unassigned",
            "hours_ago": 4,
            "sla_hours": 168,
            "is_duplicate": 0
        },

        # =========================================================================
        # HOTSPOT 5: Malleshwaram 8th Cross (Garbage & Sanitation - 5 Complaints)
        # =========================================================================
        {
            "complaint_id": "CV-2026-1023",
            "citizen_name": "[Synthetic] Preeti N.",
            "citizen_contact": "synthetic.preeti@civicai.demo",
            "title": "Massive uncollected garbage dump overflowing with toxic stench",
            "description": "Solid waste piled up for 6 days on corner plot. Rotting wet waste, street dog menace, unbearable foul stench.",
            "category": "Garbage",
            "location_name": "8th Cross Road, Malleshwaram Market Corner",
            "latitude": 13.0035,
            "longitude": 77.5689,
            "image_url": "/static/images/samples/garbage_pile_1.svg",
            "priority": "High",
            "priority_score": 82,
            "priority_explanation": "High priority: Acute sanitation collapse, stray animal infestation, and disease vector risks outside market.",
            "status": "In Progress",
            "assigned_department": "Solid Waste Management (SWM)",
            "assigned_officer": "M. Swamy (Sanitation Lead)",
            "hours_ago": 12,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1024",
            "citizen_name": "[Synthetic] Arvind K.",
            "citizen_contact": "synthetic.arvind@civicai.demo",
            "title": "Overflowing community dustbin spilling rotten waste on street",
            "description": "Garbage dump pile overflowing across footpath on 8th Cross Malleshwaram with bad smell and stray animals.",
            "category": "Garbage",
            "location_name": "8th Cross Road near Temple Gate, Malleshwaram",
            "latitude": 13.0037,
            "longitude": 77.5691,
            "image_url": "/static/images/samples/garbage_pile_1.svg",
            "priority": "High",
            "priority_score": 80,
            "priority_explanation": "Duplicate Radar: 91% match with CV-2026-1023 (Distance 28m).",
            "status": "Under Review",
            "assigned_department": "Solid Waste Management (SWM)",
            "assigned_officer": "Unassigned",
            "hours_ago": 8,
            "sla_hours": 24,
            "is_duplicate": 1,
            "merged_into_id": 23
        },
        {
            "complaint_id": "CV-2026-1025",
            "citizen_name": "[Synthetic] Geeta B.",
            "citizen_contact": "synthetic.geeta@civicai.demo",
            "title": "Illegal plastic and commercial vegetable waste dumping near temple",
            "description": "Commercial crates and plastic packing discarded on public street by wholesale vendors overnight.",
            "category": "Garbage",
            "location_name": "Margosa Road, Near 8th Cross Malleshwaram",
            "latitude": 13.0042,
            "longitude": 77.5695,
            "image_url": "/static/images/samples/garbage_pile_1.svg",
            "priority": "Medium",
            "priority_score": 54,
            "priority_explanation": "Medium priority: Commercial dumping violation. Tipper truck clearance and warning notice needed.",
            "status": "Assigned",
            "assigned_department": "Solid Waste Management (SWM)",
            "assigned_officer": "M. Swamy (Sanitation Lead)",
            "hours_ago": 15,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1026",
            "citizen_name": "[Synthetic] Sunil D.",
            "citizen_contact": "synthetic.sunil@civicai.demo",
            "title": "Rotting animal waste and unsegregated trash blocking footpath",
            "description": "Footpath unusable due to damp refuse bags left torn by dogs. Schoolchildren forced onto roadway.",
            "category": "Garbage",
            "location_name": "8th Cross Road Footpath, Malleshwaram",
            "latitude": 13.0028,
            "longitude": 77.5682,
            "image_url": "/static/images/samples/garbage_pile_1.svg",
            "priority": "Medium",
            "priority_score": 50,
            "priority_explanation": "Medium priority: Pedestrian impediment and street cleanliness restoration.",
            "status": "Submitted",
            "assigned_department": "Solid Waste Management (SWM)",
            "assigned_officer": "Unassigned",
            "hours_ago": 3,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1027",
            "citizen_name": "[Synthetic] Latha R.",
            "citizen_contact": "synthetic.latha@civicai.demo",
            "title": "Litter and scattered paper debris outside market entrance",
            "description": "Paper waste and cardboard packaging cleared by morning municipal sweep team.",
            "category": "Garbage",
            "location_name": "8th Cross Market Gate, Malleshwaram",
            "latitude": 13.0048,
            "longitude": 77.5702,
            "image_url": "/static/images/samples/garbage_resolved_1.svg",
            "priority": "Low",
            "priority_score": 24,
            "priority_explanation": "Low priority: Routine market floor sanitation completed by morning shift.",
            "status": "Resolved",
            "assigned_department": "Solid Waste Management (SWM)",
            "assigned_officer": "M. Swamy (Sanitation Lead)",
            "hours_ago": 36,
            "resolved_hours_ago": 10,
            "sla_hours": 168,
            "is_duplicate": 0,
            "resolution_notes": "Spot completely cleared, swept and disinfected with bleaching powder by market squad.",
            "resolution_image_url": "/static/images/samples/garbage_resolved_1.svg",
            "citizen_rating": 5,
            "citizen_feedback": "Market entrance is spotlessly clean now. Appreciate the swift action!"
        },

        # =========================================================================
        # STANDALONE COMPLAINTS & BENCHMARKS ACROSS CITY (13 Complaints)
        # =========================================================================
        {
            "complaint_id": "CV-2026-1028",
            "citizen_name": "[Synthetic] Vinay M.",
            "citizen_contact": "synthetic.vinay@civicai.demo",
            "title": "Large Gulmohar tree branch fell across road crushing telephone wires",
            "description": "Massive branch snapped during gale winds, blocking two lanes and snapping telecom cables near Post Office.",
            "category": "Other",
            "location_name": "Raj Bhavan Road near GPO",
            "latitude": 12.9820,
            "longitude": 77.5980,
            "image_url": "/static/images/samples/tree_fallen_1.svg",
            "priority": "High",
            "priority_score": 86,
            "priority_explanation": "High priority: Arterial road obstruction and live utility line entanglements.",
            "status": "In Progress",
            "assigned_department": "Horticulture & Forestry Wing",
            "assigned_officer": "Chainsaw Emergency Team",
            "hours_ago": 6,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1029",
            "citizen_name": "[Synthetic] Shalini T.",
            "citizen_contact": "synthetic.shalini@civicai.demo",
            "title": "Broken tree limb blocking traffic near general post office",
            "description": "Fallen tree branch on road near GPO causing major traffic jam and cable obstruction.",
            "category": "Other",
            "location_name": "Raj Bhavan Road GPO Junction",
            "latitude": 12.9822,
            "longitude": 77.5982,
            "image_url": "/static/images/samples/tree_fallen_1.svg",
            "priority": "High",
            "priority_score": 84,
            "priority_explanation": "Duplicate Radar: 90% match with CV-2026-1028 (Distance 30m).",
            "status": "Under Review",
            "assigned_department": "Horticulture & Forestry Wing",
            "assigned_officer": "Unassigned",
            "hours_ago": 4,
            "sla_hours": 24,
            "is_duplicate": 1,
            "merged_into_id": 28
        },
        {
            "complaint_id": "CV-2026-1030",
            "citizen_name": "[Synthetic] Rajesh G.",
            "citizen_contact": "synthetic.rajesh@civicai.demo",
            "title": "Dangerous deep pothole on MG Road outside metro station",
            "description": "Crater filled with cold-mix asphalt and compacted with steel roller.",
            "category": "Road Damage",
            "location_name": "MG Road Metro Station Gate 3",
            "latitude": 12.9750,
            "longitude": 77.6080,
            "image_url": "/static/images/samples/pothole_resolved_1.svg",
            "priority": "High",
            "priority_score": 76,
            "priority_explanation": "High priority: Metro station high footfall zone hazard. Remediation completed.",
            "status": "Resolved",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "Metro Corridor Rapid Crew",
            "hours_ago": 40,
            "resolved_hours_ago": 16,
            "sla_hours": 24,
            "is_duplicate": 0,
            "resolution_notes": "Hot bituminous mix laid, compacted and edges sealed with emulsified tack coat.",
            "resolution_image_url": "/static/images/samples/pothole_resolved_1.svg",
            "citizen_rating": 5,
            "citizen_feedback": "Super fast turnaround within 24 hours. The road is level now."
        },
        {
            "complaint_id": "CV-2026-1031",
            "citizen_name": "[Synthetic] Dr. Anand V.",
            "citizen_contact": "synthetic.anand@civicai.demo",
            "title": "Blocked sewage culvert overflowing onto Victoria Hospital approach road",
            "description": "Sewer overflow obstructing hospital gate. Ambulances and emergency patients facing severe unhygienic conditions.",
            "category": "Drainage",
            "location_name": "Victoria Hospital Approach Road, Kalasipalya",
            "latitude": 12.9620,
            "longitude": 77.5750,
            "image_url": "/static/images/samples/manhole_open_1.svg",
            "priority": "High",
            "priority_score": 90,
            "priority_explanation": "High priority: Direct obstruction to government hospital ambulance emergency entry corridor.",
            "status": "In Progress",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "P. Sudhir (Medical Corridor Safety)",
            "hours_ago": 14,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1032",
            "citizen_name": "[Synthetic] Fatima Z.",
            "citizen_contact": "synthetic.fatima@civicai.demo",
            "title": "Uncollected biomedical waste bags near nursing home entrance",
            "description": "Yellow hazardous waste bags left discarded on corner sidewalk. Urgent containment required.",
            "category": "Garbage",
            "location_name": "Jayanagar 4th Block, near Nursing Home",
            "latitude": 12.9580,
            "longitude": 77.5820,
            "image_url": "/static/images/samples/garbage_pile_1.svg",
            "priority": "High",
            "priority_score": 86,
            "priority_explanation": "High priority: Hazardous biomedical waste exposure. Immediate bio-containment van dispatched.",
            "status": "Assigned",
            "assigned_department": "Solid Waste Management (SWM)",
            "assigned_officer": "Bio-Waste Enforcement Officer",
            "hours_ago": 9,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1033",
            "citizen_name": "[Synthetic] Deepak C.",
            "citizen_contact": "synthetic.deepak@civicai.demo",
            "title": "Streetlight lamp broken at busy pedestrian zebra crossing",
            "description": "Fixture replaced with energy-efficient 120W LED luminaire.",
            "category": "Streetlight",
            "location_name": "Koramangala 1st Block Crosswalk",
            "latitude": 12.9410,
            "longitude": 77.6180,
            "image_url": "/static/images/samples/electrical_resolved_1.svg",
            "priority": "Medium",
            "priority_score": 50,
            "priority_explanation": "Medium priority: Pedestrian crossing illumination restored.",
            "status": "Resolved",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "BESCOM South Squad",
            "hours_ago": 52,
            "resolved_hours_ago": 18,
            "sla_hours": 72,
            "is_duplicate": 0,
            "resolution_notes": "Defective ballast replaced and new waterproof LED luminaire tested successfully.",
            "resolution_image_url": "/static/images/samples/electrical_resolved_1.svg",
            "citizen_rating": 4,
            "citizen_feedback": "Zebra crossing is well lit now. Great service."
        },
        {
            "complaint_id": "CV-2026-1034",
            "citizen_name": "[Synthetic] Ashok T.",
            "citizen_contact": "synthetic.ashok@civicai.demo",
            "title": "Road cave-in around sewer manhole chamber near bus terminal",
            "description": "Asphalt depression 30cm deep surrounding manhole collar. City buses bottoming out.",
            "category": "Road Damage",
            "location_name": "Majestic Bus Terminal Approach Road",
            "latitude": 12.9770,
            "longitude": 77.5720,
            "image_url": "/static/images/samples/pothole_crater_1.svg",
            "priority": "High",
            "priority_score": 84,
            "priority_explanation": "High priority: Heavy bus fleet corridor structural road settlement.",
            "status": "Under Review",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "Unassigned",
            "hours_ago": 5,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1035",
            "citizen_name": "[Synthetic] Mary K.",
            "citizen_contact": "synthetic.mary@civicai.demo",
            "title": "Waterlogging under railway underbridge submerging cars",
            "description": "Underpass dip filled with 3 feet of rainwater. Multiple cars stuck, underpass closed to traffic.",
            "category": "Waterlogging",
            "location_name": "Cantonment Railway Underbridge",
            "latitude": 12.9920,
            "longitude": 77.5890,
            "image_url": "/static/images/samples/waterlogging_1.svg",
            "priority": "High",
            "priority_score": 94,
            "priority_explanation": "High priority: Complete railway underbridge submergence and traffic gridlock.",
            "status": "In Progress",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "High-Capacity Pump Truck 1",
            "hours_ago": 7,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1036",
            "citizen_name": "[Synthetic] Sanjay V.",
            "citizen_contact": "synthetic.sanjay@civicai.demo",
            "title": "Heavy stormwater backflow inundating basements in residential colony",
            "description": "Secondary storm drain choked, causing backpressure and floodwater gushing into apartment parking lots.",
            "category": "Waterlogging",
            "location_name": "BTM 2nd Stage, Lake Road",
            "latitude": 12.9250,
            "longitude": 77.5930,
            "image_url": "/static/images/samples/waterlogging_2.svg",
            "priority": "High",
            "priority_score": 88,
            "priority_explanation": "High priority: Basement flooding posing electrocution and structural foundation risk.",
            "status": "Submitted",
            "assigned_department": "Water Supply & Sewerage Board (BWSSB)",
            "assigned_officer": "Unassigned",
            "hours_ago": 2,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1037",
            "citizen_name": "[Synthetic] Rekha N.",
            "citizen_contact": "synthetic.rekha@civicai.demo",
            "title": "Exposed electrical junction box with open wires outside primary school",
            "description": "Metal box door ripped off. Live 230V terminals exposed within hand reach of passing children.",
            "category": "Streetlight",
            "location_name": "Frazer Town, Coles Road School Zone",
            "latitude": 12.9860,
            "longitude": 77.6110,
            "image_url": "/static/images/samples/electrical_wire_1.svg",
            "priority": "High",
            "priority_score": 96,
            "priority_explanation": "High priority: Unshielded high voltage junction in pedestrian school corridor.",
            "status": "Assigned",
            "assigned_department": "Electricity Supply Board (BESCOM)",
            "assigned_officer": "BESCOM North Fast Response",
            "hours_ago": 11,
            "sla_hours": 24,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1038",
            "citizen_name": "[Synthetic] Balaji S.",
            "citizen_contact": "synthetic.balaji@civicai.demo",
            "title": "Unauthorized iron advertisement hoarding blocking pedestrian view at turn",
            "description": "Large steel hoarding erected on sidewalk blocking sightline of oncoming vehicular traffic.",
            "category": "Other",
            "location_name": "Old Airport Road, Kodihalli Junction",
            "latitude": 12.9690,
            "longitude": 77.6320,
            "image_url": "/static/images/samples/tree_fallen_1.svg",
            "priority": "Medium",
            "priority_score": 48,
            "priority_explanation": "Medium priority: Pedestrian right-of-way encroachment and intersection blindspot.",
            "status": "Submitted",
            "assigned_department": "Municipal Administration",
            "assigned_officer": "Unassigned",
            "hours_ago": 4,
            "sla_hours": 72,
            "is_duplicate": 0
        },
        {
            "complaint_id": "CV-2026-1039",
            "citizen_name": "[Synthetic] Girish L.",
            "citizen_contact": "synthetic.girish@civicai.demo",
            "title": "Faded pedestrian crosswalk and cracked curb near public library",
            "description": "Zebra crossing repainted with thermo-plastic retroreflective paint and curb re-mortared.",
            "category": "Road Damage",
            "location_name": "Cubbon Park Library Road",
            "latitude": 12.9730,
            "longitude": 77.5850,
            "image_url": "/static/images/samples/pothole_resolved_1.svg",
            "priority": "Low",
            "priority_score": 26,
            "priority_explanation": "Low priority: Routine traffic marking maintenance completed.",
            "status": "Resolved",
            "assigned_department": "Public Works Department (PWD)",
            "assigned_officer": "Road Marking Division",
            "hours_ago": 60,
            "resolved_hours_ago": 24,
            "sla_hours": 168,
            "is_duplicate": 0,
            "resolution_notes": "Reflective thermo-plastic road paint applied with glass beads for night visibility.",
            "resolution_image_url": "/static/images/samples/pothole_resolved_1.svg",
            "citizen_rating": 5,
            "citizen_feedback": "Zebra crossing looks pristine and safe now!"
        },
        {
            "complaint_id": "CV-2026-1040",
            "citizen_name": "[Synthetic] Usha P.",
            "citizen_contact": "synthetic.usha@civicai.demo",
            "title": "Fallen park boundary fence causing stray dog intrusion",
            "description": "Wire mesh fence bent down over 10 meters along park boundary track.",
            "category": "Other",
            "location_name": "Langford Gardens Public Park",
            "latitude": 12.9650,
            "longitude": 77.6150,
            "image_url": "/static/images/samples/tree_fallen_1.svg",
            "priority": "Low",
            "priority_score": 22,
            "priority_explanation": "Low priority: Non-hazardous civic property fencing repair work order.",
            "status": "Submitted",
            "assigned_department": "Horticulture & Forestry Wing",
            "assigned_officer": "Unassigned",
            "hours_ago": 3,
            "sla_hours": 168,
            "is_duplicate": 0
        }
    ]

    for item in raw_seed_data:
        created_time = now - timedelta(hours=item["hours_ago"])
        updated_time = created_time + timedelta(hours=1)
        sla_time = created_time + timedelta(hours=item["sla_hours"])
        
        resolved_time_str = None
        if item.get("status") == "Resolved":
            resolved_time = now - timedelta(hours=item.get("resolved_hours_ago", 10))
            resolved_time_str = resolved_time.isoformat()

        # Factors JSON
        factors = [
            {"factor": "Base Category Hazard", "points": 30, "max": 35, "detail": f"Category: {item['category']}"},
            {"factor": "Urgency & Hazard Markers", "points": item["priority_score"] // 3, "max": 35, "detail": item["title"]},
            {"factor": "Footfall & Density Multiplier", "points": 15, "max": 15, "detail": item["location_name"]}
        ]

        # Action brief JSON
        action_brief = {
            "action_title": f"[{item['priority']}] Dispatch to {item['location_name']}",
            "executive_summary": item["title"],
            "target_department": item["assigned_department"],
            "sla_urgency": f"Within {item['sla_hours']} Hours",
            "recommended_crew": "Field Rapid Response Squad"
        }

        cursor.execute("""
        INSERT INTO complaints (
            complaint_id, citizen_name, citizen_contact, title, description,
            category, location_name, latitude, longitude, image_url,
            priority, priority_score, priority_explanation, priority_factors_json,
            status, assigned_department, assigned_officer, created_at, updated_at,
            sla_deadline, is_duplicate, merged_into_id, resolution_notes,
            resolution_image_url, resolved_at, citizen_rating, citizen_feedback,
            action_brief_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item["complaint_id"], item["citizen_name"], item["citizen_contact"], item["title"], item["description"],
            item["category"], item["location_name"], item["latitude"], item["longitude"], item["image_url"],
            item["priority"], item["priority_score"], item["priority_explanation"], json.dumps(factors),
            item["status"], item["assigned_department"], item["assigned_officer"], created_time.isoformat(), updated_time.isoformat(),
            sla_time.isoformat(), item.get("is_duplicate", 0), item.get("merged_into_id"), item.get("resolution_notes"),
            item.get("resolution_image_url"), resolved_time_str, item.get("citizen_rating"), item.get("citizen_feedback"),
            json.dumps(action_brief)
        ))

        comp_db_id = cursor.lastrowid

        # Insert immutable audit log trail
        cursor.execute("""
        INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
        VALUES (?, 'SUBMITTED', 'Complaint received and digitally signed', ?, ?)
        """, (comp_db_id, item["citizen_name"], created_time.isoformat()))

        cursor.execute("""
        INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
        VALUES (?, 'AI_TRIAGE', ?, 'CivicAI Priority Engine', ?)
        """, (comp_db_id, f"Classified {item['priority']} ({item['priority_score']}/100 pts) - Target SLA: {item['sla_hours']}h", (created_time + timedelta(seconds=2)).isoformat()))

        if item["status"] != "Submitted":
            cursor.execute("""
            INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
            VALUES (?, 'STATUS_CHANGE', ?, ?, ?)
            """, (comp_db_id, f"Status updated to '{item['status']}'", item["assigned_officer"] if item["assigned_officer"] != "Unassigned" else "Municipal Admin", (created_time + timedelta(hours=1)).isoformat()))

        if item["status"] == "Resolved":
            cursor.execute("""
            INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
            VALUES (?, 'RESOLVED', ?, ?, ?)
            """, (comp_db_id, f"Remediation completed: {item.get('resolution_notes')}", item["assigned_officer"], resolved_time_str))

    # Seed Community Civic Hero Leaderboard (Synthetic accounts)
    citizens_data = [
        ("[Synthetic] Aarav S.", "synthetic.aarav@civicai.demo", 650, 9, 7, json.dumps(["Eagle Eye", "Civic Guardian", "Hazard Neutralizer"]), "Diamond"),
        ("[Synthetic] Divya S.", "synthetic.divya@civicai.demo", 520, 7, 6, json.dumps(["Eagle Eye", "Civic Guardian", "Clean Street Hero"]), "Diamond"),
        ("[Synthetic] Vikram S.", "synthetic.vikram@civicai.demo", 410, 6, 4, json.dumps(["Eagle Eye", "Road Sentinel"]), "Gold"),
        ("[Synthetic] Ananya R.", "synthetic.ananya@civicai.demo", 330, 5, 3, json.dumps(["Eagle Eye", "Green Pioneer"]), "Gold"),
        ("[Synthetic] Tanvi J.", "synthetic.tanvi@civicai.demo", 240, 4, 3, json.dumps(["Eagle Eye", "Night Watcher"]), "Silver"),
        ("[Synthetic] Harish I.", "synthetic.harish@civicai.demo", 180, 3, 2, json.dumps(["Eagle Eye"]), "Bronze"),
        ("[Synthetic] Bhavna P.", "synthetic.bhavna@civicai.demo", 140, 2, 2, json.dumps(["Eagle Eye"]), "Bronze")
    ]

    for name, contact, points, v_rep, r_rep, badges, tier in citizens_data:
        cursor.execute("""
        INSERT INTO citizens (name, contact, points, verified_reports, resolved_reports, badges_json, tier, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, contact, points, v_rep, r_rep, badges, tier, (now - timedelta(days=20)).isoformat()))

    conn.commit()
    conn.close()
    print("Database cleanly seeded with exactly 40 synthetic smart city complaints!")

def seed_database_if_empty():
    reseed_competition_demo_data(force=False)

if __name__ == "__main__":
    init_db()
    reseed_competition_demo_data(force=True)
