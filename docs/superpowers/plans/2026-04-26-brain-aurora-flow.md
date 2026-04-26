# Brain — Aurora Flow Implementation Plan (Round 7)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Replace region_glow circles with brain-shape-masked aurora flow (4 large palette-colored radial gradients drifting freely through the canvas, masked by the brain anatomy). Push the brain down +58px to clear card overlap. Remove the rgrad/region_glow system entirely.

**Architecture:** Three coordinated changes in `_compose_wrapper`: build mask paths from `paths_by_lobe`, add `<mask>` def + 4 aurora gradient defs, replace region_glow composition with the masked aurora flow group, shift brain transform y from 152→210 in three places (wobble group, mask group, classifier formula).

**Spec:** `docs/superpowers/specs/2026-04-26-brain-aurora-flow-design.md`.

---

## Task 1: Push brain down (+58px on y axis)

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1: Update centroid formula in `_classify_brain_paths`

Find the line:
```python
canvas_centroids[lobe] = (round(ax * 0.7 + 332), round(ay * 0.7 + 152))
```
Change `152` → `210`.

Also update the FALLBACK line right after (the one that fires if a lobe has no centroids):
```python
canvas_centroids[lobe] = (700, 400)  # fallback to brain center
```
Adjust if needed, or leave (700, 400) if it's a sane fallback.

Also update the docstring mention of the offset if there is one (search for "152" comments):
```bash
grep -n "+ 152" packages/cortex-core/cortex/builders/brain.py
```
Each match in `_classify_brain_paths` should be updated to 210.

### Step 2: Update brain wobble group transform

In `_compose_wrapper`'s f-string return value, find:
```
<g transform="translate(332,152) scale(0.7)">
```
Change `152` → `210`. Result:
```
<g transform="translate(332,210) scale(0.7)">
```

There should be ONE such reference (the brain wrapper group). Confirm with:
```bash
grep -n "translate(332," packages/cortex-core/cortex/builders/brain.py
```

### Step 3: Smoke build + verify

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'translate(332,210)' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `grep -c 'translate(332,152)' examples/rendered/extreme/brain-anatomical.svg` = 0
- `python -m pytest -q` → 24 passed
- Leader-line endpoints in the rendered SVG point to lobe centroids that are now ~58px lower (visually verify in browser if convenient)
- Two builds → byte-identical

### Step 4: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): shift brain down +58px to clear card overlap"
```

---

## Task 2: Delete region_glow system entirely

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1: Delete the `region_grads.append` block

In `_compose_wrapper` Python prep, find:

```python
# Per-region radial gradient — used by the region glow inside brain-3d.
# Soft falloff: full color at center, fading to transparent at edge.
region_grads.append(
    f'<radialGradient id="rgrad_{key}" cx="50%" cy="50%" r="50%">'
    f'<stop offset="0%"   stop-color="{color}" stop-opacity="0.85"/>'
    f'<stop offset="55%"  stop-color="{color}" stop-opacity="0.30"/>'
    f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
    f"</radialGradient>"
)
```

DELETE these lines (the comment + the append).

Also find the `region_grads: list[str] = []` initialization a few lines before — DELETE it too.

### Step 2: Delete the `region_glows.append` block

Find:
```python
region_glows.append(
    f'<circle cx="{bx}" cy="{by}" r="260" fill="url(#rgrad_{key})" '
    f'class="region-glow region-pulse rg{i + 1}"/>'
)
```

DELETE. Also delete the `region_glows: list[str] = []` initialization.

### Step 3: Remove the `region_grads` injection in `<defs>`

Find in the f-string:
```
{chr(10).join("    " + g for g in region_grads)}
```
DELETE this line.

### Step 4: Remove the `region_glows` injection in body

Find in the f-string brain composition:
```
{chr(10).join("        " + rg for rg in region_glows)}
```
DELETE this line.

### Step 5: Delete the region-glow CSS rules

In the `<style>` block, find and DELETE:
```
.region-glow {{ mix-blend-mode: screen; }}
.region-pulse {{ animation: rpulse 8s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
@keyframes rpulse {{
  0%, 100% {{ opacity: 0.55; transform: scale(0.92); }}
  50%      {{ opacity: 1.0;  transform: scale(1.18); }}
}}
.rg1{{animation-delay:0s}}    .rg2{{animation-delay:1.3s}}
.rg3{{animation-delay:2.6s}}  .rg4{{animation-delay:3.9s}}
.rg5{{animation-delay:5.2s}}  .rg6{{animation-delay:6.5s}}
```

DELETE all these rules. The `mix-blend-mode: screen` may also appear elsewhere — only delete the `.region-glow` rule, not other usages.

### Step 6: Smoke build + verify

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'class="region-glow' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'class="region-pulse' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c '@keyframes rpulse' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'id="rgrad_' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'url(#rgrad_' examples/rendered/extreme/brain-anatomical.svg` = 0
- `python -m pytest -q` → 24 passed (existing tests don't reference region_glow)
- XML well-formed
- Two builds → byte-identical

### Step 7: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): delete region_glow circles (replaced by aurora flow next)"
```

---

## Task 3: Add brain-masked aurora flow

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1: Build the brain mask paths in Python prep

In `_compose_wrapper`, near the other prep code (e.g., after `paths_by_lobe` is unpacked from `_ensure_classification`), ADD:

```python
    # Mask source: each brain path's d attribute as a minimal
    # <path d="..." fill="white"/> for inclusion in <mask id="brainMask">.
    # The mask is opaque wherever brain anatomy exists, transparent elsewhere
    # — so the aurora flow layer below shows only inside the brain shape.
    brain_mask_paths: list[str] = []
    for _lobe, pairs in paths_by_lobe.items():
        for _pid, d in pairs:
            brain_mask_paths.append(f'<path d="{d}" fill="white"/>')
```

(Match surrounding 4-space indent.)

### Step 2: Add the mask def in `<defs>`

In the f-string return value, find the existing `<defs>` block. Inside `<defs>`, anywhere convenient (e.g., right after `gradientFade`/aurora gradient defs, but BEFORE the closing `</defs>`), ADD:

```
    <mask id="brainMask">
      <g transform="translate(332,210) scale(0.7)">
      {chr(10).join("        " + p for p in brain_mask_paths)}
      </g>
    </mask>
```

The transform must match the brain wobble group transform (R7 Task 1 changed it to `translate(332,210)`).

### Step 3: Add 4 brainAurora radial gradient defs

In the same `<defs>` block, ADD:

```
    <radialGradient id="brainAurora_a" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="#EC4899" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#EC4899" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="brainAurora_b" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#22D3EE" stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="#22D3EE" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="brainAurora_c" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#A78BFA" stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="#A78BFA" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#A78BFA" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="brainAurora_d" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#34D399" stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="#34D399" stop-opacity="0.18"/>
      <stop offset="100%" stop-color="#34D399" stop-opacity="0"/>
    </radialGradient>
```

### Step 4: Add the aurora flow group inside the brain wobble group

In the f-string, find the brain wobble group composition. Currently it looks roughly like:

```
  <g transform="translate(332,210) scale(0.7)">
    <g filter="url(#brainRipple)">
      <g class="brain-pulse" filter="url(#brainGlow)">
        <g class="{brain_3d_class}">
          {brain_content}
          (region_glows line was here — deleted in Task 2)
          <g class="lobe-stroke-layer" filter="url(#electricGlow)">
            ...stroke overlay...
          </g>
          <g class="arc-network" filter="url(#electricGlow)">
            ...arcs + cells...
          </g>
          ...halos, spark dots...
        </g>
      </g>
    </g>
  </g>
```

INSERT a new aurora flow group BETWEEN `{brain_content}` and the lobe-stroke-layer:

```
        <!-- Aurora flow inside the brain anatomy: 4 large palette-colored
             radial gradients drifting freely, masked by the brain shape so
             colors are visible only inside the anatomy. Replaces R6 region_glow. -->
        <g mask="url(#brainMask)" class="brain-aurora">
          <rect x="-100" y="0" width="900" height="900" fill="url(#brainAurora_a)">
            <animateTransform attributeName="transform" type="translate"
                              values="0,0; 600,200; 0,0" dur="32s" repeatCount="indefinite"/>
          </rect>
          <rect x="600" y="0" width="900" height="900" fill="url(#brainAurora_b)">
            <animateTransform attributeName="transform" type="translate"
                              values="0,0; -500,250; 0,0" dur="38s" repeatCount="indefinite"/>
          </rect>
          <rect x="200" y="-100" width="900" height="900" fill="url(#brainAurora_c)">
            <animateTransform attributeName="transform" type="translate"
                              values="0,0; 200,400; 0,0" dur="41s" repeatCount="indefinite"/>
          </rect>
          <rect x="-100" y="500" width="900" height="900" fill="url(#brainAurora_d)">
            <animateTransform attributeName="transform" type="translate"
                              values="0,0; 700,-300; 0,0" dur="45s" repeatCount="indefinite"/>
          </rect>
        </g>
```

(Match the surrounding indentation — 8 spaces seems right.)

### Step 5: Verify Python imports cleanly

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
python -c "from cortex.builders.brain import _compose_wrapper; print('IMPORTS OK')"
```

### Step 6: Smoke build + verification

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'id="brainMask"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c '<mask id="brainMask">' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'fill="white"' examples/rendered/extreme/brain-anatomical.svg` ≥ 200 (one per brain path in the mask)
- `grep -c 'mask="url(#brainMask)"' examples/rendered/extreme/brain-anatomical.svg` = 1 (the brain-aurora group reference)
- `grep -c 'id="brainAurora_a"' examples/rendered/extreme/brain-anatomical.svg` = 1 (gradient def)
- `grep -c 'id="brainAurora_b"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainAurora_c"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainAurora_d"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'class="brain-aurora"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'url(#brainAurora_' examples/rendered/extreme/brain-anatomical.svg` ≥ 4 (one fill ref per aurora rect)
- `grep -c 'dur="32s"\|dur="38s"\|dur="41s"\|dur="45s"' examples/rendered/extreme/brain-anatomical.svg` ≥ 4

XML well-formed:
```bash
python -c "import xml.etree.ElementTree as ET; ET.parse('examples/rendered/extreme/brain-anatomical.svg'); print('XML OK')"
```

Run unit tests:
```bash
python -m pytest -q
```
Expected: 24 passed.

Determinism check:
```bash
python -c "
import yaml, os, filecmp
from cortex.builders.brain import build
from cortex.schema import Config
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml', encoding='utf-8')))
out_a = os.path.expanduser('~/r7-3-a.svg')
out_b = os.path.expanduser('~/r7-3-b.svg')
build(cfg, out_a)
build(cfg, out_b)
print('identical:', filecmp.cmp(out_a, out_b, shallow=False))
"
```
Expected: `identical: True`.

### Step 7: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): aurora flow through brain anatomy via mask"
```

---

## Self-Review

**Spec coverage:**
- Push brain down (+58px) → Task 1
- Delete region_glow → Task 2
- Add brain-masked aurora flow → Task 3

**Type/name consistency:**
- `brain_mask_paths` is a `list[str]` (paths with white fill)
- `brainMask` is the mask id (singular)
- `brainAurora_a/b/c/d` are 4 unique gradient ids
- `brain-aurora` is the class name on the mask group

**Placeholder scan:** No `TBD` / `<insert>`.

**Cleanup verified:**
- All region_glow / rgrad / .region-pulse / @keyframes rpulse / .rg1-.rg6 removed in Task 2.
- Brain transform 152 → 210 in three places (wobble, mask, classifier) in Tasks 1 + 3.
