"""
CivicAI - Complete Complaint Management Lifecycle Test Suite
Verifies:
1. Unique Complaint ID Generation
2. Citizen Tracking using Complaint ID
3. Current Status Visibility
4. Progression Timeline & Audit Trail
5. Admin Department & Officer Assignment
6. Admin Status Lifecycle Transitions (Submitted -> Under Review -> Assigned -> In Progress -> Resolved)
7. SQLite Persistence for all status changes
8. Citizen Tracking Page display of updated status & remediation notes
"""

import sys
import os
import sqlite3

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from database import DB_PATH

def test_full_lifecycle_workflow():
    client = app.test_client()

    print("\n=======================================================")
    print("STEP 1: CITIZEN COMPLAINT SUBMISSION & UNIQUE ID GEN")
    print("=======================================================")

    payload = {
        "citizen_name": "Siddharth Rao",
        "citizen_contact": "siddharth.rao@example.com",
        "title": "Hazardous road crater on Residency Road",
        "description": "Deep asphalt crater causing two-wheeler skid hazards near metro pillar 45.",
        "category": "Road Damage",
        "location_name": "Residency Road near Metro Pillar 45",
        "latitude": 12.9715,
        "longitude": 77.6018
    }

    res = client.post("/api/complaints", json=payload)
    assert res.status_code == 200, f"Submit failed: {res.data}"
    data = res.get_json()

    complaint_id = data.get("complaint_id")
    db_id = data.get("id")

    print(f"Generated Unique Complaint ID: {complaint_id} (DB ID: {db_id})")
    assert complaint_id is not None, "Complaint ID must not be None"
    assert complaint_id.startswith("CV-2026-"), f"Unexpected format: {complaint_id}"
    assert data["priority"] in ["High", "Medium", "Low"], "Priority must be High, Medium, or Low"

    # Verify SQLite Initial Record
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE complaint_id = ?", (complaint_id,))
    row = cursor.fetchone()
    assert row is not None, "Complaint record not found in SQLite!"
    assert row["status"] == "Submitted", f"Initial status must be 'Submitted', got {row['status']}"
    print(f"PASS: Complaint {complaint_id} saved in SQLite with status 'Submitted'.")

    # Verify Initial Audit Logs
    cursor.execute("SELECT * FROM audit_logs WHERE complaint_id = ? ORDER BY id ASC", (db_id,))
    initial_logs = cursor.fetchall()
    print(f"Initial Audit Logs Created: {len(initial_logs)} events")
    assert len(initial_logs) >= 2, "Expected at least SUBMITTED and AI_TRIAGE audit logs"
    conn.close()

    print("\n=======================================================")
    print("STEP 2: CITIZEN INITIAL TRACKING CHECK")
    print("=======================================================")

    track_res = client.get(f"/api/complaints/{complaint_id}")
    assert track_res.status_code == 200
    c_info = track_res.get_json()["complaint"]
    assert c_info["status"] == "Submitted"
    assert c_info["complaint_id"] == complaint_id
    assert c_info["citizen_name"] == "Siddharth Rao"
    print(f"PASS: Citizen can track {complaint_id}. Current status: '{c_info['status']}'.")

    print("\n=======================================================")
    print("STEP 3: ADMIN MOVES STATUS TO 'UNDER REVIEW'")
    print("=======================================================")

    update1 = client.post(f"/api/complaints/{complaint_id}/status", json={
        "status": "Under Review",
        "actor": "Triage Officer Meera"
    })
    assert update1.status_code == 200
    u1_data = update1.get_json()
    assert u1_data["status"] == "Under Review"

    # Verify SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM complaints WHERE id = ?", (db_id,))
    assert cursor.fetchone()[0] == "Under Review"
    conn.close()
    print(f"PASS: Status successfully updated to 'Under Review' and persisted in SQLite.")

    print("\n=======================================================")
    print("STEP 4: ADMIN ASSIGNS DEPARTMENT AND FIELD OFFICER")
    print("=======================================================")

    update2 = client.post(f"/api/complaints/{complaint_id}/status", json={
        "status": "Assigned",
        "assigned_department": "Public Works Department (PWD)",
        "assigned_officer": "R. Kulkarni (Executive Engineer)",
        "actor": "Operations Director"
    })
    assert update2.status_code == 200

    # Verify SQLite Persistence of Department and Officer
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT status, assigned_department, assigned_officer FROM complaints WHERE id = ?", (db_id,))
    row2 = cursor.fetchone()
    assert row2["status"] == "Assigned"
    assert row2["assigned_department"] == "Public Works Department (PWD)"
    assert row2["assigned_officer"] == "R. Kulkarni (Executive Engineer)"
    conn.close()
    print(f"PASS: Assigned to '{row2['assigned_department']}', Officer: '{row2['assigned_officer']}'.")

    print("\n=======================================================")
    print("STEP 5: FIELD CREW COMMENCES WORK ('IN PROGRESS')")
    print("=======================================================")

    update3 = client.post(f"/api/complaints/{complaint_id}/status", json={
        "status": "In Progress",
        "resolution_notes": "Road crew deployed with 2-ton roller and cold mix asphalt. Barricades placed.",
        "actor": "R. Kulkarni (Field Officer)"
    })
    assert update3.status_code == 200

    # Verify SQLite
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT status, resolution_notes FROM complaints WHERE id = ?", (db_id,))
    row3 = cursor.fetchone()
    assert row3["status"] == "In Progress"
    assert "cold mix asphalt" in row3["resolution_notes"]
    conn.close()
    print("PASS: Status updated to 'In Progress' with field deployment notes saved.")

    print("\n=======================================================")
    print("STEP 6: FIELD CREW COMPLETES REPAIR ('RESOLVED')")
    print("=======================================================")

    update4 = client.post(f"/api/complaints/{complaint_id}/status", json={
        "status": "Resolved",
        "resolution_notes": "Crater completely filled, compacted and leveled. Road cleared and reopened for safe traffic.",
        "actor": "R. Kulkarni (Field Officer)"
    })
    assert update4.status_code == 200

    # Verify SQLite Final State
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT status, resolved_at, resolution_notes, resolution_image_url FROM complaints WHERE id = ?", (db_id,))
    row4 = cursor.fetchone()
    assert row4["status"] == "Resolved"
    assert row4["resolved_at"] is not None
    assert "reopened for safe traffic" in row4["resolution_notes"]
    assert row4["resolution_image_url"] is not None

    # Verify Complete Audit Trail
    cursor.execute("SELECT event_type, description, actor, timestamp FROM audit_logs WHERE complaint_id = ? ORDER BY id ASC", (db_id,))
    all_logs = cursor.fetchall()
    print(f"\nFinal Audit Log Trail ({len(all_logs)} recorded events):")
    for log in all_logs:
        print(f"  • [{log['event_type']}] {log['description']} (By: {log['actor']})")
    
    assert len(all_logs) >= 5, "Expected comprehensive audit trail spanning all lifecycle events"
    conn.close()
    print("PASS: Complaint successfully resolved in SQLite with timestamp and photo evidence.")

    print("\n=======================================================")
    print("STEP 7: CITIZEN TRACKS RESOLVED COMPLAINT & VERIFIES")
    print("=======================================================")

    track_final = client.get(f"/api/complaints/{complaint_id}")
    assert track_final.status_code == 200
    final_info = track_final.get_json()["complaint"]

    assert final_info["status"] == "Resolved"
    assert final_info["assigned_department"] == "Public Works Department (PWD)"
    assert final_info["assigned_officer"] == "R. Kulkarni (Executive Engineer)"
    assert "reopened for safe traffic" in final_info["resolution_notes"]
    assert len(final_info["timeline"]) >= 5
    print(f"PASS: Citizen tracking view verified:")
    print(f"      • Final Status: {final_info['status']}")
    print(f"      • Department: {final_info['assigned_department']}")
    print(f"      • Field Officer: {final_info['assigned_officer']}")
    print(f"      • Notes: {final_info['resolution_notes']}")
    print(f"      • Timeline Events Count: {len(final_info['timeline'])}")

    print("\n=======================================================")
    print("STEP 8: CITIZEN SUBMITS 5-STAR VERIFICATION RATING")
    print("=======================================================")

    rate_res = client.post(f"/api/complaints/{db_id}/rate", json={
        "rating": 5,
        "feedback": "Smooth patch job, no more dangerous bike skids. Thanks BBMP!"
    })
    assert rate_res.status_code == 200

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT citizen_rating, citizen_feedback FROM complaints WHERE id = ?", (db_id,))
    row_rating = cursor.fetchone()
    assert row_rating["citizen_rating"] == 5
    assert "Smooth patch job" in row_rating["citizen_feedback"]
    print("PASS: Citizen verification rating recorded in SQLite.")

    # Clean up test complaint so DB stays pristine at 40
    cursor.execute("DELETE FROM audit_logs WHERE complaint_id = ?", (db_id,))
    cursor.execute("DELETE FROM complaints WHERE id = ?", (db_id,))
    cursor.execute("UPDATE sqlite_sequence SET seq = 40 WHERE name = 'complaints'")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    test_full_lifecycle_workflow()
    print("\n==================================================================")
    print("ALL 8 COMPLAINT WORKFLOW REQUIREMENTS VERIFIED 100% SUCCESSFULLY!")
    print("==================================================================")

