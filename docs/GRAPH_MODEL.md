# Graph model and Cypher

Nodes: `Document{id,title,state:draft|executed|superseded|current,date,author,kind,body}`, `Fact{id,text,status:current|superseded|stale,valid_from,valid_to}`,
`Decision{id,title,rationale,status}`, `Answer{id,text,status}`, `Task{id,title,state,status}`, `Person`, `Project`.

Edges (child points at what it depends on): `(Decision)-[:BASED_ON]->(Fact)`, `(Answer)-[:DERIVED_FROM]->(Decision|Fact)`,
`(Fact)-[:DERIVED_FROM]->(Fact)`, `(Task)-[:IMPLEMENTS]->(Decision)`, `(Fact)-[:STATED_IN]->(Document)`,
`(Fact)-[:CORRECTED_BY {at,note}]->(Fact)`, `(Document)-[:SUPERSEDES]->(Document)`, `(Person)-[:OWNS]->(Decision|Task)`,
`(Decision)-[:PART_OF]->(Project)`, `(Decision|Answer|Task)-[:RECORDED_IN]->(Document)`.

All queries live in `aftershock/tools.py`:
- **correct_fact**: `CREATE (new:Fact ...) CREATE (old)-[:CORRECTED_BY]->(new) SET old.status='superseded', old.valid_to=$now`
- **blast_radius**: `MATCH p=(f:Fact {id:$id})<-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*1..5]-(x) RETURN x.id, labels(x)[0], min(length(p))`
- **path_proof**: `RETURN [n IN nodes(shortestPath((x)-[:BASED_ON|DERIVED_FROM|IMPLEMENTS*..6]->(f))) | n.id]` (FalkorDB allows shortestPath only in WITH/RETURN)
- **repair_queue**: blast_radius + detail/owner query + path_proof per item
- **graph-on answers**: only `status='current'` facts, with their `STATED_IN` document states
Note: bi-temporal supersede-instead-of-delete is borrowed from Graphiti's approach (credited in INSPIRATION.md); we implement it ourselves.
