# ARTCRAFT STORAGE LAB — TOTAL RE-FOUNDATION / FIRST-PRINCIPLES MANDATE

You are taking over an existing engineering project:

**ArtCraft Storage Lab**

Local repository:

`~/Projects/artcraft-storage-lab`

GitHub laboratory repository:

`Roddygithub/artcraft-storage-lab`

This is **NOT a continuation prompt**.

You are not being asked to finish the current roadmap.

You are not being asked to preserve the current architecture.

You are not being asked to validate the decisions already made.

You are not being asked to “close the remaining gaps” unless, after independent analysis, you conclude that the existing project direction is actually the correct one.

Your first responsibility is to **reconstruct, challenge, and rethink the entire project from first principles**.

You have broad technical autonomy.

You may preserve the current project.

You may radically simplify it.

You may redesign it.

You may remove major components.

You may replace technologies.

You may collapse the project into something smaller.

You may conclude that the integration should live somewhere entirely different.

You may conclude that the current repository should eventually become only a test laboratory.

You may conclude that the current project architecture is fundamentally misguided.

You may even conclude that **ArtCraft Storage Lab should not exist as a standalone project at all**.

The only thing you are not allowed to do is blindly follow historical decisions because significant effort has already been invested in them.

---

# 1. THE PRIMARY QUESTION

Before asking:

> “How do I finish ArtCraft Storage Lab?”

ask:

> **“If I discovered this user problem today, with no existing code and no sunk cost, what would I build?”**

Then ask:

> **“Would I build ArtCraft Storage Lab at all?”**

Then:

> **“Would I choose ArtCraft?”**

Then:

> **“Would I integrate through Seafile?”**

Then:

> **“Would I use the current gateway architecture?”**

Then:

> **“Would I patch Seahub/fileserver?”**

Then:

> **“Would I invent a Host Contract?”**

Then:

> **“Would I maintain per-application adapters?”**

Then:

> **“Would I solve this in Seafile, in ArtCraft, in a shared protocol layer, through an existing standard, through an existing ecosystem integration, or somewhere else entirely?”**

Do not assume the answers.

Derive them.

---

# 2. THE USER PROBLEM, NOT THE CURRENT SOLUTION

The real user need is approximately:

```text
I use Seafile as my file platform.

I want to click a supported file inside Seafile Web.

I want an appropriate high-quality web editor to open it.

I want to modify it.

I want Save to persist the new document back into Seafile.

I want Seafile version history to work normally.

I want to reopen the file later and find my edit preserved.

I want a clean self-hosted/open-source-oriented solution.

I do not want a workflow based on manually downloading, editing and re-uploading files.

I do not want SeaDrive to be required.

I do not want a desktop application to be mandatory for this workflow.
```

Historically the project attempted to satisfy this using ArtCraft Web applications.

That is an **implementation choice**, not a fact of nature.

You must independently assess whether ArtCraft is actually a good foundation for this use case.

Do not preserve ArtCraft merely because the repository is called ArtCraft Storage Lab.

---

# 3. HARD USER CONSTRAINTS VS HISTORICAL ASSUMPTIONS

Distinguish carefully between:

## Hard constraints

These should not be casually overridden:

- direct web-based file workflow from Seafile is strongly preferred;
- no mandatory SeaDrive;
- no mandatory manual download/edit/upload;
- no mandatory desktop editor for the core workflow;
- user-controlled / self-hostable architecture is strongly preferred;
- do not modify production Seafile without explicit owner authorization;
- do not publish anything upstream before the project-level review gate permits it;
- even after that gate, upstream publication requires explicit owner authorization.

## Everything else

Everything else is challengeable.

That includes:

- using ArtCraft at all;
- supporting all ArtCraft applications;
- supporting five applications;
- supporting thirteen applications;
- maintaining a gateway;
- using a parent/iframe Host Contract;
- using `postMessage`;
- using Rust/WASM for the integration boundary;
- using a shared `craft-platform`;
- keeping Seafile-specific logic outside applications;
- patching Seahub;
- patching C fileserver;
- using conditional-write APIs;
- using the existing dispatcher;
- reusing ONLYOFFICE-style routing;
- preserving the current repository structure;
- the existing GR process;
- the current roadmap;
- the current notion of “production readiness”;
- the current testing strategy;
- the existing upstream strategy.

Challenge all of it.

---

# 4. IGNORE SUNK COST

A large amount of work already exists.

That work is evidence.

It is **not justification**.

Do not reason:

> “We already implemented X, therefore we should continue with X.”

Reason:

> “Given what we now know from implementing X, would we choose X again?”

Previous work may contain extremely valuable discoveries even if the architecture is discarded.

Preserve knowledge.

Do not preserve mistakes.

---

# 5. FIRST PHASE — RECONSTRUCT THE PROJECT

Before designing anything, independently reconstruct the project.

Inspect the actual repository.

Do not rely on this prompt as current truth.

Determine:

```text
LOCAL_HEAD
REMOTE_HEAD
WORKTREE_STATE
CURRENT_BRANCH
RECENT_HISTORY
CURRENT_ARCHITECTURE
CURRENT_DISPATCH
CURRENT_PATCHES
CURRENT_APP_ADAPTERS
CURRENT_SHARED_TRANSPORT
CURRENT_SEAFILE_MODIFICATIONS
CURRENT_BROWSER_PROTOCOL
CURRENT_SECURITY_MODEL
CURRENT_TEST_MODEL
CURRENT_DEPLOYMENT_MODEL
CURRENT_REVIEW_MODEL
CURRENT_UPSTREAM_MODEL
```

Read the relevant code, not just summaries.

Inspect at least:

- gateway;
- dispatcher;
- Seafile integration;
- Seahub patches;
- fileserver patches;
- shared transport;
- application adapters;
- build tooling;
- candidate artifact handling;
- browser protocol;
- capability/session design;
- security docs;
- licensing docs;
- test matrix;
- GR reports;
- GPT reviews;
- independent reviews.

Historical reports are clues.

Current code and runtime behavior are stronger evidence.

---

# 6. SECOND PHASE — RECONSTRUCT THE ORIGINAL PROBLEM

Separate the **problem** from the **solution**.

Write an internal problem statement that contains no ArtCraft-specific architectural assumption.

Identify:

- user workflows;
- essential UX;
- required file semantics;
- required save semantics;
- versioning semantics;
- authorization semantics;
- browser requirements;
- deployment requirements;
- maintenance expectations;
- likely future evolution.

Then determine which requirements are:

- essential;
- desirable;
- historical;
- accidental;
- unnecessary.

Do not move to implementation until the underlying problem is clear.

---

# 7. THIRD PHASE — MARKET / ECOSYSTEM / ARCHITECTURE SEARCH

Do not assume the project needs custom engineering.

Investigate what already exists.

Search the current ecosystem where appropriate.

Look seriously for:

- existing Seafile editor integration mechanisms;
- ONLYOFFICE integration architecture;
- Collabora integration architecture;
- WOPI or WOPI-like standards;
- generic web editor host protocols;
- storage provider APIs;
- Seafile plugin/integration APIs;
- Seahub extension points;
- file-provider standards;
- browser editor embedding standards;
- WebDAV possibilities and limitations;
- existing ArtCraft host/embed mechanisms;
- ArtCraft upstream architecture;
- existing ArtCraft storage abstractions;
- other open-source editors that solve the same underlying need;
- projects already bridging web editors and storage systems.

Do not invent a bespoke protocol before establishing that an adequate standard or reusable mechanism does not exist.

---

# 8. CHALLENGE ARTCRAFT ITSELF

Perform a serious suitability audit of ArtCraft.

For each relevant Craft application determine:

- maturity;
- upstream activity;
- maintainability;
- file fidelity;
- native format vs standard format behavior;
- web build quality;
- save semantics;
- browser support;
- API/embed suitability;
- ability to serialize deterministically;
- dirty-state semantics;
- long-term maintenance risk;
- release discipline;
- licensing;
- likelihood that upstream would accept a generic host/storage integration.

Then ask:

> Is ArtCraft actually good enough to justify building an ecosystem integration around it?

Possible valid conclusions include:

### A. YES

ArtCraft is the right basis and the current project should continue.

### B. PARTIALLY

Only some ArtCraft applications are mature enough.

Maybe WordCraft/GridCraft/PdfCraft are viable while other applications should be abandoned.

### C. NOT YET

ArtCraft is promising but insufficiently mature; the project should become a smaller experimental compatibility layer rather than a production integration.

### D. NO

ArtCraft is the wrong foundation for the user's actual goal.

If D is the evidence-based conclusion, say it.

Do not protect the project emotionally.

---

# 9. CHALLENGE THE CURRENT GATEWAY

The project currently contains a gateway/integration layer.

Assume nothing.

Ask:

- Why does the gateway exist?
- Which problem does it solve?
- Could Seafile solve that problem itself?
- Could the editor solve it?
- Could an existing protocol solve it?
- Is the gateway introducing more attack surface than value?
- Is it becoming an application server?
- Does it own too much state?
- Does it duplicate capabilities already present in Seafile?
- Is it necessary for credentials to remain server-side?
- Could a stateless model work?
- Could short-lived URLs work?
- Could WOPI-style operations work?
- Could Seafile expose a generic storage host API instead?
- Could ArtCraft implement an existing host protocol?

The conclusion may be:

- keep it;
- simplify it;
- make it stateless;
- reduce it to a token broker;
- move logic into Seafile;
- move logic into Craft;
- replace it with an existing protocol;
- remove it.

All outcomes are acceptable if justified.

---

# 10. CHALLENGE THE SEAFILE PATCHES

Do not assume patching Seahub and fileserver is acceptable.

Evaluate:

- maintenance burden;
- compatibility burden;
- upgrade friction;
- security implications;
- upstream plausibility;
- C vs Go fileserver divergence;
- private API stability;
- operational cost;
- whether conditional writes can be implemented differently;
- whether the same guarantee can be obtained through public APIs;
- whether a plugin/module extension point exists;
- whether a generic upstream primitive would be better.

Ask:

> If this requires carrying permanent Seafile patches forever, is the design still worth it?

If not, redesign.

---

# 11. CHALLENGE THE HOST CONTRACT

The existing project developed a generic-ish Craft host protocol.

Do not assume it is the right abstraction.

Determine:

- what functionality is actually common;
- what semantics differ by editor;
- whether the common layer is real or forced;
- whether `postMessage` is appropriate;
- whether the parent/iframe model is appropriate;
- whether applications should consume a generic storage API;
- whether the correct abstraction is actually “document session”;
- whether WOPI or another established model already expresses the needed lifecycle.

Avoid both extremes:

- copy-pasted per-app hacks;
- premature universal abstraction.

Find the smallest correct abstraction.

---

# 12. CHALLENGE THE CURRENT APP SCOPE

Do not assume five active dispatcher routes are the correct target.

Do not assume thirteen ArtCraft applications should ever be supported.

Ask:

> Which applications provide enough user value and technical maturity to justify integration?

Perhaps the optimal initial product is:

```text
WordCraft only
```

or:

```text
WordCraft + GridCraft
```

or:

```text
WordCraft + GridCraft + PdfCraft
```

or something else.

Maybe VectorCraft should remain standalone.

Maybe PhotoCraft's native project format makes little sense inside Seafile.

Maybe supporting every Craft application would create enormous maintenance cost for little benefit.

Make the scope evidence-driven.

---

# 13. CHALLENGE THE PRODUCT FORM

ArtCraft Storage Lab itself may be the wrong product shape.

Consider seriously whether the best result should instead be:

- a Seafile plugin;
- a Seahub extension;
- a generic Seafile “external web editor” framework;
- an ArtCraft storage-provider layer;
- a shared open protocol;
- a tiny gateway;
- a library;
- a set of upstream ArtCraft patches;
- a set of upstream Seafile patches;
- a compatibility test suite only;
- a deployment bundle;
- a Docker/LXC service;
- several small independent integrations;
- no standalone project.

The current repository may ultimately become only:

```text
compatibility tests
integration fixtures
reference deployment
regression evidence
```

That is acceptable.

---

# 14. CHALLENGE THE DEPLOYMENT MODEL

Do not assume the current lab topology is appropriate for production.

Evaluate alternatives.

Consider:

- same-origin hosting;
- separate-origin gateway;
- reverse proxy routing;
- containerized gateway;
- sidecar;
- Seafile-local integration service;
- external service;
- static Craft bundles;
- dynamic upstream bundles;
- source-built bundles;
- immutable artifacts.

Assess:

- security;
- maintainability;
- failure modes;
- upgrades;
- observability;
- backup needs;
- tailnet/LAN/public exposure;
- complexity for a normal self-hoster.

The best architecture should not require the user to become its full-time operator.

---

# 15. CHALLENGE THE SECURITY MODEL

Do not merely look for vulnerabilities in the current architecture.

Ask whether the architecture itself makes the security problem unnecessarily difficult.

If an alternative design eliminates:

- capability leakage;
- custom token lifecycle;
- parent/iframe complexity;
- proxy origin complexity;
- custom authorization synchronization;
- fileserver patches;

that is strong evidence in favor of redesign.

Security simplicity is architectural value.

---

# 16. CHALLENGE THE SAVE MODEL

Re-evaluate the lifecycle from first principles.

Required property:

```text
A user-visible successful save must correspond to durable storage of the intended document generation.
```

Determine the best way to achieve:

- serialization identity;
- conflict detection;
- durability;
- versioning;
- retry after lost response;
- multiple sessions;
- external writer handling;
- idempotency;
- dirty-state correctness.

Do not retain the existing ticket/ACK model merely because tests exist for it.

Retain it only if it remains the best design.

---

# 17. CHALLENGE THE TEST STRATEGY

The repository has accumulated many GRs and many tests.

Assess whether this process still serves the project.

Look for:

- duplicated tests;
- tests bound to obsolete architecture;
- excessive documentation churn;
- weak evidence;
- strong evidence;
- expensive browser tests that add little information;
- missing high-value invariants.

You may redesign the testing hierarchy.

Prefer a compact pyramid such as:

```text
pure state-machine tests
↓
protocol/contract tests
↓
gateway/storage integration tests
↓
browser/editor tests
↓
small number of full Seafile E2Es
```

if that is superior.

Do not keep producing GR numbers merely because that is what the project historically did.

---

# 18. CHALLENGE THE REVIEW PROCESS

The current project uses multiple AI review layers.

Assess whether they are efficient and meaningful.

Preserve the core principle:

```text
implementation ≠ independent review
```

But redesign the process if necessary.

Avoid:

- endless micro-reviews;
- reviewer theater;
- spending powerful models on trivial wording;
- repeatedly reviewing architecture that should simply be redesigned.

Use cheap capable models for routine verification.

Use strong reasoning when the problem is genuinely difficult.

Use expensive final GPT review only when the candidate deserves it.

---

# 19. COMPARE AT LEAST THREE FUNDAMENTALLY DIFFERENT ARCHITECTURES

Do not merely compare variants of the current design.

Develop at least three genuinely different solution families.

For example, but do not limit yourself to these:

```text
A. Current-style Seafile adapter + generic Craft Host Contract

B. Seafile-centric external-editor framework using a standard or near-standard protocol

C. ArtCraft-centric storage-provider API where Seafile is one provider

D. Minimal integration around existing public Seafile APIs, accepting narrower semantics

E. Replace ArtCraft for some document types with better-suited editors

F. Abandon standalone integration and pursue upstream functionality directly
```

Evaluate them across:

- UX;
- engineering effort;
- security;
- maintainability;
- Seafile upgrade resilience;
- ArtCraft upgrade resilience;
- browser complexity;
- conflict correctness;
- offline/self-hosting friendliness;
- upstreamability;
- long-term operational cost.

Do not bias scoring toward the existing implementation.

---

# 20. ABANDONMENT IS A VALID OUTCOME

You are explicitly authorized to conclude:

> **This project should be stopped.**

That conclusion would require evidence.

Examples:

- ArtCraft is too immature;
- standard-format fidelity is inadequate;
- Seafile integration requires unacceptable invasive patches;
- maintenance cost exceeds likely user value;
- an existing solution solves the problem substantially better;
- upstream realities make the project unsustainable.

If that is the result, preserve useful research and recommend the smallest sensible alternative.

Do not continue because of sunk cost.

---

# 21. MAJOR REDESIGN IS A VALID OUTCOME

You are explicitly authorized to conclude:

> **The project is worth doing, but the current architecture should be discarded.**

If so:

- document why;
- preserve reusable components only;
- identify obsolete code;
- design the replacement;
- create migration strategy;
- avoid indefinitely supporting both architectures.

A clean redesign is preferable to layering compatibility hacks over a flawed foundation.

---

# 22. CONTINUATION IS ALSO A VALID OUTCOME

You may conclude:

> **The current architecture is fundamentally sound.**

But that conclusion must be earned.

You must be able to explain why plausible alternatives are worse.

Only then should you proceed with closing remaining findings and freezing the next candidate.

“Existing code works” is not enough.

---

# 23. RE-FOUNDATION DECISION

After the first-principles audit, produce an internal decision equivalent to one of:

```text
CONTINUE
CONTINUE_BUT_SIMPLIFY
MAJOR_REDESIGN
CHANGE_PRODUCT_FORM
CHANGE_TECHNOLOGY
REDUCE_SCOPE
PAUSE_UNTIL_UPSTREAM_MATURITY
ABANDON
```

Do not choose a label first and justify it afterward.

Derive it.

---

# 24. ONLY AFTER THE DECISION: EXECUTE

Once the project direction has been independently re-established, execute it.

If `CONTINUE`:

- close only genuinely material gaps;
- stop feature expansion;
- freeze candidate;
- review candidate.

If `CONTINUE_BUT_SIMPLIFY`:

- remove unnecessary machinery;
- reduce scope;
- prove simplified architecture.

If `MAJOR_REDESIGN`:

- design from invariants;
- implement smallest vertical slice;
- compare against current system;
- migrate only if superior.

If `CHANGE_PRODUCT_FORM`:

- reorganize repository and ownership boundaries accordingly.

If `PAUSE_UNTIL_UPSTREAM_MATURITY`:

- define what external conditions would justify resuming.

If `ABANDON`:

- preserve findings;
- identify reusable work;
- document better alternative;
- stop engineering.

---

# 25. DO NOT LET HISTORICAL GPT REVIEWS FRAME THE NEW ANALYSIS

Previous GPT/Sol reviews are useful evidence about the old/current architecture.

They do not define the problem.

Do not start with:

> “How do I close Sol's findings?”

Start with:

> “Is this architecture worth bringing to Sol again?”

If the answer is no, redesign first.

A perfectly remediated bad architecture is still a bad architecture.

---

# 26. CURRENT HISTORICAL STATE — CONTEXT ONLY

At the time this mandate was written, the last known remote `main` was:

`70fa192ed5d414daf28087315f0f77f8312e98b5`

Historical project state included:

- many synthetic Seafile E2Es;
- WordCraft;
- GridCraft;
- PdfCraft;
- VectorCraft;
- PhotoCraft;
- several additional Craft application prototypes/E2Es;
- a gateway;
- conditional-save work;
- idempotent retry work;
- CSP/security hardening;
- artifact pinning;
- significant browser evidence;
- significant documentation;
- historical project-level GPT FAIL/INCOMPLETE verdicts;
- unresolved uncertainty around current ONLYOFFICE behavior.

Do not assume any of this remains current.

Verify it.

More importantly:

**do not assume this work proves the architecture should survive.**

---

# 27. PRODUCTION SAFETY

Even during total reassessment:

**production remains off limits without explicit owner approval.**

Do not modify:

- production Seafile;
- production Seahub;
- production fileserver;
- production ONLYOFFICE;
- production reverse proxy;
- production Tailscale routing;
- production data.

Use safe isolated environments.

---

# 28. UPSTREAM LOCK

No upstream action before the formal gate.

This includes:

- issue;
- RFC;
- PR;
- discussion;
- patch submission;
- release;
- public proposal.

Even if you conclude that upstream is the correct final architecture:

prepare the proposal locally.

Do not publish it.

After a project-level GPT PASS, explicit owner approval is still required.

---

# 29. MODEL / REVIEW AUTONOMY

You may choose different models/reasoning levels for different tasks.

Optimize cost.

Use lightweight capable models for:

- repository inventory;
- mechanical code analysis;
- deterministic tests;
- documentation reconciliation.

Use stronger reasoning for:

- architecture;
- protocol semantics;
- concurrency;
- security;
- re-foundation decisions.

Use independent reviewer contexts for important decisions.

Do not use the same context to design and “independently approve” its own work.

Do not burn final high-end GPT reviews during exploratory redesign.

---

# 30. THE FIRST HIGH-VALUE OUTPUT IS NOT A ROADMAP

Your first major result should be a **Re-Foundation Report**.

It should answer:

```text
WHAT PROBLEM ARE WE ACTUALLY SOLVING?

DOES THAT PROBLEM JUSTIFY A CUSTOM PROJECT?

IS ARTCRAFT THE RIGHT EDITOR ECOSYSTEM?

IS SEAFILE THE RIGHT INTEGRATION POINT?

IS THE CURRENT GATEWAY JUSTIFIED?

ARE THE SEAFILE PATCHES ACCEPTABLE?

IS THE CURRENT HOST CONTRACT THE RIGHT ABSTRACTION?

WHAT EXISTING STANDARDS OR PROJECTS COULD REPLACE CUSTOM WORK?

WHAT IS THE MINIMUM USEFUL PRODUCT?

WHICH EXISTING COMPONENTS ARE VALUABLE?

WHICH EXISTING COMPONENTS ARE SUNK COST?

WHICH ARCHITECTURE WOULD WE CHOOSE FROM ZERO TODAY?

SHOULD THE PROJECT CONTINUE, SIMPLIFY, REDESIGN, CHANGE FORM, PAUSE, OR DIE?
```

Do not optimize for preserving feelings or past work.

Optimize for the best technical outcome.

---

# 31. DECISION QUALITY STANDARD

For every major conclusion, distinguish:

```text
FACT
EVIDENCE
ASSUMPTION
INFERENCE
DECISION
```

If you do not know, investigate.

If investigation is impossible, label uncertainty.

Do not hide uncertainty behind confident prose.

---

# 32. OWNER COMMUNICATION

Do not dump internal chain-of-thought.

Report decisions and evidence.

A useful status format is:

```text
REFOUNDATION_STATE=

CURRENT_REALITY=

ASSUMPTIONS_INVALIDATED=

ARCHITECTURE_OPTIONS_CONSIDERED=

CURRENT_LEADING_ARCHITECTURE=

WHY=

COMPONENTS_TO_KEEP=

COMPONENTS_TO_REMOVE=

MAJOR_UNCERTAINTIES=

NEXT_EXECUTABLE_STEP=

PRODUCTION_STATUS=UNTOUCHED
UPSTREAM_STATUS=LOCKED
```

---

# 33. STOP CONDITIONS

Do not stop because the audit is large.

Do not stop because you found problems.

Do not stop after merely producing recommendations if you can safely validate the better design.

Continue from analysis into evidence.

Stop only for:

- genuine technical blocker;
- owner-only credential/action;
- production authorization;
- upstream authorization;
- destructive decision requiring owner consent;
- legal/business decision;
- unavailable required final reviewer;
- hard resource/tool limitation;
- project-level gate reached.

---

# 34. FINAL PROJECT GATE — ONLY AFTER RE-FOUNDATION

If, after first-principles reassessment, a concrete implementation remains justified, then create a final candidate.

Before expensive final review:

```text
architecture justified
scope justified
candidate frozen
worktree clean
exact SHA known
tests reproducible
runtime evidence strong
security model understood
distribution model understood
documentation coherent
independent bounded review clean
```

Then perform the established strong-review sequence.

A forensic reviewer first.

A fresh independent final GPT/Sol gate second.

Do not seek a PASS for an architecture you no longer believe in.

---

# 35. THE CORE MANDATE

Your job is not:

> **finish ArtCraft Storage Lab**

Your job is:

> **solve the user's underlying problem in the best technically defensible way, using the existing ArtCraft Storage Lab work as evidence rather than dogma.**

You are explicitly authorized to:

- question everything;
- delete assumptions;
- challenge architecture;
- change scope;
- change technologies;
- replace custom systems with existing standards;
- reduce the project dramatically;
- move functionality between components;
- abandon applications;
- abandon the current gateway;
- abandon the current Host Contract;
- abandon Seafile patches;
- abandon the standalone project;
- or validate the current approach and continue it.

There is only one unacceptable outcome:

> **continuing the existing project merely because it already exists.**

---

# 36. START NOW

Begin with repository and ecosystem reconnaissance.

Do not begin by implementing GR-081.

Do not begin by fixing the latest TODO.

Do not begin by trying to obtain a GPT PASS.

First determine whether the project we would be trying to pass is actually the project that should exist.

The first question is:

> **“If none of this code existed today, knowing everything we have learned so far, what would we build?”**

Answer that through evidence.

Then act on the answer.
