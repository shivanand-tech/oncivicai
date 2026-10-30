"""
CivicAI - AI Analysis Engine Automated Test Suite
Verifies:
1. Categorization into Road Damage, Waterlogging, Garbage, Streetlight, Drainage, Other
2. Short executive summary generation
3. Duplicate detection via NLP similarity and Haversine distance
4. Priority calculation (High, Medium, Low)
5. Explainability justifications (bullet points)
   Specifically tests: "Water is entering houses because of road flooding."
"""

import sys
import os

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import ai_engine
from app import app

def test_categorization():
    print("\n--- TEST 1: CATEGORIZATION INTO 6 CATEGORIES ---")
    test_cases = [
        ("Massive deep pothole on the asphalt road causing vehicle tire damage", "Road Damage"),
        ("Water is entering houses because of road flooding during heavy rain", "Waterlogging"),
        ("Large pile of uncollected garbage and rotting trash with bad stench", "Garbage"),
        ("Streetlight not glowing at main dark intersection, pole wire hanging", "Streetlight"),
        ("Open sewer manhole cover missing on footpath, overflow drain", "Drainage"),
        ("Large tree branch broken and blocking pedestrian sidewalk in park", "Other")
    ]

    all_passed = True
    for text, expected in test_cases:
        res = ai_engine.categorize_complaint(text)
        cat = res["category"]
        conf = res["confidence_score"]
        status = "PASS" if cat == expected else "FAIL"
        if status == "FAIL":
            all_passed = False
        print(f"[{status}] Input: '{text[:50]}...' -> Predicted: '{cat}' (Confidence: {conf}%) [Expected: '{expected}']")
    
    assert all_passed, "Categorization tests failed!"
    print(">>> All Categorization tests PASSED!")


def test_user_example_flood():
    print("\n--- TEST 2: USER SPECIFIC EXAMPLE ---")
    text = "Water is entering houses because of road flooding."
    print(f"Complaint: {text}")

    # 1. Categorization
    cat_res = ai_engine.categorize_complaint(text)
    print(f"Category: {cat_res['category']}")
    assert cat_res["category"] == "Waterlogging", f"Expected Waterlogging, got {cat_res['category']}"

    # 2. Priority & Explainability
    complaint_data = {
        "title": "Flooding issue",
        "description": text,
        "category": cat_res["category"],
        "location_name": "Residential Area"
    }
    prio_res = ai_engine.calculate_priority(complaint_data)
    print(f"Priority: {prio_res['priority']}")
    print("Reason:")
    for r in prio_res["reasons"]:
        print(f"- {r}")

    assert prio_res["priority"] == "High", f"Expected High, got {prio_res['priority']}"
    assert "Risk to residential properties." in prio_res["reasons"], "Expected 'Risk to residential properties.' in reasons"
    assert "Potential safety hazard." in prio_res["reasons"], "Expected 'Potential safety hazard.' in reasons"
    assert "Immediate attention required." in prio_res["reasons"], "Expected 'Immediate attention required.' in reasons"
    print(">>> User test case PASSED perfectly!")


def test_summary_generation():
    print("\n--- TEST 3: SHORT SUMMARY GENERATION ---")
    test_cases = [
        ("Flooding in homes", "Water is entering houses because of road flooding.", "Waterlogging", "Indiranagar 5th Cross"),
        ("Deep crater pothole", "Deep road crater causing bike accidents near school gate.", "Road Damage", "MG Road"),
        ("Rotting trash dump", "Garbage pile uncollected for days attracting stray animals.", "Garbage", "BTM Layout")
    ]

    for title, desc, cat, loc in test_cases:
        summary = ai_engine.generate_complaint_summary(title, desc, cat, loc)
        print(f"Title: {title} | Loc: {loc}")
        print(f"AI Summary: {summary}")
        assert len(summary) > 20, "Summary too short"
        assert cat.lower() in summary.lower(), "Category should be referenced"
    print(">>> Summary generation tests PASSED!")


def test_duplicate_detection():
    print("\n--- TEST 4: DUPLICATE DETECTION (TEXT SIMILARITY + HAVERSINE) ---")
    target = {
        "id": 999,
        "title": "Hazardous open sewer manhole near St. Joseph School",
        "description": "Deep open manhole without cover right outside St. Joseph School gate.",
        "category": "Drainage",
        "latitude": 12.9712,
        "longitude": 77.6015
    }

    candidates = [
        {
            "id": 101,
            "complaint_id": "CV-TEST-1",
            "title": "Open manhole chamber on school footpath",
            "description": "There is an uncovered drainage manhole on sidewalk near school.",
            "category": "Drainage",
            "latitude": 12.9714,   # ~25 meters away
            "longitude": 77.6017,
            "status": "Submitted"
        },
        {
            "id": 102,
            "complaint_id": "CV-TEST-2",
            "title": "Garbage pile in another city zone",
            "description": "Trash overflow near market place.",
            "category": "Garbage",
            "latitude": 12.9352,   # ~5 km away
            "longitude": 77.6245,
            "status": "Submitted"
        }
    ]

    dups = ai_engine.detect_duplicates(target, candidates, threshold=45)
    print(f"Duplicates detected for target: {len(dups)}")
    for d in dups:
        print(f"-> Match: {d['complaint_id']} | Distance: {d['distance_meters']}m | Similarity: {d['similarity_score']}% | Reasons: {d['reasons']}")

    assert len(dups) == 1, f"Expected 1 duplicate, got {len(dups)}"
    assert dups[0]["candidate_id"] == 101, "Expected candidate 101 to be flagged as duplicate"
    assert dups[0]["distance_meters"] < 50, "Distance should be under 50 meters"
    print(">>> Duplicate detection tests PASSED!")


def test_priority_tiers():
    print("\n--- TEST 5: PRIORITY TIERS (HIGH, MEDIUM, LOW) ---")
    # High Priority Case
    high_input = {
        "title": "Live electric wire sparking",
        "description": "Live wire snapped and sparking on wet road near children play area",
        "category": "Streetlight",
        "location_name": "Park View Road"
    }
    p_high = ai_engine.calculate_priority(high_input)
    print(f"High Case: {p_high['priority']} (Score: {p_high['score']}) - Reasons: {p_high['reasons'][:2]}")
    assert p_high["priority"] == "High"

    # Medium Priority Case
    med_input = {
        "title": "Streetlight bulb fused",
        "description": "Streetlight lamp not turning on at night, bulb is fused",
        "category": "Streetlight",
        "location_name": "Residential 3rd Cross"
    }
    p_med = ai_engine.calculate_priority(med_input)
    print(f"Medium Case: {p_med['priority']} (Score: {p_med['score']}) - Reasons: {p_med['reasons'][:2]}")
    assert p_med["priority"] == "Medium"

    # Low Priority Case
    low_input = {
        "title": "Park bench paint peeling",
        "description": "The wooden paint on the park bench has faded slightly",
        "category": "Other",
        "location_name": "Public Park"
    }
    p_low = ai_engine.calculate_priority(low_input)
    print(f"Low Case: {p_low['priority']} (Score: {p_low['score']}) - Reasons: {p_low['reasons'][:2]}")
    assert p_low["priority"] == "Low"
    print(">>> Priority tier tests PASSED!")


def test_api_integration():
    print("\n--- TEST 6: BACKEND API END-TO-END INTEGRATION ---")
    client = app.test_client()

    # 1. Submit complaint using API
    payload = {
        "citizen_name": "Ananya Roy",
        "citizen_contact": "ananya@example.com",
        "title": "Severe road flooding inundating homes",
        "description": "Water is entering houses because of road flooding.",
        "category": "Waterlogging",
        "location_name": "Koramangala 4th Block",
        "latitude": 12.9345,
        "longitude": 77.6250
    }
    res = client.post("/api/complaints", json=payload)
    assert res.status_code == 200, f"Submit failed: {res.data}"
    data = res.get_json()
    print("API Submit Response:")
    print(f"- Complaint ID: {data['complaint_id']}")
    print(f"- Category: {data['category']}")
    print(f"- Priority: {data['priority']}")
    print(f"- Summary: {data['summary']}")
    print(f"- Priority Reasons: {data['priority_reasons']}")

    assert data["category"] == "Waterlogging"
    assert data["priority"] == "High"
    assert "Risk to residential properties." in data["priority_reasons"]

    # 2. Retrieve complaint detail
    cid = data["complaint_id"]
    res2 = client.get(f"/api/complaints/{cid}")
    assert res2.status_code == 200
    c_detail = res2.get_json()["complaint"]
    assert c_detail["summary"] is not None
    assert len(c_detail["priority_reasons"]) > 0

    # Clean up test complaint so DB stays pristine at 40
    with app.app_context():
        import database
        conn = database.get_db()
        conn.execute("DELETE FROM audit_logs WHERE complaint_id = ?", (data["id"],))
        conn.execute("DELETE FROM complaints WHERE id = ?", (data["id"],))
        conn.execute("UPDATE sqlite_sequence SET seq = 40 WHERE name = 'complaints'")
        conn.commit()

    print(">>> API Integration tests PASSED!")


if __name__ == "__main__":
    test_categorization()
    test_user_example_flood()
    test_summary_generation()
    test_duplicate_detection()
    test_priority_tiers()
    test_api_integration()
    print("\n==============================================")
    print("ALL AI ENGINE VERIFICATION TESTS PASSED (6/6)!")
    print("==============================================")

