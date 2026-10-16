"""Hand-authored graph seed for the synthetic company (Larkspur Supply).

SEEDED, NOT EXTRACTED: the facts, decisions, answers, tasks and their edges below were
written by hand to match the documents in corpus/documents. Documents are loaded from the
markdown files. Everything the agent does AFTER seeding (traversal, correction, re-judging,
the repair queue) runs for real against FalkorDB.
"""

PEOPLE = [
    ("p-maya", "Maya Chen", "CEO"), ("p-raj", "Raj Patel", "Head of Operations"),
    ("p-elena", "Elena Ruiz", "Finance Lead"), ("p-tom", "Tom Becker", "Sales Lead"),
    ("p-aisha", "Aisha Khan", "Product"), ("p-leo", "Leo Novak", "Engineering Lead"),
    ("p-priya", "Priya Nair", "Legal and Contracts"), ("p-sam", "Sam Ortiz", "Customer Success"),
]
PROJECTS = [
    ("pr-pricing", "Q3 Pricing Reset"), ("pr-launch", "Meridian Marketplace Launch"),
    ("pr-renewals", "Enterprise Renewals"), ("pr-support", "Support Scale-up"),
]

# Facts. status is the state BEFORE the demo correction.
# (id, text, source_doc_ids)
FACTS = [
    ("f-comm-9", "Meridian marketplace commission rate is 9% of GMV", ["doc-02", "doc-05", "doc-08"]),
    ("f-handling-5", "Larkspur handling add-on for marketplace sales is 5%", ["doc-05"]),
    ("f-partnerfee-14", "Partner-facing marketplace fee is 14% (commission plus handling)", ["doc-05", "doc-14"]),
    ("f-margin-62", "Gross margin on a $49 Pro plan sold via Meridian is about 62%", ["doc-08"]),
    ("f-corvane-6", "Corvane fulfilment fee is 6% of order value", ["doc-17", "doc-19"]),
    ("f-gmv-1.8m", "Q3 GMV forecast is $1.8M", ["doc-07", "doc-08"]),
    ("f-pro-49", "Pro plan list price is $49 per seat per month", ["doc-05"]),
    ("f-direct-nofee", "Direct sales carry no marketplace fee", ["doc-12"]),
]
# Fact -> Fact derivations: (child, parent)
FACT_DERIVED_FROM = [
    ("f-partnerfee-14", "f-comm-9"), ("f-partnerfee-14", "f-handling-5"),
    ("f-margin-62", "f-comm-9"), ("f-margin-62", "f-corvane-6"),
]

# Decisions: (id, title, rationale, owner, project, source_doc, based_on_facts)
DECISIONS = [
    ("d-price-49", "Set Pro plan list price at $49 per seat on Meridian",
     "At a 9% Meridian commission the $49 price keeps gross margin above the 62% target.",
     "p-elena", "pr-pricing", "doc-06", ["f-margin-62", "f-comm-9"]),
    ("d-partnerfee-14", "Set partner-facing marketplace fee at 14%",
     "14% is the 9% Meridian commission plus 5% Larkspur handling.",
     "p-elena", "pr-pricing", "doc-06", ["f-partnerfee-14"]),
    ("d-halden-disc", "Offer Halden Foods a 10% volume discount",
     "Margin after the 9% commission leaves room for a 10% discount on 40 seats.",
     "p-tom", "pr-pricing", "doc-06", ["f-margin-62"]),
    ("d-margin-target", "Raise annual gross margin target to 62% in the board update",
     "Marketplace pricing was modelled to deliver about 62% gross margin.",
     "p-maya", "pr-launch", "doc-16", ["f-margin-62"]),
    ("d-hire-2", "Approve two support reps for Q4",
     "The Q3 GMV forecast of $1.8M supports two more support reps.",
     "p-raj", "pr-support", "doc-18", ["f-gmv-1.8m"]),
    ("d-corvane", "Choose Corvane as fulfilment partner",
     "Lowest fee (6%) and best SLA among three candidates.",
     "p-raj", "pr-launch", "doc-19", ["f-corvane-6"]),
]

# Answers the company already gave out: (id, text, source_doc, derived_from decisions/facts)
ANSWERS = [
    ("a-halden-quote", "Quote to Halden Foods: $49 per seat, 10% volume discount", "doc-09", ["d-halden-disc", "d-price-49"]),
    ("a-brightwater-quote", "Quote to Brightwater Clinics: $49 per seat, partner fee 14%", "doc-10", ["d-price-49", "d-partnerfee-14"]),
    ("a-orla-quote", "Quote to Orla Retail: Team plan $29 per seat, partner fee 14%", "doc-11", ["d-partnerfee-14"]),
    ("a-pike-quote", "Quote to Pike & Rowe: Team plan $29 per seat, direct sale, no marketplace fee", "doc-12", ["f-direct-nofee"]),
    ("a-faq-fee", "Support FAQ: partners see a 14% fee on Meridian orders", "doc-13", ["f-partnerfee-14"]),
]

# Tasks: (id, title, state, owner, implements decision, source_doc)
TASKS = [
    ("t-pricing-page", "Pricing page shows Pro at $49 per seat", "done", "p-aisha", "d-price-49", "doc-15"),
    ("t-billing-config", "Billing service meridian.channel_fee_pct = 14", "done", "p-leo", "d-partnerfee-14", "doc-14"),
    ("t-halden-send", "Send Halden Foods quote and contract paperwork", "in_progress", "p-tom", "d-halden-disc", "doc-15"),
    ("t-hire-reqs", "Open two support rep requisitions", "in_progress", "p-raj", "d-hire-2", "doc-18"),
    ("t-corvane-onboard", "Onboard Corvane integration", "done", "p-leo", "d-corvane", "doc-19"),
]

# Document-to-document state edges: (newer, older) meaning newer SUPERSEDES older
SUPERSEDES = [("doc-02", "doc-01"), ("doc-03", "doc-02")]

# The correction used in the demo (the executed contract fact).
CORRECTION = {
    "old_fact": "f-comm-9",
    "new_fact_id": "f-comm-12",
    "new_text": "Meridian marketplace commission rate is 12% of GMV",
    "source_doc": "doc-03",
    "note": "Executed agreement (22 Sep 2026) sets 12%; the 9% figure came from an unsigned draft.",
}
