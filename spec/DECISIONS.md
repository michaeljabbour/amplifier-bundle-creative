# DECISIONS

Rolling log of resolved design decisions for the Amplifier Creative Agent system.
Newest at top (within each date). Each entry records what was chosen, why, and who signed off.

The spec at [`SPEC.md`](./SPEC.md) is frozen at v0.1 — decisions here supersede anything in
SPEC.md they conflict with. Only cut a new spec version when the conceptual frame itself
changes; every other refinement lives here.

**Format conventions:**
- Decisions are numbered monotonically (D001, D002, …). Numbers are never reused.
- Each decision has a status: `resolved`, `open`, `deferred`, `revisited`.
- Spec-section cross-references point to sections of `SPEC.md` affected by the decision.
- Dates are ISO-8601 (UTC).

---

## Index

| # | Title | Status |
|---|-------|--------|
| D001 | Surface taxonomy → Tool protocol | resolved |
| D002 | Repo topology → 2 MCPs + 1 bundle, Critic in bundle | resolved |
| D003 | Async video generation → job_id + Hook events | **superseded by D018** |
| D004 | Critic implementation → agent delegation for v0.1 | resolved |
| D005 | Relationship to amplifier-bundle-imagen → compose, don't deprecate | resolved |
| D006 | Coordination file storage → per-project folder | resolved |
| D007 | Cost accounting → response.usage + fallback price table | resolved |
| D008 | Style Bible format → Markdown + YAML frontmatter + Pydantic loader | resolved |
| D009 | Drift scoring → calibrate in 2c, binary fallback documented | resolved |
| D010 | Sora 2 provider → stub in 2a, skip implementation | resolved |
| D011 | Hooks as the async event mechanism (formalized) | **superseded by D018** |
| D012 | Coordination files as a Context module (not raw filesystem) | resolved |
| D013 | Operator overrides Critic on taste; Critic authoritative on hard rules | resolved |
| D014 | Style Bible versioning → append-only | resolved |
| D015 | Provider adapter → conform to Amplifier Provider protocol | **superseded by D021** |
| D016 | v0.1 scope locked → five-item 2a list | resolved |
| D017 | Privacy / terms / ownership review required before provider integration | **resolved (see D019)** |
| D018 | Async pattern corrected — `task` tool + polling MCP tool (supersedes D003, D011) | resolved |
| D019 | D017 resolved — provider privacy audit complete, scorecard captured | resolved |
| D020 | Phase 2a provider scope updated — drop BFL and Ideogram (supersedes D016 provider list) | resolved |
| D021 | Provider adapter is MCP-internal, not an Amplifier Provider primitive (supersedes D015) | resolved |
| D022 | ElevenLabs — audio-only approval (v0.2); aggregator is NOT a privacy proxy for image/video | resolved |
| D023 | BFL and Ideogram permanently removed (strengthens D020) | resolved |
| D024 | User-facing warnings at config time — Google (billing) + xAI (de-id data clause) | resolved (impl deferred to 2b) |
| D025 | File storage policy — user Downloads folder only; no app-controlled dirs or caches (extends D006) | resolved |
| D026 | Recraft permanently removed (strengthens D019; same principle as D023) | resolved |
| D027 | xAI Grok Imagine ungated to active integration (CONDITIONAL with D024 warning) | resolved |
| D028 | Reference-image-first generation policy for existing-IP work (supersedes text-only prompts) | resolved |
| D029 | Reference-page selection must match SETTING as well as character (refines D028) | resolved |
| D030 | Reference-image downsizing policy for efficient API calls (operational, MCP-internal) | resolved |
| D031 | OpenAI TTS added to v0.1 audio stack; AudioGeneration expanded (refines D022) | resolved |
| D032 | Ken-Burns still-frame fallback when Veo quota is exhausted (production resilience) | resolved |
| D033 | Per-tier Veo duration constraints are API-enforced — validate at shot-spec time | resolved |
| D034 | VO mixing pattern — use concat filter, never amix+apad or single-pass loudnorm | resolved |
| D035 | Text overlays in existing-IP animations show literal page text, not narration anchors | resolved |
| D036 | Audio QA must sample amplitude at anchors, not just confirm stream existence | resolved |
| D037 | Font identification needs multi-sample vision + handwriting-vs-serif prompting | resolved |
| D038 | Music is an intake question; music duration drives the edit, visuals fit music | resolved |
| D039 | Project directory structure follows film-production layout (enforced by bundle toolkit) | resolved |
| D040 | Operator-provided audio track supersedes synthesized narration (no TTS layered on baked-in narration) | resolved |
| D041 | Multi-modal operator reference intake is mandatory before any production (vision + Whisper of mockups, decks, storyboards) | resolved |
| D042 | Text overlays timed to narration segments, not shot cuts (Whisper segment timestamps drive enable ranges) | resolved |
| D043 | Held-frame extensions must carry Ken-Burns motion, not static holds (perceived as transition gaps) | resolved |
| D044 | Asset intake protocol added to project-intake checklist as first-class step (refines D041) | resolved |

---

## 2026-04-21 — Initial decisions from Phase 2 planning

### D001. Surface taxonomy → Tool protocol

- **Status:** resolved
- **Spec section:** §2 Glossary ("Surface" definition); §3.3 Surface primitives
- **Resolution:** Drop the "Surface" term from the Creative Agent vocabulary. What the spec calls a "Surface" is a Tool-protocol contract under Amplifier's existing five-module taxonomy (Provider, Tool, Orchestrator, Context, Hook). No new kernel primitive is introduced. Next spec revision will rename to "Tool protocol" or "CapabilityContract". `foundation:foundation-expert` validates the mapping before code is written.
- **Rationale:** The "Surface" term imported a concept that doesn't exist in Amplifier's vocabulary. Aligning terminology prevents drift from kernel primitives; a redundant abstraction would be cost without benefit.
- **Decided by:** Operator, confirming planner recommendation.

### D002. Repo topology → two MCPs + one bundle, Critic in bundle

- **Status:** resolved
- **Spec section:** §3.3 (three Surfaces)
- **Resolution:** v0.1 ships two MCP servers — `imagen-mcp` (extended with new image providers) and a new `video-mcp` — plus one bundle, `amplifier-bundle-creative`, that composes both. The CreativeCritique "Surface" is not a third MCP; it lives inside the bundle as delegated vision-LLM calls (see D004). A dedicated `critique-mcp` is deferred until cost pressure justifies it — likely not before Phase 2d.
- **Rationale:** Matches the bricks-and-studs philosophy. Critique cost per trailer is under $1; MCP overhead is not warranted for v0.1. Keeping the MCP surface area small reduces deployment complexity.
- **Decided by:** Operator, modifying the planner's three-MCP option.

### D003. Async video generation → job_id + Hook events

- **Status:** resolved
- **Spec section:** §3.3 VideoGeneration; §5 (example flow — sync-looking text superseded by this decision)
- **Resolution:** Every video-generation MCP tool returns immediately with a `job_id` when the request is accepted. Progress and completion are broadcast via Amplifier Hook module events (`video.generation.started`, `video.generation.progress`, `video.generation.completed`, `video.generation.failed`). The bundle subscribes via its own Hook implementations; the conductor agent reacts to events. The orchestrator never polls the MCP directly, and the MCP call never blocks the caller for the full generation duration.
- **Rationale:** Veo, Sora, and Grok Imagine all take 30–120s per clip. Blocking MCP calls would hit tool-call timeouts and waste orchestrator context on waiting. Hooks are Amplifier's kernel primitive for lifecycle events and fit this use case exactly.
- **Decided by:** Operator, correcting the spec's sync-looking §5 flow. `foundation:foundation-expert` validates the Hook contract shape before video-mcp implementation begins.

### D004. Critic implementation → agent delegation for v0.1

- **Status:** resolved
- **Spec section:** §3.3 CreativeCritique
- **Resolution:** v0.1 Critic is a delegated agent with access to vision-capable LLMs (Claude Opus 4.7 primary; GPT-5.4 and Gemini 3.1 Pro for triangulation) via Amplifier's routing matrix. No new MCP tool for critique in v0.1. Critic is promoted to `critique-mcp` only when volume pressure justifies it.
- **Cost math:** ~$0.02 per single-judge critique, ~$0.06 triangulated. A 60-second trailer at 8 shots averages ~16 critique calls. Total critique spend per trailer stays under $1. Optimization is not warranted at current volume.
- **Rationale:** Agent delegation is the cheapest/simplest existing Amplifier primitive for this job. Cost is trivial at current volume. The option to promote to an MCP tool remains open when ROI justifies it.
- **Decided by:** Planner recommendation accepted by operator.

### D005. Relationship to amplifier-bundle-imagen → compose, don't deprecate

- **Status:** resolved
- **Spec section:** (none — pertains to existing shipped bundle)
- **Resolution:** `amplifier-bundle-creative` composes `amplifier-bundle-imagen` as a sub-behavior. The Visual Director role in SPEC §3.1 is satisfied by reusing the imagen bundle's existing agents (`image-director`, `image-prompt-engineer`, `image-editor`, `image-researcher`). The creative bundle adds: Motion Director (new), delegated Critic (new), Brief Interpreter (new), Shot Planner (new), Style Bible Keeper (new), Finisher (new), coordination-file behaviors (new), and the end-to-end orchestration skill (new).
- **Rationale:** Phase 1 (`amplifier-bundle-imagen` v1.1.0) is validated and shipping. Throwing it away costs effort without gain. Composition aligns with the Amplifier bundle philosophy.
- **Decided by:** Operator, accepting planner recommendation.

### D006. Coordination file storage → per-project folder

- **Status:** resolved
- **Spec section:** §3.2 (coordination files)
- **Resolution:** All coordination files (PROJECT_CONTEXT.md, STYLE_BIBLE.md, SHOT_LIST.md, etc.) live under `~/amplifier/projects/{project_name}/`. Sessions within a given project share these files. A new session on an existing project reads the existing files as warm state. Session-scoped storage is rejected explicitly — it would lose the cross-session continuity the whole design depends on. Project-context template conventions from `the project-context template` map cleanly onto this storage layout.
- **Rationale:** Humans think in projects, not sessions. A trailer is a project that spans weeks and many sessions. Continuity is a first-class concern, not an add-on.
- **Decided by:** Operator, sharpening planner recommendation.

### D007. Cost accounting → response.usage + fallback price table

- **Status:** resolved
- **Spec section:** §4.3 (budget behaviors); §6 (PROVENANCE)
- **Resolution:** Each provider adapter attempts to read `response.usage` from the provider response for actual token/cost data (OpenAI gpt-image-2 returns this; newer Gemini models are beginning to). When `response.usage` is absent or incomplete, the adapter falls back to a hardcoded price table. The price table lives in `amplifier-bundle-creative` (NOT in the MCPs) so pricing updates ship without cutting new MCP releases.
- **Rationale:** Prices change often; decoupling pricing from the MCP release cycle keeps the update path simple. The bundle is the orchestration layer and owns economics.
- **Decided by:** Operator, accepting planner recommendation.

### D008. Style Bible format → Markdown + YAML frontmatter + Pydantic loader

- **Status:** resolved
- **Spec section:** §3.2 Tier 1 files; §A.1 template
- **Resolution:** `STYLE_BIBLE.md` is a human-edited Markdown document with a YAML frontmatter block for structured fields (characters, palette, forbidden_colors, tone rules, etc.). A Pydantic-based loader in the bundle parses it into a typed model. Schema validation runs on load — a malformed Style Bible fails fast with an explicit error rather than silently degrading downstream generations.
- **Rationale:** Humans edit the file; agents consume the typed model. Fast-fail on schema errors prevents mysterious downstream failures. YAML frontmatter keeps the Markdown readable while allowing structured access.
- **Decided by:** Operator, accepting planner recommendation.

### D009. Drift scoring → calibrate in 2c, binary fallback documented

- **Status:** resolved
- **Spec section:** §4.2 (continuity behaviors); §2 Glossary ("Drift vector")
- **Resolution:** Budget an explicit half-day experiment in Phase 2c: select 20 generations spanning obvious-pass, obvious-fail, and borderline; score each manually against the Style Bible; prompt-engineer the Critic until it reproduces the manual scores within ±0.05 on repeat runs. If the Critic cannot be stabilized to that tolerance, the drift-threshold architecture in SPEC §4.2 falls back to binary accept/reject with operator tiebreak. A documented fallback design is a gate for shipping Phase 2c.
- **Rationale:** Drift scoring is the riskiest unvalidated assumption in the spec. The original framing ("calibrate in 2c") was too casual. Explicit methodology plus an explicit fallback prevents architectural collapse mid-production.
- **Decided by:** Operator, sharpening planner recommendation.

### D010. Sora 2 provider → stub only, skip implementation

- **Status:** resolved
- **Spec section:** §3.3 VideoGeneration providers; §4.1 routing
- **Resolution:** Sora 2 appears in `video-mcp` as a stubbed provider that returns a structured "not implemented, substitute Veo 3.1 Standard" error when invoked. This allows the routing logic (including `physics-required` tag handling) to be tested end-to-end without Sora API code. Real Sora 2 implementation is deferred indefinitely — the API shuts down 2026-09-24 (five months out). Implementation is triggered only by an active, specific need for physics between now and then.
- **Rationale:** Building a provider against an API with a five-month lifespan is negative engineering value. Veo 3.1's physics is acceptable for pilot-project work. Sora 3 (anticipated) will get its own decision when the API shape is known.
- **Decided by:** Operator, strengthening planner recommendation (planner said "add in 2e"; operator said "stub only, don't implement absent active need").

### D011. Hooks as the async event mechanism (formalized)

- **Status:** resolved
- **Spec section:** §3.2 (coordination files — event log emerges here); §4 (all async behaviors)
- **Resolution:** Amplifier's Hook module type is the formal mechanism for all async video-generation lifecycle events. Canonical event names: `video.generation.started`, `video.generation.progress`, `video.generation.completed`, `video.generation.failed`. The bundle installs its own Hook implementations that subscribe to these events and update coordination state. The conductor agent reacts to state changes (via Context module notifications — see D012), not to the raw events. MCP-side polling is explicitly rejected; filesystem polling is explicitly rejected. `foundation:foundation-expert` validates the exact Hook contract before implementation.
- **Rationale:** Hooks are the kernel primitive for lifecycle events. Using them avoids inventing a parallel event bus. Mapping MCP async operations onto Hooks is the natural Amplifier integration path.
- **Decided by:** Operator, flagged as missing from planner's original review.

### D012. Coordination files as a Context module (not raw filesystem)

- **Status:** resolved
- **Spec section:** §3.2 (all coordination files)
- **Resolution:** Coordination files are backed by an Amplifier Context module implementation with a typed API for read/append/update. Agents (Critic, Style Bible Keeper, Brief Interpreter, …) access coordination state through the Context module — not by parsing Markdown at every call. The Markdown files remain the canonical on-disk format for human editing; the Context module is the read/write surface for code. Schema validation happens at write time via the module's typed API.
- **Rationale:** Context is Amplifier's kernel primitive for memory management. Using it provides: (a) programmatic access without repeated Markdown parsing, (b) schema validation at write time, (c) change-detection hooks that enable continuity behaviors, (d) a natural integration point for cross-session persistence.
- **Decided by:** Operator, flagged as missing from planner's original review.

### D013. Operator overrides Critic on taste; Critic authoritative on hard rules

- **Status:** resolved
- **Spec section:** §4.4 (human-in-loop); §8 (CLAIMS_TRACKER)
- **Resolution:** When the Critic rejects a generation but the operator accepts it, the operator override wins. The override appends an entry to `CRITIC_JOURNAL.md` flagging the disagreement and capturing the operator's rationale. The Critic is advisory on taste and aesthetics; it is authoritative on hard rules: (1) reference images present for character-critical shots, (2) SynthID watermark attached where required, (3) budget ceiling not exceeded, (4) child likeness generated only from approved reference assets. Hard-rule violations are non-overridable; they halt the session and require operator action to resolve.
- **Rationale:** Creative judgment belongs to humans. Compliance and safety are enforced structurally, not by convention. This split keeps the Critic useful without letting it block creative work.
- **Decided by:** Operator, flagged as missing from planner's original review.

### D014. Style Bible versioning → append-only

- **Status:** resolved
- **Spec section:** §4.2 (ripple updates); §6 PROVENANCE; §11 Open Question #3
- **Resolution:** Style Bible edits append new versions rather than mutating in place. Every generation's provenance record carries a `style_token` pointing at the Style Bible version active at generation time. Prior generations' `style_token` values remain valid indefinitely, even after subsequent Style Bible updates. Concurrent edits from multiple sessions are resolved by serializing writes through the Context module; conflicts are impossible because every edit produces a new version.
- **Rationale:** Provenance clarity wins over iteration speed. Concurrency safety falls out of the append-only discipline for free. Aligns with SPEC §6's append-only PROVENANCE rule.
- **Decided by:** Operator, flagged as missing from planner's original review. Resolves SPEC §11 Open Question #3 definitively.

### D015. Provider adapter → conform to Amplifier Provider protocol

- **Status:** resolved (pending foundation-expert validation)
- **Spec section:** Appendix B (provider adapter interface)
- **Resolution:** The generic `ProviderAdapter` interface sketched in SPEC Appendix B is rewritten to conform to Amplifier's existing Provider module protocol — same method signatures, same error types, same health-check semantics. Adding a new image or video provider becomes an Amplifier Provider module implementation, not a bespoke adapter class. `foundation:foundation-expert` validates the exact protocol mapping before any code ships.
- **Rationale:** Don't invent a parallel abstraction over an existing kernel primitive. Reusing the Provider protocol means new providers integrate with Amplifier's existing provider lifecycle, health checks, and error handling for free.
- **Decided by:** Operator, flagged as missing from planner's original review.

### D016. v0.1 scope locked → five-item 2a list

- **Status:** resolved
- **Spec section:** §10 Roadmap
- **Resolution:** Phase 2a scope is:
    1. Extend `imagen-mcp` with additional image providers: Nano Banana Pro (already shipped), Images 2.0 family, Ideogram V3, Recraft V4, Flux 2 Pro, Flux Kontext.
    2. Build new `video-mcp` with async-job pattern and Hook integration (per D003, D011). First tranche of providers: Veo 3.1 Lite, Fast, Standard. Second tranche: Grok Imagine Video. Sora 2 stubbed only (per D010).
    3. Create `amplifier-bundle-creative` composing both MCPs, with Visual Director (reused from imagen bundle), Motion Director (new), and delegated Critic (per D004).
    4. Implement coordination files as a Context module (per D012), not raw filesystem.
    5. Run the drift scoring calibration experiment during Phase 2c (per D009), with the binary accept/reject fallback documented as the safety net.

    Phases 2b through 2e handle everything else in SPEC §10. The MVP forcing function is shipping the pilot project 60-second book trailer end-to-end at the close of Phase 2c.
- **Rationale:** Concrete, bounded, and each item independently valuable. Lets the pilot project deliverable drive the framework rather than the framework driving the deliverable.
- **Decided by:** Operator.

### D017. Privacy / terms / ownership review required before provider integration

- **Status:** **open** — research task to be dispatched before Phase 2a coding begins
- **Spec section:** §3.3 (provider lists); §6 PROVENANCE
- **Resolution (provisional — pending research):** Before any provider is integrated into `video-mcp` or the extended `imagen-mcp`, validate the provider's terms of service and privacy policy against three criteria:
    1. **Training-data opt-out.** Can the user's prompts and outputs be excluded from future model training? Default on by default if available; otherwise documented as a constraint.
    2. **Content ownership.** Does the user retain full, unencumbered ownership of generated outputs? No shared rights, no derivative claims, no "provider may use outputs in marketing" clauses.
    3. **Data retention.** How long are prompts and outputs retained on the provider's infrastructure? Is there an operator-controllable deletion path?

    Providers failing any of the three criteria are flagged in this decision log and handled as one of:
    - (a) skip entirely,
    - (b) gate behind an explicit operator warning at every call,
    - (c) deprioritize relative to providers that pass cleanly.

    Providers to audit for Phase 2a:
    - OpenAI (image + video)
    - Google (Gemini + Vertex AI)
    - xAI (Grok Imagine)
    - Anthropic (Claude Opus vision critic)
    - Black Forest Labs (Flux)
    - Recraft
    - Ideogram

    Privacy review sits on the critical path for 2a. No provider code ships until the matrix is filled.
- **Rationale:** Creative deliverables for the pilot project and other client work involve IP that must remain the operator's property. Privacy review is a structural gate, not a procedural checklist. Raised explicitly at the design-v0.1 checkpoint as a concern that was missing from the planner's review.
- **Decided by:** Operator.

---

### D021. Provider adapter is MCP-internal, not an Amplifier kernel primitive (supersedes D015)

- **Status:** resolved
- **Supersedes:** D015 (adapter conforms to Amplifier Provider protocol)
- **Spec section:** Appendix B (provider adapter interface)
- **The error we're correcting:** D015 said "adding a new image or video provider becomes an Amplifier Provider module implementation." This is wrong. Amplifier's `Provider` primitive is exclusively for LLM text completion — the contract is `complete(ChatRequest) -> ChatResponse`, with fields like `context_window`, `max_output_tokens`, conversation history, and tool schemas. None of those concepts exist for image or video generation. Image/video producers take a prompt string and emit bytes (or a job_id); they are a fundamentally different shape.

- **Correct model:**
    - **Amplifier-facing boundary:** the MCP Tool. `imagen-mcp.generate_image`, `video-mcp.generate_video`, and `video-mcp.get_job_status` are kernel `Tool` primitives. That is the single integration point with Amplifier.
    - **MCP-internal dispatch:** plain Python ABCs, scoped to the MCP server process. No kernel involvement; no Provider protocol conformance.
    - For images, `imagen-mcp/src/providers/base.py` already defines the correct shape: `ImageProvider` ABC + `ProviderCapabilities` dataclass + `ImageResult` dataclass (the latter with `usage_tokens`, `enhanced_prompt`, etc. — already correct per D007).
    - For video, `video-mcp` gets a parallel `VideoProvider` ABC shaped for D018's async pattern. Reference shape (Python stubs use triple-quoted docstrings; reproduced verbatim here for implementers):

```
class VideoProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def capabilities(self) -> VideoCapabilities: ...

    @abstractmethod
    async def submit(
        self,
        prompt: str,
        *,
        first_frame: str | None = None,      # base64 PNG
        duration: float | None = None,
        aspect_ratio: str | None = None,
        **kwargs: Any,
    ) -> VideoJobResult:
        # Submit a generation job. Returns immediately with job_id.
        ...

    @abstractmethod
    async def get_status(self, job_id: str) -> VideoJobResult:
        # Polled by the D018 task-tool sub-agent.
        ...

    async def close(self) -> None: ...

    def to_provenance_record(self, result: VideoJobResult) -> dict[str, Any]: ...


@dataclass
class VideoCapabilities:
    name: str
    display_name: str
    supported_durations: list[float]
    supported_resolutions: list[str]
    supports_first_frame: bool
    supports_last_frame: bool
    max_duration_seconds: float
    typical_latency_seconds: float
    cost_tier: str
    best_for: list[str] = field(default_factory=list)


@dataclass
class VideoJobResult:
    job_id: str
    provider: str
    model: str
    status: str                              # submitted | pending | complete | failed
    progress: float | None = None
    output_url: str | None = None
    last_frame_url: str | None = None
    usage: dict[str, Any] | None = None
    error_code: str | None = None
    retry_hint: str | None = None
    prompt: str = ""
    duration_seconds: float | None = None
```

- **`surface` field dropped** from SPEC Appendix B's generic adapter. Separate ABCs (`ImageProvider`, `VideoProvider`) do the type discrimination. Critique is a delegated agent (D004), not a provider.

- **`cost_per_unit` and `estimate_latency` callables dropped.** Cost uses D007's pattern: read `response.usage` from the provider when available, fall back to a bundle-side price table. Latency is a static field on the capabilities dataclass (`typical_latency_seconds`), not a callable.

- **Error types are MCP-internal**, not `amplifier_core.llm_errors`. Mirror `imagen-mcp/src/exceptions.py` for `video-mcp`: `VideoError` base + `ConfigurationError`, `ProviderError`, `AuthenticationError`, `RateLimitError`, `GenerationError`, `JobNotFoundError`, `ValidationError`. These bubble up through the MCP Tool boundary as structured `ToolResult(success=False, output={...})` payloads, not as kernel LLM errors.

- **Routing clarification** (two distinct mechanisms, do not conflate):
    - **LLM provider selection** (Anthropic for reasoning, OpenAI for fast, etc.) is resolved by the routing matrix against `model_role` declarations on agent spawns. In-process, coordinator-level.
    - **Image/video backend selection** (gpt-image-2 vs Nano Banana, Veo vs Grok) is NOT routed by the kernel. Agents call the MCP tool with an optional `provider=` parameter. The MCP's internal `ProviderRegistry` + `selector.py` dispatches to the right `ImageProvider` or `VideoProvider`. Agents never see individual provider instances — they see one Tool.

- **Rationale:** Amplifier's Provider primitive models a specific conversational shape (messages, context window, tool schemas, streamed text/tool-call output). Image and video generation are a different shape — prompt in, bytes (or a job_id) out. Forcing media generation into the Provider protocol would require faking `ChatRequest`/`ChatResponse` around byte payloads and misusing capability flags. MCP-internal ABCs keep concerns where they belong — scoped to the MCP process where implementation detail stays invisible to the kernel.

- **Impact on Phase 2a code:** video-mcp coding can start immediately against the VideoProvider ABC above. imagen-mcp is unchanged — its existing `ImageProvider` ABC is already the right shape.

- **Decided by:** Operator, accepting foundation-expert's source-grounded correction (cross-referenced against canonical providers `amplifier-module-provider-openai` and `amplifier-module-provider-anthropic`).

---

## 2026-04-21 — Third-pass decisions (privacy deep-dive + storage policy)

Operator commissioned an independent privacy comparison covering all seven providers plus ElevenLabs as a potential aggregator. Full research landed at `docs/api-privacy-comparison.md`. These four decisions lock in the operational consequences.

### D022. ElevenLabs — audio-only approval; aggregator path rejected for image/video

- **Status:** resolved
- **Spec section:** §3.3 (creates future AudioGeneration surface at v0.2); §10 Roadmap
- **Research:** `docs/api-privacy-comparison.md`
- **Context:** ElevenLabs offers Flux 2 Pro, Flux Kontext, Nano Banana, GPT Image 1/1.5, Sora 2, Veo 3/3.1, Kling 2.5/3.0, and others through a single API. It looked like a possible privacy bypass for BFL.
- **Resolution (image / video):** ElevenLabs is **not** approved as an image or video aggregator. Their own Image & Video Terms explicitly route data to the underlying third-party provider: "you may interact with and direct information to these Third-Party Providers and that you must comply with any and all applicable Third-Party Provider terms." Underlying terms still apply — using Flux via ElevenLabs still hits BFL's abusive training license. Worse, ElevenLabs stacks **its own** terms on top: a worldwide royalty-free sublicensable license over any publicly shared output (opt-out only via account settings, prior sublicenses survive); training defaults ON for non-Enterprise tiers. Net effect: routing already-cleared providers (OpenAI, Google, Anthropic) through ElevenLabs actively degrades their data posture.
- **Resolution (audio):** ElevenLabs **is** approved for audio generation — voice narration, sound effects, and music — on the **Enterprise tier with training opted out**. Enterprise tier contractually excludes training-data use and honors the publish-privacy toggle. This fills the audio gap in the Creative Agent stack; no other provider in the current roster generates audio.
- **Scoping:** audio integration lives in the v0.2 `AudioGeneration` surface (SPEC §10). NOT in v0.1. When v0.2 begins, ElevenLabs Enterprise + training-opt-out is the default audio provider.
- **Rationale:** aggregator convenience does not override downstream provider terms. The only clean ElevenLabs use case is audio, where they are first-party.
- **Decided by:** Operator, based on the independent privacy comparison research.

### D023. Black Forest Labs and Ideogram permanently removed (strengthens D020)

- **Status:** resolved
- **Strengthens:** D020 (which dropped both from v0.1 scope but left open "reconsider if terms change")
- **Spec section:** §3.3 provider lists
- **Resolution:** BFL (Flux 2 Pro, Flux Kontext) and Ideogram (V3) are **permanently removed** from the Amplifier Creative Agent provider roster. Not stubbed. Not gated. Not deferred. Removed.
  - **BFL** grants itself a "fully paid, royalty-free, perpetual, irrevocable, worldwide, non-exclusive and fully sublicensable" license over all inputs and outputs, with no opt-out and an explicit carve-out that these rights include training their AI models. This is structurally incompatible with user sovereignty.
  - **Ideogram's** own legal documents contradict each other — the API ToS says the service "shall not use any User Input or User Output to train the Ideogram AI Model" while a separate clause claims "the right to use in any manner all User data received via the API." Self-contradictory terms create unlimited interpretation risk and are not a basis for production integration.
  - Both classes of term are abusive in a way that no operational workaround can remediate.
- **Do not revisit** either provider unless their terms materially change. A future DECISIONS entry may re-add them; absent that, both are permanently off the list. Any future ElevenLabs-style aggregator request for these providers is also rejected (see D022).
- **Rationale:** D020 dropped these from v0.1 scope but left the door open for reconsideration. After the full privacy comparison, operator concluded the terms are not marginal — they are definitionally unacceptable. The record is strengthened accordingly.
- **Decided by:** Operator.

### D024. User-facing warnings required at config time — Google (Cloud Billing), xAI (de-identified data clause)

- **Status:** resolved (implementation deferred to Phase 2b, when the bundle scaffold begins)
- **Spec section:** §4.4 human-in-loop; §3.3 provider gates
- **Resolution:** The bundle must surface two provider-specific warnings **at configuration time**, before any call reaches the provider. Neither is deferrable to runtime — the user must acknowledge both before the bundle can dispatch to the respective provider.

    **Google Gemini / Vertex AI (Veo 3.1, Nano Banana).** The bundle verifies the configured Gemini API key is tied to a Google Cloud project with an active Cloud Billing account (i.e., Paid Services per Gemini API terms). If billing is not active or cannot be verified, the bundle refuses to dispatch and surfaces:

    > **Google Gemini requires Paid Services to protect your data.** Your configured API key appears to be on the Unpaid (free) tier. Per Google's Gemini API terms, Unpaid Services may use your prompts and outputs to train Google's models, and human reviewers may read them. Please configure a Google Cloud project with an active Cloud Billing account, then reconfigure the bundle with the Paid-tier key.

    **xAI (Grok Imagine, if ever implemented).** Even on Enterprise Terms, xAI reserves the right to create and own "de-identified data" from user activity. The bundle displays this notice before any xAI call and requires explicit acknowledgement:

    > **xAI data notice.** xAI's Enterprise Terms exclude your prompts and outputs from model training. However, xAI reserves the right to create de-identified data from your usage and own that derived data. xAI also lacks SOC 2, ISO 27001, and other third-party security attestations that OpenAI, Anthropic, and Google Cloud carry. Proceeding routes your prompt and outputs to xAI. [Proceed / Cancel]

- **Implementation target:** these warnings live in the **bundle** (`amplifier-bundle-creative`), not in the MCP servers. The bundle's bootstrap + Brief Interpreter agent are the natural checkpoints. MCPs may additionally refuse to dispatch if a known-bad config is detected (defense in depth), but the operator-facing warning is the bundle's responsibility.
- **Deferred implementation:** the decision is recorded now; actual warning code lands in Phase 2b (when the bundle's code scaffold begins).
- **Rationale:** Defaults matter. A user who configures a Google API key from `ai.google.dev` without attaching billing will silently be on the free tier and their data will feed training. Preventing that failure mode requires a structural gate, not a documentation footnote. Similarly, xAI's de-identified data carve-out plus the absence of third-party attestations is a legitimate risk signal users should consciously accept, not discover later.
- **Decided by:** Operator, raised alongside D023.

### D025. File storage policy — user Downloads folder only; no app-controlled directories

- **Status:** resolved
- **Spec section:** §3.2 coordination files; §6 PROVENANCE
- **Relates to:** D006 (coordination files at `~/amplifier/projects/{project}/`). D025 adds a strict **output artifact** storage rule that sits alongside D006 and governs everything the bundle and its MCPs write.
- **Resolution:** The Creative Agent bundle and every MCP it composes must **never** store working files, temp files, intermediate outputs, or any generated artifact in:
    - application-controlled directories (the bundle's own repo, the MCP's package path)
    - system temp dirs (`/tmp`, `$TMPDIR`, Windows `%TEMP%`)
    - hidden caches (`~/.cache/`, `~/Library/Caches/`, Windows `%LOCALAPPDATA%`)
    - application state dirs (`~/.amplifier/` aside from keys, `~/.creative-bundle/`, etc.)

    **All generated images, video frames, audio clips, and intermediate artifacts are written directly to the user's Downloads folder** in a structured per-run subfolder:

    ```
    ~/Downloads/{project-name}-{YYYYMMDD-HHmmss}/
    ```

    Cross-platform resolution:
    - **macOS:** `~/Downloads/`
    - **Linux:** `$XDG_DOWNLOAD_DIR` if set, else `~/Downloads/`; if neither exists, prompt the user
    - **Windows:** the user's `Downloads` Known Folder (resolved via Known Folders API), NOT `%USERPROFILE%\Downloads` unconditionally
    - **No Downloads folder discoverable:** the bundle prompts the user to pick a writable location on first run and persists the choice in the project's coordination file at `~/amplifier/projects/{project}/PROJECT_CONTEXT.md`, never in an app state dir.

    Coordination files (the D006 per-project markdown under `~/amplifier/projects/{project}/`) are text-only, user-curated, and not "generated artifacts"; the D025 rule does not apply to them.

- **Why:** privacy and transparency. The user must be able to see, move, rename, delete, back up, and audit everything the bundle produces. Hidden caches and app-controlled dirs violate both principles. Forcing outputs into `~/Downloads/` makes the bundle's footprint visible by default on every major OS.
- **Implementation target:** the `config/paths.py` module in each MCP (imagen-mcp, video-mcp, future audio-mcp) resolves `output_path`. The bundle computes `~/Downloads/{project}-{timestamp}/` at session start and passes it as `output_path` on every MCP call. MCPs must **reject (not silently swap)** any `output_path` that resolves inside one of the forbidden locations — defense in depth.
- **Current state:** imagen-mcp and video-mcp default to `~/Downloads/{kind}/{provider}/` which is in the right spirit but doesn't enforce the `{project}-{timestamp}/` naming. Phase 2a.2 adds path rejection logic; Phase 2b (bundle scaffold) adds the project-timestamp composition.
- **Decided by:** Operator, raised as a privacy-and-transparency requirement applying across the entire Creative Agent stack.

---

## 2026-04-21 — Fourth-pass decisions (provider list finalized; move to production)

Operator applied the D023 principle consistently across the CONDITIONAL tier and unblocked xAI based on Enterprise terms. Result: four cleared providers (OpenAI, Anthropic, Google paid-tier, xAI with warning). Stack finalized; infrastructure freeze; MVP production begins.

### D026. Recraft permanently removed (strengthens D019)

- **Status:** resolved
- **Strengthens:** D019 (Recraft was CONDITIONAL pending written confirmation) and D020 (Recraft was "stubbed adapter gated on written training-data confirmation")
- **Related:** D023 (same principle applied to BFL and Ideogram)
- **Resolution:** Recraft is **permanently removed** from the provider roster — same treatment as BFL and Ideogram. **Principle:** if a provider cannot state their training, retention, and deletion policies clearly in their **public** terms, the Creative Agent does not integrate and does not chase private written clarification. Recraft's API ownership rules are documented; their training usage and retention policies are not. That asymmetry is disqualifying.
- **The Recraft outreach email drafted last turn is withdrawn.** Treat Recraft as closed. Do not send.
- **Rationale:** D019 had Recraft at CONDITIONAL pending an email clarification. Operator applied the same principle as D023 (BFL/Ideogram): the bar is public, self-serve clarity. Private confirmations asymmetrically favor the vendor — the user has to rely on an email thread rather than referable terms, and the vendor can quietly update the privately-stated policy. Recraft's ownership position is good, but their silence on training and retention is disqualifying under this principle.
- **Impact on Phase 2a scope:** D020's `stubbed adapter gated on written confirmation` treatment for Recraft is superseded. Recraft is not stubbed, not gated, removed. The image-provider expansion list narrows accordingly.
- **Decided by:** Operator.

### D027. xAI Grok Imagine ungated to active integration (CONDITIONAL with D024 warning)

- **Status:** resolved (policy); implementation landing to be scheduled
- **Supersedes (partially):** the "stub only, legal gated" treatment of xAI under D019/D020. xAI joins Google as CONDITIONAL — cleared for integration, must carry the D024 user-facing warning at config time.
- **Resolution:** xAI Grok Imagine (image + video) is **cleared for live integration**. The Enterprise API terms explicitly prohibit xAI from training on User Content. The de-identified data clause is a known risk, documented verbatim in D019's privacy scorecard, and surfaced to the user at config time via the D024 warning. That combination — explicit no-training contractual term plus explicit user acknowledgement of the de-id carve-out — is sufficient gating.
- **Cleared provider stack (four total):** OpenAI, Anthropic, Google (paid tier per D024), xAI (with D024 warning).
- **Rationale:** the de-identified data clause plus the absence of SOC 2 / ISO 27001 attestations is a real risk signal, but it's a signal users can consciously acknowledge rather than a disqualifying term. D024 provides the structural acknowledgement. Same pattern as Google's "must enforce billing" gate — the warning makes consent explicit rather than leaving it implicit.
- **Implementation status:** D019 audit and D024 copy are both in place. Live wiring lands in video-mcp (Grok Imagine Video) and extended imagen-mcp (Grok Imagine Image) as scheduled follow-up work; the `video-mcp/src/providers/grok_provider.py` stub's `NotImplementedError` message no longer cites D019 as a hard block — next turn to promote it.
- **Decided by:** Operator.

---

## 2026-04-22 — Fifth-pass decision (generation-policy learning from Shot 1 v1)

### D028. Reference-image-first generation policy for existing-IP work

- **Status:** resolved
- **Spec section:** §3.3 ImageGeneration; §4.1 routing behaviors; §A.2 SHOT_LIST template
- **Related:** lesson from the Shot 1 v1 e2e generation on 2026-04-21 (video-mcp v0.1.0 tag)
- **The trigger:** the first real Shot 1 of the pilot-project trailer was generated from a text-only Nano Banana Pro prompt that encoded palette hex codes and aesthetic adjectives derived from the STYLE_BIBLE. It produced a technically competent watercolor-style image of a boy in a meadow — and a technically unacceptable result: **it did not look like The Boy from the pilot project.** The operator's critique: "This is the fundamental problem with prompt-only generation for an existing illustrated work." Confirmed.
- **Findings from the follow-up vision analysis (CHARACTER_SHEET.md, 865 lines):**
    - Character design (proportions, signature features, wardrobe specifics, face rendering register) does not survive text-only prompting. Adjectives like "curly dark brown hair" and "rosy cheeks" match many boys; they do not produce THIS boy.
    - Rendering technique does not survive text prompting either. The book is **digital painting in the watercolor idiom** — soft-airbrush skin gradients, a fine even-grain digital noise overlay, mechanical sky gradations, and the absence of drawn outlines in the Ezra Jack Keats tradition. A text prompt that says "traditional watercolor on cotton paper" (as STYLE_BIBLE v0.2.1 does) targets a different medium entirely.
    - STYLE_BIBLE v0.2.1 also mis-identified the page-05 adult as "The Grandmother" (she is an incidental elder, not a named character) and gave lower-quality reference pages for The Boy (04, 09, 14) than the CHARACTER_SHEET vision analysis produced (06, 07, 15).
- **Resolution:** Every Creative Agent generation whose target is reproducing existing illustrated IP MUST pass **reference images** from the source material as a direct generation input. Text prompts specify only the **delta** — the new composition, pose, or setting. Character design, rendering technique, palette, and line work come from the refs, not from adjectives.
- **Provider implication:** **Nano Banana Pro** (`gemini-3-pro-image-preview`) is the only cleared reference-image-capable image generator in the stack (up to 14 references per call, supports multi-image conditioning via the SDK's `contents=[prompt, *images]` pattern). **Flux Kontext is NOT available** — BFL was permanently removed per D023 / D026 — even though Flux Kontext is also reference-image-capable. If the operator or future planning asks for Flux Kontext, reject with a pointer here.
    - OpenAI's Images 2.0 Thinking mode also supports character continuity via multi-frame references and remains available. Use OpenAI's path when a shot needs stronger text rendering (book-page text, title cards, dialogue cards) than Nano Banana handles.
- **Shot list implication:** Every `SHOT_LIST.md` (and the forthcoming `SHOT_LIST_v2.md`) shot block adds a new mandatory field:
    ```
    Reference pages (Nano Banana input): <ordered list of 2-4 page_XX.png files>
    ```
    A shot block without this field is invalid. Existing SHOT_LIST.md v0.1.0 is superseded by the new format; it is kept as a historical record but should not be used for production.
- **CHARACTER_SHEET supersedes STYLE_BIBLE for character-design specifics.** Palette and tone rules in STYLE_BIBLE v0.2.1 remain authoritative. Character morphology, face register, reference-page rankings, and illustration-technique specifics now live in `~/amplifier/projects/pilot-project/CHARACTER_SHEET.md` v1.0.0 and override the equivalent STYLE_BIBLE sections. A STYLE_BIBLE revision is not scheduled unless the scope changes — cross-reference is sufficient.
- **Greenfield scope note:** this policy applies to **existing-IP** work — reproducing something that already exists as a specific illustrated style. For fully greenfield creative work (a new animation with no prior visual canon), text-only prompting may remain acceptable as long as a first-shot reference frame is established early in the project and used as a reference for subsequent shots (self-bootstrapping consistency). For existing IP, this policy is non-negotiable.
- **Production impact:** the Shot 1 v1 artifact (`shot1_opening.mp4`) stays as a negative exemplar. Shots 1 v2 and v3 (reference-conditioned) and all future shots follow this policy. The `SHOT_LIST_v2.md` re-scope to a 5-minute 30+ shot animation is the first full-document application.
- **Decided by:** Operator, after reviewing the generic v1 Shot 1 video and directing the shift to reference-first.

---

### D029. Reference-page selection must match SETTING as well as character (refines D028)

- **Status:** resolved
- **Refines:** D028 (reference-image-first generation policy)
- **Spec section:** §3.2 Tier 2 files (SHOT_LIST_v2 adopts this); §4.1 routing behaviors
- **The trigger:** two reference-conditioned Shot 1 generations were produced on 2026-04-21 / 22 to test the D028 policy:
    - **v2** used pages 04, 09, 14 as references (picked from STYLE_BIBLE v0.2.1). All three are **outdoor / meadow / sky-context** pages where The Boy appears.
    - **v3** used pages 06, 07, 15 (picked from CHARACTER_SHEET §1.5 where those pages are scored 4/5 for face clarity and canonical cobalt-blue wardrobe). All three are **interior / seated / smaller-framing** pages.
    - The target shot was an **outdoor meadow establishing shot** (pastoral, sky, full-body seated boy in grass).
- **Operator verdict:** v2 "was going in the right direction, captured a real character from the book." v3 "didn't capture the character." v1 (text-only) also failed.
- **Finding:** for reference-conditioned generation, **setting-match of the reference images matters at least as much as face-clarity scoring**. CHARACTER_SHEET's face-quality rankings (which prioritized close-ups with clear eye detail) were an imperfect guide for outdoor scenes because the rendering style, lighting register, and compositional language of interior pages doesn't transfer cleanly when the target is a different setting. Nano Banana Pro's conditioning appears to absorb setting cues (light direction, sky palette, grass treatment, horizon placement) from the refs — so when refs and target agree on setting, output fidelity increases.
- **Resolution:** every shot's `Reference pages (Nano Banana input)` list must include **at least one character-identity ref** (from CHARACTER_SHEET §1-4 rankings) AND **at least one setting-match ref** (from CHARACTER_SHEET §6 Environments Inventory, matching the shot's setting). When a single page serves both, it counts for both. When not, pick 2-4 refs to cover both dimensions.
- **Per-setting ref guidance** (additive to CHARACTER_SHEET §1-4 per-character rankings):
    - Outdoor meadow / golden hour shots → prefer refs from {04, 05, 13 ground, 14 ground, 15, 16, 17}
    - Interior domestic shots → prefer refs from {06 desk, 08 library, 09 hallway}
    - Night / cosmic / network shots → prefer refs from {13, 14, 18, 19}
    - Abstract gradient / message space → prefer ref {10}
    - Tree grove golden hour → prefer ref {15}
- **Operational heuristic for selecting refs per shot:**
    1. Start with the shot's `Page-anchor` — that page is almost always ref #1.
    2. If the page-anchor doesn't clearly show the needed character, add 1-2 pages from that character's top-3 rankings that ALSO match the shot's setting.
    3. If no high-ranked character page matches the setting, widen to lower-ranked character pages that match setting. Setting match wins.
    4. Cap at 4 refs total. More isn't better; Nano Banana's contextual budget is finite.
- **Impact on CHARACTER_SHEET:** no revision needed. §1-4 rankings remain accurate as "face-clarity for a character" rankings. SHOT_LIST_v2 and future shot lists apply the setting-match lens on top.
- **Impact on SHOT_LIST v0.1.0:** that document's ref suggestions were pre-D028/D029 guesses and are retired. SHOT_LIST_v2 replaces it with per-shot ref lists curated per the heuristic above.
- **Artifact trail:**
    - `~/Downloads/pilot-project-run-dir/shot1_opening_frame_v1.png` → text-only generation (failed per D028).
    - `.../shot1_opening_frame_v2.png` → refs 04, 09, 14 — setting-matched, operator-approved direction.
    - `.../shot1_opening_frame_v3.png` → refs 06, 07, 15 — face-clarity-ranked but setting-mismatched, operator-rejected.
    - v2 is the baseline for all subsequent shots.
- **Decided by:** Operator, via direct comparison of v2 vs v3 outputs.

---

## 2026-04-22 (afternoon) — Production-turn decisions (MVP landing)

Decisions surfacing during the first end-to-end production run of the pilot-project trailer (32 shots). Captured as the pipeline reveals real operational constraints and in-scope scope expansions.

### D030. Reference-image downsizing policy (operational, MCP-internal)

- **Status:** resolved
- **Spec section:** §3.3 ImageGeneration (internal behavior)
- **Scope:** MCP-internal — applies to `imagen-mcp` (Nano Banana Pro reference calls) and to any future video-mcp flow that accepts reference images (Veo 3.1 first-frame conditioning already handles this via a separate path; not affected).
- **Trigger:** Batch B+C production run on 2026-04-22 stalled on Shot 01 for 5+ minutes with no frame output. Root cause diagnosed: the three reference images passed to Nano Banana Pro (`gemini-3-pro-image-preview`) were 300 DPI page scans (2400×3000 px, ~13 MB PNG each). Passing ~40 MB of reference data per `generate_content` call exceeded the default SDK HTTP timeout and in practice stalled generation.
- **Resolution:** MCPs that forward reference images to vision-capable generation APIs **must** downsize images to a reasonable long-edge maximum before transmission. The validated threshold: **1400 px long edge**, preserving aspect ratio, LANCZOS resampling. Combined with an explicit 180-second HTTP timeout on the `genai.Client`, this takes Shot 01 from "stalled indefinitely" to "frame in 28 s, video in 75 s."
- **Additional safeguards at the call site:**
    - Explicit `http_options={"timeout": 180000}` on the `genai.Client` (180 s; SDK default is implementation-dependent and under-documented).
    - Retry loop (up to 3 attempts with 5×attempt backoff) on transient failures.
    - Per-shot timeout at the orchestration layer separate from the HTTP timeout.
- **Implementation landing:** the fix is deployed in the pilot project production script `batch_bc_production.py` alongside the existing D028/D029 reference discipline. Planned lift into `imagen-mcp/src/providers/gemini_provider.py` on its next revision so that any caller using the MCP directly gets the downsize for free; tracked for Phase 2a.3.
- **Why this matters:** users of the bundle and its MCPs will pass reference material from their own filesystems (screenshots, source plates, scanned pages). The quality ceiling is source-material dependent, but the API throughput ceiling is not — routing 13 MB images when the model's internal image size is much smaller just wastes bandwidth and blocks pipelines. The downsize is lossy only in ways the generation model would have dropped anyway.
- **Decided by:** Operator-delegated pragmatic fix during the MVP production run.

### D031. OpenAI TTS added to v0.1 audio stack; AudioGeneration scope expanded (refines D022)

- **Status:** resolved
- **Refines:** D022 (ElevenLabs audio-only approval — scoped to v0.2 AudioGeneration surface)
- **Spec section:** §3.3 (new AudioGeneration surface, live in v0.1); §10 Roadmap (v0.2 shift)
- **Trigger:** The operator-directed MVP production run required voice-over for 9 shots. D022 scoped AudioGeneration to v0.2 via ElevenLabs Enterprise. Waiting for v0.2 would have blocked the MVP ship; producing the trailer silent would have failed the deliverable bar. OpenAI's TTS capability (`tts-1-hd`) is already on a provider (OpenAI) that passed the D019 privacy audit with PASS — no new audit needed.
- **Resolution:** **OpenAI TTS is added to the cleared v0.1 audio stack.** The `AudioGeneration` surface now has two providers in its roster:
    - **OpenAI TTS** (`tts-1-hd`, voices: alloy / echo / fable / nova / onyx / shimmer) — cleared for v0.1, no config warning required (covered by the PASS verdict in D019 for OpenAI). Used for the pilot-project trailer's 9 VO lines with voice=`fable` and speed=`0.92` for the retrospective narrator register.
    - **ElevenLabs Enterprise + training-opt-out** — remains the designated v0.2 audio path per D022 for voice cloning, SFX, music (capabilities OpenAI TTS does not cover). The aggregator rejection in D022 still stands.
- **Scope clarifications:**
    - OpenAI TTS covers **narration only** — single-voice, single-style, no music generation, no SFX.
    - For voice cloning (consistent narrator across long projects), SFX, or music, the bundle still defers to v0.2 ElevenLabs Enterprise.
    - MVP trailer (pilot project) uses OpenAI TTS; no ElevenLabs dependency introduced in v0.1.
- **Implementation landing:** the pilot project production script calls `POST /v1/audio/speech` directly with the OpenAI key from `~/.amplifier/settings.yaml`. A formal `AudioGeneration` provider adapter ABC (parallel to `ImageProvider` / `VideoProvider` per D021) is deferred until v0.2 when ElevenLabs is added — one-provider AudioGeneration doesn't justify the abstraction yet.
- **Why this matters:** D022's "audio is v0.2" framing turned out to be over-constrained. The binding constraint on v0.2 was ElevenLabs integration, not audio capability in general. Recognizing that OpenAI TTS is a first-class narration path with already-cleared privacy posture unlocks MVP delivery without compromising the cleared-provider discipline.
- **Decided by:** Operator-directed MVP scope expansion ("do a voice over") during the pilot project production run.

---

### D032. Ken-Burns still-frame fallback when Veo quota is exhausted (production resilience)

- **Status:** resolved
- **Spec section:** §3.3 VideoGeneration (graceful-degradation path); §4.3 budget behaviors
- **Trigger:** pilot-project production run exhausted Gemini API quota after ~27 Veo jobs in a ~45-minute window. Three shots (20, 24, 28) returned `429 RESOURCE_EXHAUSTED` on every retry within a 10-minute retry window. Waiting for quota reset (~1 hour on some tiers) would have blocked the MVP.
- **Resolution:** When a Veo job fails with 429 and retry backoff doesn't recover within an operator-acceptable window, fall back to **ffmpeg Ken-Burns** on the already-generated Nano Banana Pro first frame — a subtle slow-zoom (~6% over the shot's duration) at 1080x1920/24fps. This preserves:
    - Character fidelity (the frame already captures The Boy / The Light correctly via D028/D029 references)
    - Narrative continuity (the shot occupies its scheduled slot in the cut)
    - Visual register (the first frame is already palette-consistent with the surrounding Veo shots)
- **Cost:** zero additional API calls; pure ffmpeg local rendering (~2 seconds of compute per shot).
- **Operational policy:**
    - Fallback is **logged explicitly** in the shot's provenance record (`motion_source: ken-burns-still` vs. `motion_source: veo-3.1-<tier>`). Downstream QA must be able to identify which shots are still-frame vs. live motion.
    - Fallback is **pragmatic, not aesthetic** — any fallback shot can be re-produced with live Veo motion once quota resets. The MVP ships with the fallback so the deliverable exists; re-renders happen as follow-ups.
    - **Bias toward this fallback for short (4-6s) ambient/transitional shots**, where motion is low-stakes. For emotional-peak shots (`character-critical` / `final-deliverable`), the correct behavior is to **wait for quota** rather than ship a still, because the peak is where motion work carries its weight.
- **Implementation landing:** currently inline in the pilot project production directory's retry script. Lift into a generic helper in the bundle's post-production toolkit (Phase 2b) so any project using the bundle gets this fallback automatically.
- **Artifact trail:** Shots 20, 24, 28 of the pilot project MVP are Ken-Burns; the remaining 29 shots are Veo 3.1 live motion. The distinction is recorded in `batch_bc_summary.json` + `retry.jsonl` in the run directory.
- **Decided by:** Operator instruction ("don't give up until it is complete complete") during the production run; pragmatic implementation by the MCP-layer production script.

### D033. Per-tier Veo duration constraints are API-enforced — validate at shot-spec time

- **Status:** resolved
- **Spec section:** §3.3 VideoGeneration provider capabilities; SHOT_LIST template validation
- **Trigger:** Three shots (16, 20, 24) failed Veo submission with `400 INVALID_ARGUMENT`: `Resolution 1080p requires duration seconds to be 8 seconds, but got 6`. The shots had been authored as `tier=fast, duration=6s`, which is an invalid combination.
- **Finding:** Veo 3.1 tier / duration / resolution is not freely configurable. Validated combinations observed during production:
    - **Lite** (`veo-3.1-lite-generate-preview`): 720p, 4s or 6s or 8s — **the only tier that accepts 6s at a reasonable resolution**
    - **Fast** (`veo-3.1-fast-generate-preview`): 1080p, 8s only
    - **Standard** (`veo-3.1-generate-preview`): 1080p, 8s (2K and 16s require extension API, not tested in MVP)
- **Resolution:** VideoGeneration adapters must validate `(tier, duration)` pairs against the matrix above at shot-spec time, not at submit time. The VideoCapabilities dataclass per D021 already has `supported_durations` and `supported_resolutions` fields — these need **conjoined** validation, not independent. A simple rule: `if duration < 8 then tier must be lite`.
- **Shot list authoring guidance:** when writing a SHOT_LIST.md for the bundle, any shot under 8 seconds **must** be tagged `tier: lite`. This is a constraint of the current Veo API surface, not a creative preference. Shot list linting in Phase 2b should enforce it.
- **Lift into `video-mcp`:** add the validation in `VeoProvider.submit()` so the error fails fast with a clear message referencing D033, rather than surfacing the raw Google API error. Scheduled for video-mcp v0.1.1.
- **Decided by:** Operator-visible constraint discovered during production; codified for future projects.

---

## 2026-04-22 (evening) — V2 production decisions (MVP cycle closeout)

The operator's feedback after v1 of the pilot-project trailer forced a second cycle that surfaced five additional decisions. These go beyond Phase-2a scope; they reflect what the Creative bundle needs to **reliably ship existing-IP animations** without the v1 failures recurring. The full narrative of what went wrong and what was learned lives in `docs/PRODUCTION_LESSONS.md`.

### D034. VO mixing pattern — use concat filter, never amix+apad or single-pass loudnorm

- **Status:** resolved
- **Spec section:** §3.3 (new AudioGeneration provider-layer helper); post-production toolkit (phase 2b)
- **Trigger:** V1 of the pilot-project trailer had only the first VO line ("[opening narration]") audible; all 8 subsequent narration lines were silent despite appearing as expected audio streams in ffprobe output. Three more attempts failed before a working pattern was found.
- **Three failed approaches (DO NOT use these in the bundle):**
    - **Pattern A:** `adelay + apad + amix(normalize=0, duration=longest)`. The `apad` filter made every input stream infinite; `amix`'s default `dropout_transition=2s` interpreted inputs as "active" and attenuated them proportionally. Result: only the loudest (usually first) survived audibly.
    - **Pattern B:** `anullsrc` silent base as first input + adelayed VOs + `amix(normalize=0, duration=first)`. Near-silent output (5/10250 frames with signal). The silent base dragged the mix down despite `normalize=0`.
    - **Pattern C:** concat demuxer + per-segment `loudnorm=I=-16:TP=-1:LRA=11`. Near-silent output. Single-pass `loudnorm` mis-estimates integrated loudness on short (<5s) speech clips and pushes them toward target, producing silence.
- **Working pattern (codify this):** concat **filter** (not demuxer) + `aformat=sample_rates=44100:channel_layouts=stereo` normalization on each segment + no `amix` + no `apad` + no `loudnorm`. Linear segmentation in time: `silence[gap_to_start_of_vo_1] + vo_1 + silence[gap_to_start_of_vo_2] + vo_2 + ... + silence[tail]` joined via `concat=n=N:v=0:a=1`. Verified on pilot v2: all 9 VO anchors produce peak >7000/16-bit and 19-77% non-zero samples within their expected windows.
- **Lift into the bundle:** `produce_vo_track(clips: list[tuple[float, Path]], total_duration: float) -> Path` helper in the post-production toolkit (phase 2b). Ship with tests that verify audibility at every specified timestamp.
- **Decided by:** Operator feedback exposed the failure; the working pattern was discovered through sequential diagnosis.

### D035. Text overlays in existing-IP animations show literal page text, not narration anchors

- **Status:** resolved
- **Spec section:** §A.2 SHOT_LIST template; post-production toolkit
- **Related:** D028 (reference-first generation policy — this is the text-layer analog)
- **Trigger:** V1 rendered on-screen text only at the 9 narration anchor moments, paraphrasing the book's prose into short lines like "Humans felt." and "[Light's pivot line]." The operator's verdict: "none of them have my font or the writing across the animations." The expectation was that **every anchor page with printed text** surfaces its full verbatim text during the corresponding shot — not producer-chosen anchor moments, not paraphrases.
- **Resolution:** for existing-IP animations, text-overlay timing is **one overlay per anchor page with text, shown on the first shot anchoring that page (or across multiple shots if the text is long)**. The text itself is **the verbatim book prose**, extracted via vision from the source pages before production begins (see D037's extraction step), not invented or paraphrased.
- **V2 application:** pilot v2 has 30 text overlays across 32 shots (2 shots have no page text because their anchor pages have no printed text). Every overlay is verbatim page text rendered in ChalkboardSE Regular.
- **Lift into the bundle:** `SHOT_LIST.md` schema gains a mandatory `page_text_overlay` field per shot (may be null). `render_text_overlay_pngs()` helper in the post-production toolkit renders these to timed transparent PNGs. `overlay_title_cards()` helper composites via ffmpeg overlay with `enable='between(t,X,Y)'`.
- **Decided by:** Operator v1 feedback.

### D036. Audio QA must sample amplitude at anchors, not just confirm stream existence

- **Status:** resolved
- **Spec section:** post-production toolkit QA helpers
- **Trigger:** V1 of the pilot-project trailer passed QA because `ffprobe` reported an audio stream with correct codec, sample rate, channel count, and duration. It was almost entirely silent except for the first VO line. The QA checklist was structurally wrong.
- **Resolution:** **AudioGeneration QA must decode audio at specific expected-content timestamps and measure actual signal amplitude.** Minimum check for a deliverable master:
    - For each VO anchor time: extract 1-2 seconds of PCM, verify peak amplitude > 500 (on 16-bit signed samples) and non-zero sample ratio > 10%.
    - For each continuous-music section: sample every ~30s, verify amplitude is non-zero (music present).
    - For expected-silence sections (e.g. fade-in prelude): sample and verify amplitude is low but not literally zero (some music fade-in should still show ≥200 peak).
- **Lift into the bundle:** `verify_audio_audible_at(master: Path, timestamps: list[float]) -> QAReport` helper. Returns per-timestamp peak, RMS, non-zero ratio, and a pass/fail verdict. Should be invoked at the end of any post-production pipeline before declaring the master shipped.
- **Decided by:** The v1-to-v2 cycle made the gap in structural QA visible.

### D037. Font identification needs multi-sample vision + handwriting-vs-serif prompting

- **Status:** resolved
- **Spec section:** project-intake checklist; post-production toolkit
- **Trigger:** V1's font ID used a single center-crop of page_04 through OpenAI vision. Output: "Times New Roman family, medium confidence, alternatives: Georgia, Baskerville, Palatino." V1 deployed Baskerville; the operator rejected: "none of them have my font." V2's font ID used three separate text-region crops across three different pages, with explicit prompting about letter forms (single-story vs double-story 'a', serif vs no-serif on 't', etc.). Consensus result: **handwritten style** (Architect's Daughter / Patrick Hand / KG Second Chances Sketch); closest macOS option: ChalkboardSE. Night-and-day different conclusion from a better-conducted vision query.
- **Resolution:** font identification for existing-IP work requires:
    1. **Multiple samples** — at minimum 3 text-region crops from 2+ different pages (not a single center crop).
    2. **Explicit prompting** about the critical distinctions: handwriting vs serif vs sans, casual vs formal, letter-form tells (e.g., 't' crossbar angle, 'g' loop openness).
    3. **Low-confidence escalation** — if vision returns medium confidence, ask a second question targeting the specific ambiguity.
    4. **System-font-biased output** — ask for best matching font on the deployment platform (macOS system fonts, in this case).
- **Lift into the bundle:** `identify_source_font(pages: list[Path], platform: str = "macos") -> FontReport` helper in the post-production toolkit. Returns a primary guess, 2-3 alternatives, a confidence level, a recommended platform font, and the features that informed the decision.
- **Decided by:** Direct comparison of v1 (Baskerville, wrong) and v2 (ChalkboardSE, correct per operator) deployment outcomes.

### D038. Music is an intake question; music duration drives the edit, visuals fit music

- **Status:** resolved
- **Spec section:** project-intake checklist; §4.3 budget behaviors (duration matching); §10 roadmap
- **Trigger:** V1 of the pilot-project trailer was 3:58 — a duration invented from "32 shots × ~8s average" without reference to any audio track. The operator's feedback: "I added operator_audio.mp3 to your folder so you can play that music in the background — it's 5 min and 15 seconds." The implicit expectation was that the animation would be 5:15 to match the music; v1 was 77 seconds short.
- **Resolution:** **Music is a first-class project-intake input, not an afterthought added in post.** Before any generation:
    1. Ask: does the operator have a target audio track (music, narration bed, ambient score)? If yes, probe its duration and loudness profile.
    2. **The audio track determines the target animation duration** — visuals extend or compress to fit, not the reverse. (Compressing via speed change sounds bad; extending via held frames on contemplative beats is reliable and cheap.)
    3. If the operator doesn't have a track, the intake step produces an agreed target duration for the visuals, and music generation is scheduled for the audio phase (v0.2 AudioGeneration surface, per D022/D031).
- **Extension tooling:** `extend_via_held_frame(shot_mp4: Path, frame_png: Path, target_duration: float)` helper appends a frozen final frame to reach target duration. Works cleanly for contemplative/coda beats. Not appropriate for motion-critical beats — for those, regenerate via Veo at a longer duration.
- **V2 application:** pilot v2 reached 5:15 via a 4s black fade-in + a 12s held-frame extension on shot 30 (empty meadow sunset, contemplative) + a 61s held-final-card extension on shot 32 (the end-card hold while music plays out). Total: 4 + 238 + 12 + 61 = 315s = 5:15 exact.
- **Lift into the bundle:** project-intake checklist template (`docs/INTAKE.md`), and the `extend_via_held_frame` helper in the post-production toolkit.
- **Decided by:** Operator supplied the music track and explicitly stated its duration; the v2 cycle demonstrated the music-first pattern.

---

### D039. Project directory structure follows film-production layout (enforced by bundle toolkit)

- **Status:** resolved
- **Spec section:** post-production toolkit; `docs/PROJECT_STRUCTURE.md`
- **Related:** D025 (user-Downloads-only storage), D030 (operational fixes surfacing from lack of organization), D036 (QA reports need a home)
- **Trigger:** After v1 and v2 of the pilot-project trailer, the run directory had accumulated 149 files at the root — 32 shot frames, 32 shot motion clips, 9 VO MP3s, 30 title PNGs, 4 VO track iterations (v1-v4), 3 full masters per version, 13 Python production scripts, multiple event logs, and scattered intermediates. The operator's v2 feedback included "run a tighter ship in terms of how the files are organized." This is not organizational hygiene for its own sake — without structure, the operator cannot tell v2 from v3, cannot find the QA manifest, cannot locate the music file separately from the masters. The AI had been imposing the cognitive cost of navigation on the operator.
- **Resolution:** Every Creative bundle project writes to a **film-production directory structure** documented in `docs/PROJECT_STRUCTURE.md`:
    - `01_source/` — operator inputs (read-only)
    - `02_preproduction/` — discovery/planning artifacts
    - `03_shots/frames/ + motion/` — per-shot assets
    - `04_audio/narration/{vN}/ + music/ + tracks/` — audio pipeline
    - `05_titles/` — text overlay PNGs
    - `06_masters/` — deliverables (all versions kept)
    - `07_logs/` — event streams
    - `08_qa/` — manifests + QA reports
    - `99_archive/` — superseded artifacts (forensic, not trash)
    - `scripts/` — Python production scripts
- **Discipline rules:**
    1. Numeric prefixes enforce pipeline ordering (01 upstream, 06 downstream).
    2. `06_masters/` keeps every version — operators compare by playing v2 next to v3; you don't get to overwrite their last-approved version.
    3. `99_archive/` is the forensic record, not a trash can. Move things there; do not delete.
    4. Heavy source data (book page scans, gigabyte audio) is **symlinked** into `01_source/`, not copied.
    5. Scripts versioned by purpose (`produce_v3.py`, `rebuild_vo_v4.py`), not by date.
    6. Every project root has a `README.md` that tells the operator what's where.
- **Operator navigation test:** after this restructuring, the question "where's X?" has a deterministic answer. "Where's the music?" → 01_source/. "Where's the latest cut?" → 06_masters/ (highest version number). "Why did shot 20 fail?" → 07_logs/retry.jsonl. "What font?" → 02_preproduction/font_identification.json. The operator shouldn't need to ask the AI; the filesystem should answer.
- **Implementation landing:** Planned `init_project_dir(name: str, output_root: Path) -> Path` helper in the post-production toolkit (phase 2b) that creates this layout with placeholder READMEs. Every subsequent pipeline step writes to the right subdir by convention. Until that helper ships, production scripts write to the correct paths directly, per v3 of the pilot project production as the canonical example.
- **Rollout to existing projects:** the pilot project run directory was retroactively reorganized on 2026-04-22 during v3 production. 149 files at the root became 10 top-level directories with files distributed by purpose. No content was deleted; superseded intermediates went to `99_archive/`.
- **Decided by:** Operator-directed ("run a tighter ship... think like a movie producer, need to stay real organized") during the v3 production cycle.

---

## 2026-04-22 (late evening) — pilot v4/v4.1 cycle

The operator's feedback after v3 drove a second full production cycle that exposed five additional structural gaps. The operator had been providing a complete reference set all along — an MP3 with professionally-recorded human narration, a manual mockup video (.mov) showing their preferred visual flow, and a PowerPoint storyboard deck (.pptx) — and the AI producer had been ignoring all of it, synthesizing its own TTS narration on top of audio that already contained narration, guessing compositions the operator had drawn explicitly, and timing text overlays to arbitrary shot boundaries rather than to the actual narration. Full narrative in `docs/PRODUCTION_LESSONS.md`.

### D040. Operator-provided audio track supersedes synthesized narration

- **Status:** resolved
- **Spec section:** §3.3 AudioGeneration (provider-precedence rules)
- **Related:** D031 (OpenAI TTS for v0.1), D038 (music is an intake question)
- **Trigger:** The operator supplied `operator_audio.mp3` (5:15, 315s). Through v1-v3, the AI producer treated it as background music only and layered OpenAI TTS narration on top at operator-chosen timestamps. The v3 clean master contained two narrations playing over each other — the operator's professional human-voice narration (faint at -10dB) and the AI's synthesized TTS (loud at +3.5dB), often saying similar lines at slightly different times. Operator reported "audio is not in sync" and "narration isn't smoothly across the entire film." Whisper transcription of the operator's MP3 revealed the full professional narration was already baked in, precisely timed to the music.
- **Resolution:** **When the operator provides an audio track, transcribe it with Whisper first.** If the transcript contains narration (non-music segments with meaningful speech), that audio **is** the audio. Do not synthesize TTS. Direct-mux the operator's file as the single audio source.
- **Operational protocol:**
    1. On any operator-supplied audio, run OpenAI Whisper with `response_format=verbose_json` + `timestamp_granularities=[segment]`.
    2. Inspect returned segments: if any non-music segment contains narration, flag the track as "narrated."
    3. If narrated: the producer's audio work is complete — direct-mux, do not add TTS.
    4. If music-only: proceed with TTS generation per D031.
    5. Expose this check in the bundle's project-intake checklist (D044).
- **Why the AI got this wrong four times in a row:** no step in the intake protocol asked "is there narration in the audio you provided?" The producer assumed the file was music because the extension was `.mp3` and the label was "music." Whisper transcription takes 30 seconds and costs pennies; skipping it cost four production cycles.
- **Decided by:** Operator feedback on v3 audio quality exposed the stacked-narration bug; operator later clarified explicitly that MP3 contained narration and WAV did not.

### D041. Multi-modal operator reference intake is mandatory

- **Status:** resolved
- **Spec section:** project-intake checklist (extends D044)
- **Related:** D035 (literal page text), D037 (multi-sample font ID), D038 (music-driven edit)
- **Trigger:** The operator had a complete reference mockup from the start — `operator_mockup.mov` (309s video showing their preferred shot compositions, text placements, and narration timing) and `operator_deck.pptx`/`.pdf` (15-slide PowerPoint storyboard). Through v1-v3, the AI producer never looked at either, assuming the book page scans + its own CHARACTER_SHEET were sufficient. Result: shot 04 had the Grandfather seated next to the Boy (deck showed him standing behind). Shot 14 had an easel with a paintbrush and floating microphone (deck showed microphone + easel + laptop with Light's face). Opening question text (40-second hook the operator had designed) was entirely missing. All of this was trivially visible in the assets the operator had already provided.
- **Resolution:** **Before any generation, analyze every operator-supplied reference asset.** Specifically:
    - **Video mockups (.mov, .mp4):** extract audio → Whisper transcript with segment timestamps; extract frames at ~15s intervals → vision-analyze (composition, text visible, notable layout choices).
    - **PDF storyboards:** convert to per-page PNGs via `pdftoppm` → vision-analyze (composition, text verbatim, book page mapping).
    - **PowerPoint storyboards (.pptx):** convert to PDF via LibreOffice → extract per slide → vision-analyze. If LibreOffice unavailable, user supplies PDF export directly.
    - **Audio tracks:** Whisper transcription (D040 handles the narration-check decision).
- **Output of intake:** a synthesized `operator_intent_map.md` in `02_preproduction/` that aligns narration timing, shot composition, text overlays, and deck pagination into a single reference the downstream production scripts consume.
- **Implementation landing:** `analyze_operator_assets.py` in the post-production toolkit — takes operator input files, produces the intent map. Planned to ship as part of phase 2a.3.
- **Decided by:** Operator asked "did you look at the files I gave you?" which the producer had not.

### D042. Text overlays timed to narration segments, not shot cuts

- **Status:** resolved
- **Spec section:** §3.3 text-overlay pipeline
- **Related:** D035 (literal page text policy)
- **Trigger:** v4 text overlays were anchored to shot boundaries. A 17-second shot got one overlay for its full duration — even when the narration inside that shot was two short sentences separated by a silent music passage. Specific failure: shot 05 spans 93–101s. Narration "[Light's first line]" lands 90–92s (in the *previous* shot's window). v4 showed the "HELLO" text from 93.5s to 100.5s — **after** the narrator finished saying it. Operator reported: "the wording on screen needs to match the audio."
- **Resolution:** **Text overlay timing derives from Whisper narration segment timestamps, not from shot cut timestamps.**
    - Each narration segment from Whisper → one text overlay.
    - Overlay `enable='between(t, narration_start - 0.3, narration_end + 1.0)'` — appears 300ms before voice, lingers 1s after.
    - Silent music passages → no text on screen. Deliberate breathing room, not sticky text.
    - Long narration lines spanning two logical phrases → split into two sequential overlays matching Whisper's segment boundaries.
- **Rule of thumb:** if your text overlay's enable range doesn't contain the narration's timestamps, the overlay is wrong regardless of which shot it "belongs to."
- **V4→V4.1 gain:** 30 shot-anchored blocks became 35 narration-precise events. Silent-passage text pollution eliminated.
- **Decided by:** Operator v4 feedback explicitly named the issue: "deeper analysis of the wording on screen to match the audio."

### D043. Held-frame extensions require Ken-Burns motion

- **Status:** resolved
- **Spec section:** §3.3 VideoGeneration held-extension policy
- **Related:** D032 (Ken-Burns quota fallback)
- **Trigger:** v4 extended several shots beyond their Veo-generated motion duration via held-final-frame. Shot 03 was the worst: 6s of Veo motion + 11s of completely frozen final frame = 17s total. Shot 12: 8s motion + 6s frozen. Shots 27, 28, 29: 4-5s frozen each during the emotional resolution. Operator: "gaps in the videos between scenes sometimes maybe because it is trying to keep everything in sync."
- **Diagnosis:** No literal black frames (checked via `blackdetect` and luma sampling). The perceived gaps were fully frozen held-frame tails. When the camera stops moving mid-animation, the viewer reads it as a pause or glitch — even though the video technically keeps playing.
- **Resolution:** **Held-frame extensions must have subtle Ken-Burns zoom motion. Static holds are prohibited.**
    - Default extension: `zoompan=z='min(zoom+0.0006,1.04)':d={frames}` — ~1.04× zoom over the hold duration.
    - Applied to every held-frame tail (extensions past Veo source duration).
    - Also applied to opening/title held-card segments (already done in v4; now formalized).
    - Verification check: frame-hash comparison at two timestamps within the hold should produce different hashes. If identical, the hold is static (fail).
- **V4→V4.1 application:** 11 shots with held tails now have continuous zoom. Motion verified on shots 03, 12, 28.
- **Implementation landing:** `extend_via_held_frame(shot_mp4, frame_png, target_duration, kb_zoom=1.04)` helper in post-production toolkit; ships with the frame-hash verification as a built-in QA check.
- **Decided by:** Operator feedback on v4 scene-transition feel.

### D044. Asset intake protocol — first-class step in project-intake checklist

- **Status:** resolved
- **Spec section:** project-intake checklist (top of pre-production phase)
- **Related:** D038, D040, D041 (the three components this codifies)
- **Trigger:** The pattern across D040/D041 made it clear: the AI producer consistently skipped analyzing operator-supplied reference material because the existing intake checklist didn't prompt for it. Result was multiple wasted cycles reproducing work the operator had already done.
- **Resolution:** **Asset intake is the first step of pre-production**, before character sheets, shot lists, or any generation. The checklist template (to be added as `docs/OPERATOR_ASSET_INTAKE.md`) asks:
    1. **Is there audio?** → Whisper-transcribe. If narration detected, that audio is the master track (D040).
    2. **Is there a reference video/mockup?** → Extract frames, vision-analyze, Whisper the audio, build visual-flow map.
    3. **Is there a deck/storyboard?** → Extract as per-slide PNGs, vision-analyze each slide for composition + text.
    4. **Is there existing IP art?** → Vision-extract literal page text (D035), identify font via multi-sample (D037).
    5. **Any brief / style notes?** → Read them before any generation.
- **Output of intake:** a written `operator_intent_map.md` in `02_preproduction/` that serves as authoritative reference for all downstream decisions (shot durations, narration timing, text overlay content, character compositions). Every subsequent "should X look like Y?" question is answered by cross-referencing this map, not by AI inference.
- **Non-negotiable:** this step cannot be skipped "to save time." Skipping it repeatedly cost the pilot project project three full production cycles.
- **Implementation landing:** `docs/OPERATOR_ASSET_INTAKE.md` template ships with this commit. Post-production toolkit helpers: `whisper_transcribe(audio)`, `extract_frames(video, interval_s)`, `vision_analyze_frames(frames)`, `pdf_to_pngs(pdf)`, `build_operator_intent_map(assets)`.
- **Decided by:** Pattern recognition across D040 and D041 — both were symptoms of the same root cause.

---

*Add new decisions at the top of a new date section. Keep the Index table updated when adding, resolving, or revisiting a decision.*
