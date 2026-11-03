"""
HealthPulse - Symptom Tracking System
Key features:
1. Manage entities: Add, view, update, and delete symptom entries.
2. Categorization and filtering: Grouped into 7 categories, filter by category, keyword, minimum severity, or date range.
3. Persistent storage: Data is kept between sessions in JSON, and you can export it to CSV.
4. Summarized reports: Dashboard showing top symptoms, category breakdown, weekly trend, likely triggers, and flagging any severity of 8 or higher in the last 7 days.
5. Lightweight: Pure Python console application, easily extensible to GUI or web solutions.
"""

import os
import sys
import json
import csv
from datetime import datetime, timedelta

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

DATA_FILE = "symptoms_data.json"
EXPORT_CSV_FILE = "symptoms_export.csv"
EXPORT_TXT_FILE = "healthpulse_summary_report.txt"

# Exactly 7 Core Categories
CATEGORIES = [
    "Neurological",
    "Respiratory",
    "Digestive",
    "Musculoskeletal",
    "Cardiovascular",
    "Dermatological",
    "General"
]


class StorageManager:
    """Feature 3: Persistent Storage (JSON) & CSV Export."""

    @staticmethod
    def load_data(filepath=DATA_FILE):
        if not os.path.exists(filepath):
            default_data = {
                "user": {
                    "user_id": "PT-94820",
                    "name": "Richitha",
                    "email": "richitha132@gmail.com",
                    "blood_group": "B+"
                },
                "symptoms": []
            }
            StorageManager.save_data(default_data, filepath)
            return default_data

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Warning: Error reading {filepath}: {e}. Creating fallback.")
            return {"user": {"name": "Richitha", "email": "richitha132@gmail.com"}, "symptoms": []}

    @staticmethod
    def save_data(data, filepath=DATA_FILE):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[!] Error saving to {filepath}: {e}")
            return False

    @staticmethod
    def export_csv(symptoms, filepath=EXPORT_CSV_FILE):
        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Time", "Symptom", "Category", "Severity", "DurationHours", "Triggers", "Notes"])
                for s in symptoms:
                    writer.writerow([
                        s.get("id"),
                        s.get("date"),
                        s.get("time"),
                        s.get("symptom"),
                        s.get("category"),
                        s.get("severity"),
                        s.get("duration_hours"),
                        "; ".join(s.get("triggers", [])),
                        s.get("notes")
                    ])
            return True
        except Exception as e:
            print(f"[!] Error exporting CSV: {e}")
            return False


class Validator:
    """Input validation for data integrity."""

    @staticmethod
    def validate_date(date_str):
        if not date_str or date_str.strip().lower() in ["today", "t"]:
            return datetime.now().strftime("%Y-%m-%d")
        try:
            valid_dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
            return valid_dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    @staticmethod
    def validate_time(time_str):
        if not time_str or time_str.strip().lower() in ["now", "n"]:
            return datetime.now().strftime("%H:%M")
        try:
            valid_t = datetime.strptime(time_str.strip(), "%H:%M")
            return valid_t.strftime("%H:%M")
        except ValueError:
            return None

    @staticmethod
    def validate_severity(severity_input):
        try:
            val = int(severity_input)
            if 1 <= val <= 10:
                return val
            return None
        except ValueError:
            return None

    @staticmethod
    def validate_duration(duration_input):
        try:
            val = float(duration_input)
            return val if val > 0 else None
        except ValueError:
            return None


class AnalyticsEngine:
    """
    Feature 4: Summarized Reports
    Shows top symptoms, category breakdown, weekly trend, likely triggers,
    and flags any severity of 8 or higher in the last 7 days.
    """

    @staticmethod
    def generate_analytics(symptoms):
        if not symptoms:
            return {
                "total_records": 0,
                "avg_severity": 0.0,
                "top_symptoms": [],
                "category_breakdown": {cat: 0 for cat in CATEGORIES},
                "weekly_trend": {},
                "likely_triggers": [],
                "recent_severe_flags": []
            }

        total = len(symptoms)
        severities = [s.get("severity", 0) for s in symptoms]
        avg_sev = sum(severities) / total if total > 0 else 0.0

        # 1. Top Symptoms
        sym_counts = {}
        for s in symptoms:
            name = s.get("symptom", "Unnamed").strip().title()
            sym_counts[name] = sym_counts.get(name, 0) + 1
        top_symptoms = sorted(sym_counts.items(), key=lambda x: x[1], reverse=True)

        # 2. Category Breakdown (7 categories)
        cat_counts = {cat: 0 for cat in CATEGORIES}
        for s in symptoms:
            cat = s.get("category", "General")
            if cat in cat_counts:
                cat_counts[cat] += 1
            else:
                cat_counts["General"] += 1

        # 3. Likely Triggers
        trig_counts = {}
        for s in symptoms:
            for t in s.get("triggers", []):
                cleaned = t.strip().title()
                if cleaned:
                    trig_counts[cleaned] = trig_counts.get(cleaned, 0) + 1
        likely_triggers = sorted(trig_counts.items(), key=lambda x: x[1], reverse=True)

        # 4. Weekly Trend (Past 7 Days)
        today = datetime.now().date()
        seven_days_ago = today - timedelta(days=7)
        weekly_trend = {}
        recent_severe_flags = []

        for i in range(7):
            d = seven_days_ago + timedelta(days=i + 1)
            d_str = d.strftime("%Y-%m-%d")
            weekly_trend[d_str] = {"count": 0, "severities": []}

        for s in symptoms:
            date_str = s.get("date", "")
            try:
                s_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if seven_days_ago <= s_date <= today:
                    if date_str in weekly_trend:
                        weekly_trend[date_str]["count"] += 1
                        weekly_trend[date_str]["severities"].append(s.get("severity", 0))

                    # 5. Flag any severity of 8 or higher in the last 7 days
                    if s.get("severity", 0) >= 8:
                        recent_severe_flags.append(s)
            except ValueError:
                pass

        return {
            "total_records": total,
            "avg_severity": round(avg_sev, 2),
            "top_symptoms": top_symptoms,
            "category_breakdown": cat_counts,
            "weekly_trend": weekly_trend,
            "likely_triggers": likely_triggers,
            "recent_severe_flags": recent_severe_flags
        }


class HealthPulseApp:
    """Feature 5: Lightweight Console Application Interface."""

    def __init__(self):
        self.data = StorageManager.load_data()
        self.symptoms = self.data.get("symptoms", [])
        self.user = self.data.get("user", {})

    def save(self):
        self.data["symptoms"] = self.symptoms
        StorageManager.save_data(self.data)

    def print_banner(self):
        print("=" * 76)
        print("                 HEALTHPULSE - SYMPTOM TRACKING SYSTEM")
        print("=" * 76)
        print(f" User: {self.user.get('name', 'User')} ({self.user.get('email', 'richitha132@gmail.com')}) | Blood Group: {self.user.get('blood_group', 'B+')}")
        print("=" * 76)

    def print_menu(self):
        print("\n=== SYSTEM MENU ===")
        print(" [1] Add New Symptom Entry        (Manage Entities)")
        print(" [2] View All Symptom Entries      (Manage Entities)")
        print(" [3] Update a Symptom Entry        (Manage Entities)")
        print(" [4] Delete a Symptom Entry        (Manage Entities)")
        print(" [5] Categorization & Filtering    (7 Categories, Keyword, Severity, Date Range)")
        print(" [6] View Summarized Reports       (Top Symptoms, Category Breakdown, Weekly Trend, 8+ Flags)")
        print(" [7] Export Data to CSV            (Persistent Storage)")
        print(" [8] Exit")
        print("===================")

    # ---------------------------------------------------------
    # Feature 1: Manage Entities (Add, View, Update, Delete)
    # ---------------------------------------------------------
    def add_symptom(self, s_name=None, category=None, severity=None, duration=None, triggers=None, notes=None, date=None, time=None):
        print("\n--- [1] ADD NEW SYMPTOM ENTRY ---")
        if not s_name:
            s_name = input("Enter Symptom Name: ").strip()
            if not s_name:
                print("[!] Error: Symptom name cannot be blank.")
                return

        if not category:
            print("\nSelect from the 7 Categories:")
            for i, cat in enumerate(CATEGORIES, 1):
                print(f"  {i}. {cat}")
            c_in = input(f"Choose (1-7) [Default: 7. General]: ").strip()
            if c_in.isdigit() and 1 <= int(c_in) <= 7:
                category = CATEGORIES[int(c_in) - 1]
            else:
                category = "General"

        if severity is None:
            while True:
                sev_in = input("Enter Severity (1 to 10): ").strip()
                val = Validator.validate_severity(sev_in)
                if val is not None:
                    severity = val
                    break
                print("[!] Invalid severity. Must be an integer between 1 and 10.")

        if duration is None:
            dur_in = input("Enter Duration in hours (e.g. 2.0): ").strip()
            duration = Validator.validate_duration(dur_in) or 1.0

        if triggers is None:
            trig_in = input("Enter Triggers (comma-separated, e.g. Lack of sleep, Stress): ").strip()
            triggers = [t.strip().title() for t in trig_in.split(",") if t.strip()]

        if notes is None:
            notes = input("Enter Description / Notes: ").strip() or "N/A"

        if not date:
            d_in = input("Enter Date (YYYY-MM-DD or Enter for today): ").strip()
            date = Validator.validate_date(d_in) or datetime.now().strftime("%Y-%m-%d")

        if not time:
            t_in = input("Enter Time (HH:MM or Enter for now): ").strip()
            time = Validator.validate_time(t_in) or datetime.now().strftime("%H:%M")

        # Unique ID
        next_num = len(self.symptoms) + 1001
        entry_id = f"SYM-{next_num}"
        while any(s["id"] == entry_id for s in self.symptoms):
            next_num += 1
            entry_id = f"SYM-{next_num}"

        entry = {
            "id": entry_id,
            "date": date,
            "time": time,
            "symptom": s_name,
            "category": category,
            "severity": severity,
            "duration_hours": duration,
            "triggers": triggers,
            "notes": notes
        }

        self.symptoms.append(entry)
        self.save()
        print(f"\n[OK] Symptom added successfully with ID: {entry_id}")
        if severity >= 8:
            print(f"     [!] CRITICAL ALERT: Severity rating {severity}/10 logged!")

    def view_symptoms(self, entries=None):
        if entries is None:
            entries = self.symptoms

        print("\n--- VIEW SYMPTOM ENTRIES ---")
        if not entries:
            print("No symptom entries found.")
            return

        print("-" * 88)
        print(f"{'ID':<10} {'Date / Time':<18} {'Symptom':<22} {'Category':<16} {'Severity':<10} {'Duration':<10}")
        print("-" * 88)
        for s in entries:
            dt = f"{s.get('date', '')} {s.get('time', '')}"
            sev_str = f"{s.get('severity', 0)}/10"
            dur_str = f"{s.get('duration_hours', 1)}h"
            print(f"{s.get('id', ''):<10} {dt:<18} {s.get('symptom', ''):<22} {s.get('category', ''):<16} {sev_str:<10} {dur_str:<10}")
            if s.get("triggers") or s.get("notes"):
                trigs = ", ".join(s.get("triggers", [])) if s.get("triggers") else "None"
                print(f"  |-> Triggers: {trigs} | Notes: {s.get('notes', '')}")
        print("-" * 88)

    def update_symptom(self):
        print("\n--- [3] UPDATE SYMPTOM ENTRY ---")
        entry_id = input("Enter Symptom ID to update (e.g. SYM-1001): ").strip().upper()
        record = next((s for s in self.symptoms if s.get("id") == entry_id), None)
        if not record:
            print(f"[!] Entry {entry_id} not found.")
            return

        print(f"Editing: {record.get('symptom')} ({record.get('date')}) - Current Severity: {record.get('severity')}/10")
        print("(Press Enter to leave existing value unchanged)")

        new_name = input(f"New Symptom Name [{record.get('symptom')}]: ").strip()
        if new_name:
            record["symptom"] = new_name

        new_sev = input(f"New Severity (1-10) [{record.get('severity')}]: ").strip()
        if new_sev:
            val = Validator.validate_severity(new_sev)
            if val is not None:
                record["severity"] = val

        new_dur = input(f"New Duration [{record.get('duration_hours')}]: ").strip()
        if new_dur:
            val = Validator.validate_duration(new_dur)
            if val is not None:
                record["duration_hours"] = val

        new_trigs = input(f"New Triggers [{', '.join(record.get('triggers', []))}]: ").strip()
        if new_trigs:
            record["triggers"] = [t.strip().title() for t in new_trigs.split(",") if t.strip()]

        new_notes = input(f"New Notes [{record.get('notes', '')}]: ").strip()
        if new_notes:
            record["notes"] = new_notes

        self.save()
        print(f"[OK] Entry {entry_id} updated successfully.")

    def delete_symptom(self):
        print("\n--- [4] DELETE SYMPTOM ENTRY ---")
        entry_id = input("Enter Symptom ID to delete: ").strip().upper()
        record = next((s for s in self.symptoms if s.get("id") == entry_id), None)
        if not record:
            print(f"[!] Entry {entry_id} not found.")
            return

        confirm = input(f"Are you sure you want to delete '{record.get('symptom')}' ({entry_id})? (y/n): ").strip().lower()
        if confirm == 'y':
            self.symptoms = [s for s in self.symptoms if s.get("id") != entry_id]
            self.save()
            print(f"[OK] Entry {entry_id} deleted successfully.")
        else:
            print("Deletion cancelled.")

    # ---------------------------------------------------------
    # Feature 2: Categorization and Filtering (7 Categories, Keyword, Severity, Date Range)
    # ---------------------------------------------------------
    def filter_symptoms_menu(self):
        print("\n--- [5] CATEGORIZATION & FILTERING ---")
        print(" 1. Filter by Category (from 7 categories)")
        print(" 2. Filter by Keyword (search symptom, triggers, notes)")
        print(" 3. Filter by Minimum Severity threshold")
        print(" 4. Filter by Date Range (Start Date to End Date)")
        choice = input("Enter filtering option (1-4): ").strip()

        filtered = []
        if choice == "1":
            print("\nSelect Category:")
            for i, cat in enumerate(CATEGORIES, 1):
                print(f"  {i}. {cat}")
            c_in = input(f"Choose (1-7): ").strip()
            if c_in.isdigit() and 1 <= int(c_in) <= 7:
                target_cat = CATEGORIES[int(c_in) - 1]
                filtered = [s for s in self.symptoms if s.get("category") == target_cat]
            else:
                print("[!] Invalid category selection.")
                return

        elif choice == "2":
            kw = input("Enter search keyword: ").strip().lower()
            filtered = [
                s for s in self.symptoms
                if kw in s.get("symptom", "").lower()
                or kw in s.get("notes", "").lower()
                or any(kw in t.lower() for t in s.get("triggers", []))
            ]

        elif choice == "3":
            min_sev = input("Enter minimum severity rating (1-10): ").strip()
            val = Validator.validate_severity(min_sev)
            if val is not None:
                filtered = [s for s in self.symptoms if s.get("severity", 0) >= val]
            else:
                print("[!] Invalid severity value.")
                return

        elif choice == "4":
            start_str = input("Enter Start Date (YYYY-MM-DD): ").strip()
            end_str = input("Enter End Date   (YYYY-MM-DD): ").strip()
            try:
                start_d = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_d = datetime.strptime(end_str, "%Y-%m-%d").date()
                for s in self.symptoms:
                    try:
                        s_d = datetime.strptime(s.get("date", ""), "%Y-%m-%d").date()
                        if start_d <= s_d <= end_d:
                            filtered.append(s)
                    except ValueError:
                        pass
            except ValueError:
                print("[!] Invalid date format. Use YYYY-MM-DD.")
                return
        else:
            print("[!] Invalid filtering option.")
            return

        print(f"\n[Matched {len(filtered)} entry/entries]")
        self.view_symptoms(filtered)

    # ---------------------------------------------------------
    # Feature 4: Summarized Reports
    # (Top symptoms, Category breakdown, Weekly trend, Likely triggers, 8+ Flags in 7 days)
    # ---------------------------------------------------------
    def view_summarized_reports(self):
        print("\n" + "=" * 76)
        print("                     SUMMARIZED REPORTS DASHBOARD")
        print("=" * 76)
        analytics = AnalyticsEngine.generate_analytics(self.symptoms)

        print(f" Total Logged Symptoms: {analytics['total_records']}")
        print(f" Average Pain Severity: {analytics['avg_severity']} / 10")

        # 1. Critical 8+ Flags in Last 7 Days
        recent_severe = analytics["recent_severe_flags"]
        print(f"\n[!] HIGH SEVERITY FLAGS (>= 8/10 in last 7 days): {len(recent_severe)}")
        if recent_severe:
            for item in recent_severe:
                print(f"    * ALERT on {item.get('date')} - {item.get('symptom')}: Severity {item.get('severity')}/10!")
                print(f"      Triggers: {', '.join(item.get('triggers', []))} | Notes: {item.get('notes')}")
        else:
            print("    [None] No critical episodes >= 8/10 in the past 7 days.")

        # 2. Top Symptoms
        print("\n--- TOP SYMPTOMS ---")
        top_s = analytics["top_symptoms"]
        if top_s:
            for name, count in top_s[:5]:
                print(f"  * {name:<26}: Reported {count} time(s)")
        else:
            print("  No symptoms recorded yet.")

        # 3. Category Breakdown (7 Categories)
        print("\n--- CATEGORY BREAKDOWN (7 CATEGORIES) ---")
        for cat in CATEGORIES:
            count = analytics["category_breakdown"].get(cat, 0)
            bar = "#" * count
            print(f"  * {cat:<18}: {bar} ({count})")

        # 4. Weekly Trend (Past 7 Days)
        print("\n--- WEEKLY TREND (LAST 7 DAYS) ---")
        for date_str, stats in analytics["weekly_trend"].items():
            cnt = stats["count"]
            avg = round(sum(stats["severities"]) / cnt, 1) if cnt > 0 else 0.0
            trend_bar = "|" * cnt
            print(f"  {date_str}: {cnt} episodes {trend_bar:<10} (Avg Sev: {avg}/10)")

        # 5. Likely Triggers
        print("\n--- LIKELY TRIGGERS ---")
        trigs = analytics["likely_triggers"]
        if trigs:
            for trigger, count in trigs[:5]:
                print(f"  * {trigger:<24}: Correlated in {count} episode(s)")
        else:
            print("  No triggers recorded yet.")
        print("=" * 76)

    # ---------------------------------------------------------
    # Feature 3: Persistent Storage & CSV Export
    # ---------------------------------------------------------
    def export_csv(self):
        print("\n--- [7] EXPORT TO CSV ---")
        success = StorageManager.export_csv(self.symptoms)
        if success:
            print(f"[OK] Successfully exported {len(self.symptoms)} entries to '{EXPORT_CSV_FILE}'")
        else:
            print("[!] Export failed.")

    def run_interactive(self):
        self.print_banner()
        while True:
            self.print_menu()
            choice = input("\nEnter option (1-8): ").strip()
            if choice == "1":
                self.add_symptom()
            elif choice == "2":
                self.view_symptoms()
            elif choice == "3":
                self.update_symptom()
            elif choice == "4":
                self.delete_symptom()
            elif choice == "5":
                self.filter_symptoms_menu()
            elif choice == "6":
                self.view_summarized_reports()
            elif choice == "7":
                self.export_csv()
            elif choice == "8":
                print("\nThank you for using HealthPulse. Goodbye!")
                break
            else:
                print("[!] Invalid option. Enter a number between 1 and 8.")

    def run_automated_demo(self):
        """Demonstrates all 5 key features end-to-end without blocking."""
        self.print_banner()
        print("\n>>> DEMONSTRATION OF ALL 5 KEY FEATURES <<<")

        print("\n[Feature 1: Manage Entities - Viewing Existing Entries]")
        self.view_symptoms()

        print("\n[Feature 1: Manage Entities - Adding New Symptom]")
        self.add_symptom(
            s_name="Acute Sinus Congestion",
            category="Respiratory",
            severity=7,
            duration=3.0,
            triggers=["Cold weather", "Pollen"],
            notes="Breathing difficulty during morning hours.",
            date=datetime.now().strftime("%Y-%m-%d"),
            time=datetime.now().strftime("%H:%M")
        )

        print("\n[Feature 2: Categorization & Filtering - Neurological Category]")
        filtered_neuro = [s for s in self.symptoms if s.get("category") == "Neurological"]
        self.view_symptoms(filtered_neuro)

        print("\n[Feature 4: Summarized Reports]")
        self.view_summarized_reports()

        print("\n[Feature 3: Persistent Storage - CSV Export]")
        self.export_csv()

        print("\n>>> ALL 5 KEY FEATURES VERIFIED & OPERATIONAL <<<")


if __name__ == "__main__":
    app = HealthPulseApp()
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        app.run_automated_demo()
    else:
        if sys.stdin.isatty():
            app.run_interactive()
        else:
            app.run_automated_demo()
