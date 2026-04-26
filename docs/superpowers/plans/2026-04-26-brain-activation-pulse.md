# Brain — Activation Pulse + Organic Ripple Implementation Plan (Round 6)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Replace the per-lobe gradient sweep system (R1–R5) with discrete activation pulses (enhanced region_glow) + organic tissue ripple (`feDisplacementMap`). Body color stays unchanged (`brainGrad_unified` rose hue cycle). Per-lobe color identity moves from gradient channel to glow channel.

**Architecture:** All edits in `packages/cortex-core/cortex/builders/brain.py`. Subtractive (delete 6 lobe gradients + substitution loop) + additive (new filter + tuned glow CSS). No new helpers, no schema changes.

**Spec:** `docs/superpowers/specs/2026-04-26-brain-activation-pulse-design.md`.

---

## Task 1: Delete per-lobe wave gradients + substitution loop

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1.1: Delete all 6 per-lobe gradient defs

In `_compose_wrapper`'s `<defs>` block, find and DELETE all 6 `<linearGradient id="brainGrad_<lobe>">` blocks (frontal, parietal, occipital, temporal, cerebellum, brainstem). Each is ~9-10 lines (open tag + animateTransform + 5 stops + close tag).

After deletion, only `brainGrad_unified` remains as the brain-fill gradient. Confirm with:
```bash
grep -c 'id="brainGrad_frontal"\|id="brainGrad_parietal"\|id="brainGrad_occipital"\|id="brainGrad_temporal"\|id="brainGrad_cerebellum"\|id="brainGrad_brainstem"' packages/cortex-core/cortex/builders/brain.py
```
Expected: 0.

### Step 1.2: Delete the `brain_content_lobed` substitution loop

In `_compose_wrapper` Python prep, find and DELETE the entire block:

```python
    # Per-lobe fill substitution: paths that classify into a lobe get that
    # lobe's gradient (e.g., brainGrad_frontal). Unclassified paths keep
    # url(#brainGrad_unified) ...
    brain_content_lobed = brain_content
    for lobe, pairs in paths_by_lobe.items():
        grad_url = f"url(#brainGrad_{lobe})"
        for pid, _d in pairs:
            pattern = (
                rf'(<path\b[^>]*?\sid="{re.escape(pid)}"[^>]*?\sstyle="[^"]*?fill:)'
                rf'url\(#brainGrad_unified\)'
            )
            brain_content_lobed = re.sub(pattern, rf"\1{grad_url}", brain_content_lobed)
```

Confirm with:
```bash
grep -c 'brain_content_lobed' packages/cortex-core/cortex/builders/brain.py
```
Expected: 0.

### Step 1.3: Replace `{brain_content_lobed}` with `{brain_content}` in the SVG composition

Find the line in the f-string return value that renders `{brain_content_lobed}`. Change to `{brain_content}`.

### Step 1.4: Update integration test

The test `test_no_legacy_gradient_ids_in_output` in `packages/cortex-core/tests/test_brain_integration.py` was updated in R3 to expect the per-lobe ids to be present. Now that we're deleting them again, update the test back:

Change this block:
```python
def test_no_legacy_gradient_ids_in_output(tmp_path: Path, extreme_config: Config) -> None:
    """Old gradient defs must be gone; unified fallback + 6 per-lobe defs must be present."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    # Truly legacy ids that must never appear
    for legacy in ('id="brainGrad"', 'id="brainGradAlt"', 'id="brainGrad_specular"'):
        assert legacy not in text, f"legacy gradient {legacy} still in output"
    # Unified fallback must remain (for unclassified paths)
    assert 'id="brainGrad_unified"' in text
    # 6 per-lobe gradients must be present (R3 Task 1)
    for lobe in ("frontal", "parietal", "occipital", "temporal", "cerebellum", "brainstem"):
        assert f'id="brainGrad_{lobe}"' in text, f"per-lobe gradient missing for {lobe}"
```

To:
```python
def test_no_legacy_gradient_ids_in_output(tmp_path: Path, extreme_config: Config) -> None:
    """Only brainGrad_unified should remain — per-lobe gradients deleted in R6."""
    out = tmp_path / "brain.svg"
    build(extreme_config, out)
    text = out.read_text(encoding="utf-8")
    # Truly legacy ids that must never appear
    for legacy in (
        'id="brainGrad"', 'id="brainGradAlt"', 'id="brainGrad_specular"',
        'id="brainGrad_frontal"', 'id="brainGrad_parietal"',
        'id="brainGrad_occipital"', 'id="brainGrad_temporal"',
        'id="brainGrad_cerebellum"', 'id="brainGrad_brainstem"',
    ):
        assert legacy not in text, f"legacy gradient {legacy} still in output"
    # Unified gradient must remain (carries the rose body color)
    assert 'id="brainGrad_unified"' in text
```

### Step 1.5: Smoke build + verification

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'id="brainGrad_unified"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainGrad_frontal"\|id="brainGrad_parietal"\|id="brainGrad_occipital"\|id="brainGrad_temporal"\|id="brainGrad_cerebellum"\|id="brainGrad_brainstem"' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'url(#brainGrad_unified)' examples/rendered/extreme/brain-anatomical.svg` ≥ 100 (all brain paths now reference unified)
- `grep -c 'url(#brainGrad_frontal)\|url(#brainGrad_parietal)\|url(#brainGrad_occipital)\|url(#brainGrad_temporal)\|url(#brainGrad_cerebellum)\|url(#brainGrad_brainstem)' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'spreadMethod="repeat"' examples/rendered/extreme/brain-anatomical.svg` = 0 (was 6 from R5)
- `python -m pytest -q` → 24 passed
- Two builds → byte-identical

### Step 1.6: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py packages/cortex-core/tests/test_brain_integration.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): delete per-lobe wave gradients (replaced by region pulse next)"
```

---

## Task 2: Boost region_glow as primary lobe-color carrier

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 2.1: Bump radial gradient saturation

Find the `region_grads.append` line in `_compose_wrapper` (around line 365 in R1 source, may have moved). Currently:
```python
region_grads.append(
    f'<radialGradient id="rgrad_{key}" cx="50%" cy="50%" r="50%">'
    f'<stop offset="0%"   stop-color="{color}" stop-opacity="0.55"/>'
    f'<stop offset="55%"  stop-color="{color}" stop-opacity="0.18"/>'
    f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
    f"</radialGradient>"
)
```

Change opacities `0.55 → 0.85` and `0.18 → 0.30`:
```python
region_grads.append(
    f'<radialGradient id="rgrad_{key}" cx="50%" cy="50%" r="50%">'
    f'<stop offset="0%"   stop-color="{color}" stop-opacity="0.85"/>'
    f'<stop offset="55%"  stop-color="{color}" stop-opacity="0.30"/>'
    f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
    f"</radialGradient>"
)
```

### Step 2.2: Bump glow circle radius from 200 to 260

Find the `region_glows.append` line in `_compose_wrapper`. Currently:
```python
region_glows.append(
    f'<circle cx="{bx}" cy="{by}" r="200" fill="url(#rgrad_{key})" '
    f'class="region-glow region-pulse rg{i + 1}"/>'
)
```

Change `r="200"` → `r="260"`:
```python
region_glows.append(
    f'<circle cx="{bx}" cy="{by}" r="260" fill="url(#rgrad_{key})" '
    f'class="region-glow region-pulse rg{i + 1}"/>'
)
```

### Step 2.3: Update `.region-pulse` CSS — slower cycle + bigger scale

Find the existing `.region-pulse` CSS rules. Currently:
```
.region-pulse {{ animation: rpulse 5s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
@keyframes rpulse {{
  0%, 100% {{ opacity: 0.65; transform: scale(1); }}
  50%      {{ opacity: 1.0;  transform: scale(1.10); }}
}}
.rg1{{animation-delay:0s}}    .rg2{{animation-delay:0.6s}}
.rg3{{animation-delay:1.2s}}  .rg4{{animation-delay:1.8s}}
.rg5{{animation-delay:2.4s}}  .rg6{{animation-delay:3.0s}}
```

Replace with:
```
.region-pulse {{ animation: rpulse 8s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
@keyframes rpulse {{
  0%, 100% {{ opacity: 0.55; transform: scale(0.92); }}
  50%      {{ opacity: 1.0;  transform: scale(1.18); }}
}}
.rg1{{animation-delay:0s}}    .rg2{{animation-delay:1.3s}}
.rg3{{animation-delay:2.6s}}  .rg4{{animation-delay:3.9s}}
.rg5{{animation-delay:5.2s}}  .rg6{{animation-delay:6.5s}}
```

Three changes:
- Cycle `5s` → `8s` (slower, more cinematic breathing)
- Scale range `1↔1.10` → `0.92↔1.18` (more dramatic — glow shrinks slightly at trough, expands more at peak)
- Opacity range `0.65↔1.0` → `0.55↔1.0` (slightly deeper trough so the pulse is more noticeable)
- Delays `0s/0.6s/1.2s/1.8s/2.4s/3.0s` → `0s/1.3s/2.6s/3.9s/5.2s/6.5s` (spread across full 8s cycle for max staggering)

### Step 2.4: Smoke build + verify

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'r="260"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6 (one per region glow)
- `grep -c 'stop-opacity="0.85"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6 (one per rgrad)
- `grep -c 'stop-opacity="0.30"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6 (one per rgrad)
- `grep -c 'animation: rpulse 8s' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'animation-delay:1.3s\|animation-delay:2.6s\|animation-delay:3.9s\|animation-delay:5.2s\|animation-delay:6.5s' examples/rendered/extreme/brain-anatomical.svg` ≥ 5
- `grep -c 'animation: rpulse 5s' examples/rendered/extreme/brain-anatomical.svg` = 0 (old cycle gone)
- `python -m pytest -q` → 24 passed
- Two builds → byte-identical

### Step 2.5: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): promote region_glow to primary lobe-color carrier"
```

---

## Task 3: Add `feDisplacementMap` ripple filter

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 3.1: Add the `brainRipple` filter to `<defs>`

Find the existing `<filter id="brainGlow">` def in `_compose_wrapper`'s `<defs>` block. ADD the new filter immediately AFTER it:

```
    <filter id="brainRipple" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.018" numOctaves="2" seed="2" result="noise">
        <animate attributeName="baseFrequency" values="0.018;0.024;0.018"
                 dur="11s" repeatCount="indefinite"/>
      </feTurbulence>
      <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.5"/>
    </filter>
```

### Step 3.2: Apply the ripple filter to the brain wobble group

Find the existing wobble group in the f-string return value:
```
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="{brain_3d_class}">
        ...
```

The `brain-pulse` group has `filter="url(#brainGlow)"`. SVG doesn't support comma-separated filter values, so we need to wrap the brainGlow group in another group that applies brainRipple, OR chain the filters via nested groups.

Use the nested-group approach: wrap the existing `<g class="brain-pulse">` in a new outer group that applies brainRipple:

Change:
```
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
```

To:
```
  <g transform="translate(332,152) scale(0.7)">
    <g filter="url(#brainRipple)">
      <g class="brain-pulse" filter="url(#brainGlow)">
```

And add a matching `</g>` closing tag at the END of the brain-pulse group, BEFORE the `</g>` that closes `transform="translate(332,152) scale(0.7)"`. The structure becomes:

```
  <g transform="translate(332,152) scale(0.7)">    <!-- existing transform group -->
    <g filter="url(#brainRipple)">                  <!-- NEW: ripple wrapper -->
      <g class="brain-pulse" filter="url(#brainGlow)">  <!-- existing -->
        <g class="{brain_3d_class}">                <!-- existing wobble -->
          ... brain content ...
        </g>
      </g>
    </g>                                            <!-- NEW: close ripple wrapper -->
  </g>                                              <!-- existing close -->
```

### Step 3.3: Smoke build + verify

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'id="brainRipple"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'feDisplacementMap' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'feTurbulence' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'filter="url(#brainRipple)"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'filter="url(#brainGlow)"' examples/rendered/extreme/brain-anatomical.svg` = 1 (still present)
- XML well-formed
- `python -m pytest -q` → 24 passed
- Two builds → byte-identical (filter is deterministic via `seed="2"`)

### Step 3.4: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): organic feDisplacementMap ripple — brain anatomy breathes"
```

---

## Self-Review

**Spec coverage:**
- Delete per-lobe gradients → Task 1 (with test update)
- Boost region_glow → Task 2
- Add ripple filter → Task 3

**Type/name consistency:**
- `brainGrad_unified` is now the only brain-fill gradient (referenced by all paths)
- `rgrad_<key>` defs unchanged in name; only stop opacities tweaked
- `brainRipple` is a new filter id; `brainGlow` is unchanged
- The `.region-pulse` CSS rule and `@keyframes rpulse` are tuned but keep the same names

**Placeholder scan:** No `TBD` / `<insert>`.

**Cleanup verified:**
- Per-lobe gradient defs deleted (Task 1.1).
- `brain_content_lobed` deleted (Task 1.2).
- Reference in composition updated (Task 1.3).
- Test updated for new architecture (Task 1.4).
- Old `r="200"` for region_glows replaced with `r="260"` (Task 2.2).
- Old 5s cycle / 1.10 scale replaced with 8s / 1.18 (Task 2.3).
