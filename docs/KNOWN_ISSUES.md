# Known Issues (Non-Blocking)

Issues present in the surrounding Amplifier ecosystem that surface when loading this bundle. Non-fatal — the bundle loads and all 7 agents resolve — but worth documenting so operators don't spend time chasing them.

---

## Issue 1 — `tool-skills` protocol_compliance validator error

**Symptom** (visible in session startup output):
```
Failed to load module 'tool-skills': Module 'tool-skills' failed validation:
FAILED: 3/4 checks passed (1 errors, 0 warnings).
Errors: protocol_compliance: Error during protocol compliance check:
'str' object has no attribute 'get'
```

**Trace:**
- Raised by `amplifier_core/validation/hook.py:358` in the `_check_protocol_compliance` method's exception handler.
- Root cause is upstream in the amplifier-core hook validator's `_check_hook_methods` — it attempts `.get()` on a handler object that, in some registration paths, is a callable wrapped as a string reference rather than a class instance.
- Tool-skills registers a `SkillsVisibilityHook` whose callable binding shape trips the validator's assumptions.

**Impact:**
- `tool-skills` fails to mount. The `/skills` visibility layer is unavailable in sessions where this hits.
- Session continues. All other tools, agents, hooks, and recipes work normally.
- Agents in this bundle do not depend on `tool-skills`.

**Upstream fix required:**
- Either `amplifier-core`'s `validation/hook.py` should tolerate string-referenced handler bindings (or defer them to runtime validation), or
- `amplifier-module-tool-skills` should register its hook via a pattern that the current validator recognizes.

**Workaround:**
- None needed for this bundle. The bundle functions fully without `tool-skills`.
- If `/skills` is needed in the active session, report the full error to amplifier-core or amplifier-module-tool-skills maintainers for the upstream fix.

---

## Issue 2 — Historical: `research` bundle malformed `tools:` (FIXED upstream)

**Former symptom**:
```
Failed to compose behavior 'git+https://github.com/michaeljabbour/amplifier-bundle-research@main':
Bundle 'research' has malformed tools: expected list, got dict.
Correct format: tools: [{module: 'module-id', source: 'git+https://...'}]
```

**Root cause:** `research` bundle's `bundle.md` used the deprecated `tools: {include: [...]}` wrapper format.

**Fix pushed:** `amplifier-bundle-research@main` commit [`f9e7e7d`](https://github.com/michaeljabbour/amplifier-bundle-research/commit/f9e7e7d) — "fix(bundle): tools must be a flat list, not {include: [...]} wrapper" — converts to the flat-list form the current loader expects.

**Status:** resolved. No action needed.

---

*Add new non-blocking ecosystem issues here with full trace + impact + resolution pointer. Blocking issues go in `spec/DECISIONS.md` with a D-number entry.*
