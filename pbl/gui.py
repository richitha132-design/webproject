"""
HealthPulse - GUI Symptom Tracking System
Tkinter Desktop Application
Reads and updates 'symptoms_data.json' persistently.
"""

import os
import json
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DATA_FILE = "symptoms_data.json"
CATEGORIES = [
    "Neurological",
    "Respiratory",
    "Digestive",
    "Musculoskeletal",
    "Cardiovascular",
    "Dermatological",
    "General"
]


class HealthPulseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("HealthPulse - Symptom Tracking System")
        self.root.geometry("980x680")
        self.root.minsize(850, 550)

        # Apply Modern Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"))
        self.style.configure("Treeview", font=("Helvetica", 9), rowheight=24)

        self.load_data()
        self.create_widgets()
        self.refresh_table()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.data = {
                "user": {"name": "Alex Morgan", "user_id": "USR-001", "blood_group": "B+"},
                "symptoms": []
            }
            self.save_data()
        else:
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = {"user": {"name": "User"}, "symptoms": []}

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def create_widgets(self):
        # Header Frame
        header = tk.Frame(self.root, bg="#1a365d", height=70)
        header.pack(fill=tk.X)

        title = tk.Label(
            header,
            text="HealthPulse - Symptom Tracking System",
            font=("Helvetica", 18, "bold"),
            fg="#ffffff",
            bg="#1a365d"
        )
        title.pack(side=tk.LEFT, padx=20, pady=15)

        user_name = self.data.get("user", {}).get("name", "User")
        bg_grp = self.data.get("user", {}).get("blood_group", "N/A")
        sub = tk.Label(
            header,
            text=f"User: {user_name} | Blood Group: {bg_grp}",
            font=("Helvetica", 10),
            fg="#cbd5e0",
            bg="#1a365d"
        )
        sub.pack(side=tk.RIGHT, padx=20, pady=20)

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Tab 1: Records Table
        self.tab_table = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_table, text=" Symptom Records ")
        self.setup_table_tab()

        # Tab 2: Add New Entry
        self.tab_add = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_add, text=" Log New Symptom ")
        self.setup_add_tab()

        # Tab 3: Analytics & Reports
        self.tab_analytics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_analytics, text=" Health Analytics & Alerts ")
        self.setup_analytics_tab()

    def setup_table_tab(self):
        # Top toolbar
        toolbar = ttk.Frame(self.tab_table)
        toolbar.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(toolbar, text="Filter Category:").pack(side=tk.LEFT, padx=5)
        self.filter_cat = ttk.Combobox(toolbar, values=["All"] + CATEGORIES, state="readonly", width=16)
        self.filter_cat.current(0)
        self.filter_cat.pack(side=tk.LEFT, padx=5)
        self.filter_cat.bind("<<ComboboxSelected>>", lambda e: self.refresh_table())

        ttk.Button(toolbar, text="Refresh Table", command=self.refresh_table).pack(side=tk.LEFT, padx=10)
        ttk.Button(toolbar, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT, padx=5)

        # Treeview Table
        cols = ("id", "date", "time", "symptom", "category", "severity", "duration", "triggers", "medication")
        self.tree = ttk.Treeview(self.tab_table, columns=cols, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date")
        self.tree.heading("time", text="Time")
        self.tree.heading("symptom", text="Symptom")
        self.tree.heading("category", text="Category")
        self.tree.heading("severity", text="Severity")
        self.tree.heading("duration", text="Duration")
        self.tree.heading("triggers", text="Triggers")
        self.tree.heading("medication", text="Medication")

        self.tree.column("id", width=70, anchor=tk.CENTER)
        self.tree.column("date", width=85, anchor=tk.CENTER)
        self.tree.column("time", width=60, anchor=tk.CENTER)
        self.tree.column("symptom", width=160)
        self.tree.column("category", width=120)
        self.tree.column("severity", width=70, anchor=tk.CENTER)
        self.tree.column("duration", width=75, anchor=tk.CENTER)
        self.tree.column("triggers", width=180)
        self.tree.column("medication", width=140)

        # Scrollbars
        scroll_y = ttk.Scrollbar(self.tab_table, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=(0, 10))

    def setup_add_tab(self):
        container = ttk.Frame(self.tab_add)
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Form Fields
        labels = [
            ("Symptom Name:", "name"),
            ("Category:", "category"),
            ("Severity (1-10):", "severity"),
            ("Duration (Hours):", "duration"),
            ("Triggers (comma-separated):", "triggers"),
            ("Medication / Remedies:", "medication"),
            ("Notes / Observations:", "notes")
        ]

        self.form_entries = {}

        for i, (label_text, key) in enumerate(labels):
            ttk.Label(container, text=label_text, font=("Helvetica", 10, "bold")).grid(row=i, column=0, sticky=tk.W, pady=8)
            if key == "category":
                w = ttk.Combobox(container, values=CATEGORIES, state="readonly", width=30)
                w.current(0)
            elif key == "severity":
                f_sev = ttk.Frame(container)
                self.sev_var = tk.IntVar(value=5)
                w = ttk.Scale(f_sev, from_=1, to=10, orient=tk.HORIZONTAL, variable=self.sev_var, length=200)
                lbl_val = ttk.Label(f_sev, text="5")
                w.config(command=lambda val, lbl=lbl_val: lbl.config(text=f"{int(float(val))}"))
                w.pack(side=tk.LEFT)
                lbl_val.pack(side=tk.LEFT, padx=10)
                f_sev.grid(row=i, column=1, sticky=tk.W, pady=8)
                self.form_entries[key] = self.sev_var
                continue
            else:
                w = ttk.Entry(container, width=35)
                if key == "duration":
                    w.insert(0, "2.0")

            w.grid(row=i, column=1, sticky=tk.W, pady=8)
            self.form_entries[key] = w

        btn_submit = ttk.Button(container, text="Save Symptom Entry", command=self.save_new_entry)
        btn_submit.grid(row=len(labels), column=1, sticky=tk.W, pady=15)

    def setup_analytics_tab(self):
        container = ttk.Frame(self.tab_analytics)
        container.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        ttk.Button(container, text="Refresh Analytics", command=self.update_analytics_display).pack(anchor=tk.W, pady=5)

        self.txt_analytics = tk.Text(container, wrap=tk.WORD, font=("Consolas", 10), height=22, bg="#f8fafc")
        self.txt_analytics.pack(fill=tk.BOTH, expand=True, pady=10)
        self.update_analytics_display()

    def update_analytics_display(self):
        symptoms = self.data.get("symptoms", [])
        if not symptoms:
            self.txt_analytics.delete("1.0", tk.END)
            self.txt_analytics.insert(tk.END, "No records available for analysis.")
            return

        total = len(symptoms)
        severities = [s.get("severity", 0) for s in symptoms]
        avg_sev = sum(severities) / total if total > 0 else 0.0

        # Category Counts
        cat_counts = {}
        for s in symptoms:
            cat = s.get("category", "General")
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        # Triggers
        trig_counts = {}
        for s in symptoms:
            for t in s.get("triggers", []):
                t_clean = t.strip().title()
                if t_clean:
                    trig_counts[t_clean] = trig_counts.get(t_clean, 0) + 1

        high_sev = [s for s in symptoms if s.get("severity", 0) >= 7]

        text = "=" * 65 + "\n"
        text += "           HEALTHPULSE ANALYTICS & TRENDS SUMMARY\n"
        text += "=" * 65 + "\n\n"
        text += f"Total Logged Episodes    : {total}\n"
        text += f"Average Pain Severity    : {round(avg_sev, 2)} / 10\n\n"
        text += "--- CATEGORY DISTRIBUTION ---\n"
        for cat, cnt in cat_counts.items():
            text += f"  * {cat:<18}: {'#' * cnt} ({cnt})\n"

        text += "\n--- TOP IDENTIFIED TRIGGERS ---\n"
        if trig_counts:
            sorted_t = sorted(trig_counts.items(), key=lambda x: x[1], reverse=True)
            for t, cnt in sorted_t[:5]:
                text += f"  * {t:<20}: {cnt} occurrence(s)\n"
        else:
            text += "  No triggers identified yet.\n"

        text += f"\n--- HIGH SEVERITY ALERTS (>= 7/10) [{len(high_sev)}] ---\n"
        for h in high_sev:
            text += f"  [!] {h.get('date')} - {h.get('symptom')} (Severity: {h.get('severity')}/10)\n"
            text += f"      Triggers: {', '.join(h.get('triggers', []))} | Meds: {h.get('medication')}\n"

        self.txt_analytics.delete("1.0", tk.END)
        self.txt_analytics.insert(tk.END, text)

    def refresh_table(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_cat = self.filter_cat.get()
        symptoms = self.data.get("symptoms", [])

        for s in symptoms:
            if selected_cat != "All" and s.get("category") != selected_cat:
                continue

            self.tree.insert("", tk.END, values=(
                s.get("id"),
                s.get("date"),
                s.get("time"),
                s.get("symptom"),
                s.get("category"),
                f"{s.get('severity')}/10",
                f"{s.get('duration_hours')}h",
                ", ".join(s.get("triggers", [])),
                s.get("medication")
            ))

    def save_new_entry(self):
        name = self.form_entries["name"].get().strip()
        if not name:
            messagebox.showwarning("Validation Warning", "Please enter a symptom name.")
            return

        cat = self.form_entries["category"].get()
        sev = self.sev_var.get()
        dur_str = self.form_entries["duration"].get().strip()
        try:
            dur = float(dur_str)
        except ValueError:
            dur = 1.0

        trig_str = self.form_entries["triggers"].get().strip()
        triggers = [t.strip().title() for t in trig_str.split(",") if t.strip()]
        meds = self.form_entries["medication"].get().strip() or "None"
        notes = self.form_entries["notes"].get().strip() or "N/A"

        # Unique ID
        symptoms = self.data.get("symptoms", [])
        next_id = f"SYM-{len(symptoms) + 1001}"
        while any(s["id"] == next_id for s in symptoms):
            next_id = f"SYM-{int(next_id.split('-')[1]) + 1}"

        now = datetime.now()
        new_entry = {
            "id": next_id,
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M"),
            "symptom": name,
            "category": cat,
            "severity": sev,
            "duration_hours": dur,
            "triggers": triggers,
            "medication": meds,
            "notes": notes
        }

        symptoms.append(new_entry)
        self.data["symptoms"] = symptoms
        self.save_data()

        messagebox.showinfo("Success", f"Symptom logged successfully as {next_id}!")
        self.form_entries["name"].delete(0, tk.END)
        self.form_entries["triggers"].delete(0, tk.END)
        self.form_entries["medication"].delete(0, tk.END)
        self.form_entries["notes"].delete(0, tk.END)

        self.refresh_table()
        self.update_analytics_display()
        self.notebook.select(self.tab_table)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a record to delete.")
            return

        item = self.tree.item(selected[0])
        entry_id = item["values"][0]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {entry_id}?"):
            self.data["symptoms"] = [s for s in self.data["symptoms"] if s.get("id") != entry_id]
            self.save_data()
            self.refresh_table()
            self.update_analytics_display()
            messagebox.showinfo("Deleted", f"Record {entry_id} deleted.")


if __name__ == "__main__":
    root = tk.Tk()
    app = HealthPulseGUI(root)
    root.mainloop()

