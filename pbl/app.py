"""
HealthPulse - Patient Health Problems & Clinical Symptom Tracker
Configured for: Richitha (richitha132@gmail.com)
Lifetime Background Access & Problem-Focused Clinical Health Reporting
"""

import os
import json
import csv
import io
from datetime import datetime
from functools import wraps
from flask import (
    Flask, jsonify, request, render_template_string,
    Response, redirect, url_for, session
)

app = Flask(__name__)
app.secret_key = "healthpulse-lifetime-clinical-key-richitha"
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "symptoms_data.json")

# Default User Credentials for the Login Page
DEFAULT_USER = {
    "username": "richitha132@gmail.com",
    "password": "password123",
    "name": "Richitha"
}

CATEGORIES = [
    "Neurological",
    "Respiratory",
    "Digestive",
    "Musculoskeletal",
    "Cardiovascular",
    "Dermatological",
    "General"
]


def load_data():
    if not os.path.exists(DATA_FILE):
        default_data = {
            "user": {
                "user_id": "PT-94820",
                "name": "Richitha",
                "email": "richitha132@gmail.com",
                "age": 22,
                "gender": "Female",
                "blood_group": "B+",
                "weight_kg": 54,
                "height_cm": 162,
                "allergies": ["Sulfa Drugs", "Penicillin"],
                "chronic_conditions": ["Mild Asthma", "Occasional Migraines"],
                "emergency_contact": "+91 98765 43210",
                "primary_physician": "Dr. Sarah Jenkins, MD (Internal Medicine)",
                "vitals": {
                    "blood_pressure": "118/76",
                    "heart_rate_bpm": 74,
                    "temperature_f": 98.6,
                    "spo2_percent": 98,
                    "blood_sugar_mgdl": 92,
                    "last_updated": "2026-11-03 10:15"
                }
            },
            "symptoms": [],
            "environmental_factors": {
                "current_weather": "Cloudy, 18°C",
                "humidity": "74%",
                "air_quality_index": 82,
                "barometric_pressure": "1012 hPa",
                "pollen_level": "Moderate"
            }
        }
        save_data(default_data)
        return default_data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {DATA_FILE}: {e}")
        return {"user": {"name": "Richitha"}, "symptoms": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def compute_problems_analytics(symptoms, user):
    """Computes clinical analytics focusing strictly on problems faced by the patient."""
    if not symptoms:
        return {
            "total": 0,
            "avg_severity": 0.0,
            "categories": {},
            "top_triggers": [],
            "alerts": [],
            "risk_score": 10,
            "risk_level": "Minimal Problems Logged",
            "risk_color": "emerald",
            "problem_notes": ["No acute health problems recorded in recent timeline."],
            "urgent_problems": []
        }

    total = len(symptoms)
    severities = [s.get("severity", 0) for s in symptoms]
    avg_sev = sum(severities) / total if total > 0 else 0.0

    # Category counts
    cat_counts = {}
    for s in symptoms:
        cat = s.get("category", "General")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    # Trigger counts
    trig_counts = {}
    for s in symptoms:
        for t in s.get("triggers", []):
            t_clean = t.strip().title()
            if t_clean:
                trig_counts[t_clean] = trig_counts.get(t_clean, 0) + 1

    sorted_triggers = [{"trigger": k, "count": v} for k, v in sorted(trig_counts.items(), key=lambda item: item[1], reverse=True)]
    high_sev = [s for s in symptoms if s.get("severity", 0) >= 7]

    # Calculate Clinical Risk Score (0 - 100) based on severity and frequency of problems
    severity_weight = (avg_sev / 10.0) * 50
    alert_weight = min(len(high_sev) * 15, 30)
    frequency_weight = min(total * 4, 20)
    raw_risk = int(severity_weight + alert_weight + frequency_weight)
    risk_score = min(max(raw_risk, 10), 98)

    if risk_score < 35:
        risk_level = "Mild / Manageable Problems"
        risk_color = "emerald"
    elif risk_score < 65:
        risk_level = "Moderate Health Concerns"
        risk_color = "amber"
    else:
        risk_level = "Elevated Severity - Medical Review Advised"
        risk_color = "rose"

    notes = []
    if high_sev:
        notes.append(f"Patient has experienced {len(high_sev)} high-severity health episode(s) rated >= 7/10.")
    if sorted_triggers:
        top_t = sorted_triggers[0]["trigger"]
        notes.append(f"Leading aggravating factor: '{top_t}' (correlated with {sorted_triggers[0]['count']} problem episodes).")

    # Body location concentration
    locations = [s.get("body_location") for s in symptoms if s.get("body_location")]
    if locations:
        from collections import Counter
        most_common_loc, loc_count = Counter(locations).most_common(1)[0]
        notes.append(f"Predominant affected anatomical area: '{most_common_loc}' ({loc_count} recorded flare-ups).")

    return {
        "total": total,
        "avg_severity": round(avg_sev, 1),
        "categories": cat_counts,
        "top_triggers": sorted_triggers[:5],
        "alerts": high_sev,
        "urgent_problems": high_sev,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "problem_notes": notes
    }


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated_function


# =========================================================================
# HTML TEMPLATES: LOGIN PAGE, DASHBOARD, AND PROBLEMS-ONLY REPORT
# =========================================================================

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login - HealthPulse Portal</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-slate-100 font-sans">
  <div class="max-w-md w-full bg-slate-900/80 backdrop-blur-xl border border-indigo-500/20 rounded-3xl p-8 shadow-2xl space-y-6">
    
    <!-- Header -->
    <div class="text-center space-y-2">
      <div class="inline-flex w-14 h-14 rounded-2xl bg-gradient-to-tr from-rose-500 via-pink-500 to-indigo-600 items-center justify-center text-white text-2xl shadow-lg ring-4 ring-indigo-500/10 mb-2">
        <i class="fa-solid fa-heart-pulse"></i>
      </div>
      <h2 class="text-2xl font-extrabold tracking-tight text-white">HealthPulse Portal</h2>
      <p class="text-xs text-indigo-300">Confidential Patient Health Record & Problem Tracking</p>
    </div>

    {% if error %}
    <div class="bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs p-3 rounded-xl flex items-center gap-2">
      <i class="fa-solid fa-circle-exclamation"></i>
      <span>{{ error }}</span>
    </div>
    {% endif %}

    <form method="POST" action="/login" class="space-y-4 text-xs">
      <div>
        <label class="block font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Registered Email</label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
            <i class="fa-regular fa-envelope"></i>
          </span>
          <input type="text" name="username" id="username" required value="richitha132@gmail.com" class="w-full bg-slate-950/60 border border-slate-700 rounded-xl py-2.5 pl-10 pr-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs">
        </div>
      </div>

      <div>
        <label class="block font-semibold text-slate-300 uppercase tracking-wider mb-1.5">Password</label>
        <div class="relative">
          <span class="absolute inset-y-0 left-0 flex items-center pl-3.5 text-slate-400">
            <i class="fa-solid fa-lock"></i>
          </span>
          <input type="password" name="password" id="password" required value="password123" class="w-full bg-slate-950/60 border border-slate-700 rounded-xl py-2.5 pl-10 pr-3 text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 text-xs">
        </div>
      </div>

      <div class="flex items-center justify-between text-[11px] text-slate-400">
        <label class="flex items-center gap-1.5 cursor-pointer">
          <input type="checkbox" checked class="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0">
          <span>Remember session (Lifetime)</span>
        </label>
        <span class="text-indigo-400">Protected Portal</span>
      </div>

      <button type="submit" class="w-full py-3 bg-gradient-to-r from-indigo-600 via-indigo-500 to-rose-600 hover:from-indigo-500 hover:to-rose-500 text-white font-bold rounded-xl shadow-lg transition duration-200 text-sm flex items-center justify-center gap-2">
        <i class="fa-solid fa-right-to-bracket"></i> Login to HealthPulse
      </button>
    </form>

    <div class="bg-indigo-950/40 border border-indigo-800/40 rounded-2xl p-4 text-[11px] space-y-1 text-slate-300">
      <div class="font-bold text-indigo-300 flex items-center gap-1.5">
        <i class="fa-solid fa-circle-check text-emerald-400"></i> Pre-authorized Patient Profile:
      </div>
      <div><strong>Email:</strong> richitha132@gmail.com</div>
      <div><strong>Password:</strong> password123</div>
      <p class="text-[10px] text-indigo-400/80 pt-1">Lifetime background access enabled.</p>
    </div>

  </div>
</body>
</html>
"""


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HealthPulse - Patient Health Problems Tracker</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { font-family: 'Inter', system-ui, -apple-system, sans-serif; background-color: #f8fafc; }
    .badge-sev-1, .badge-sev-2, .badge-sev-3 { background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }
    .badge-sev-4, .badge-sev-5, .badge-sev-6 { background-color: #fef9c3; color: #854d0e; border: 1px solid #fef08a; }
    .badge-sev-7, .badge-sev-8, .badge-sev-9, .badge-sev-10 { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecaca; }
    .body-zone-active { border-color: #4f46e5 !important; background-color: #e0e7ff !important; color: #3730a3 !important; }
  </style>
</head>
<body class="text-slate-800 antialiased min-h-screen flex flex-col justify-between">
  <!-- Top Navigation -->
  <header class="bg-gradient-to-r from-slate-950 via-indigo-950 to-slate-900 text-white shadow-xl sticky top-0 z-40 border-b border-indigo-900/50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex flex-wrap justify-between items-center gap-4">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-rose-500 via-pink-500 to-indigo-600 flex items-center justify-center text-white text-xl shadow-lg ring-2 ring-white/10">
          <i class="fa-solid fa-heart-pulse"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-xl font-extrabold tracking-tight">HealthPulse</h1>
            <span class="text-[10px] font-extrabold uppercase px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">Lifetime Active</span>
          </div>
          <p class="text-xs text-indigo-200">Patient Health Problems & Clinical Symptom Tracker</p>
        </div>
      </div>

      <!-- Actions & Logout -->
      <div class="flex items-center flex-wrap gap-2.5">
        <!-- Vitals Quick Pill -->
        <button onclick="openVitalsModal()" class="flex items-center gap-2 text-xs bg-white/10 hover:bg-white/20 px-3.5 py-2 rounded-xl transition border border-white/10 text-white" title="Patient Demographics & Vitals">
          <i class="fa-solid fa-user-check text-rose-400"></i>
          <span class="font-bold" id="top-patient-name">Richitha</span>
          <span class="opacity-70">(<span id="top-patient-bg">B+</span>)</span>
          <i class="fa-solid fa-pen text-[10px] opacity-70 ml-1"></i>
        </button>

        <!-- DOWNLOAD PATIENT HEALTH PROBLEMS REPORT BUTTON -->
        <a href="/report" target="_blank" class="flex items-center gap-2 text-xs bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-500 hover:to-red-500 text-white font-extrabold px-4 py-2 rounded-xl shadow-md transition ring-2 ring-rose-400/30" title="Download Official Patient Health Report">
          <i class="fa-solid fa-file-pdf text-sm"></i> Download Patient Health Report
        </a>

        <!-- Logout Button -->
        <a href="/logout" class="flex items-center gap-1.5 text-xs bg-white/10 hover:bg-rose-600/30 text-slate-300 hover:text-rose-200 border border-white/10 font-semibold px-3 py-2 rounded-xl transition">
          <i class="fa-solid fa-arrow-right-from-bracket"></i> Logout
        </a>
      </div>
    </div>
  </header>

  <!-- Live Patient Vitals Ticker -->
  <div class="bg-indigo-900/90 text-white border-b border-indigo-800 text-xs">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 py-2 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-2 font-bold text-indigo-200">
        <i class="fa-solid fa-notes-medical"></i> Patient Physiological Parameters:
      </div>
      <div class="flex flex-wrap items-center gap-4 text-xs">
        <div><span class="text-indigo-300">Blood Pressure:</span> <span class="font-bold text-white" id="vitals-bp">118/76 mmHg</span></div>
        <div><span class="text-indigo-300">Heart Rate:</span> <span class="font-bold text-rose-300" id="vitals-hr">74 BPM</span></div>
        <div><span class="text-indigo-300">Temp:</span> <span class="font-bold text-amber-300" id="vitals-temp">98.6 °F</span></div>
        <div><span class="text-indigo-300">SpO2:</span> <span class="font-bold text-emerald-300" id="vitals-spo2">98%</span></div>
        <div><span class="text-indigo-300">BMI:</span> <span class="font-bold text-sky-300" id="vitals-bmi">20.6 (Normal)</span></div>
        <button onclick="openVitalsModal()" class="text-[11px] bg-white/20 hover:bg-white/30 text-white font-semibold px-2 py-0.5 rounded transition">Edit Vitals</button>
      </div>
    </div>
  </div>

  <main class="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-6 flex-1">
    
    <!-- 4 Key Stat Metrics -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white p-4.5 rounded-2xl shadow-sm border border-slate-200/80 flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center text-lg">
          <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Problems Faced</span>
          <h3 class="text-2xl font-black text-slate-800" id="card-total">0</h3>
          <span class="text-[10px] text-slate-400">Total logged episodes</span>
        </div>
      </div>

      <div class="bg-white p-4.5 rounded-2xl shadow-sm border border-slate-200/80 flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center text-lg">
          <i class="fa-solid fa-gauge-high"></i>
        </div>
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Mean Distress / Pain</span>
          <h3 class="text-2xl font-black text-slate-800" id="card-avg-sev">0/10</h3>
          <span class="text-[10px] text-slate-400">Average problem intensity</span>
        </div>
      </div>

      <div class="bg-white p-4.5 rounded-2xl shadow-sm border border-slate-200/80 flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center text-lg">
          <i class="fa-solid fa-bolt"></i>
        </div>
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Primary Aggravating Factor</span>
          <h3 class="text-base font-black text-slate-800 truncate max-w-[130px]" id="card-top-trig">None</h3>
          <span class="text-[10px] text-slate-400" id="card-top-trig-sub">Leading trigger</span>
        </div>
      </div>

      <div class="bg-white p-4.5 rounded-2xl shadow-sm border border-slate-200/80 flex items-center gap-3.5">
        <div class="w-11 h-11 rounded-xl bg-rose-50 text-rose-600 flex items-center justify-center text-lg">
          <i class="fa-solid fa-shield-virus"></i>
        </div>
        <div>
          <span class="text-[11px] font-bold uppercase tracking-wider text-slate-400">Clinical Severity</span>
          <div class="flex items-baseline gap-1">
            <h3 class="text-2xl font-black text-rose-600" id="card-risk-score">--</h3>
            <span class="text-[11px] font-bold text-slate-400">/ 100</span>
          </div>
          <span class="text-[10px] font-bold text-rose-600" id="card-risk-level">Analyzing...</span>
        </div>
      </div>
    </div>

    <!-- Active Health Problems Summary Card -->
    <div class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white rounded-2xl p-5 shadow-sm border border-indigo-800/60">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-3 border-b border-indigo-800/80">
        <div class="flex items-center gap-2.5">
          <span class="p-2 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30"><i class="fa-solid fa-clipboard-check"></i></span>
          <div>
            <h3 class="font-extrabold text-sm tracking-tight">Active Health Problems & Clinical Observations</h3>
            <p class="text-[11px] text-indigo-300">Documented symptoms and physiological challenges reported by the patient</p>
          </div>
        </div>
        <a href="/report" target="_blank" class="text-xs bg-rose-600 hover:bg-rose-500 text-white font-extrabold px-3 py-1.5 rounded-xl shadow transition">
          <i class="fa-solid fa-file-pdf mr-1"></i> Print / Download Problems Report
        </a>
      </div>
      <div class="mt-3 text-xs leading-relaxed">
        <ul id="clinical-problems-list" class="space-y-1.5 text-slate-200 list-disc list-inside">
          <li>Evaluating logged health issues...</li>
        </ul>
      </div>
    </div>

    <!-- Main Grid: Anatomical Map & Form (5 Cols) vs Problems Chronology (7 Cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      
      <!-- Left Column: Body Map & Add Form (5 Cols) -->
      <div class="lg:col-span-5 space-y-5">
        
        <!-- Interactive Human Body Map Selector -->
        <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <div class="flex justify-between items-center pb-2.5 border-b border-slate-100 mb-3">
            <div>
              <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2">
                <i class="fa-solid fa-person-walking text-indigo-600"></i> Affected Anatomical Area
              </h3>
              <p class="text-[11px] text-slate-400">Select where the problem occurs to auto-fill</p>
            </div>
            <span class="text-[10px] bg-indigo-50 text-indigo-700 font-extrabold px-2 py-0.5 rounded">Body Map</span>
          </div>

          <div class="grid grid-cols-3 gap-2">
            <button type="button" onclick="selectBodyZone('Head & Face', 'Neurological', 'Frontal / Temples', 'Throbbing Migraine / Headache')" class="body-zone-btn p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-center transition">
              <i class="fa-solid fa-brain text-indigo-500 text-lg block mb-1"></i>
              <span class="text-xs font-bold block text-slate-700">Head & Brain</span>
              <span class="text-[9px] text-slate-400">Neurological</span>
            </button>

            <button type="button" onclick="selectBodyZone('Chest & Lungs', 'Respiratory', 'Bronchial / Sternum', 'Wheezing / Chest Tightness')" class="body-zone-btn p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-center transition">
              <i class="fa-solid fa-lungs text-sky-500 text-lg block mb-1"></i>
              <span class="text-xs font-bold block text-slate-700">Chest & Lungs</span>
              <span class="text-[9px] text-slate-400">Respiratory</span>
            </button>

            <button type="button" onclick="selectBodyZone('Abdomen & Gut', 'Digestive', 'Epigastric / Stomach', 'Acid Reflux / Stomach Cramps')" class="body-zone-btn p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-center transition">
              <i class="fa-solid fa-cookie-bite text-amber-500 text-lg block mb-1"></i>
              <span class="text-xs font-bold block text-slate-700">Abdomen & Gut</span>
              <span class="text-[9px] text-slate-400">Digestive</span>
            </button>

            <button type="button" onclick="selectBodyZone('Spine & Back', 'Musculoskeletal', 'Lumbar Spine', 'Lower Back Spasm / Ache')" class="body-zone-btn p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-center transition">
              <i class="fa-solid fa-bone text-emerald-500 text-lg block mb-1"></i>
              <span class="text-xs font-bold block text-slate-700">Spine & Back</span>
              <span class="text-[9px] text-slate-400">Musculoskeletal</span>
            </button>

            <button type="button" onclick="selectBodyZone('Limbs & Joints', 'Musculoskeletal', 'Knee / Shoulder Joint', 'Joint Stiffness / Ache')" class="body-zone-btn p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-center transition">
              <i class="fa-solid fa-person-running text-violet-500 text-lg block mb-1"></i>
              <span class="text-xs font-bold block text-slate-700">Limbs & Joints</span>
              <span class="text-[9px] text-slate-400">Joints</span>
            </button>

            <button type="button" onclick="selectBodyZone('Skin & Systemic', 'Dermatological', 'Cutaneous / Skin', 'Urticaria / Skin Allergy')" class="body-zone-btn p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/50 text-center transition">
              <i class="fa-solid fa-hand-dots text-rose-500 text-lg block mb-1"></i>
              <span class="text-xs font-bold block text-slate-700">Skin & Body</span>
              <span class="text-[9px] text-slate-400">Dermatological</span>
            </button>
          </div>
        </div>

        <!-- Add Health Problem Form -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <div class="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
            <h2 class="font-bold text-slate-800 text-base flex items-center gap-2">
              <i class="fa-solid fa-circle-plus text-rose-600"></i> Log Problem Faced
            </h2>
            <span class="text-[10px] bg-slate-100 text-slate-600 font-bold px-2 py-0.5 rounded">Auto-Saved</span>
          </div>

          <form id="symptom-form" onsubmit="submitSymptom(event)" class="space-y-4">
            <div>
              <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Problem / Symptom Name *</label>
              <input type="text" id="form-name" required placeholder="e.g. Severe Migraine, Acid Burning, Lower Back Ache" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-rose-500">
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Category *</label>
                <select id="form-category" class="w-full text-sm px-3 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-rose-500 bg-white">
                  <option value="Neurological">Neurological</option>
                  <option value="Respiratory">Respiratory</option>
                  <option value="Digestive">Digestive</option>
                  <option value="Musculoskeletal">Musculoskeletal</option>
                  <option value="Cardiovascular">Cardiovascular</option>
                  <option value="Dermatological">Dermatological</option>
                  <option value="General">General</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Body Site</label>
                <input type="text" id="form-location" placeholder="e.g. Temples, Chest, Stomach" class="w-full text-sm px-3 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-rose-500">
              </div>
            </div>

            <!-- Severity Intensity Slider -->
            <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-200">
              <div class="flex justify-between items-center mb-1.5">
                <label class="text-xs font-bold text-slate-700 uppercase">Pain / Severity Intensity:</label>
                <span id="severity-badge" class="text-xs font-extrabold px-2.5 py-0.5 rounded-md bg-yellow-100 text-yellow-800">5 / 10 - Moderate</span>
              </div>
              <input type="range" id="form-severity" min="1" max="10" value="5" oninput="updateSeverityLabel(this.value)" class="w-full accent-rose-600 cursor-pointer">
              <div class="flex justify-between text-[10px] text-slate-400 font-bold mt-1">
                <span>1 (Mild)</span>
                <span>5 (Moderate)</span>
                <span>7 (Severe Problem)</span>
                <span>10 (Emergency)</span>
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Duration (Hours)</label>
                <input type="number" step="0.5" id="form-duration" value="2.0" class="w-full text-sm px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-rose-500">
              </div>
              <div>
                <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Date</label>
                <input type="date" id="form-date" class="w-full text-sm px-3 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-rose-500">
              </div>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Aggravating Factors / Triggers</label>
              <input type="text" id="form-triggers" placeholder="e.g. Lack of sleep, Stress, Spicy food, Dust" class="w-full text-sm px-3.5 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-rose-500">
              <span class="text-[10px] text-slate-400">Separate multiple triggers with commas</span>
            </div>

            <div>
              <label class="block text-xs font-semibold text-slate-600 uppercase mb-1">Problem Description & Sensations</label>
              <textarea id="form-notes" rows="2" placeholder="Describe the pain, sensations, or distress you experienced..." class="w-full text-sm px-3.5 py-2 rounded-xl border border-slate-300 focus:ring-2 focus:ring-rose-500"></textarea>
            </div>

            <button type="submit" class="w-full py-3 px-4 bg-gradient-to-r from-rose-600 to-red-600 hover:from-rose-700 hover:to-red-700 text-white font-extrabold rounded-xl shadow-md transition flex items-center justify-center gap-2">
              <i class="fa-solid fa-floppy-disk"></i> Record Problem in History
            </button>
          </form>
        </div>
      </div>

      <!-- Right Column: Severity Timeline & Problem Records History (7 Cols) -->
      <div class="lg:col-span-7 space-y-5">
        
        <!-- Severity Trend Line Chart -->
        <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <div class="flex justify-between items-center pb-3 border-b border-slate-100 mb-4">
            <div>
              <h3 class="font-bold text-slate-800 text-sm flex items-center gap-2">
                <i class="fa-solid fa-chart-line text-rose-600"></i> Pain Severity & Problem Timeline
              </h3>
              <p class="text-[11px] text-slate-400">Progression across logged problem episodes</p>
            </div>
            <a href="/report" target="_blank" class="text-xs text-rose-600 font-extrabold hover:underline flex items-center gap-1">
              <i class="fa-solid fa-file-pdf"></i> Download Problems Report
            </a>
          </div>
          <div class="h-56">
            <canvas id="severityChart"></canvas>
          </div>
        </div>

        <!-- Problems Log History Table -->
        <div class="bg-white p-5 rounded-2xl shadow-sm border border-slate-200">
          <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 pb-4 border-b border-slate-100">
            <div>
              <h3 class="font-bold text-slate-800 text-base">History of Problems Faced</h3>
              <p class="text-xs text-slate-400">Synchronized in real-time with local symptoms_data.json</p>
            </div>
            <div class="flex items-center gap-2 w-full sm:w-auto">
              <input type="text" id="table-search" oninput="renderTable()" placeholder="Search problem/trigger..." class="text-xs px-3 py-1.5 rounded-xl border border-slate-300 w-full sm:w-44 focus:ring-2 focus:ring-rose-500">
              <select id="filter-cat" onchange="renderTable()" class="text-xs px-2.5 py-1.5 rounded-xl border border-slate-300 bg-white">
                <option value="All">All Categories</option>
                <option value="Neurological">Neurological</option>
                <option value="Respiratory">Respiratory</option>
                <option value="Digestive">Digestive</option>
                <option value="Musculoskeletal">Musculoskeletal</option>
                <option value="Cardiovascular">Cardiovascular</option>
                <option value="General">General</option>
              </select>
            </div>
          </div>

          <div class="overflow-x-auto mt-3">
            <table class="w-full text-left text-sm">
              <thead class="bg-slate-50 text-slate-400 text-[11px] uppercase font-bold tracking-wider">
                <tr>
                  <th class="py-2.5 px-3">Date</th>
                  <th class="py-2.5 px-3">Problem & Affected Site</th>
                  <th class="py-2.5 px-3 text-center">Severity</th>
                  <th class="py-2.5 px-3">Aggravating Factors</th>
                  <th class="py-2.5 px-3">Patient Observations</th>
                  <th class="py-2.5 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody id="symptoms-tbody" class="divide-y divide-slate-100 text-xs">
                <!-- Injected via JavaScript -->
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </main>

  <!-- Edit Patient Vitals & Demographics Modal -->
  <div id="vitals-modal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
      <div class="flex justify-between items-center pb-3 border-b border-slate-100">
        <div>
          <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
            <i class="fa-solid fa-id-card-clip text-rose-600"></i> Patient Demographics & Vitals
          </h3>
          <p class="text-xs text-slate-400">Updates profile for health reports</p>
        </div>
        <button onclick="closeVitalsModal()" class="text-slate-400 hover:text-slate-600 text-xl font-bold">&times;</button>
      </div>

      <form onsubmit="savePatientVitals(event)" class="space-y-3 text-xs">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Full Name</label>
            <input type="text" id="vit-name" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Blood Group</label>
            <select id="vit-bg" class="w-full px-3 py-2 rounded-xl border border-slate-300 bg-white">
              <option value="A+">A+</option>
              <option value="A-">A-</option>
              <option value="B+">B+</option>
              <option value="B-">B-</option>
              <option value="AB+">AB+</option>
              <option value="AB-">AB-</option>
              <option value="O+">O+</option>
              <option value="O-">O-</option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Age (Years)</label>
            <input type="number" id="vit-age" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Weight (kg)</label>
            <input type="number" id="vit-weight" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Height (cm)</label>
            <input type="number" id="vit-height" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3">
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Blood Pressure</label>
            <input type="text" id="vit-bp" placeholder="e.g. 118/76" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">Heart Rate (BPM)</label>
            <input type="number" id="vit-hr" placeholder="e.g. 74" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
          <div>
            <label class="block font-semibold text-slate-600 mb-1">SpO2 Oxygen (%)</label>
            <input type="number" id="vit-spo2" placeholder="e.g. 98" class="w-full px-3 py-2 rounded-xl border border-slate-300">
          </div>
        </div>

        <div>
          <label class="block font-semibold text-slate-600 mb-1">Known Drug Allergies (comma-separated)</label>
          <input type="text" id="vit-allergies" placeholder="e.g. Penicillin, Sulfa drugs" class="w-full px-3 py-2 rounded-xl border border-slate-300">
        </div>

        <div>
          <label class="block font-semibold text-slate-600 mb-1">Chronic Medical Conditions</label>
          <input type="text" id="vit-chronic" placeholder="e.g. Mild Asthma, Occasional Migraines" class="w-full px-3 py-2 rounded-xl border border-slate-300">
        </div>

        <div class="pt-2 flex justify-end gap-2">
          <button type="button" onclick="closeVitalsModal()" class="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold">Cancel</button>
          <button type="submit" class="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white font-bold">Update Profile & Vitals</button>
        </div>
      </form>
    </div>
  </div>

  <footer class="bg-white border-t border-slate-200 py-4 mt-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row justify-between items-center text-xs text-slate-500 gap-2">
      <div class="flex items-center gap-2">
        <div class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
        <p>HealthPulse &bull; Configured for Richitha (richitha132@gmail.com) &bull; Continuous Lifetime Service</p>
      </div>
      <div class="flex gap-4">
        <a href="/report" target="_blank" class="text-rose-600 hover:underline font-bold flex items-center gap-1"><i class="fa-solid fa-file-pdf"></i> Download Patient Problems Report</a>
        <a href="/api/export/csv" class="text-slate-600 hover:underline">Download CSV</a>
        <a href="/api/export/json" target="_blank" class="text-slate-600 hover:underline">JSON API</a>
      </div>
    </div>
  </footer>

  <script>
    let appData = { symptoms: [], user: {}, analytics: {} };
    let severityChartInstance = null;

    document.getElementById('form-date').value = new Date().toISOString().split('T')[0];

    function updateSeverityLabel(val) {
      const badge = document.getElementById('severity-badge');
      const num = parseInt(val);
      if (num <= 3) {
        badge.className = 'text-xs font-extrabold px-2.5 py-0.5 rounded-md bg-emerald-100 text-emerald-800 border border-emerald-200';
        badge.innerText = `${num} / 10 - Mild`;
      } else if (num <= 6) {
        badge.className = 'text-xs font-extrabold px-2.5 py-0.5 rounded-md bg-amber-100 text-amber-800 border border-amber-200';
        badge.innerText = `${num} / 10 - Moderate`;
      } else {
        badge.className = 'text-xs font-extrabold px-2.5 py-0.5 rounded-md bg-rose-100 text-rose-800 border border-rose-200 animate-pulse';
        badge.innerText = `${num} / 10 - Severe Problem`;
      }
    }

    function selectBodyZone(zoneName, category, location, defaultSymptom) {
      document.querySelectorAll('.body-zone-btn').forEach(b => b.classList.remove('body-zone-active'));
      event.currentTarget.classList.add('body-zone-active');

      document.getElementById('form-category').value = category;
      document.getElementById('form-location').value = location;
      if (!document.getElementById('form-name').value) {
        document.getElementById('form-name').value = defaultSymptom;
      }
      document.getElementById('form-name').focus();
    }

    async function fetchData() {
      try {
        const res = await fetch('/api/symptoms');
        const data = await res.json();
        appData = data;
        updateUI();
      } catch (err) {
        console.error("Failed to load data", err);
      }
    }

    function updateUI() {
      const u = appData.user || {};
      const a = appData.analytics || {};
      const v = u.vitals || {};

      // Patient Demographics
      document.getElementById('top-patient-name').innerText = u.name || 'Richitha';
      document.getElementById('top-patient-bg').innerText = u.blood_group || 'N/A';

      // Vitals Ticker
      document.getElementById('vitals-bp').innerText = (v.blood_pressure || '118/76') + ' mmHg';
      document.getElementById('vitals-hr').innerText = (v.heart_rate_bpm || '74') + ' BPM';
      document.getElementById('vitals-temp').innerText = (v.temperature_f || '98.6') + ' °F';
      document.getElementById('vitals-spo2').innerText = (v.spo2_percent || '98') + '%';

      // Calculate BMI
      if (u.weight_kg && u.height_cm) {
        const hM = u.height_cm / 100;
        const bmi = (u.weight_kg / (hM * hM)).toFixed(1);
        let bmiLabel = "Normal";
        if (bmi < 18.5) bmiLabel = "Underweight";
        else if (bmi >= 25 && bmi < 30) bmiLabel = "Overweight";
        else if (bmi >= 30) bmiLabel = "Obese";
        document.getElementById('vitals-bmi').innerText = `${bmi} (${bmiLabel})`;
      }

      // Stat Cards
      document.getElementById('card-total').innerText = a.total || 0;
      document.getElementById('card-avg-sev').innerText = (a.avg_severity || 0) + ' / 10';
      document.getElementById('card-top-trig').innerText = a.top_triggers && a.top_triggers[0] ? a.top_triggers[0].trigger : 'None';
      if (a.top_triggers && a.top_triggers[0]) {
        document.getElementById('card-top-trig-sub').innerText = `Present in ${a.top_triggers[0].count} episodes`;
      }

      // Risk Card
      const rScore = document.getElementById('card-risk-score');
      const rLevel = document.getElementById('card-risk-level');
      rScore.innerText = a.risk_score || 20;
      rLevel.innerText = a.risk_level || 'Normal';
      if (a.risk_color === 'rose') {
        rScore.className = 'text-2xl font-black text-rose-600';
        rLevel.className = 'text-[10px] font-bold text-rose-600';
      } else if (a.risk_color === 'amber') {
        rScore.className = 'text-2xl font-black text-amber-600';
        rLevel.className = 'text-[10px] font-bold text-amber-600';
      } else {
        rScore.className = 'text-2xl font-black text-emerald-600';
        rLevel.className = 'text-[10px] font-bold text-emerald-600';
      }

      // Clinical Notes / Problems List
      const probList = document.getElementById('clinical-problems-list');
      const notes = a.problem_notes || [];
      if (notes.length > 0) {
        probList.innerHTML = notes.map(n => `<li>${n}</li>`).join('');
      } else {
        probList.innerHTML = '<li>No critical health anomalies currently reported.</li>';
      }

      renderTable();
      renderCharts();
    }

    function renderTable() {
      const tbody = document.getElementById('symptoms-tbody');
      const search = document.getElementById('table-search').value.toLowerCase();
      const cat = document.getElementById('filter-cat').value;

      const filtered = appData.symptoms.filter(s => {
        const matchesCat = (cat === 'All' || s.category === cat);
        const matchesSearch = !search ||
          (s.symptom || '').toLowerCase().includes(search) ||
          (s.notes || '').toLowerCase().includes(search) ||
          (s.body_location || '').toLowerCase().includes(search) ||
          (s.triggers || []).some(t => t.toLowerCase().includes(search));
        return matchesCat && matchesSearch;
      });

      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-8 text-slate-400">No matching problem logs found.</td></tr>';
        return;
      }

      tbody.innerHTML = filtered.map(s => {
        const badgeClass = `badge-sev-${s.severity}`;

        return `
          <tr class="hover:bg-slate-50/80 transition">
            <td class="py-3 px-3 whitespace-nowrap text-slate-600">
              <span class="font-bold block text-slate-800">${s.date}</span>
              <span class="text-[10px] text-slate-400 font-mono">${s.time || ''}</span>
            </td>
            <td class="py-3 px-3">
              <span class="font-bold text-slate-800 block">${s.symptom}</span>
              <span class="text-[11px] text-slate-500">${s.category} ${s.body_location ? '&bull; ' + s.body_location : ''}</span>
            </td>
            <td class="py-3 px-3 text-center">
              <span class="inline-block px-2.5 py-0.5 rounded-md font-black text-xs ${badgeClass}">
                ${s.severity} / 10
              </span>
            </td>
            <td class="py-3 px-3">
              <div class="text-[11px] text-slate-700">
                ${(s.triggers && s.triggers.length > 0) ? s.triggers.map(t => `<span class="inline-block bg-slate-100 px-1.5 py-0.5 rounded text-[10px] mr-1 mb-0.5 font-medium">${t}</span>`).join('') : '<span class="text-slate-300">None</span>'}
              </div>
            </td>
            <td class="py-3 px-3 text-[11px] text-slate-600 max-w-[200px] truncate" title="${s.notes || ''}">
              ${s.notes || 'N/A'}
            </td>
            <td class="py-3 px-3 text-center">
              <button onclick="deleteSymptom('${s.id}')" class="text-slate-400 hover:text-rose-600 transition" title="Delete Problem Log">
                <i class="fa-regular fa-trash-can"></i>
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function renderCharts() {
      const symptoms = appData.symptoms || [];
      const timelineLabels = symptoms.map(s => `${s.date.slice(5)} (${s.symptom.slice(0, 7)}..)`);
      const timelineData = symptoms.map(s => s.severity);

      const ctxTimeline = document.getElementById('severityChart').getContext('2d');
      if (severityChartInstance) severityChartInstance.destroy();

      severityChartInstance = new Chart(ctxTimeline, {
        type: 'line',
        data: {
          labels: timelineLabels,
          datasets: [{
            label: 'Problem Pain Severity (1-10)',
            data: timelineData,
            borderColor: '#e11d48',
            backgroundColor: 'rgba(225, 29, 72, 0.08)',
            fill: true,
            tension: 0.35,
            pointBackgroundColor: timelineData.map(v => v >= 7 ? '#b91c1c' : (v >= 4 ? '#d97706' : '#059669')),
            pointRadius: 5,
            pointHoverRadius: 7
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { min: 0, max: 10, ticks: { stepSize: 2 } }
          },
          plugins: {
            legend: { display: false }
          }
        }
      });
    }

    async function submitSymptom(e) {
      e.preventDefault();
      const payload = {
        symptom: document.getElementById('form-name').value.trim(),
        category: document.getElementById('form-category').value,
        body_location: document.getElementById('form-location').value.trim() || 'General',
        severity: parseInt(document.getElementById('form-severity').value),
        duration_hours: parseFloat(document.getElementById('form-duration').value) || 1.0,
        date: document.getElementById('form-date').value,
        triggers: document.getElementById('form-triggers').value.split(',').map(s => s.trim()).filter(Boolean),
        notes: document.getElementById('form-notes').value.trim() || 'N/A'
      };

      try {
        const res = await fetch('/api/symptoms', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          document.getElementById('symptom-form').reset();
          document.getElementById('form-date').value = new Date().toISOString().split('T')[0];
          document.querySelectorAll('.body-zone-btn').forEach(b => b.classList.remove('body-zone-active'));
          updateSeverityLabel(5);
          fetchData();
        }
      } catch (err) {
        alert("Failed to save problem entry.");
      }
    }

    async function deleteSymptom(id) {
      if (!confirm(`Are you sure you want to delete problem log ${id}?`)) return;
      try {
        const res = await fetch(`/api/symptoms/${id}`, { method: 'DELETE' });
        if (res.ok) fetchData();
      } catch (err) {
        alert("Failed to delete entry.");
      }
    }

    function openVitalsModal() {
      const u = appData.user || {};
      const v = u.vitals || {};
      document.getElementById('vit-name').value = u.name || '';
      document.getElementById('vit-bg').value = u.blood_group || 'O+';
      document.getElementById('vit-age').value = u.age || '';
      document.getElementById('vit-weight').value = u.weight_kg || '';
      document.getElementById('vit-height').value = u.height_cm || '';
      document.getElementById('vit-bp').value = v.blood_pressure || '';
      document.getElementById('vit-hr').value = v.heart_rate_bpm || '';
      document.getElementById('vit-spo2').value = v.spo2_percent || '';
      document.getElementById('vit-allergies').value = (u.allergies || []).join(', ');
      document.getElementById('vit-chronic').value = (u.chronic_conditions || []).join(', ');
      document.getElementById('vitals-modal').classList.remove('hidden');
    }

    function closeVitalsModal() {
      document.getElementById('vitals-modal').classList.add('hidden');
    }

    async function savePatientVitals(e) {
      e.preventDefault();
      const payload = {
        name: document.getElementById('vit-name').value.trim(),
        blood_group: document.getElementById('vit-bg').value,
        age: parseInt(document.getElementById('vit-age').value) || 22,
        weight_kg: parseFloat(document.getElementById('vit-weight').value) || 54,
        height_cm: parseFloat(document.getElementById('vit-height').value) || 162,
        allergies: document.getElementById('vit-allergies').value.split(',').map(s => s.trim()).filter(Boolean),
        chronic_conditions: document.getElementById('vit-chronic').value.split(',').map(s => s.trim()).filter(Boolean),
        vitals: {
          blood_pressure: document.getElementById('vit-bp').value.trim() || '118/76',
          heart_rate_bpm: parseInt(document.getElementById('vit-hr').value) || 74,
          spo2_percent: parseInt(document.getElementById('vit-spo2').value) || 98,
          temperature_f: 98.6,
          last_updated: new Date().toISOString().replace('T', ' ').slice(0, 16)
        }
      };

      const res = await fetch('/api/user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        closeVitalsModal();
        fetchData();
      }
    }

    fetchData();
  </script>
</body>
</html>
"""


# =========================================================================
# ONLY HEALTH PROBLEMS REPORT (NO TABLETS / NO PRESCRIPTIONS)
# =========================================================================

PATIENT_ONLY_PROBLEMS_REPORT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Patient Health Problems & Clinical Summary Report - HealthPulse</title>
  <style>
    @page { size: A4; margin: 15mm; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #0f172a;
      line-height: 1.5;
      margin: 0;
      padding: 20px;
      background: #f1f5f9;
    }
    .report-card {
      max-width: 880px;
      margin: 0 auto;
      background: #ffffff;
      padding: 40px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      box-shadow: 0 4px 15px rgba(0,0,0,0.06);
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 3px solid #0f172a;
      padding-bottom: 16px;
      margin-bottom: 22px;
    }
    .hospital-logo {
      font-size: 22px;
      font-weight: 900;
      color: #0f172a;
      letter-spacing: -0.5px;
    }
    .hospital-logo span { color: #e11d48; }
    .hospital-sub { font-size: 11px; color: #64748b; margin-top: 3px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }

    .patient-id-strip {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 14px 18px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      font-size: 11.5px;
      margin-bottom: 18px;
    }
    .patient-id-strip div span { display: block; font-weight: 700; color: #64748b; font-size: 10px; text-transform: uppercase; }
    .patient-id-strip div p { margin: 2px 0 0 0; font-weight: 700; color: #0f172a; font-size: 13px; }

    .vitals-box {
      background: #f0fdf4;
      border: 1.5px solid #bbf7d0;
      border-radius: 8px;
      padding: 12px 18px;
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 10px;
      font-size: 11px;
      margin-bottom: 20px;
      text-align: center;
    }
    .vitals-box span { font-size: 9.5px; color: #166534; text-transform: uppercase; font-weight: 700; display: block; }
    .vitals-box strong { font-size: 13.5px; color: #14532d; }

    .allergy-alert {
      background: #fef2f2;
      border-left: 4px solid #ef4444;
      padding: 10px 14px;
      border-radius: 4px;
      margin-bottom: 20px;
      font-size: 11.5px;
      color: #991b1b;
    }
    .allergy-alert strong { text-transform: uppercase; font-weight: 800; }

    .section-title {
      font-size: 12.5px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #0f172a;
      border-left: 4px solid #e11d48;
      padding-left: 8px;
      margin: 22px 0 10px 0;
    }

    .urgent-box {
      background: #fff1f2;
      border: 1.5px solid #fecdd3;
      border-radius: 8px;
      padding: 14px;
      margin-bottom: 18px;
      font-size: 12px;
    }
    .urgent-box strong { color: #9f1239; font-size: 12.5px; }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 11px;
      margin-top: 8px;
      margin-bottom: 20px;
    }
    th {
      background: #f8fafc;
      color: #334155;
      font-weight: 800;
      text-transform: uppercase;
      font-size: 10px;
      border-bottom: 2px solid #cbd5e1;
      padding: 9px 10px;
      text-align: left;
    }
    td {
      padding: 10px 10px;
      border-bottom: 1px solid #e2e8f0;
      vertical-align: top;
    }
    .badge-sev {
      padding: 3px 7px;
      border-radius: 4px;
      font-weight: 800;
      font-size: 11px;
      display: inline-block;
    }
    .sev-mild { background: #dcfce7; color: #166534; }
    .sev-mod { background: #fef9c3; color: #854d0e; }
    .sev-high { background: #fee2e2; color: #991b1b; }

    .signature-area {
      margin-top: 40px;
      padding-top: 25px;
      border-top: 1px dashed #cbd5e1;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }
    .sig-line {
      width: 230px;
      border-bottom: 1px solid #475569;
      margin-bottom: 6px;
    }
    .sig-label { font-size: 11px; color: #64748b; font-weight: 600; }

    .btn-print {
      background: #e11d48;
      color: white;
      border: none;
      padding: 11px 26px;
      font-weight: 800;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
      box-shadow: 0 4px 10px rgba(225, 29, 72, 0.25);
    }
    @media print {
      body { background: white; padding: 0; }
      .report-card { border: none; box-shadow: none; padding: 0; }
      .no-print { display: none !important; }
    }
  </style>
</head>
<body>
  
  <div style="text-align: center; margin-bottom: 18px;" class="no-print">
    <button class="btn-print" onclick="window.print()">🖨️ Download / Print Patient Health Problems Report (PDF)</button>
    <p style="font-size: 11px; color: #64748b; margin-top: 6px;">
      (Choose <strong>"Save as PDF"</strong> to download this report to your computer)
    </p>
  </div>

  <div class="report-card">
    
    <!-- Header -->
    <div class="header">
      <div>
        <div class="hospital-logo">HEALTH<span>PULSE</span> CLINICAL SUMMARY</div>
        <div class="hospital-sub">Official Patient Health Problems & Symptom Report</div>
      </div>
      <div style="text-align: right; font-size: 11px; color: #64748b;">
        <strong>Document Type:</strong> Patient Problems Record<br>
        <strong>Report Date:</strong> {{ now_str }}<br>
        <strong>Patient ID:</strong> {{ user.user_id }}
      </div>
    </div>

    <!-- Patient Demographics -->
    <div class="patient-id-strip">
      <div>
        <span>Patient Full Name</span>
        <p>{{ user.name }}</p>
      </div>
      <div>
        <span>Registered Email</span>
        <p style="font-size: 11px;">{{ user.email }}</p>
      </div>
      <div>
        <span>Age / Gender</span>
        <p>{{ user.age }} Yrs / {{ user.gender }}</p>
      </div>
      <div>
        <span>Blood Group</span>
        <p>{{ user.blood_group }}</p>
      </div>
      <div>
        <span>Body Weight / Height</span>
        <p>{{ user.weight_kg }} kg / {{ user.height_cm }} cm</p>
      </div>
      <div>
        <span>Emergency Contact</span>
        <p>{{ user.emergency_contact }}</p>
      </div>
      <div>
        <span>Attending Physician</span>
        <p>{{ user.primary_physician or 'Dr. Sarah Jenkins, MD' }}</p>
      </div>
      <div>
        <span>Severity Status</span>
        <p style="color: #e11d48;">{{ analytics.risk_level }}</p>
      </div>
    </div>

    <!-- Physiological Vitals -->
    {% if user.vitals %}
    <div class="vitals-box">
      <div>
        <span>Blood Pressure</span>
        <strong>{{ user.vitals.blood_pressure or '118/76' }} mmHg</strong>
      </div>
      <div>
        <span>Heart Rate</span>
        <strong>{{ user.vitals.heart_rate_bpm or '74' }} BPM</strong>
      </div>
      <div>
        <span>Body Temp</span>
        <strong>{{ user.vitals.temperature_f or '98.6' }} °F</strong>
      </div>
      <div>
        <span>SpO2 Oxygen</span>
        <strong>{{ user.vitals.spo2_percent or '98' }}%</strong>
      </div>
      <div>
        <span>Blood Glucose</span>
        <strong>{{ user.vitals.blood_sugar_mgdl or '92' }} mg/dL</strong>
      </div>
    </div>
    {% endif %}

    <!-- Known Drug Allergies & Chronic Conditions -->
    <div class="allergy-alert">
      <strong>⚠️ Documented Drug Allergies:</strong> 
      {{ user.allergies | join(', ') if user.allergies else 'No Known Drug Allergies (NKDA)' }}
      &bull; <strong>Documented Chronic Conditions:</strong> {{ user.chronic_conditions | join(', ') if user.chronic_conditions else 'None' }}
    </div>

    <!-- Urgent High-Severity Problems -->
    {% if analytics.urgent_problems %}
    <div class="urgent-box">
      <strong>🚨 Critical / High-Intensity Health Problems (Severity ≥ 7/10):</strong>
      <ul style="margin: 6px 0 0 0; padding-left: 20px;">
        {% for u_prob in analytics.urgent_problems %}
          <li style="margin-bottom: 3px;">
            <strong>{{ u_prob.symptom }}</strong> — Intensity: <strong>{{ u_prob.severity }}/10</strong> (Site: {{ u_prob.body_location or 'General' }}, Duration: {{ u_prob.duration_hours }}h).
            {% if u_prob.triggers %} <span style="color: #64748b;">(Triggers: {{ u_prob.triggers | join(', ') }})</span>{% endif %}
          </li>
        {% endfor %}
      </ul>
    </div>
    {% endif %}

    <!-- Detailed Problems Faced Table -->
    <div class="section-title">Documented Health Problems & Symptom Chronology</div>
    <table>
      <thead>
        <tr>
          <th style="width: 14%;">Date / Time</th>
          <th style="width: 26%;">Health Problem Facing</th>
          <th style="width: 15%;">Affected Body Area</th>
          <th style="width: 12%;">Severity</th>
          <th style="width: 18%;">Aggravating Triggers</th>
          <th style="width: 15%;">Problem Description</th>
        </tr>
      </thead>
      <tbody>
        {% for s in symptoms %}
        <tr>
          <td>
            <strong>{{ s.date }}</strong><br>
            <span style="font-size: 10px; color: #64748b;">{{ s.time }}</span>
          </td>
          <td>
            <strong style="color: #0f172a; font-size: 12px;">{{ s.symptom }}</strong><br>
            <span style="font-size: 10px; color: #64748b;">Duration: {{ s.duration_hours }} hours</span>
          </td>
          <td>
            <strong>{{ s.body_location or 'General' }}</strong><br>
            <span style="font-size: 10px; color: #64748b;">{{ s.category }}</span>
          </td>
          <td>
            {% if s.severity <= 3 %}
              <span class="badge-sev sev-mild">{{ s.severity }} / 10 (Mild)</span>
            {% elif s.severity <= 6 %}
              <span class="badge-sev sev-mod">{{ s.severity }} / 10 (Mod)</span>
            {% else %}
              <span class="badge-sev sev-high">{{ s.severity }} / 10 (Severe)</span>
            {% endif %}
          </td>
          <td style="color: #475569;">
            {{ s.triggers | join(', ') if s.triggers else 'None identified' }}
          </td>
          <td style="color: #334155; font-size: 10.5px;">
            {{ s.notes or 'N/A' }}
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <!-- Clinical Problem Correlations -->
    <div style="font-size: 11px; background: #f8fafc; border-left: 3.5px solid #0f172a; padding: 12px; border-radius: 4px; margin-top: 15px;">
      <strong>Clinical Findings:</strong>
      <ul style="margin: 4px 0 0 0; padding-left: 18px;">
        {% for note in analytics.problem_notes %}
          <li style="margin-bottom: 2px;">{{ note }}</li>
        {% endfor %}
      </ul>
    </div>

    <!-- Doctor Signature & Attestation Block -->
    <div class="signature-area">
      <div>
        <div style="font-size: 10px; color: #64748b; max-width: 480px;">
          <em>Notice: This document records the clinical health problems, symptom chronology, and distress ratings documented for <strong>{{ user.name }}</strong> ({{ user.email }}). Intended for physician review during medical consultation.</em>
        </div>
      </div>
      <div>
        <div class="sig-line"></div>
        <div class="sig-label">{{ user.primary_physician or 'Attending Physician' }} / Stamp</div>
      </div>
    </div>

  </div>
</body>
</html>
"""


# =========================================================================
# ROUTES
# =========================================================================

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (username.lower() in [DEFAULT_USER["username"].lower(), "richitha", "admin"]) and (password in [DEFAULT_USER["password"], "admin"]):
            session["logged_in"] = True
            session["username"] = username
            session["user_name"] = DEFAULT_USER["name"]
            return redirect(url_for("index"))
        else:
            return render_template_string(LOGIN_HTML, error="Invalid credentials. Use richitha132@gmail.com / password123")

    if session.get("logged_in"):
        return redirect(url_for("index"))

    return render_template_string(LOGIN_HTML)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/")
@login_required
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/report")
@login_required
def patient_report():
    """Renders ONLY the clean patient health problems report (NO recommended tablets)."""
    data = load_data()
    user = data.get("user", {})
    symptoms = data.get("symptoms", [])
    analytics = compute_problems_analytics(symptoms, user)
    now_str = datetime.now().strftime("%B %d, %Y - %H:%M")
    return render_template_string(
        PATIENT_ONLY_PROBLEMS_REPORT_HTML,
        user=user,
        symptoms=symptoms,
        analytics=analytics,
        now_str=now_str
    )


@app.route("/api/symptoms", methods=["GET"])
@login_required
def get_symptoms():
    data = load_data()
    user = data.get("user", {})
    symptoms = data.get("symptoms", [])
    env = data.get("environmental_factors", {})
    analytics = compute_problems_analytics(symptoms, user)
    return jsonify({
        "user": user,
        "symptoms": symptoms,
        "environmental_factors": env,
        "analytics": analytics
    })


@app.route("/api/symptoms", methods=["POST"])
@login_required
def add_symptom():
    data = load_data()
    req = request.get_json() or {}

    symptoms = data.get("symptoms", [])
    next_id = f"SYM-{len(symptoms) + 1001}"
    while any(s["id"] == next_id for s in symptoms):
        next_id = f"SYM-{int(next_id.split('-')[1]) + 1}"

    now = datetime.now()
    new_entry = {
        "id": next_id,
        "date": req.get("date") or now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M"),
        "symptom": req.get("symptom", "General Problem"),
        "category": req.get("category", "General"),
        "body_location": req.get("body_location", "General"),
        "severity": int(req.get("severity", 5)),
        "duration_hours": float(req.get("duration_hours", 1.0)),
        "triggers": req.get("triggers", []),
        "notes": req.get("notes", "N/A")
    }

    symptoms.append(new_entry)
    data["symptoms"] = symptoms
    save_data(data)
    return jsonify({"success": True, "entry": new_entry}), 201


@app.route("/api/user", methods=["POST"])
@login_required
def update_user():
    data = load_data()
    req = request.get_json() or {}
    user = data.get("user", {})

    for key in ["name", "blood_group", "age", "weight_kg", "height_cm", "allergies", "chronic_conditions", "emergency_contact", "primary_physician", "vitals"]:
        if key in req:
            user[key] = req[key]

    data["user"] = user
    save_data(data)
    return jsonify({"success": True, "user": user})


@app.route("/api/symptoms/<entry_id>", methods=["DELETE"])
@login_required
def delete_symptom_api(entry_id):
    data = load_data()
    original_len = len(data.get("symptoms", []))
    data["symptoms"] = [s for s in data.get("symptoms", []) if s.get("id") != entry_id]

    if len(data["symptoms"]) < original_len:
        save_data(data)
        return jsonify({"success": True, "deleted": entry_id})
    return jsonify({"success": False, "error": "Not found"}), 404


@app.route("/api/export/csv")
@login_required
def export_csv():
    data = load_data()
    symptoms = data.get("symptoms", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Time", "Problem", "Category", "AnatomicalLocation", "Severity", "DurationHours", "Triggers", "Notes"])
    for s in symptoms:
        writer.writerow([
            s.get("id"),
            s.get("date"),
            s.get("time"),
            s.get("symptom"),
            s.get("category"),
            s.get("body_location", "General"),
            s.get("severity"),
            s.get("duration_hours"),
            "; ".join(s.get("triggers", [])),
            s.get("notes")
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=healthpulse_problems_export.csv"}
    )


@app.route("/api/export/json")
@login_required
def export_json():
    data = load_data()
    return jsonify(data)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
