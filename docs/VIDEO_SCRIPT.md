# Demo video script (~2.5 min, screen capture + voiceover)

Record at 1500x900, dark UI, browser fullscreen on localhost:8000. Narration below each shot.
If no LLM key by recording time, record the honest no-key version: re-judge cards say "needs human",
Ask says "answered by: none (extractive)" - say so on camera. Do not hide it.

## Shot 1 - hook (0:00-0:12)
Screen: the graph view, idle.
"Companies make decisions on facts. Then the facts change - a draft contract gets replaced by the signed
one - and everything built on the old number quietly goes stale. Aftershock fixes one fact and finds
everything built on it."

## Shot 2 - the company brain (0:12-0:35)
Screen: pan the graph; hover nodes; click Reset first so state is pre-correction.
"This is Larkspur Supply, a synthetic 25-person company. Its knowledge lives in a FalkorDB graph: facts,
decisions, tasks and answers, connected by BASED_ON, DERIVED_FROM and IMPLEMENTS edges, and every fact
carries provenance - which document stated it, and whether that document is a draft or executed.
It priced its Pro plan assuming Meridian takes 9 percent. That number came from an unsigned draft."

## Shot 3 - the stale answer, graph off (0:35-0:55)
Screen: toggle Graph OFF, ask "What commission rate does Meridian take on our marketplace sales?"
"With the graph off, this is ordinary document search. The top hit is the unsigned draft, and the system
confidently answers 9 percent - even after the real contract says 12."

## Shot 4 - the correction (0:55-1:35)
Screen: toggle Graph ON, click Apply correction, let the trace play, scroll the repair queue.
"Now the correction lands: the executed agreement says 12 percent. Watch the agent. It supersedes the old
fact - nothing is deleted, a CORRECTED_BY edge is written. Then a Cypher traversal finds the blast radius:
13 nodes downstream, up to 3 hops - a derived margin fact, the partner fee, pricing decisions, three
customer quotes, the support FAQ, and a live billing config. Five unrelated items are left alone.
The repair queue is ranked by graph impact, and the three decisions with the most dependents get re-judged
by an LLM against the old and new fact." (No key: "...are flagged for human re-judgment - we never fake a verdict.")

## Shot 5 - evidence (1:35-1:55)
Screen: click a queue item (e.g. the billing config task), show the Evidence path card.
"Every item carries its proof: the exact dependency path back to the stale fact, and the documents the fact
was stated in, with their state. This is what 'tracing decisions back to their source' looks like as data."

## Shot 6 - multi-hop Q&A (1:55-2:25)
Screen: click the Try link: "Who owns the tasks affected by the Meridian commission change?"
"Graph on, a multi-hop question: who owns the affected work? The agent walks Fact to Decision to Task to
Person and names Elena, Tom, Maya, Aisha and Leo with their items." (Key: "The LLM answers only by calling
the graph tools - you can see the exact Cypher-backed calls it made.") Then toggle Graph OFF and re-ask.
"Graph off, the same question retrieves the unsigned draft and cannot name a single owner."

## Shot 7 - close (2:25-2:40)
Screen: README on GitHub (or docs/REAL_VS_SEEDED.md).
"What's real: FalkorDB, every traversal, the correction semantics, path proofs, the repair queue and the
re-judging. What's seeded: the company and its documents - disclosure is in the repo. One docker command
and pip install runs it locally. Aftershock: fix one fact, find everything built on it."
