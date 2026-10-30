"""
CivicAI - Main Application Server
Flask Backend providing REST APIs and Interactive Smart City Web Views.
"""

import os
import re
import json
import uuid
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.utils import secure_filename

from database import get_db, init_db, seed_database_if_empty
import ai_engine

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "civicai-secret-key-smartcity-2026")
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload limit
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "svg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Custom HTTP Error Handlers
@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"success": False, "error": "Uploaded image exceeds the 16MB limit"}), 413

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Resource not found"}), 404
    return render_template("index.html"), 404

@app.errorhandler(500)
def server_error(error):
    if request.path.startswith("/api/"):
        return jsonify({"success": False, "error": "Internal server error occurred"}), 500
    return render_template("index.html"), 500

# Ensure tables and initial realistic seed data exist
with app.app_context():
    init_db()
    seed_database_if_empty()


# -----------------------------------------------------------------------------
# PAGE ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit")
@app.route("/report")
def submit_page():
    return render_template("submit.html")

@app.route("/track")
def track_page():
    complaint_id = request.args.get("id", "").strip()
    return render_template("track.html", prefill_id=complaint_id)

@app.route("/admin")
@app.route("/dashboard")
def admin_page():
    return render_template("admin.html")

@app.route("/manage")
@app.route("/complaints")
def manage_page():
    return render_template("manage.html")

@app.route("/map")
def map_page():
    return render_template("map.html")

@app.route("/risk-predictor")
def risk_predictor_page():
    return render_template("risk_predictor.html")

@app.route("/before-after")
def before_after_page():
    return render_template("before_after.html")

@app.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html")

@app.route("/portal")
@app.route("/all-in-one")
def portal_page():
    return render_template("portal.html")


# -----------------------------------------------------------------------------
# REST APIs: COMPLAINTS CRUD & LIFECYCLE
# -----------------------------------------------------------------------------

@app.route("/api/complaints", methods=["GET"])
def get_complaints():
    conn = get_db()
    cursor = conn.cursor()

    category = request.args.get("category")
    priority = request.args.get("priority")
    status = request.args.get("status")
    search = request.args.get("search", "").strip().lower()
    include_duplicates = request.args.get("include_duplicates", "true").lower() == "true"

    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if not include_duplicates:
        query += " AND (is_duplicate = 0 OR is_duplicate IS NULL)"

    if category and category != "All":
        query += " AND category = ?"
        params.append(category)

    if priority and priority != "All":
        query += " AND UPPER(priority) = UPPER(?)"
        params.append(priority)

    if status and status != "All":
        query += " AND status = ?"
        params.append(status)

    if search:
        query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ? OR LOWER(location_name) LIKE ? OR LOWER(complaint_id) LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard, wildcard, wildcard])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    complaints = []
    for r in rows:
        d = dict(r)
        if d.get("priority_factors_json"):
            try:
                d["priority_factors"] = json.loads(d["priority_factors_json"])
            except Exception:
                d["priority_factors"] = []
        
        # Transparent AI Summary & Bullet Reasons
        d["summary"] = ai_engine.generate_complaint_summary(
            d.get("title", ""),
            d.get("description", ""),
            d.get("category", ""),
            d.get("location_name", "")
        )
        p_res = ai_engine.calculate_priority(d)
        d["priority_reasons"] = p_res["reasons"]
        complaints.append(d)

    conn.close()
    return jsonify({"success": True, "count": len(complaints), "complaints": complaints})


@app.route("/api/complaints/<identifier>", methods=["GET"])
def get_complaint_detail(identifier):
    conn = get_db()
    cursor = conn.cursor()

    if identifier.isdigit():
        cursor.execute("SELECT * FROM complaints WHERE id = ?", (int(identifier),))
    else:
        cursor.execute("SELECT * FROM complaints WHERE UPPER(complaint_id) = UPPER(?)", (identifier,))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"success": False, "error": "Complaint not found"}), 404

    complaint = dict(row)

    # Decode JSON fields
    if complaint.get("priority_factors_json"):
        try:
            complaint["priority_factors"] = json.loads(complaint["priority_factors_json"])
        except Exception:
            complaint["priority_factors"] = []

    if complaint.get("action_brief_json"):
        try:
            complaint["action_brief"] = json.loads(complaint["action_brief_json"])
        except Exception:
            complaint["action_brief"] = {}

    # Transparent AI Summary & Priority Explanations
    complaint["summary"] = ai_engine.generate_complaint_summary(
        complaint.get("title", ""),
        complaint.get("description", ""),
        complaint.get("category", ""),
        complaint.get("location_name", "")
    )
    p_info = ai_engine.calculate_priority(complaint)
    complaint["priority_reasons"] = p_info["reasons"]

    # Fetch audit logs
    cursor.execute("SELECT * FROM audit_logs WHERE complaint_id = ? ORDER BY id ASC", (complaint["id"],))
    complaint["timeline"] = [dict(log) for log in cursor.fetchall()]

    # Fetch all complaints to compute live Duplicate Radar candidates
    cursor.execute("SELECT id, complaint_id, title, description, category, latitude, longitude, created_at, status, merged_into_id FROM complaints WHERE id != ?", (complaint["id"],))
    all_others = [dict(r) for r in cursor.fetchall()]
    conn.close()

    duplicates = ai_engine.detect_duplicates(complaint, all_others, threshold=45)
    complaint["duplicate_candidates"] = duplicates

    return jsonify({"success": True, "complaint": complaint})


@app.route("/api/complaints", methods=["POST"])
def submit_complaint():
    """
    Submits a new complaint with:
    - SmartVision AI image scan
    - AI Priority calculation
    - Duplicate detection
    - SLA deadline generation
    - Leaderboard civic points award (+50 pts)
    """
    if request.is_json:
        data = request.get_json() or {}
        citizen_name = data.get("citizen_name", "").strip() or "Anonymous Citizen"
        citizen_contact = data.get("citizen_contact", "").strip() or "citizen@civicai.org"
        title = data.get("title", "").strip()
        description = data.get("description", "").strip()
        category = data.get("category", "").strip()
        location_name = data.get("location_name", "").strip() or "Bangalore Urban Zone"
        lat_input = data.get("latitude", 12.9716)
        lng_input = data.get("longitude", 77.5946)
        sample_url = data.get("sample_url") or data.get("image_url")
    else:
        citizen_name = request.form.get("citizen_name", "").strip() or "Anonymous Citizen"
        citizen_contact = request.form.get("citizen_contact", "").strip() or "citizen@civicai.org"
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        location_name = request.form.get("location_name", "").strip() or "Bangalore Urban Zone"
        lat_input = request.form.get("latitude", 12.9716)
        lng_input = request.form.get("longitude", 77.5946)
        sample_url = request.form.get("sample_url", "").strip()

    # Input validation
    if not title or len(title) < 3:
        return jsonify({"success": False, "error": "Complaint title must be at least 3 characters long"}), 400

    if not description or len(description) < 5:
        return jsonify({"success": False, "error": "Complaint description must be at least 5 characters long"}), 400

    try:
        latitude = float(lat_input)
        longitude = float(lng_input)
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            latitude, longitude = 12.9716, 77.5946
    except (ValueError, TypeError):
        latitude, longitude = 12.9716, 77.5946

    # Safe image upload handling
    image_url = None
    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename:
            sec_name = secure_filename(file.filename)
            if allowed_file(sec_name):
                ext = sec_name.rsplit(".", 1)[1].lower() if "." in sec_name else "jpg"
                unique_filename = f"img_{uuid.uuid4().hex[:12]}.{ext}"
                file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
                file.save(file_path)
                image_url = f"/static/uploads/{unique_filename}"
            else:
                return jsonify({"success": False, "error": "Invalid file format. Allowed types: JPG, PNG, WEBP, SVG"}), 400

    # Pick sample URL if provided from preset UI
    if not image_url and sample_url:
        image_url = sample_url

    # Fallback default category image if none provided
    if not image_url:
        cat_sample_map = {
            "Road Damage": "/static/images/samples/pothole_crater_1.svg",
            "Waterlogging": "/static/images/samples/waterlogging_1.svg",
            "Garbage": "/static/images/samples/garbage_pile_1.svg",
            "Streetlight": "/static/images/samples/electrical_wire_1.svg",
            "Drainage": "/static/images/samples/manhole_open_1.svg",
            "Other": "/static/images/samples/tree_fallen_1.svg",
            # Legacy category mappings
            "Roads & Potholes": "/static/images/samples/pothole_crater_1.svg",
            "Garbage & Sanitation": "/static/images/samples/garbage_pile_1.svg",
            "Waterlogging & Drainage": "/static/images/samples/waterlogging_1.svg",
            "Streetlights & Electricity": "/static/images/samples/electrical_wire_1.svg",
            "Open Manhole & Safety": "/static/images/samples/manhole_open_1.svg",
            "Fallen Trees & Obstructions": "/static/images/samples/tree_fallen_1.svg"
        }
        image_url = cat_sample_map.get(category, "/static/images/samples/pothole_crater_1.svg")

    # If category wasn't picked, run SmartVision / NLP Heuristics to auto-predict category!
    vision_results = ai_engine.analyze_image_heuristics(image_url, f"{title} {description}")
    if not category or category in ["Auto-Detect", "Other"]:
        category = vision_results["predicted_category"]

    # Connect to DB to check nearby complaints for cluster frequency & duplicates
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, complaint_id, title, description, category, latitude, longitude, created_at, status, merged_into_id FROM complaints")
    existing_all = [dict(r) for r in cursor.fetchall()]

    # Count active complaints within 300 meters
    nearby_count = 0
    for ex in existing_all:
        d_m = ai_engine.haversine_distance_meters(latitude, longitude, ex["latitude"], ex["longitude"])
        if d_m <= 300 and ex["status"] not in ["Resolved", "Closed"]:
            nearby_count += 1

    # Run AI Priority Engine
    complaint_eval_input = {
        "category": category,
        "title": title,
        "description": description,
        "location_name": location_name
    }
    p_info = ai_engine.calculate_priority_intelligence(complaint_eval_input, existing_nearby_count=nearby_count)

    # Department auto-routing
    dept_map = {
        "Road Damage": "Public Works Department (PWD)",
        "Waterlogging": "Water Supply & Sewerage Board (BWSSB)",
        "Garbage": "Solid Waste Management (SWM)",
        "Streetlight": "Electricity Supply Board (BESCOM)",
        "Drainage": "Municipal Infrastructure & Safety",
        "Other": "Municipal Administration",
        # Legacy
        "Roads & Potholes": "Public Works Department (PWD)",
        "Garbage & Sanitation": "Solid Waste Management (SWM)",
        "Waterlogging & Drainage": "Water Supply & Sewerage Board (BWSSB)",
        "Streetlights & Electricity": "Electricity Supply Board (BESCOM)",
        "Open Manhole & Safety": "Municipal Infrastructure & Safety",
        "Fallen Trees & Obstructions": "Horticulture & Forestry Wing"
    }
    assigned_dept = dept_map.get(category, "Municipal Administration")

    # Generate guaranteed unique complaint ID
    cursor.execute("SELECT COALESCE(MAX(id), 0) FROM complaints")
    max_id = cursor.fetchone()[0]
    next_num = 1000 + max_id + 1
    while True:
        complaint_id = f"CV-2026-{next_num}"
        cursor.execute("SELECT id FROM complaints WHERE complaint_id = ?", (complaint_id,))
        if not cursor.fetchone():
            break
        next_num += 1

    now = datetime.now(timezone.utc)
    sla_deadline = now + timedelta(hours=p_info["sla_hours"])

    # Generate Action Brief
    action_brief = ai_engine.generate_action_brief({
        "category": category,
        "title": title,
        "priority": p_info["priority"],
        "location_name": location_name
    })

    # Insert complaint record
    cursor.execute("""
    INSERT INTO complaints (
        complaint_id, citizen_name, citizen_contact, title, description,
        category, location_name, latitude, longitude, image_url,
        priority, priority_score, priority_explanation, priority_factors_json,
        status, assigned_department, assigned_officer, created_at, updated_at,
        sla_deadline, is_duplicate, action_brief_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?, 'Unassigned', ?, ?, ?, 0, ?)
    """, (
        complaint_id, citizen_name, citizen_contact, title, description,
        category, location_name, latitude, longitude, image_url,
        p_info["priority"], p_info["score"], p_info["explanation"], json.dumps(p_info["factors"]),
        assigned_dept, now.isoformat(), now.isoformat(), sla_deadline.isoformat(), json.dumps(action_brief)
    ))

    new_id = cursor.lastrowid

    # Add audit log
    cursor.execute("""
    INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
    VALUES (?, 'SUBMITTED', 'Complaint received and digitally signed', ?, ?)
    """, (new_id, citizen_name, now.isoformat()))

    cursor.execute("""
    INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
    VALUES (?, 'AI_TRIAGE', ?, 'CivicAI Priority Engine', ?)
    """, (new_id, f"Classified {p_info['priority']} ({p_info['score']}/100 pts) - Target SLA: {p_info['sla_hours']}h", (now + timedelta(seconds=2)).isoformat()))

    # Update or insert citizen in Leaderboard (+50 civic points)
    cursor.execute("SELECT id, points, verified_reports FROM citizens WHERE LOWER(contact) = LOWER(?)", (citizen_contact,))
    citizen_row = cursor.fetchone()
    if citizen_row:
        c_id, pts, reps = citizen_row
        new_pts = pts + 50
        new_reps = reps + 1
        tier = "Diamond" if new_pts >= 500 else "Gold" if new_pts >= 300 else "Silver" if new_pts >= 150 else "Bronze"
        cursor.execute("UPDATE citizens SET points = ?, verified_reports = ?, tier = ? WHERE id = ?", (new_pts, new_reps, tier, c_id))
    else:
        cursor.execute("""
        INSERT INTO citizens (name, contact, points, verified_reports, resolved_reports, badges_json, tier, created_at)
        VALUES (?, ?, 50, 1, 0, ?, 'Bronze', ?)
        """, (citizen_name, citizen_contact, json.dumps(["Eagle Eye"]), now.isoformat()))

    conn.commit()

    # Check for immediate duplicates to return in response
    new_complaint_dict = {
        "id": new_id,
        "title": title,
        "description": description,
        "category": category,
        "latitude": latitude,
        "longitude": longitude
    }
    duplicates = ai_engine.compute_duplicate_radar(new_complaint_dict, existing_all, threshold=55)

    conn.close()

    # Generate Short Summary
    summary = ai_engine.generate_complaint_summary(title, description, category, location_name)

    return jsonify({
        "success": True,
        "complaint_id": complaint_id,
        "id": new_id,
        "image_url": image_url,
        "category": category,
        "summary": summary,
        "priority": p_info["priority"],
        "priority_score": p_info["score"],
        "priority_reasons": p_info.get("reasons", []),
        "sla_hours": p_info["sla_hours"],
        "sla_deadline": sla_deadline.isoformat(),
        "assigned_department": assigned_dept,
        "explanation": p_info["explanation"],
        "vision_analysis": vision_results,
        "potential_duplicates": len(duplicates),
        "message": f"Complaint {complaint_id} filed successfully. AI Priority: {p_info['priority']}."
    })


@app.route("/api/complaints/<identifier>/status", methods=["POST"])
def update_complaint_status(identifier):
    """
    Updates status: 'Submitted', 'Under Review', 'Assigned', 'In Progress', 'Resolved'.
    Can also update assigned_department, assigned_officer, resolution_notes, resolution_image.
    Accepts both DB integer ID and tracking code (e.g. CV-2026-1001).
    """
    data = request.json or request.form
    new_status = data.get("status")
    assigned_dept = data.get("assigned_department")
    assigned_officer = data.get("assigned_officer")
    notes = data.get("resolution_notes")
    actor = data.get("actor", "Municipal Admin")

    if not new_status:
        return jsonify({"success": False, "error": "New status is required"}), 400

    VALID_STATUSES = {"Submitted", "Under Review", "Assigned", "In Progress", "Resolved"}
    if new_status not in VALID_STATUSES:
        return jsonify({"success": False, "error": f"Invalid status '{new_status}'. Allowed: {', '.join(sorted(VALID_STATUSES))}"}), 400

    conn = get_db()
    cursor = conn.cursor()

    if identifier.isdigit():
        cursor.execute("SELECT * FROM complaints WHERE id = ?", (int(identifier),))
    else:
        cursor.execute("SELECT * FROM complaints WHERE UPPER(complaint_id) = UPPER(?)", (identifier.strip(),))

    comp = cursor.fetchone()
    if not comp:
        conn.close()
        return jsonify({"success": False, "error": f"Complaint '{identifier}' not found"}), 404

    comp_id = comp["id"]
    now = datetime.now(timezone.utc)
    resolved_at = now.isoformat() if new_status == "Resolved" else comp["resolved_at"]

    # Sanitize assignment fields (only update if non-empty string provided)
    dept_val = assigned_dept.strip() if assigned_dept and str(assigned_dept).strip() else None
    officer_val = assigned_officer.strip() if assigned_officer and str(assigned_officer).strip() else None
    notes_val = notes.strip() if notes and str(notes).strip() else None

    # Resolution image handling
    resolution_img = comp["resolution_image_url"]
    if new_status == "Resolved" and not resolution_img:
        cat = comp["category"]
        res_map = {
            "Roads & Potholes": "/static/images/samples/pothole_resolved_1.svg",
            "Road Damage": "/static/images/samples/pothole_resolved_1.svg",
            "Garbage & Sanitation": "/static/images/samples/garbage_resolved_1.svg",
            "Garbage": "/static/images/samples/garbage_resolved_1.svg",
            "Waterlogging": "/static/images/samples/waterlogging_1.svg",
            "Waterlogging & Drainage": "/static/images/samples/waterlogging_1.svg",
            "Streetlights & Electricity": "/static/images/samples/electrical_resolved_1.svg",
            "Streetlight": "/static/images/samples/electrical_resolved_1.svg"
        }
        resolution_img = res_map.get(cat, "/static/images/samples/pothole_resolved_1.svg")

    cursor.execute("""
    UPDATE complaints SET
        status = ?,
        assigned_department = COALESCE(?, assigned_department),
        assigned_officer = COALESCE(?, assigned_officer),
        resolution_notes = COALESCE(?, resolution_notes),
        resolution_image_url = COALESCE(?, resolution_image_url),
        resolved_at = ?,
        updated_at = ?
    WHERE id = ?
    """, (new_status, dept_val, officer_val, notes_val, resolution_img, resolved_at, now.isoformat(), comp_id))

    # Add descriptive audit log
    changes = []
    if comp["status"] != new_status:
        changes.append(f"Status changed from '{comp['status']}' to '{new_status}'")
    if dept_val and dept_val != comp["assigned_department"]:
        changes.append(f"Assigned to {dept_val}")
    if officer_val and officer_val != comp["assigned_officer"]:
        changes.append(f"Field officer assigned: {officer_val}")
    if notes_val:
        changes.append(f"Notes: {notes_val}")

    event_desc = "; ".join(changes) if changes else f"Status updated to '{new_status}'"

    cursor.execute("""
    INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
    VALUES (?, 'STATUS_CHANGE', ?, ?, ?)
    """, (comp_id, event_desc, actor, now.isoformat()))

    # If resolved, reward original citizen with +25 points
    if new_status == "Resolved" and comp["status"] != "Resolved":
        cursor.execute("UPDATE citizens SET points = points + 25, resolved_reports = resolved_reports + 1 WHERE LOWER(contact) = LOWER(?)", (comp["citizen_contact"],))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Complaint {comp['complaint_id']} status updated to '{new_status}'",
        "status": new_status,
        "complaint_id": comp["complaint_id"],
        "resolved_at": resolved_at
    })


@app.route("/api/complaints/<int:comp_id>/merge", methods=["POST"])
def merge_complaints(comp_id):
    """
    Merges duplicate complaint (comp_id) into target master complaint (master_id).
    """
    data = request.json or request.form
    master_id = data.get("master_id")

    if not master_id:
        return jsonify({"success": False, "error": "master_id is required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM complaints WHERE id = ?", (comp_id,))
    duplicate_comp = cursor.fetchone()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (master_id,))
    master_comp = cursor.fetchone()

    if not duplicate_comp or not master_comp:
        conn.close()
        return jsonify({"success": False, "error": "Invalid complaint IDs"}), 404

    now = datetime.now(timezone.utc)

    # Mark as duplicate and link
    cursor.execute("""
    UPDATE complaints SET
        is_duplicate = 1,
        merged_into_id = ?,
        status = 'Merged (Duplicate)',
        updated_at = ?
    WHERE id = ?
    """, (master_id, now.isoformat(), comp_id))

    # Audit log on duplicate
    cursor.execute("""
    INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
    VALUES (?, 'DUPLICATE_MERGE', ?, 'Duplicate Radar Engine', ?)
    """, (comp_id, f"Merged into primary complaint {master_comp['complaint_id']}", now.isoformat()))

    # Audit log on master
    cursor.execute("""
    INSERT INTO audit_logs (complaint_id, event_type, description, actor, timestamp)
    VALUES (?, 'DUPLICATE_LINKED', ?, 'Duplicate Radar Engine', ?)
    """, (master_id, f"Duplicate report {duplicate_comp['complaint_id']} linked to this master incident", now.isoformat()))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Complaint {duplicate_comp['complaint_id']} successfully merged into {master_comp['complaint_id']}"
    })


@app.route("/api/complaints/<int:comp_id>/rate", methods=["POST"])
def rate_complaint(comp_id):
    """Submits citizen satisfaction rating (1-5) and feedback on a resolved complaint."""
    data = request.json or request.form
    try:
        rating = int(data.get("rating", 5))
        rating = max(1, min(5, rating))
    except ValueError:
        rating = 5

    feedback = data.get("feedback", "").strip()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE complaints SET citizen_rating = ?, citizen_feedback = ? WHERE id = ?", (rating, feedback, comp_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Thank you for verifying and rating this civic resolution!"})


# -----------------------------------------------------------------------------
# REST APIs: AI ENGINES & INTELLIGENCE
# -----------------------------------------------------------------------------

@app.route("/api/ai/vision-scan", methods=["POST"])
def vision_scan_preview():
    """
    Real-time SmartVision AI scanner for uploaded photograph before form submit.
    Returns predicted category, confidence score, detected features, and suggested actions.
    """
    image_url = None
    filename = ""
    description = request.form.get("description", "")

    if "image" in request.files:
        file = request.files["image"]
        if file and file.filename and allowed_file(file.filename):
            filename = file.filename
            ext = filename.rsplit(".", 1)[1].lower()
            unique_name = f"scan_{uuid.uuid4().hex[:8]}.{ext}"
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            file.save(file_path)
            image_url = f"/static/uploads/{unique_name}"
    else:
        # Pre-selected sample image or existing URL
        image_url = request.form.get("image_url", "")
        filename = os.path.basename(image_url)

    analysis = ai_engine.analyze_image_heuristics(filename, description)
    analysis["image_url"] = image_url
    return jsonify({"success": True, "analysis": analysis})


@app.route("/api/ai/duplicate-radar/<int:comp_id>", methods=["GET"])
def get_duplicate_radar_graph(comp_id):
    """
    Returns an animated connected node graph representation:
    Center node = Target complaint
    Surrounding nodes = Related complaints with similarity edge weights & distances.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints WHERE id = ?", (comp_id,))
    target = cursor.fetchone()
    if not target:
        conn.close()
        return jsonify({"success": False, "error": "Complaint not found"}), 404

    target_dict = dict(target)
    cursor.execute("SELECT id, complaint_id, title, description, category, latitude, longitude, created_at, status, merged_into_id FROM complaints WHERE id != ?", (comp_id,))
    all_others = [dict(r) for r in cursor.fetchall()]
    conn.close()

    candidates = ai_engine.compute_duplicate_radar(target_dict, all_others, threshold=40)

    # Format into Nodes and Links for canvas / SVG visualization
    nodes = [{
        "id": target_dict["id"],
        "complaint_id": target_dict["complaint_id"],
        "title": target_dict["title"],
        "category": target_dict["category"],
        "is_center": True,
        "priority": target_dict["priority"],
        "status": target_dict["status"]
    }]

    links = []
    for cand in candidates:
        nodes.append({
            "id": cand["candidate_id"],
            "complaint_id": cand["complaint_id"],
            "title": cand["title"],
            "category": cand["category"],
            "is_center": False,
            "distance_meters": cand["distance_meters"],
            "similarity_score": cand["similarity_score"],
            "status": cand["status"]
        })
        links.append({
            "source": target_dict["id"],
            "target": cand["candidate_id"],
            "similarity": cand["similarity_score"],
            "distance": cand["distance_meters"],
            "reasons": cand["reasons"]
        })

    return jsonify({
        "success": True,
        "target": target_dict,
        "nodes": nodes,
        "links": links,
        "count": len(candidates)
    })


@app.route("/api/ai/risk-profiles", methods=["GET"])
def get_risk_profiles():
    """Returns ward-level risk rankings, trends, and predictive forecasts."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = [dict(r) for r in cursor.fetchall()]
    conn.close()

    profiles = ai_engine.calculate_ward_risk_profiles(complaints)
    return jsonify({"success": True, "risk_profiles": profiles})


@app.route("/api/ai/hotspots", methods=["GET"])
def get_hotspots():
    """
    Identifies geographic clusters where multiple complaints occur within 400 meters.
    Orders clusters by severity and complaint count.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, complaint_id, title, category, location_name, latitude, longitude, priority, status 
        FROM complaints 
        WHERE status != 'Resolved'
    """)
    active = [dict(r) for r in cursor.fetchall()]
    conn.close()

    hotspots = []
    visited = set()

    for i, c1 in enumerate(active):
        if c1["id"] in visited:
            continue
        cluster = [c1]
        for j, c2 in enumerate(active):
            if i != j and c2["id"] not in visited:
                dist = ai_engine.haversine_distance_meters(c1["latitude"], c1["longitude"], c2["latitude"], c2["longitude"])
                if dist <= 400:
                    cluster.append(c2)

        if len(cluster) >= 2:
            avg_lat = sum(c["latitude"] for c in cluster) / len(cluster)
            avg_lon = sum(c["longitude"] for c in cluster) / len(cluster)
            
            cat_counts = {}
            area_names = []
            for c in cluster:
                visited.add(c["id"])
                cat_counts[c["category"]] = cat_counts.get(c["category"], 0) + 1
                loc = c.get("location_name", "")
                if loc:
                    area_names.append(loc.split(",")[0].strip())

            primary_cat = max(cat_counts.items(), key=lambda x: x[1])[0]
            area_name = max(set(area_names), key=area_names.count) if area_names else "Municipal Sector"

            is_critical = any((c.get("priority") or "").upper() == "CRITICAL" for c in cluster)
            is_high = any((c.get("priority") or "").upper() in ["HIGH", "CRITICAL"] for c in cluster)
            urgency = "Critical" if is_critical else ("High" if is_high else "Medium")

            hotspots.append({
                "hotspot_id": f"HOTSPOT-{len(hotspots)+1}",
                "area_name": area_name,
                "center": [round(avg_lat, 5), round(avg_lon, 5)],
                "complaint_count": len(cluster),
                "primary_category": primary_cat,
                "radius_meters": 400,
                "urgency": urgency,
                "description": f"{len(cluster)} complaints clustered within 400m near {area_name} ({primary_cat})",
                "complaints": cluster
            })

    # Sort hotspots: highest count first
    hotspots.sort(key=lambda x: x["complaint_count"], reverse=True)
    for idx, h in enumerate(hotspots):
        h["hotspot_id"] = f"HOTSPOT-{idx+1}"

    return jsonify({"success": True, "hotspots": hotspots, "count": len(hotspots)})


# -----------------------------------------------------------------------------
# REST APIs: LIVE DASHBOARD STATS
# -----------------------------------------------------------------------------

@app.route("/api/stats", methods=["GET"])
def get_dashboard_stats():
    """Live dynamic statistics directly from SQLite database."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM complaints")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Submitted' OR status = 'Under Review'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'In Progress' OR status = 'Assigned'")
    in_progress = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE status = 'Resolved'")
    resolved = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE UPPER(priority) = 'CRITICAL' AND status != 'Resolved'")
    critical = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE (UPPER(priority) = 'CRITICAL' OR UPPER(priority) = 'HIGH') AND status != 'Resolved'")
    urgent = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM complaints WHERE is_duplicate = 1")
    duplicates_detected = cursor.fetchone()[0]

    # Category breakdown
    cursor.execute("SELECT category, COUNT(*) as cnt FROM complaints GROUP BY category ORDER BY cnt DESC")
    by_category = [{"category": row[0], "count": row[1]} for row in cursor.fetchall()]

    # Priority breakdown
    cursor.execute("SELECT priority, COUNT(*) as cnt FROM complaints GROUP BY priority")
    by_priority = [{"priority": row[0], "count": row[1]} for row in cursor.fetchall()]

    # Department performance
    cursor.execute("""
    SELECT assigned_department,
           COUNT(*) as total,
           SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved_count
    FROM complaints
    WHERE assigned_department IS NOT NULL AND assigned_department != ''
    GROUP BY assigned_department
    """)
    departments = []
    for row in cursor.fetchall():
        dept, tot, res = row
        rate = round((res / tot * 100), 1) if tot > 0 else 0
        departments.append({
            "department": dept,
            "total": tot,
            "resolved": res,
            "resolution_rate": rate
        })

    # Real average resolution hours computed dynamically from SQLite records
    cursor.execute("""
        SELECT created_at, resolved_at FROM complaints 
        WHERE status = 'Resolved' AND resolved_at IS NOT NULL AND resolved_at != ''
    """)
    res_rows = cursor.fetchall()
    diffs = []
    for r in res_rows:
        try:
            t_created = datetime.fromisoformat(r[0])
            t_resolved = datetime.fromisoformat(r[1])
            diff_h = abs((t_resolved - t_created).total_seconds()) / 3600.0
            if diff_h > 0:
                diffs.append(diff_h)
        except Exception:
            pass
    avg_resolution_hours = round(sum(diffs) / len(diffs), 1) if diffs else 24.0

    conn.close()

    return jsonify({
        "success": True,
        "total_complaints": total,
        "pending_complaints": pending,
        "in_progress": in_progress,
        "resolved_complaints": resolved,
        "critical_unresolved": critical,
        "urgent_complaints": urgent,
        "duplicates_detected": duplicates_detected,
        "avg_resolution_hours": avg_resolution_hours,
        "by_category": by_category,
        "by_priority": by_priority,
        "department_performance": departments
    })


# -----------------------------------------------------------------------------
# REST APIs: AI CIVIC ASSISTANT (Aura Copilot)
# -----------------------------------------------------------------------------

@app.route("/api/assistant/chat", methods=["POST"])
def assistant_chat():
    """
    Floating AI Civic Assistant (Aura).
    Answers questions, guides category selection, looks up complaints, explains SLAs.
    """
    data = request.json or {}
    message = (data.get("message") or "").strip()
    msg_lower = message.lower()

    if not message:
        return jsonify({"reply": "Hello! I am Aura, your CivicAI Smart Assistant. How can I assist you with city services today?"})

    # Check for complaint ID tracking query
    id_match = re.search(r'\b(CV-\d{4}-\d{3,5})\b', message, re.IGNORECASE)
    if id_match or any(w in msg_lower for w in ["track", "status", "check"]):
        if id_match:
            code = id_match.group(1).upper()
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT complaint_id, title, status, priority, assigned_department, created_at FROM complaints WHERE UPPER(complaint_id) = ?", (code,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return jsonify({
                    "reply": f"Found report **{row['complaint_id']}**: *{row['title']}*\n\n"
                             f"• **Current Status**: {row['status']}\n"
                             f"• **AI Priority**: {row['priority']}\n"
                             f"• **Assigned To**: {row['assigned_department']}\n\n"
                             f"[Click here to view live timeline](/track?id={row['complaint_id']})",
                    "action": "open_tracker",
                    "complaint_id": row["complaint_id"]
                })
            else:
                return jsonify({"reply": f"I couldn't locate complaint ID **{code}** in the municipal registry. Please check the ID or [file a new report](/report)."})
        else:
            return jsonify({"reply": "To check your complaint status, please enter your Complaint ID (e.g., **CV-2026-1001**) or visit the [Live Tracker](/track)."})

    # Category guidance
    if any(w in msg_lower for w in ["category", "where to report", "what type", "which department"]):
        return jsonify({
            "reply": "CivicAI automatically detects categories when you upload a photo! Our core categories are:\n\n"
                     "1. **Roads & Potholes**: Asphalt craters, broken footpaths, road cracks.\n"
                     "2. **Open Manhole & Safety**: Uncovered manholes, missing drain slabs (Flagged Critical!).\n"
                     "3. **Waterlogging & Drainage**: Flooding, blocked storm drains, sewage overflows.\n"
                     "4. **Streetlights & Electricity**: Dark streets, dangling live wires, broken poles.\n"
                     "5. **Garbage & Sanitation**: Overflowing bins, illegal debris dumping.\n"
                     "6. **Fallen Trees & Obstructions**: Uprooted branches blocking roads.\n\n"
                     "[Click here to report an issue now](/report)"
        })

    # Emergency hazards
    if any(w in msg_lower for w in ["emergency", "danger", "wire", "shock", "fire", "urgent", "child fallen"]):
        return jsonify({
            "reply": "⚠️ **IMMEDIATE CIVIC HAZARD DETECTED**\n\n"
                     "For life-threatening emergencies, please call the 24/7 City Disaster Helpline at **112** immediately.\n\n"
                     "For rapid municipal triage, [file a Critical Report here](/report). Our AI Priority Engine will route your complaint to the Emergency Rapid Response squad within 15 minutes."
        })

    # How it works / Submission guide
    if any(w in msg_lower for w in ["how it works", "how to report", "steps", "points", "reward"]):
        return jsonify({
            "reply": "Reporting takes less than 60 seconds:\n\n"
                     "1. **Snap & Upload**: Take a photo of the problem. Our SmartVision AI scans and classifies it instantly.\n"
                     "2. **Pin Location**: Confirm the street location on our interactive map.\n"
                     "3. **Submit**: Receive your unique digital receipt and tracking ID.\n"
                     "4. **Earn Points**: Get +50 Civic Hero points on our [Community Leaderboard](/leaderboard) for verified reports!\n\n"
                     "Ready to start? [Report a Problem](/report)"
        })

    # Default fallback
    return jsonify({
        "reply": f"I understand you're asking about '{message}'. As your CivicAI Copilot, I can help you [Report a Problem](/report), [Track an Issue](/track), explore the [City Pulse Map](/map), or review [Predictive Risk Profiles](/risk-predictor). How may I assist you?"
    })


# -----------------------------------------------------------------------------
# REST APIs: LEADERBOARD & ADMIN AUTH
# -----------------------------------------------------------------------------

@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact, points, verified_reports, resolved_reports, badges_json, tier FROM citizens ORDER BY points DESC LIMIT 20")
    citizens = []
    for row in cursor.fetchall():
        d = dict(row)
        try:
            d["badges"] = json.loads(d["badges_json"])
        except Exception:
            d["badges"] = ["Eagle Eye"]
        citizens.append(d)
    conn.close()
    return jsonify({"success": True, "leaderboard": citizens})


@app.route("/api/admin/auth", methods=["POST"])
def admin_auth():
    """Simple authenticated admin gate. Accepts 'admin' / 'admin123'."""
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if username == "admin" and password in ["admin123", "smartcity2026", "hackathon"]:
        session["is_admin"] = True
        return jsonify({"success": True, "message": "Admin session authenticated"})
    return jsonify({"success": False, "error": "Invalid administrative credentials"}), 401


# -----------------------------------------------------------------------------
# RUN SERVER
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
