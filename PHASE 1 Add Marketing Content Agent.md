PHASE 1: Add Marketing Content Agent (Agent 13)
Goal: A lightweight, always-on agent that turns key scenes, hooks, and theological beats into ready-to-post social content, newsletter blurbs, Royal Road chapter notes, TikTok scripts, Amazon A+ modules, and grant-application copy.
Step-by-step

1. Create the new agent folder and files
   In your project root (nephilim_chronicles/), run this in terminal (or let Copilot do it):

Bash

mkdir -p agents/marketing_agent

2. Feed this exact prompt to VS Code Copilot (create marketing_agent.py)
   Copy the entire block below and paste it into a new file agents/marketing_agent.py. Tell Copilot:

“Generate the complete Python FastAPI service from this specification”

Markdown

Create a FastAPI service called Marketing Content Agent (Agent 13) on port 8770.

Requirements:

- POST /generate_content
  Input JSON:
  {
  "content_type": "twitter_thread | tiktok_script | newsletter_blurb | royalroad_chapter_note | amazon_a_plus | grant_application",
  "source_text": "the full scene or chapter excerpt",
  "target_audience": "Christian speculative fiction readers",
  "key_themes": ["acoustic reality", "endurance commission", "Two Witnesses"],
  "book_number": 3,
  "chapter_number": 4,
  "tone": "urgent | hopeful | mysterious | theological"
  }
- The agent uses Ollama (llama3.1 or mistral) locally for speed.
- It pulls context from the Story Prototype (Role Graph + Plot Graph) via Qdrant if needed.
- Output must include:

  - Ready-to-post text
  - Suggested hashtags / emojis
  - Length-optimized versions (short / medium / long)
  - SEO keywords for that piece
- Add a simple health check endpoint GET /health
- Log every generation to /data/TNC_Books35/LOGS/marketing_log.json
- Include rate limiting (max 10 requests per minute) to protect local Ollama.

Use Pydantic models for input/output validation.

Copilot will generate the full FastAPI app. Review it, then run:

Bash

cd agents/marketing_agent
python -m venv .venv
.venv\Scripts\activate
pip install fastapi uvicorn httpx qdrant-client
uvicorn marketing_agent:app --port 8770 --reload

Test it immediately with a simple curl or Postman call using a scene from Book 3.

3. Wire it into n8n (quick win)
   Create a new n8n workflow called “Marketing Content Dispatch”:

Trigger: Manual or Webhook
Node 1: HTTP Request → POST to http://localhost:8770/generate_content
Node 2: Switch based on content_type
Node 3: Send to your private Discord/Telegram/Substack via their APIs

PHASE 2: Simple Monitoring Dashboard (Next 30–60 minutes)
Goal: One glance tells you if the entire swarm is healthy.

Prompt for Copilot (create monitoring_dashboard.py in a new monitoring/ folder)

Markdown

Create a lightweight FastAPI + HTMX dashboard on port 8780 called Swarm Health Monitor.

Pages:

- / → Overview: Nemoclaw status, Qdrant collections count, pending CRDT proposals, last nightly audit time, last marketing generation.
- /logs → Live tail of DAEMON_HEALTH.log and marketing_log.json
- /freeze → Toggle Author Freeze Mode (writes a flag file that Nemoclaw and n8n respect)

Use Tailwind CSS via CDN for quick styling.
Show green/red status indicators.
Include a "Force Nightly Audit" button that calls the n8n webhook.

Once running, bookmark http://localhost:8780 — it becomes your command centre.

PHASE 3: Author Freeze Mode
This is a simple flag file (FREEZE_MODE.lock) that Nemoclaw checks before firing any auto-dispatches.
Add this to nemoclaw_daemon.py (Copilot prompt):
MarkdownIn the file-watch handler, first check if /data/TNC_Books35/FREEZE_MODE.lock exists.
If it does, log "Author Freeze active — skipping dispatch" and do nothing.
Add an endpoint in the monitoring dashboard to create/delete the lock file.


### Immediate Next Step: Get the Marketing Agent Running

Since the dashboard shows it as  **down** , let’s bring Agent 13 online right now. This agent will immediately start generating:

* Twitter/X threads
* TikTok scripts
* Newsletter blurbs
* Royal Road chapter notes
* Amazon A+ content
* Grant application copy

**Action for you (2 minutes):**

1. In VS Code, open the file agents/marketing_agent/marketing_agent.py (the one Copilot generated from my previous prompt).
2. Make sure the virtual environment is activated and the dependencies are installed:
   Bash

   ```
   cd agents/marketing_agent
   .venv\Scripts\activate
   pip install fastapi uvicorn httpx qdrant-client
   ```
3. Start the service:
   Bash

   ```
   uvicorn marketing_agent:app --port 8770 --reload
   ```

Once it’s running, the dashboard should turn green for “Marketing Agent” within ~30 seconds (refresh the page).

**Test it immediately** with the new Book 3 chapter you just delivered. Use this exact payload in a tool like Postman or curl:

JSON

```
{
  "content_type": "twitter_thread",
  "source_text": "Paste the full text of CHAPTER_02_TheFrequencyBeneathTheCure.md here (or the key excerpt with Brennan's 'tuning them' line)",
  "target_audience": "Christian speculative fiction readers",
  "key_themes": ["acoustic reality", "endurance commission", "False Prophet", "Cydonian technology"],
  "book_number": 3,
  "chapter_number": 2,
  "tone": "urgent"
}
```

Send that POST to http://localhost:8770/generate_content and I need the output
