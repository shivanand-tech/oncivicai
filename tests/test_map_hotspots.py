"""
CivicAI - Map & Hotspot Radar Automated Test Suite
Verifies:
1. Map view route and Leaflet/OpenStreetMap markup
2. Hotspot detection API and multi-complaint clustering
3. Marker coordinates and priority color mappings
4. Category filters and search criteria
5. Admin dashboard hotspot panel integration
"""

import sys
import os

# Add root project path to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
import ai_engine

def test_map_route_and_markup():
    print("\n--- TEST 1: MAP PAGE ROUTE & OPENSTREETMAP LEAFLET MARKUP ---")
    client = app.test_client()
    res = client.get("/map")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.get_data(as_text=True)

    # Verify Leaflet and Map components
    assert "mapContainer" in html, "mapContainer div missing from /map"
    assert "leaflet" in html.lower(), "Leaflet assets missing from /map"
    assert "OpenStreetMap" in html, "OpenStreetMap reference missing from /map"
    assert "mapCategoryFilter" in html, "Category filter dropdown missing from /map"
    assert "mapPriorityFilter" in html, "Priority filter dropdown missing from /map"
    assert "hotspotsList" in html, "Hotspots list container missing from /map"
    assert "pin-high" in html, "High priority marker pin styling missing"
    assert "pin-medium" in html, "Medium priority marker pin styling missing"
    assert "pin-low" in html, "Low priority marker pin styling missing"
    print("PASS: /map route loads successfully with Leaflet, OpenStreetMap, category filters, and priority styling.")


def test_hotspot_detection_api():
    print("\n--- TEST 2: HOTSPOT DETECTION & MULTI-COMPLAINT CLUSTERING ---")
    client = app.test_client()
    res = client.get("/api/ai/hotspots")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()

    assert data.get("success") is True, "API call should return success: True"
    hotspots = data.get("hotspots", [])
    print(f"Detected Active Hotspots: {len(hotspots)}")
    assert len(hotspots) >= 2, f"Expected at least 2 hotspots, found {len(hotspots)}"

    for h in hotspots:
        print(f"-> {h['hotspot_id']} | Area: '{h['area_name']}' | {h['complaint_count']} complaints clustered | Category: {h['primary_category']} | Urgency: {h['urgency']} | Radius: {h['radius_meters']}m")
        assert h["complaint_count"] >= 2, "Hotspot must contain multiple complaints (>= 2)"
        assert len(h["center"]) == 2, "Center must be [lat, lng]"
        assert -90 <= h["center"][0] <= 90, "Latitude must be valid"
        assert -180 <= h["center"][1] <= 180, "Longitude must be valid"
        assert h["radius_meters"] > 0, "Radius must be positive"
        assert len(h["complaints"]) == h["complaint_count"], "Complaints array length must match complaint_count"

    print("PASS: Hotspot clustering algorithm successfully groups multiple complaints geographically.")


def test_complaint_coordinates_and_priorities():
    print("\n--- TEST 3: COMPLAINT COORDINATES & PRIORITY DATA INTEGRITY ---")
    client = app.test_client()
    res = client.get("/api/complaints?include_duplicates=true")
    assert res.status_code == 200
    complaints = res.get_json().get("complaints", [])
    assert len(complaints) > 0, "Expected complaints in database"

    valid_coords_count = 0
    prio_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for c in complaints:
        lat = c.get("latitude")
        lng = c.get("longitude")
        assert lat is not None and lng is not None, f"Complaint {c['complaint_id']} missing GPS coordinates"
        assert isinstance(lat, (int, float)) and isinstance(lng, (int, float))
        assert 12.0 <= lat <= 14.0, f"Latitude {lat} out of expected Bangalore range"
        assert 77.0 <= lng <= 78.0, f"Longitude {lng} out of expected Bangalore range"
        valid_coords_count += 1

        prio = (c.get("priority") or "MEDIUM").upper()
        if prio in ["HIGH", "CRITICAL"]:
            prio_counts["HIGH"] += 1
        elif prio == "MEDIUM":
            prio_counts["MEDIUM"] += 1
        else:
            prio_counts["LOW"] += 1

    print(f"Total valid geo-located complaints: {valid_coords_count}")
    print(f"Priority breakdown: High/Critical={prio_counts['HIGH']}, Medium={prio_counts['MEDIUM']}, Low={prio_counts['LOW']}")
    assert prio_counts["HIGH"] > 0, "Should have High priority complaints"
    assert prio_counts["MEDIUM"] > 0, "Should have Medium priority complaints"
    assert prio_counts["LOW"] > 0, "Should have Low priority complaints"
    print("PASS: All complaints have valid synthetic GPS coordinates and span High, Medium, Low priorities.")


def test_admin_dashboard_hotspot_section():
    print("\n--- TEST 4: ADMIN DASHBOARD HOTSPOT INTEGRATION ---")
    client = app.test_client()
    res = client.get("/admin")
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    assert "adminHotspotsGrid" in html, "adminHotspotsGrid element missing from /admin"
    assert "adminHotspotCountBadge" in html, "adminHotspotCountBadge missing from /admin"
    assert "AI Hotspot Radar" in html, "AI Hotspot Radar title missing from /admin"
    print("PASS: Admin dashboard includes Hotspot Radar cards and count badge.")


if __name__ == "__main__":
    test_map_route_and_markup()
    test_hotspot_detection_api()
    test_complaint_coordinates_and_priorities()
    test_admin_dashboard_hotspot_section()
    print("\n==============================================")
    print("ALL MAP & HOTSPOT TESTS PASSED SUCCESSFULLY!")
    print("==============================================")

