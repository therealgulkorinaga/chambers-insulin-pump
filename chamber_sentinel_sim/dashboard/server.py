"""Local dashboard server — serves simulation results as a web UI."""

from __future__ import annotations

import json
import os
import sqlite3
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any


def generate_dashboard_html(output_dir: str) -> str:
    """Generate a self-contained HTML dashboard from simulation output."""
    stats = {}
    stats_path = os.path.join(output_dir, "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path) as f:
            stats = json.load(f)

    assertions = []
    results_path = os.path.join(output_dir, "assertions", "results.json")
    if os.path.exists(results_path):
        with open(results_path) as f:
            assertions = json.load(f)

    # Count items per world
    world_counts: dict[str, int] = {}
    relay_dir = os.path.join(output_dir, "relay")
    if os.path.exists(relay_dir):
        for world_name in os.listdir(relay_dir):
            db_path = os.path.join(relay_dir, world_name, f"{world_name}.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                row = conn.execute("SELECT COUNT(*) FROM items").fetchone()
                world_counts[world_name] = row[0] if row else 0
                conn.close()

    # Portable record stats
    vault_counts: dict[str, int] = {}
    pr_dir = os.path.join(output_dir, "portable_record")
    if os.path.exists(pr_dir):
        for pid in os.listdir(pr_dir):
            db_path = os.path.join(pr_dir, pid, "vault.db")
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                row = conn.execute("SELECT COUNT(*) FROM items").fetchone()
                vault_counts[pid] = row[0] if row else 0
                conn.close()

    # Recent audit entries
    audit_entries: list[dict] = []
    audit_path = os.path.join(output_dir, "audit", "audit.jsonl")
    if os.path.exists(audit_path):
        with open(audit_path) as f:
            lines = f.readlines()
        for line in lines[-100:]:
            if line.strip():
                audit_entries.append(json.loads(line))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Chamber Sentinel Simulation Dashboard</title>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #0d1117; color: #c9d1d9; }}
  h1 {{ color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
  h2 {{ color: #79c0ff; margin-top: 30px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin: 16px 0; }}
  .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 16px; }}
  .card h3 {{ margin: 0 0 8px 0; color: #8b949e; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }}
  .card .value {{ font-size: 28px; font-weight: bold; color: #58a6ff; }}
  .pass {{ color: #3fb950; }} .fail {{ color: #f85149; }}
  table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
  th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #21262d; }}
  th {{ color: #8b949e; font-size: 12px; text-transform: uppercase; }}
  .audit {{ max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 12px; }}
  .audit-entry {{ padding: 4px 8px; border-bottom: 1px solid #21262d; }}
  .audit-entry:nth-child(even) {{ background: #161b22; }}
</style>
</head>
<body>
<h1>Chamber Sentinel Simulation Dashboard</h1>

<h2>Simulation Stats</h2>
<div class="grid">
  <div class="card"><h3>Duration</h3><div class="value">{stats.get('sim_days', 0):.0f} days</div></div>
  <div class="card"><h3>Wall Time</h3><div class="value">{stats.get('wall_time_seconds', 0):.1f}s</div></div>
  <div class="card"><h3>Items Generated</h3><div class="value">{stats.get('items_generated', 0):,}</div></div>
  <div class="card"><h3>Items Classified</h3><div class="value">{stats.get('items_classified', 0):,}</div></div>
  <div class="card"><h3>Items Burned</h3><div class="value">{stats.get('items_burned', 0):,}</div></div>
  <div class="card"><h3>Delivered to Vault</h3><div class="value">{stats.get('items_delivered_to_vault', 0):,}</div></div>
  <div class="card"><h3>Reports Generated</h3><div class="value">{stats.get('reports_generated', 0):,}</div></div>
</div>

<h2>Assertions</h2>
<table>
  <tr><th>Assertion</th><th>Status</th><th>Details</th></tr>
  {''.join(f'<tr><td>{a["name"]}</td><td class="{"pass" if a["passed"] else "fail"}">{"PASS" if a["passed"] else "FAIL"}</td><td>{a["details"]}</td></tr>' for a in assertions)}
</table>

<h2>World Occupancy (Post-Simulation)</h2>
<table>
  <tr><th>World</th><th>Remaining Items</th></tr>
  {''.join(f'<tr><td>{w}</td><td>{c}</td></tr>' for w, c in world_counts.items())}
</table>

<h2>Portable Records</h2>
<table>
  <tr><th>Patient</th><th>Items in Vault</th></tr>
  {''.join(f'<tr><td>{p}</td><td>{c:,}</td></tr>' for p, c in vault_counts.items())}
</table>

<h2>Recent Audit Log (last 100 entries)</h2>
<div class="audit">
  {''.join(f'<div class="audit-entry"><b>{e.get("event_type","")}</b> t={e.get("sim_time",0):.0f} patient={e.get("patient_id","")} item={e.get("item_id","")[:8]} {json.dumps(e.get("details") or {})}</div>' for e in audit_entries)}
</div>
</body>
</html>"""


def serve_dashboard(output_dir: str, port: int = 8090) -> None:
    """Serve the dashboard on localhost."""
    html = generate_dashboard_html(output_dir)
    html_path = os.path.join(output_dir, "dashboard.html")
    with open(html_path, "w") as f:
        f.write(html)
    print(f"Dashboard written to {html_path}")
    print(f"Open file://{os.path.abspath(html_path)} in your browser")
