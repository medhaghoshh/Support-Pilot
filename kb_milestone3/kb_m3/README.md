# Milestone 3 - Knowledge Base / Data Engineer (Member 4)

Task:
- Support the Diagnosis Agent by structuring ticket-analysis rules/data
  (symptom -> likely category mapping)
- Make sure KB content supports multi-step agent reasoning, not just
  single-shot retrieval

Both parts are implemented, wired into the Milestone 2 pipeline, and
covered by a self-test script.

===================================================
WHAT IS NEW IN MILESTONE 3
===================================================

Part 1 - Diagnosis Agent support (symptom -> category)
  diagnosis_rules.py  - 168 weighted symptom indicators across 6
                        categories, plus severity indicators, a
                        category -> KB shortlist map, and clarifying
                        questions for low-confidence tickets
  diagnose.py         - the engine: ticket text in, structured analysis
                        out (category, confidence, matched symptoms,
                        suggested priority, KB shortlist)

Part 2 - Multi-step reasoning support
  kb_reasoning.py     - per-article reasoning layer: structured symptom
                        lists, prerequisites, ORDERED resolution steps
                        (each with an expected outcome), cross-references
                        to related articles, an explicit
                        "next_if_unresolved" hop, escalation target and
                        trigger condition, and an auto_resolvable flag

Milestone 2 gave single-shot retrieval: query in, article out.
Milestone 3 turns that into a plan an agent can walk:
  diagnose -> shortlist -> retrieve -> step 1..N -> if unresolved, next
  article -> if still unresolved, escalate to a named team.

===================================================
FILES
===================================================
kb_articles.py       - the 10 KB articles (unchanged from Milestone 2)
diagnosis_rules.py   - NEW: symptom -> category rules and severity data
diagnose.py          - NEW: diagnosis engine for the Diagnosis Agent
kb_reasoning.py      - NEW: multi-step reasoning layer over the articles
ingest.py            - UPDATED: also populates the 4 new SQL tables and
                       carries reasoning hooks into ChromaDB metadata
search.py            - semantic retrieval (unchanged from Milestone 2)
api.py               - UPDATED: 5 new endpoints for the agent pipeline
view_table.py        - UPDATED: shows all tables
test_milestone3.py   - NEW: 15-check self-test
requirements.txt     - dependencies

===================================================
DATABASE SCHEMA
===================================================

Knowledge_Base (unchanged - still exactly the 5 required columns)
  article_id, title, content, category, embedding_id

New Milestone 3 tables (kept separate so nothing consuming the
original schema breaks):

  KB_Symptoms          kb_id, symptom
  KB_Resolution_Steps  kb_id, step_number, action, expected_outcome
  KB_Reasoning         kb_id, prerequisites, related_articles,
                       next_if_unresolved, escalate_to, escalate_when,
                       auto_resolvable
  Diagnosis_Rules      category, indicator, weight

Row counts after ingestion:
  Knowledge_Base 10 | KB_Symptoms 34 | KB_Resolution_Steps 42
  KB_Reasoning 10   | Diagnosis_Rules 168

===================================================
API ENDPOINTS
===================================================

From Milestone 2:
  GET /knowledge/search?q=<text>&top_k=3

New in Milestone 3:
  GET /diagnose?text=<ticket text>
      -> predicted_category, confidence, matched_symptoms,
         suggested_priority, suggested_kb_ids, needs_clarification,
         clarifying_questions

  GET /knowledge/reasoning/{kb_id}
      -> symptoms, prerequisites, ordered resolution_steps,
         related_articles, escalate_to, escalate_when, auto_resolvable

  GET /knowledge/related/{kb_id}
      -> cross-referenced articles for multi-hop reasoning

  GET /knowledge/chain/{kb_id}
      -> the ordered fallback path if the first article does not resolve

  GET /workflow/analyze?text=<ticket text>&top_k=3
      -> the full Diagnosis + Retrieval handoff in one call: diagnosis,
         retrieved articles each with their reasoning attached, and the
         reasoning chain. This is the endpoint the agent pipeline should
         call - it saves the Resolution and Escalation Agents from making
         their own separate lookups.

===================================================
HOW CONFIDENCE IS CALCULATED
===================================================
Confidence blends three signals:
  share    - how much of the total matched evidence the winning category holds
  margin   - how far clear it is of the runner-up
  evidence - how much absolute evidence was found at all

The evidence term is deliberate: without it, a ticket matching a single
keyword would report near-certainty. Confidence is capped at 0.95, and
below 0.45 the result is flagged needs_clarification with questions
attached, so the workflow asks rather than guesses.

Note on tie-breaks: when two categories score equally, Security wins.
Misrouting a phishing or breach report costs far more than misrouting a
routine request.

===================================================
STEPS TO RUN IN VS CODE
===================================================

1. Unzip and open the "kb_m3" folder in VS Code
   (File -> Open Folder -> select kb_m3)

2. Terminal -> New Terminal

3. Create a virtual environment (use py -3.12 if plain python picks 3.14):
   py -3.12 -m venv venv

4. Activate it:
   Windows: venv\Scripts\activate
   Mac:     source venv/bin/activate

   If Windows blocks the script, run this first then retry:
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

5. Install packages:
   pip install -r requirements.txt

6. Run the ingestion pipeline:
   python ingest.py

   Expected output:
     Ingested 10 articles as 10 chunks.
     - ChromaDB vector store: ./chroma_db
     - Knowledge_Base SQL table: knowledge_base.db
     Milestone 3 reasoning data:
     - KB_Symptoms:          34 rows
     - KB_Resolution_Steps:  42 rows
     - KB_Reasoning:         10 rows
     - Diagnosis_Rules:      168 rows

   (If the embedding model is not cached yet it downloads ~80MB once.)

7. Run the self-test:
   python test_milestone3.py
   Expected: ALL CHECKS PASSED

8. Try the diagnosis engine on its own:
   python diagnose.py

9. View all the tables:
   python view_table.py

10. Start the API:
    uvicorn api:app --reload

11. Test in your browser at http://127.0.0.1:8000/docs
    Good ones to try:
      /diagnose          text = my vpn keeps disconnecting
      /workflow/analyze  text = outlook is not receiving emails
      /knowledge/chain/KB-110

===================================================
HONEST NOTES
===================================================
- The diagnosis engine is deterministic rule-based matching, not an ML
  model. That is intentional for an agent's first step: it is fast,
  explainable (it returns exactly which symptoms matched), and easy for
  the team to tune. It is not the same thing as the Milestone 1
  classifier, which predicts a support department from a trained model.
- The 10 KB articles are realistic sample content, not real company
  documentation. The reasoning layer, cross-references and escalation
  targets were written to be plausible for a mid-size IT department.
- Confidence values come from the scoring formula above. They are a
  measure of how clearly the symptoms point at one category, not a
  measured accuracy rate.
- Adding a new article means adding a matching entry in kb_reasoning.py.
  test_milestone3.py will fail loudly if one is missing, so this cannot
  be forgotten silently.

===================================================
NOTES FOR TEAMMATES
===================================================
- Member 2 (Backend): /workflow/analyze is the single call for the
  Diagnosis -> Retrieval handoff. Everything the later agents need is in
  that one response.
- Member 3 (Vector DB): ChromaDB metadata now also carries symptoms,
  escalate_to, auto_resolvable and related_articles per chunk, so the
  Retrieval Agent can pass these through without a second lookup.
- Member 5 (RAG/LLM): resolution_steps are ordered and individually
  addressable with an expected outcome per step, for the Resolution
  Agent. escalate_to / escalate_when / auto_resolvable are for the
  Escalation Agent. next_if_unresolved gives the multi-hop fallback.
- Categories are unchanged: Networking, Password Reset, Email, Hardware,
  Software, Security.
