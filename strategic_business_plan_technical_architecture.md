Kerman Gild Publishing: Strategic Business Plan & Technical Architecture
1. Strategic Financial Framework & Profit Optimization
The objective for Kerman Gild Publishing is to move from the industry-standard 33% Year-1 EBITDA to an optimized 40–45% target by 2028. This pivot relies on aggressive operating leverage: utilizing high-ASP (Average Selling Price) products to absorb the $455,900 annual fixed overhead base while shifting to a Direct-to-Consumer (DTC) model to eliminate the 11% variable fee erosion typical in traditional publishing.
Margin Structure Comparison: Standard Industry vs. Kerman Gild DTC
To maximize the contribution margin (CM), Kerman Gild will bypass the standard distributor-retailer ecosystem.| Fee Component | Standard Industry Model (11% Variable Fee) | Kerman Gild DTC Model || ------ | ------ | ------ || Distributor Commission | 8% | 0% || Digital Platform Fee | 3% | 0%–3% (Internalized) || Total Variable Fee Erosion | 11% | 0%–3% || Fiction Unit COGS | $300.00 (Standard Physical COGS) | $150.00 (Target Cost Floor) || Primary Revenue Driver | High Volume (Low ASP) | High Density (Business Guide $3,499 ASP) || Profit Retention | Compressed | Optimized (+11% Revenue Retention) |
Lean Pilot: The $100 NZD Budget Allocation
In the initial "Lean Pilot" phase, Kerman Gild operates with a $0 hosting cost by utilizing local Alienware hardware. The $100 NZD budget is allocated with a focus on high-yield visibility:
$0 (0%):  Infrastructure/Hosting (Internalized via SINGULA layer).
$65 (65%):  Metadata Optimization & Keyword Research Tools (Targeting a 300% visibility increase).
$35 (35%):  Domain Registration and SEC-compliant legal landing pages for Direct-to-Consumer sales.
Fixed Overhead & Operating Expense Strategy
The $455,900 fixed overhead will be managed through the "OpEx Lag" principle. Kerman Gild will delay all non-essential hires, specifically the Sales & Distribution Manager (budgeted at $70,000), until 2028. This ensures OpEx growth remains below revenue expansion, saving $35,000 in 2027 alone.
2. Global Positioning: Direct-to-Consumer & Social Sales
Kerman Gild will leverage the global reach of #BookTok and serialized digital models to drive sales for  The Cydonian Oaths  and  The Cauldron of God .
Growth Levers & Social Sales
TikTok Shop Affiliate Strategy:  Target an affiliate network to tap into the 400–600% sales increase observed for #BookTok titles.
Tiered Subscription Serialization:  Sequels to  The Stone and the Sceptre Chronicles  will be serialized on Substack/Patreon. Tiers will be structured to provide "Lore Early Access" and "Digital Vault" permissions, increasing Average Order Value (AOV) by 25–40%.
High-ASP Scaling:  The primary lever for overhead absorption is the  $3,499 Business Guide . Selling approximately 11 units per month covers the entire  $38,000/month fixed cost base ($ 455.9k annually), allowing high-volume fiction to serve as pure profit and brand equity.
Metadata Optimization Checklist (Priority 1)
  Keyword Saturation:  Research high-traffic, low-competition tags on Amazon and global search engines.
  Category Injection:  Map titles into underserved sub-niches to secure "Bestseller" badges quickly.
  A/B Creative Testing:  Deploy split-tests for digital covers to increase click-through rates (CTR) by 20–30%.
  Back-end Optimization:  Update 7-keyword slots to prioritize search visibility over brand-name terms.
3. NZ Local Strategy: Agent 9 Autonomous Intelligence
Agent 9 represents the transition from passive software to  Goal-Oriented Execution . Hosted within the SINGULA layer, this agent proactively monitors the New Zealand literary ecosystem.
Target Monitoring & Entities
Agent 9 is tasked with tracking specific entities critical for funding and innovation:
New Zealand Society of Authors (NZSA):  Monitor for manuscript assessments and professional development opportunities.
Mātātuhi Foundation:  Track annual funding rounds for "Innovative Readership" projects.
Michael King Writers Centre:  Monitor residency calls to ensure Kerman Gild authors have dedicated time for high-value draft production.
Autonomous Workflow & Self-Correction
Agent 9 utilizes a "Self-Correction Loop" for robust execution. If the agent encounters a 403 error (blocked path) or a site layout change on the NZSA portal, it is programmed to:
Analyze the failure reason.
Attempt an alternative path (e.g., RSS feed, Sitemap, or archived cache).
Log the outcome and flag for human review only if a logical workaround is unreachable.
Output: OPPORTUNITIES_LOG.md
Deadline,Entity,Offer Type,Required Action
YYYY-MM-DD,NZSA,MS Assessment,Submit  The Stone and the Sceptre
YYYY-MM-DD,Mātātuhi,Project Grant,"Draft ""Digital Serialization"" proposal"
4. Technical Architecture: The 'SINGULA' Layer
The SINGULA layer is a high-efficiency agentic swarm that operates at $0 hosting cost.
Hardware Utilization & Latent MoE
Local Infrastructure:  Alienware Desktop utilizing llama.cpp for GGUF CPU inference.
Nemotron 3 Super Integration:  The model features 120B total parameters but only  12B active parameters  per request.
Latent MoE Logic:  Through token compression before expert routing, Latent MoE allows the model to consult  4x more expert specialists  (512 experts total) for the same computational cost as running a single expert. This efficiency enables high-capacity reasoning on consumer-grade hardware.
NVFP4 Quantization:  Nemotron 3 Super is natively pretrained in NVFP4 (4-bit floating point), optimized for Blackwell-ready architectures, cutting memory requirements by 4x compared to FP8 while maintaining high reasoning accuracy.
Execution Control: Thinking Budgets
To manage the "Thinking Tax"—the latency and cost of multi-agent reasoning—the system utilizes granular controls:
/think  Mode:  Used for complex planning, grant drafting, and strategic financial analysis (Chain-of-Thought enabled).
/no_think  Mode:  Used for high-speed data logging, web scraping, and OPPORTUNITIES_LOG.md updates to keep the swarm efficient and latency-free.
Speculative Decoding:  Accelerated by Multi-Token Prediction (MTP) heads, enabling the model to predict several future tokens simultaneously, reducing tool-calling latency.
5. Implementation Deliverable: GitHub Copilot Architect Prompt
### SYSTEM ARCHITECT PROMPT: SINGULA LAYER DEPLOYMENT


Command: Architect an n8n Docker environment and local model integration for the SINGULA layer.


Core Specifications:
1. **Model Swap**: Configure all LLM nodes to use the Nemotron 3 Super (120B-A12B) via an OpenAI-compatible API endpoint (local llama.cpp server).
2. **Reasoning Control**: 
   - Implement logic to toggle between `/think` (for grant analysis) and `/no_think` (for data logging) based on the "Thinking Tax" optimization strategy.
   - Set a 1M-token context window limit for long-form manuscript reasoning.
3. **Agent 9 Scraper Logic**:
   - Construct n8n webhooks to trigger scraping of NZSA (authors.org.nz) and Mātātuhi Foundation.
   - Implement **Self-Correction Loops**: Use an 'if-fail' node to catch 403/404 errors and retry via alternative selectors or sitemap paths.
4. **Autonomous Logging**:
   - Write scraped opportunities directly to a structured Markdown table in `/logs/OPPORTUNITIES_LOG.md`.
   - Columns: Deadline, Entity, Offer Type, Required Action.
5. **Inference Optimization**: 
   - Enable Speculative Decoding logic to utilize Nemotron’s Multi-Token Prediction (MTP) for accelerated tool calls.


Expected Directory Tree:
/singula
  /docker-compose.yml
  /n8n_workflows/
    /agent_9_nz_monitoring.json
  /models/
    /nemotron-3-super-q4.gguf
  /logs/
    /OPPORTUNITIES_LOG.md


6. Risk Mitigation & Scalability
Operational Capacity Checks
Inventory vs. Cash Flow:  High-value print runs for the $3,499 Business Guide carry significant inventory risk (hypothetical $1,000 COGS). Initial runs must align with confirmed pre-orders.
Unit Cost Targets:  For Fiction, a standard 500-unit run spikes costs to  $300/unit. The primary goal is scaling to 5,000+ units to hit the $ 150 unit cost target floor.
Royalty Compression:  High-ASP items must cover the  $455,900 fixed base before author royalties ($ 70 to $100 per copy for premium guides) begin to compress net margins.
Swarm Reliability
Blocked Path Mitigation:  Agent 9 is tasked with analyzing failure states on NZSA/Mātātuhi sites. If a selector fails, the agent searches for archived versions of the page to extract deadline dates.
Reasoning Drift:  To prevent alignment loss during "Context Explosion," agents are forced to re-verify the primary objective ("Goal-Oriented Execution") every 5 turns within the 1M-token context window.

