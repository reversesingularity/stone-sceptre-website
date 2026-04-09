"""
DESKTOP-SINGULA — n8n Workflow Deployer
=========================================
Creates / updates all 10 v2.0 HAWK swarm workflows in n8n via the REST API.

Run:
    python n8n_deploy_workflows.py [--dry-run] [--force]

Options:
    --dry-run  Print workflow names and skip count without creating anything
    --force    Re-create workflows even if they already exist (by name)
"""

import sys
import json
import argparse
import requests
from datetime import datetime

# ── Config ─────────────────────────────────────────────────────────────────

N8N_BASE = "http://localhost:5678"
N8N_KEY  = None   # loaded from .env

PYTHON_SERVICES = {
    "canon_search":     "http://host.docker.internal:8765",
    "kdp_format":       "http://host.docker.internal:8766",
    "story_prototype":  "http://host.docker.internal:8767",
    "nemotron_router":  "http://host.docker.internal:8768",
    "utility":          "http://host.docker.internal:8769",
    "theological_guard": "http://host.docker.internal:8770",
    "conductor":        "http://host.docker.internal:8771",
}

# File paths as seen from INSIDE the n8n container
DATA_ROOT    = "/data/TNC"
MANUSCRIPT   = f"{DATA_ROOT}/MANUSCRIPT"
ANALYSIS     = f"{DATA_ROOT}/02_ANALYSIS"
LOGS         = f"{DATA_ROOT}/LOGS"
STAGING      = f"{DATA_ROOT}/STAGING/crdt_proposals"


# ── .env Loader ─────────────────────────────────────────────────────────────

def load_env():
    import os
    from pathlib import Path
    env_path = Path(r"F:\Projects-cmodi.000\book_writer_ai_toolkit\output\nephilim_chronicles\.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    return os.environ.get("N8N_API_KEY", "")


# ── n8n API Helpers ─────────────────────────────────────────────────────────

def api_headers():
    return {"X-N8N-API-KEY": N8N_KEY, "Content-Type": "application/json"}


def get_existing_workflows() -> dict:
    """Returns {name: id} for all existing workflows."""
    r = requests.get(f"{N8N_BASE}/api/v1/workflows", headers=api_headers(), timeout=10)
    r.raise_for_status()
    return {w["name"]: w["id"] for w in r.json().get("data", [])}


def create_workflow(wf_def: dict) -> str:
    payload = {k: v for k, v in wf_def.items() if k != "active"}
    r = requests.post(
        f"{N8N_BASE}/api/v1/workflows",
        headers=api_headers(),
        json=payload,
        timeout=15,
    )
    if not r.ok:
        print(f"    [DEBUG] Response body: {r.text[:600]}")
    r.raise_for_status()
    return r.json().get("id", "?")


def update_workflow(wf_id: str, wf_def: dict) -> str:
    payload = {k: v for k, v in wf_def.items() if k != "active"}
    r = requests.patch(
        f"{N8N_BASE}/api/v1/workflows/{wf_id}",
        headers=api_headers(),
        json=payload,
        timeout=15,
    )
    r.raise_for_status()
    return wf_id


def activate_workflow(wf_id: str):
    r = requests.post(
        f"{N8N_BASE}/api/v1/workflows/{wf_id}/activate",
        headers=api_headers(),
        timeout=10,
    )
    r.raise_for_status()


# ── Workflow Definitions ────────────────────────────────────────────────────

def wf_swarm_dispatch():
    """WF1: Master router — /webhook/swarm-dispatch"""
    return {
        "name": "TNC_WF1_SWARM_DISPATCH",
        "active": True,
        "nodes": [
            {
                "id": "sw-webhook",
                "name": "Swarm Dispatch",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "swarm-dispatch",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "sw-switch",
                "name": "Route Job Type",
                "type": "n8n-nodes-base.switch",
                "typeVersion": 3,
                "position": [340, 300],
                "parameters": {
                    "mode": "rules",
                    "rules": {
                        "values": [
                            {
                                "conditions": {"options": {"caseSensitive": False},
                                    "conditions": [{"leftValue": "={{ $json.body.job_type }}", "rightValue": "analyse_chapter", "operator": {"type": "string", "operation": "equals"}}]},
                                "renameOutput": True, "outputKey": "analyse_chapter"
                            },
                            {
                                "conditions": {"options": {"caseSensitive": False},
                                    "conditions": [{"leftValue": "={{ $json.body.job_type }}", "rightValue": "extract_triples", "operator": {"type": "string", "operation": "equals"}}]},
                                "renameOutput": True, "outputKey": "extract_triples"
                            },
                            {
                                "conditions": {"options": {"caseSensitive": False},
                                    "conditions": [{"leftValue": "={{ $json.body.job_type }}", "rightValue": "constitution_update", "operator": {"type": "string", "operation": "equals"}}]},
                                "renameOutput": True, "outputKey": "constitution_update"
                            },
                            {
                                "conditions": {"options": {"caseSensitive": False},
                                    "conditions": [{"leftValue": "={{ $json.body.job_type }}", "rightValue": "kdp_assemble", "operator": {"type": "string", "operation": "equals"}}]},
                                "renameOutput": True, "outputKey": "kdp_assemble"
                            },
                            {
                                "conditions": {"options": {"caseSensitive": False},
                                    "conditions": [{"leftValue": "={{ $json.body.job_type }}", "rightValue": "nightly_audit", "operator": {"type": "string", "operation": "equals"}}]},
                                "renameOutput": True, "outputKey": "nightly_audit"
                            },
                        ]
                    },
                    "fallbackOutput": "none"
                }
            },
            {
                "id": "sw-analyse",
                "name": "Trigger Analyse-Chapter",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [600, 100],
                "parameters": {
                    "method": "POST",
                    "url": f"{N8N_BASE}/webhook/analyse-chapter",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($node['Swarm Dispatch'].json.body) }}"
                }
            },
            {
                "id": "sw-triples",
                "name": "Trigger Extract-Triples",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [600, 220],
                "parameters": {
                    "method": "POST",
                    "url": f"{N8N_BASE}/webhook/extract-story-prototype",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($node['Swarm Dispatch'].json.body) }}"
                }
            },
            {
                "id": "sw-crdt",
                "name": "Trigger Constitution-Update",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [600, 340],
                "parameters": {
                    "method": "POST",
                    "url": f"{N8N_BASE}/webhook/constitution-update",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($node['Swarm Dispatch'].json.body) }}"
                }
            },
            {
                "id": "sw-kdp",
                "name": "Trigger KDP-Assemble",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [600, 460],
                "parameters": {
                    "method": "POST",
                    "url": f"{N8N_BASE}/webhook/kdp-assemble",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($node['Swarm Dispatch'].json.body) }}"
                }
            },
            {
                "id": "sw-audit",
                "name": "Trigger Nightly-Audit",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [600, 580],
                "parameters": {
                    "method": "POST",
                    "url": f"{N8N_BASE}/webhook/nightly-continuity-prep",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "{}"
                }
            },
            {
                "id": "sw-log",
                "name": "Log Dispatch",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [860, 300],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const logPath = '/data/TNC/LOGS/workflow_runs.jsonl';\n"
                        "const entry = JSON.stringify({\n"
                        "  ts: new Date().toISOString(),\n"
                        "  job_type: $input.first().json?.body?.job_type || 'unknown',\n"
                        "  payload: $input.first().json?.body || {}\n"
                        "}) + '\\n';\n"
                        "try { fs.appendFileSync(logPath, entry); } catch(e) {}\n"
                        "return [{ json: { dispatched: true } }];"
                    )
                }
            },
            {
                "id": "sw-respond",
                "name": "Respond OK",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [1080, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={ \"status\": \"dispatched\" }"
                }
            }
        ],
        "connections": {
            "Swarm Dispatch":             {"main": [[{"node": "Route Job Type",              "type": "main", "index": 0}]]},
            "Route Job Type":             {"main": [
                [{"node": "Trigger Analyse-Chapter",     "type": "main", "index": 0}],
                [{"node": "Trigger Extract-Triples",     "type": "main", "index": 0}],
                [{"node": "Trigger Constitution-Update", "type": "main", "index": 0}],
                [{"node": "Trigger KDP-Assemble",        "type": "main", "index": 0}],
                [{"node": "Trigger Nightly-Audit",       "type": "main", "index": 0}],
            ]},
            "Trigger Analyse-Chapter":     {"main": [[{"node": "Log Dispatch", "type": "main", "index": 0}]]},
            "Trigger Extract-Triples":     {"main": [[{"node": "Log Dispatch", "type": "main", "index": 0}]]},
            "Trigger Constitution-Update": {"main": [[{"node": "Log Dispatch", "type": "main", "index": 0}]]},
            "Trigger KDP-Assemble":        {"main": [[{"node": "Log Dispatch", "type": "main", "index": 0}]]},
            "Trigger Nightly-Audit":       {"main": [[{"node": "Log Dispatch", "type": "main", "index": 0}]]},
            "Log Dispatch":                {"main": [[{"node": "Respond OK",   "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_nemoclaw_file_event():
    """NEMOCLAW FILE EVENT handler — /webhook/nemoclaw-file-event"""
    return {
        "name": "TNC_WF_NEMOCLAW_FILE_EVENT",
        "active": True,
        "nodes": [
            {
                "id": "nfe-webhook",
                "name": "Nemoclaw File Event",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "nemoclaw-file-event",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "nfe-read",
                "name": "Read Changed File",
                "type": "n8n-nodes-base.readWriteFile",
                "typeVersion": 1,
                "position": [340, 300],
                "parameters": {
                    "operation": "read",
                    "fileName": "={{ $json.body.path.replace('/data/TNC_Books35', '/data/TNC') }}"
                }
            },
            {
                "id": "nfe-embed",
                "name": "Auto-Vectorise via Canon Search",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [580, 200],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['canon_search']}/ingest",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify({ file_path: $node['Nemoclaw File Event'].json.body.path, text: $node['Read Changed File'].binary?.data_text || '' }) }}"
                }
            },
            {
                "id": "nfe-triples",
                "name": "Queue Story Prototype Extraction",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [580, 400],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['story_prototype']}/extract-triples",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify({ chapter_path: $node['Nemoclaw File Event'].json.body.path, book_num: $node['Nemoclaw File Event'].json.body.book || 3, chapter_num: $node['Nemoclaw File Event'].json.body.chapter || 0 }) }}"
                }
            },
            {
                "id": "nfe-respond",
                "name": "Respond OK",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [820, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={\"status\":\"ingested\"}"
                }
            }
        ],
        "connections": {
            "Nemoclaw File Event":              {"main": [[{"node": "Read Changed File",                    "type": "main", "index": 0}]]},
            "Read Changed File":                {"main": [[{"node": "Auto-Vectorise via Canon Search",      "type": "main", "index": 0}, {"node": "Queue Story Prototype Extraction", "type": "main", "index": 0}]]},
            "Auto-Vectorise via Canon Search":  {"main": [[{"node": "Respond OK", "type": "main", "index": 0}]]},
            "Queue Story Prototype Extraction": {"main": [[{"node": "Respond OK", "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_story_prototype():
    """WF3: Story Prototype Extractor — /webhook/extract-story-prototype"""
    return {
        "name": "TNC_WF3_STORY_PROTOTYPE",
        "active": True,
        "nodes": [
            {
                "id": "sp-webhook",
                "name": "Story Prototype Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "extract-story-prototype",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "sp-extract",
                "name": "Extract Triples",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [340, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['story_prototype']}/extract-triples",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($json.body) }}"
                }
            },
            {
                "id": "sp-if-contradictions",
                "name": "Contradictions Found?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [580, 300],
                "parameters": {
                    "conditions": {
                        "combinator": "and",
                        "conditions": [{
                            "leftValue": "={{ ($json.contradictions || []).length }}",
                            "rightValue": 0,
                            "operator": {"type": "number", "operation": "gt"}
                        }]
                    }
                }
            },
            {
                "id": "sp-log-contradiction",
                "name": "Log Contradiction Alert",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [820, 200],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const d = $input.first().json;\n"
                        "const chap = d.chapter_num || '?';\n"
                        "const book = d.book_num || '?';\n"
                        "const n = (d.contradictions || []).length;\n"
                        "const msg = `[${new Date().toISOString()}] STORY PROTOTYPE: `\n"
                        "  + `${n} contradiction(s) in Book ${book} Ch ${chap}\\n`;\n"
                        "const logPath = '/data/TNC/LOGS/DRIFT_LOG.md';\n"
                        "try { fs.appendFileSync(logPath, msg); } catch(e) {}\n"
                        "return [{ json: { alerted: true, contradiction_count: n } }];"
                    )
                }
            },
            {
                "id": "sp-foreshadow",
                "name": "Get Foreshadow Brief",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [820, 400],
                "parameters": {
                    "method": "GET",
                    "url": f"={PYTHON_SERVICES['story_prototype']}/foreshadow-brief/{{{{$node['Story Prototype Webhook'].json.body.book_num || 3}}}}/{{{{$node['Story Prototype Webhook'].json.body.chapter_num || 1}}}}"
                }
            },
            {
                "id": "sp-write",
                "name": "Write Foreshadow Brief",
                "type": "n8n-nodes-base.readWriteFile",
                "typeVersion": 1,
                "position": [1060, 400],
                "parameters": {
                    "operation": "write",
                    "fileName": f"={ANALYSIS}/FORESHADOW_BRIEF_B{{{{$node['Story Prototype Webhook'].json.body.book_num || 3}}}}_CH{{{{String($node['Story Prototype Webhook'].json.body.chapter_num || 1).padStart(2,'0')}}}}.md",
                    "dataPropertyName": "data",
                    "options": {}
                }
            },
            {
                "id": "sp-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [1300, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify({ status: 'ok', triples_saved: $node['Extract Triples'].json.triples_saved || 0, contradictions: ($node['Extract Triples'].json.contradictions || []).length }) }}"
                }
            }
        ],
        "connections": {
            "Story Prototype Webhook":  {"main": [[{"node": "Extract Triples",          "type": "main", "index": 0}]]},
            "Extract Triples":          {"main": [[{"node": "Contradictions Found?",    "type": "main", "index": 0}]]},
            "Contradictions Found?":    {"main": [
                [{"node": "Log Contradiction Alert", "type": "main", "index": 0}],
                [{"node": "Get Foreshadow Brief",    "type": "main", "index": 0}],
            ]},
            "Log Contradiction Alert":  {"main": [[{"node": "Respond",                  "type": "main", "index": 0}]]},
            "Get Foreshadow Brief":     {"main": [[{"node": "Write Foreshadow Brief",   "type": "main", "index": 0}]]},
            "Write Foreshadow Brief":   {"main": [[{"node": "Respond",                  "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_constitution_updater_v2():
    """WF4: Constitution Updater v2 (CRDT) — /webhook/constitution-update"""
    return {
        "name": "TNC_WF4_CONSTITUTION_UPDATER_V2",
        "active": True,
        "nodes": [
            {
                "id": "cu-webhook",
                "name": "Constitution Update Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "constitution-update",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "cu-merge",
                "name": "Run CRDT Merge",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [340, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['utility']}/crdt-merge",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": f"={{{{ JSON.stringify({{ staging_dir: '{STAGING}', dry_run: false }}) }}}}"
                }
            },
            {
                "id": "cu-if-conflicts",
                "name": "Author Review Needed?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [580, 300],
                "parameters": {
                    "conditions": {
                        "combinator": "and",
                        "conditions": [{
                            "leftValue": "={{ ($json.report?.escalated || 0) }}",
                            "rightValue": 0,
                            "operator": {"type": "number", "operation": "gt"}
                        }]
                    }
                }
            },
            {
                "id": "cu-log-conflict",
                "name": "Log CRDT Conflict",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [820, 200],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const d = $input.first().json?.report || {};\n"
                        "const ts = new Date().toISOString();\n"
                        "const msg = `[${ts}] CRDT CONFLICT — Author review needed in TODO.md. `\n"
                        "  + `escalated=${d.escalated||0} merged=${d.merged_safe||0}+${d.merged_additive||0}\\n`;\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/DRIFT_LOG.md', msg); } catch(e) {}\n"
                        "return [{ json: { conflict_logged: true } }];"
                    )
                }
            },
            {
                "id": "cu-log-ok",
                "name": "Log Merge Success",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [820, 400],
                "parameters": {
                    "jsCode": (
                        "const d = $input.first().json?.report || {};\n"
                        "const ts = new Date().toISOString();\n"
                        "const fs = require('fs');\n"
                        "const msg = `[${ts}] SSOT updated: merged=${d.merged_safe||0}+${d.merged_additive||0} `\n"
                        "  + `rejected=${d.rejected||0}\\n`;\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/DRIFT_LOG.md', msg); } catch(e) {}\n"
                        "return [{ json: { merge_logged: true } }];"
                    )
                }
            },
            {
                "id": "cu-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [1060, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify({ status: 'ok', report: $node['Run CRDT Merge'].json.report || {} }) }}"
                }
            }
        ],
        "connections": {
            "Constitution Update Webhook": {"main": [[{"node": "Run CRDT Merge",          "type": "main", "index": 0}]]},
            "Run CRDT Merge":              {"main": [[{"node": "Author Review Needed?",    "type": "main", "index": 0}]]},
            "Author Review Needed?":       {"main": [
                [{"node": "Log CRDT Conflict", "type": "main", "index": 0}],
                [{"node": "Log Merge Success",  "type": "main", "index": 0}],
            ]},
            "Log CRDT Conflict":           {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
            "Log Merge Success":           {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_analyse_chapter():
    """WF2/5/6/7 combined — /webhook/analyse-chapter
    Triggers Drift (Nemotron), Reader Reaction, Dopamine Ladder, Image Prompts in parallel.
    """
    return {
        "name": "TNC_WF2567_ANALYSE_CHAPTER",
        "active": True,
        "nodes": [
            {
                "id": "ac-webhook",
                "name": "Analyse Chapter Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 400],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "analyse-chapter",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "ac-read",
                "name": "Read Chapter File",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [340, 400],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const body = $input.first().json.body || $input.first().json;\n"
                        "const book    = body.book || 3;\n"
                        "const chapter = body.chapter || '';\n"
                        "const p = chapter.startsWith('/') ? chapter\n"
                        "  : `/data/TNC/MANUSCRIPT/book_${book}/${chapter}`;\n"
                        "let text = '';\n"
                        "try { text = fs.readFileSync(p, 'utf8'); } catch(e) { text = ''; }\n"
                        "return [{ json: { book, chapter, chapter_path: p, chapter_text: text } }];"
                    )
                }
            },
            # ── Agent 2: Drift Manager (Nemotron) ─────────────────────────────
            {
                "id": "ac-canon-search",
                "name": "Canon Context Search",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [580, 200],
                "parameters": {
                    "method": "GET",
                    "url": f"{PYTHON_SERVICES['canon_search']}/search",
                    "sendQuery": True,
                    "queryParameters": {
                        "parameters": [{"name": "q", "value": "locked canon timeline characters abilities acoustic paradigm"}, {"name": "n", "value": "20"}]
                    }
                }
            },
            {
                "id": "ac-drift",
                "name": "Drift Analysis (Nemotron)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [820, 200],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['nemotron_router']}/route",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": (
                        "={{ JSON.stringify({\n"
                        "  task_type: 'drift_analysis',\n"
                        "  system: 'You are the Drift Manager for THE NEPHILIM CHRONICLES covering Books 3-5. "
                        "Check the chapter strictly against SSOT canon. Report violations as JSON array: "
                        "[{severity,category,passage,canon_ref,correction}]. "
                        "Categories: CANON_CONTRADICTION,CHARACTER_STATE,TIMELINE_ERROR,ACOUSTIC_PARADIGM,THEOLOGY_DRIFT,CONTINUITY_GAP',\n"
                        "  prompt: 'Canon context:\\n' + JSON.stringify($node['Canon Context Search'].json?.results || []).slice(0,6000) + '\\n\\nChapter:\\n' + $node['Read Chapter File'].json.chapter_text.slice(0,12000),\n"
                        "  max_tokens: 2048\n"
                        "}) }}"
                    )
                }
            },
            {
                "id": "ac-drift-append",
                "name": "Append Drift Log",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [1060, 200],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const d = $input.first().json;\n"
                        "const chap = $node['Read Chapter File'].json;\n"
                        "const ts = new Date().toISOString();\n"
                        "const content_raw = (d.choices||[{message:{content:''}}])[0].message?.content || JSON.stringify(d);\n"
                        "const entry = `\\n## Drift Check ${ts} — Book ${chap.book} ${chap.chapter}\\n${content_raw}\\n---\\n`;\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/DRIFT_LOG.md', entry); } catch(e) {}\n"
                        "return [{ json: { drift_logged: true } }];"
                    )
                }
            },
            # ── Agent 4: Reader Reaction (Ollama) ─────────────────────────────
            {
                "id": "ac-reader",
                "name": "Reader Reaction (Ollama)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [580, 400],
                "parameters": {
                    "method": "POST",
                    "url": "http://host.docker.internal:11434/api/generate",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": (
                        "={{ JSON.stringify({\n"
                        "  model: 'llama3.1',\n"
                        "  stream: false,\n"
                        "  prompt: 'Score this chapter scene by scene on 8 criteria: "
                        "hook strength, tension arc, character revelation, sensory detail, pacing, "
                        "emotional beat, theological resonance, ending punch (each 1-10). "
                        "Return JSON array of scene objects.\\n\\nChapter:\\n'"
                        " + $node['Read Chapter File'].json.chapter_text.slice(0,6000),\n"
                        "  options: { num_predict: 1500 }\n"
                        "}) }}"
                    )
                }
            },
            {
                "id": "ac-reader-write",
                "name": "Write Reader Report",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [820, 400],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const chap = $node['Read Chapter File'].json;\n"
                        "const d = $input.first().json;\n"
                        "const chNum = String(chap.chapter || 'XX').replace(/[^0-9A-Za-z_-]/g,'_');\n"
                        "const outPath = `/data/TNC/02_ANALYSIS/REPORTS/matrix_B${chap.book}_${chNum}.json`;\n"
                        "const content = JSON.stringify({ book: chap.book, chapter: chap.chapter, ts: new Date().toISOString(), raw: d.response || '' }, null, 2);\n"
                        "try { fs.mkdirSync('/data/TNC/02_ANALYSIS/REPORTS', {recursive:true}); fs.writeFileSync(outPath, content); } catch(e) {}\n"
                        "return [{ json: { reader_report: outPath } }];"
                    )
                }
            },
            # ── Agent 5: Dopamine Ladder (Ollama) ─────────────────────────────
            {
                "id": "ac-dopamine",
                "name": "Dopamine Ladder (Ollama)",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [580, 600],
                "parameters": {
                    "method": "POST",
                    "url": "http://host.docker.internal:11434/api/generate",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": (
                        "={{ JSON.stringify({\n"
                        "  model: 'llama3.1',\n"
                        "  stream: false,\n"
                        "  prompt: 'Map ALL hooks and reward cycles in this chapter. "
                        "Identify: opening hook, micro-hooks per scene, dopamine release points, "
                        "cliffhanger strength, chapter-end reward. Rate overall dopamine density 1-10. "
                        "Return JSON.\\n\\nChapter:\\n' + $node['Read Chapter File'].json.chapter_text.slice(0,6000),\n"
                        "  options: { num_predict: 1000 }\n"
                        "}) }}"
                    )
                }
            },
            {
                "id": "ac-dopamine-write",
                "name": "Write Dopamine Report",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [820, 600],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const chap = $node['Read Chapter File'].json;\n"
                        "const d = $input.first().json;\n"
                        "const chNum = String(chap.chapter || 'XX').replace(/[^0-9A-Za-z_-]/g,'_');\n"
                        "const outPath = `/data/TNC/02_ANALYSIS/REPORTS/dopamine_B${chap.book}_${chNum}.json`;\n"
                        "const content = JSON.stringify({ book: chap.book, chapter: chap.chapter, ts: new Date().toISOString(), raw: d.response || '' }, null, 2);\n"
                        "try { fs.mkdirSync('/data/TNC/02_ANALYSIS/REPORTS', {recursive:true}); fs.writeFileSync(outPath, content); } catch(e) {}\n"
                        "return [{ json: { dopamine_report: outPath } }];"
                    )
                }
            },
            # ── Respond ───────────────────────────────────────────────────────
            {
                "id": "ac-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [1300, 400],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={\"status\":\"analysis_queued\"}"
                }
            }
        ],
        "connections": {
            "Analyse Chapter Webhook":  {"main": [[{"node": "Read Chapter File",         "type": "main", "index": 0}]]},
            "Read Chapter File":        {"main": [[
                {"node": "Canon Context Search",     "type": "main", "index": 0},
                {"node": "Reader Reaction (Ollama)", "type": "main", "index": 0},
                {"node": "Dopamine Ladder (Ollama)", "type": "main", "index": 0},
            ]]},
            "Canon Context Search":         {"main": [[{"node": "Drift Analysis (Nemotron)",  "type": "main", "index": 0}]]},
            "Drift Analysis (Nemotron)":    {"main": [[{"node": "Append Drift Log",           "type": "main", "index": 0}]]},
            "Append Drift Log":             {"main": [[{"node": "Respond",                    "type": "main", "index": 0}]]},
            "Reader Reaction (Ollama)":     {"main": [[{"node": "Write Reader Report",        "type": "main", "index": 0}]]},
            "Write Reader Report":          {"main": [[{"node": "Respond",                    "type": "main", "index": 0}]]},
            "Dopamine Ladder (Ollama)":     {"main": [[{"node": "Write Dopamine Report",      "type": "main", "index": 0}]]},
            "Write Dopamine Report":        {"main": [[{"node": "Respond",                    "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_self_refine():
    """WF8: SELF-REFINE Loop — /webhook/refine-scene"""
    return {
        "name": "TNC_WF8_SELF_REFINE",
        "active": True,
        "nodes": [
            {
                "id": "sr-webhook",
                "name": "Refine Scene Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "refine-scene",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "sr-refine",
                "name": "Run Self-Refine",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [340, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['utility']}/self-refine",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($json.body) }}"
                }
            },
            {
                "id": "sr-if-pass",
                "name": "Passed Threshold?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [580, 300],
                "parameters": {
                    "conditions": {
                        "combinator": "and",
                        "conditions": [{"leftValue": "={{ $json.passed }}", "rightValue": True, "operator": {"type": "boolean", "operation": "equals"}}]
                    }
                }
            },
            {
                "id": "sr-log",
                "name": "Log Refine Result",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [820, 300],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const d = $input.first().json;\n"
                        "const status = d.passed ? 'PASS' : 'BEST-EFFORT';\n"
                        "const entry = JSON.stringify({ ts: new Date().toISOString(), status, final_score: d.final_score, iterations: d.iterations, report: d.report }) + '\\n';\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/refine_history.jsonl', entry); } catch(e) {}\n"
                        "return [{ json: d }];"
                    )
                }
            },
            {
                "id": "sr-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [1060, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify({ status: 'ok', passed: $node['Run Self-Refine'].json.passed, final_score: $node['Run Self-Refine'].json.final_score, iterations: $node['Run Self-Refine'].json.iterations }) }}"
                }
            }
        ],
        "connections": {
            "Refine Scene Webhook": {"main": [[{"node": "Run Self-Refine",    "type": "main", "index": 0}]]},
            "Run Self-Refine":      {"main": [[{"node": "Passed Threshold?",  "type": "main", "index": 0}]]},
            "Passed Threshold?":    {"main": [[{"node": "Log Refine Result",  "type": "main", "index": 0}, {"node": "Log Refine Result", "type": "main", "index": 0}]]},
            "Log Refine Result":    {"main": [[{"node": "Respond",            "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_kdp_assembler():
    """WF9: KDP Assembler — /webhook/kdp-assemble"""
    return {
        "name": "TNC_WF9_KDP_ASSEMBLER",
        "active": True,
        "nodes": [
            {
                "id": "ka-webhook",
                "name": "KDP Assemble Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "kdp-assemble",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "ka-format",
                "name": "KDP Format",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [340, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['kdp_format']}/kdp-format",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify({ book_num: $json.body.book || 2 }) }}"
                }
            },
            {
                "id": "ka-log",
                "name": "Log Assembly",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [580, 300],
                "parameters": {
                    "jsCode": (
                        "const d = $input.first().json;\n"
                        "const fs = require('fs');\n"
                        "const msg = `[${new Date().toISOString()}] KDP assembled: `\n"
                        "  + `output=${d.output_path||'?'} words=${d.word_count||'?'}\\n`;\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/workflow_runs.jsonl', msg); } catch(e) {}\n"
                        "return [{ json: d }];"
                    )
                }
            },
            {
                "id": "ka-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [820, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify({ status: 'ok', output_path: $node['KDP Format'].json.output_path || '', word_count: $node['KDP Format'].json.word_count || 0 }) }}"
                }
            }
        ],
        "connections": {
            "KDP Assemble Webhook": {"main": [[{"node": "KDP Format",    "type": "main", "index": 0}]]},
            "KDP Format":           {"main": [[{"node": "Log Assembly",  "type": "main", "index": 0}]]},
            "Log Assembly":         {"main": [[{"node": "Respond",       "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_nightly_audit():
    """WF10: Nightly Cross-Book Audit — cron 02:00 + /webhook/nightly-continuity-prep"""
    return {
        "name": "TNC_WF10_NIGHTLY_AUDIT",
        "active": True,
        "nodes": [
            {
                "id": "na-cron",
                "name": "Nightly Cron 02:00",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.2,
                "position": [100, 200],
                "parameters": {
                    "rule": {
                        "interval": [{
                            "field": "cronExpression",
                            "expression": "0 2 * * *"
                        }]
                    }
                }
            },
            {
                "id": "na-webhook",
                "name": "Continuity Prep Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 400],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "nightly-continuity-prep",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "na-audit",
                "name": "Run Cross-Book Audit",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [400, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{PYTHON_SERVICES['utility']}/cross-book-audit",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "{\"books\": [3, 4, 5], \"fast\": false}"
                }
            },
            {
                "id": "na-if-critical",
                "name": "Critical Violations?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [640, 300],
                "parameters": {
                    "conditions": {
                        "combinator": "and",
                        "conditions": [{"leftValue": "={{ $json.critical_count }}", "rightValue": 0, "operator": {"type": "number", "operation": "gt"}}]
                    }
                }
            },
            {
                "id": "na-log-critical",
                "name": "Log Critical Alert",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [880, 200],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const d = $input.first().json;\n"
                        "const ts = new Date().toISOString();\n"
                        "const msg = `[${ts}] ⚠ CRITICAL AUDIT: ${d.critical_count} critical violations. Review 02_ANALYSIS/!\\n`;\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/AUDIT_SUMMARY.log', msg); } catch(e) {}\n"
                        "return [{ json: d }];"
                    )
                }
            },
            {
                "id": "na-log-clean",
                "name": "Log Audit Clean",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [880, 400],
                "parameters": {
                    "jsCode": (
                        "const fs = require('fs');\n"
                        "const d = $input.first().json;\n"
                        "const ts = new Date().toISOString();\n"
                        "const msg = `[${ts}] ✓ Nightly audit: ${d.violation_count||0} violations (0 critical)\\n`;\n"
                        "try { fs.appendFileSync('/data/TNC/LOGS/AUDIT_SUMMARY.log', msg); } catch(e) {}\n"
                        "return [{ json: d }];"
                    )
                }
            },
            {
                "id": "na-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [1120, 400],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify({ status: 'ok', violations: $node['Run Cross-Book Audit'].json.violation_count || 0, critical: $node['Run Cross-Book Audit'].json.critical_count || 0 }) }}"
                }
            }
        ],
        "connections": {
            "Nightly Cron 02:00":        {"main": [[{"node": "Run Cross-Book Audit",   "type": "main", "index": 0}]]},
            "Continuity Prep Webhook":   {"main": [[{"node": "Run Cross-Book Audit",   "type": "main", "index": 0}]]},
            "Run Cross-Book Audit":      {"main": [[{"node": "Critical Violations?",   "type": "main", "index": 0}]]},
            "Critical Violations?":      {"main": [
                [{"node": "Log Critical Alert", "type": "main", "index": 0}],
                [{"node": "Log Audit Clean",    "type": "main", "index": 0}],
            ]},
            "Log Critical Alert":        {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
            "Log Audit Clean":           {"main": [[{"node": "Respond", "type": "main", "index": 0}]]},
        },
        "settings": {"executionOrder": "v1"}
    }


# ── Registry ────────────────────────────────────────────────────────────────

def wf_image_prompt():
    """WF6: Agent 6 — Image Prompt Designer. Calls Ollama mistral."""
    ollama_gen_url = "http://host.docker.internal:11434/api/generate"
    return {
        "name": "TNC_WF6_IMAGE_PROMPT",
        "active": True,
        "nodes": [
            {
                "id": "img-webhook",
                "name": "Image Prompt Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "image-prompt",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "img-ollama",
                "name": "Ollama — Generate Image Prompt",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [360, 300],
                "parameters": {
                    "method": "POST",
                    "url": ollama_gen_url,
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": (
                        "={"
                        "\"model\": \"mistral\","
                        "\"stream\": false,"
                        "\"prompt\": \"You are a KDP illustration prompt designer for The Nephilim Chronicles. "
                        "Generate a vivid, detailed, KDP-safe image prompt for the following scene. "
                        "Include style notes: cinematic, dark fantasy, biblical epic. "
                        "Do NOT include faces clearly (KDP AI art policy). "
                        "Scene: \" + $('Image Prompt Trigger').item.json.body.scene_text.substring(0, 800)"
                        "}"
                    )
                }
            },
            {
                "id": "img-save",
                "name": "Write Prompt to File",
                "type": "n8n-nodes-base.writeFile",
                "typeVersion": 1,
                "position": [620, 300],
                "parameters": {
                    "fileName": (
                        f"={DATA_ROOT}/03_IMAGE_PROMPTS/"
                        "book_{{ $('Image Prompt Trigger').item.json.body.book }}_"
                        "ch{{ $('Image Prompt Trigger').item.json.body.chapter }}_"
                        "{{ new Date().toISOString().replace(/:/g,'').substr(0,15) }}.txt"
                    ),
                    "dataPropertyName": "={{ $json.response }}"
                }
            },
            {
                "id": "img-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [880, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": (
                        "={ \"prompt\": $('Ollama — Generate Image Prompt').item.json.response, "
                        "\"status\": \"saved\" }"
                    )
                }
            }
        ],
        "connections": {
            "Image Prompt Trigger": {
                "main": [[{"node": "Ollama — Generate Image Prompt", "type": "main", "index": 0}]]
            },
            "Ollama — Generate Image Prompt": {
                "main": [[{"node": "Write Prompt to File", "type": "main", "index": 0}]]
            },
            "Write Prompt to File": {
                "main": [[{"node": "Respond", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_theological_guard():
    """WF: Agent 9 — Theological Guard. Calls theological_guard_server.py."""
    guard_url = PYTHON_SERVICES["theological_guard"]
    return {
        "name": "TNC_WF_THEOLOGICAL_GUARD",
        "active": True,
        "nodes": [
            {
                "id": "tg-webhook",
                "name": "Theological Guard Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "theological-guard",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "tg-validate",
                "name": "Validate Scene",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [360, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{guard_url}/validate-scene",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($('Theological Guard Trigger').item.json.body) }}"
                }
            },
            {
                "id": "tg-check-violations",
                "name": "Check Violations",
                "type": "n8n-nodes-base.if",
                "typeVersion": 2,
                "position": [620, 300],
                "parameters": {
                    "conditions": {
                        "options": {"caseSensitive": False},
                        "conditions": [
                            {
                                "leftValue": "={{ $json.passed }}",
                                "rightValue": False,
                                "operator": {"type": "boolean", "operation": "equals"}
                            }
                        ]
                    }
                }
            },
            {
                "id": "tg-flag-todo",
                "name": "Write Flag to LOGS",
                "type": "n8n-nodes-base.writeFile",
                "typeVersion": 1,
                "position": [880, 200],
                "parameters": {
                    "fileName": f"{LOGS}/THEOLOGICAL_FLAGS_n8n.log",
                    "dataPropertyName": (
                        "={{ 'VIOLATIONS: ' + JSON.stringify($('Validate Scene').item.json.violations) + '\\n' }}"
                    ),
                    "options": {"append": True}
                }
            },
            {
                "id": "tg-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [880, 420],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify($('Validate Scene').item.json) }}"
                }
            }
        ],
        "connections": {
            "Theological Guard Trigger": {
                "main": [[{"node": "Validate Scene", "type": "main", "index": 0}]]
            },
            "Validate Scene": {
                "main": [[{"node": "Check Violations", "type": "main", "index": 0}]]
            },
            "Check Violations": {
                "main": [
                    [{"node": "Write Flag to LOGS", "type": "main", "index": 0}],
                    [{"node": "Respond", "type": "main", "index": 0}]
                ]
            },
            "Write Flag to LOGS": {
                "main": [[{"node": "Respond", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"}
    }


def wf_conductor():
    """WF0: Swarm Conductor — /webhook/conductor-dispatch → conductor_server.py."""
    conductor_url = PYTHON_SERVICES["conductor"]
    return {
        "name": "TNC_WF0_CONDUCTOR",
        "active": True,
        "nodes": [
            {
                "id": "cd-webhook",
                "name": "Conductor Dispatch",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 2,
                "position": [100, 300],
                "parameters": {
                    "httpMethod": "POST",
                    "path": "conductor-dispatch",
                    "responseMode": "responseNode",
                    "options": {}
                }
            },
            {
                "id": "cd-conduct",
                "name": "Conduct Intent",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.2,
                "position": [360, 300],
                "parameters": {
                    "method": "POST",
                    "url": f"{conductor_url}/conduct",
                    "sendBody": True,
                    "specifyBody": "json",
                    "jsonBody": "={{ JSON.stringify($('Conductor Dispatch').item.json.body) }}"
                }
            },
            {
                "id": "cd-respond",
                "name": "Respond",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1.1,
                "position": [620, 300],
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ JSON.stringify($('Conduct Intent').item.json) }}"
                }
            }
        ],
        "connections": {
            "Conductor Dispatch": {
                "main": [[{"node": "Conduct Intent", "type": "main", "index": 0}]]
            },
            "Conduct Intent": {
                "main": [[{"node": "Respond", "type": "main", "index": 0}]]
            }
        },
        "settings": {"executionOrder": "v1"}
    }


WORKFLOWS_TO_DEPLOY = [
    wf_swarm_dispatch,
    wf_nemoclaw_file_event,
    wf_story_prototype,
    wf_constitution_updater_v2,
    wf_analyse_chapter,
    wf_self_refine,
    wf_kdp_assembler,
    wf_nightly_audit,
    # Phase 3 additions
    wf_image_prompt,
    wf_theological_guard,
    # Phase 4 addition
    wf_conductor,
]


# ── Main ────────────────────────────────────────────────────────────────────

def deploy(dry_run: bool = False, force: bool = False):
    global N8N_KEY
    N8N_KEY = load_env()
    if not N8N_KEY:
        print("ERROR: N8N_API_KEY not found in .env")
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"  n8n WORKFLOW DEPLOYER — TNC v2.0 HAWK Swarm")
    print(f"  Mode: {'DRY RUN' if dry_run else 'LIVE DEPLOY'}")
    print(f"  Target: {N8N_BASE}")
    print(f"{'=' * 60}\n")

    existing = get_existing_workflows()
    print(f"  Existing workflows: {len(existing)}")
    for name, wid in existing.items():
        print(f"    [{wid}] {name}")

    print()
    results = {"created": [], "updated": [], "skipped": [], "failed": []}

    for wf_factory in WORKFLOWS_TO_DEPLOY:
        wf_def = wf_factory()
        name   = wf_def["name"]

        if dry_run:
            status = "WOULD CREATE" if name not in existing else ("WOULD UPDATE" if force else "WOULD SKIP")
            print(f"  [{status:14s}] {name}")
            continue

        try:
            if name in existing and not force:
                print(f"  [SKIP — exists ] {name}")
                results["skipped"].append(name)
                continue

            if name in existing and force:
                wid = update_workflow(existing[name], wf_def)
                try:
                    activate_workflow(wid)
                except Exception:
                    pass
                print(f"  [UPDATED        ] {name}  id={wid}")
                results["updated"].append(name)
            else:
                wid = create_workflow(wf_def)
                try:
                    activate_workflow(wid)
                except Exception:
                    pass
                print(f"  [CREATED OK     ] {name}  id={wid}")
                results["created"].append(name)

        except Exception as e:
            print(f"  [FAILED         ] {name}  error={e}")
            results["failed"].append({"name": name, "error": str(e)})

    print(f"\n{'─' * 60}")
    if not dry_run:
        print(f"  Created : {len(results['created'])}")
        print(f"  Updated : {len(results['updated'])}")
        print(f"  Skipped : {len(results['skipped'])}")
        print(f"  Failed  : {len(results['failed'])}")
        if results["failed"]:
            print("\n  FAILURES:")
            for f in results["failed"]:
                print(f"    {f['name']}: {f['error']}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy n8n workflows for TNC v2.0 HAWK Swarm")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating")
    parser.add_argument("--force",   action="store_true", help="Re-create existing workflows")
    args = parser.parse_args()
    deploy(dry_run=args.dry_run, force=args.force)
