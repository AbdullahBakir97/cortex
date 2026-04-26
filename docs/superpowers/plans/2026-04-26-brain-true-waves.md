# Brain — True Waves Implementation Plan (Round 5)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development.

**Goal:** Replace `<animateTransform type="rotate">` on the 6 per-lobe gradients with `type="translate">`, add `spreadMethod="repeat"`, and set unique direction vectors per lobe so each shows a directional wave instead of a rotating band.

**Architecture:** Per-lobe gradient animations only. No structural changes. No new helpers. No CSS changes. The unified gradient (`brainGrad_unified`) stays rotating because its 4-stop rose-family pattern doesn't read as a spinner.

**Spec:** `docs/superpowers/specs/2026-04-26-brain-true-waves-design.md`.

---

## Task 1: Switch all 6 per-lobe gradients from rotate → translate

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1: Replace each per-lobe gradient with the wave variant

Find each of the 6 per-lobe gradient defs in `_compose_wrapper`'s `<defs>` block. Currently each looks like:

```xml
<linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="1"
                gradientUnits="objectBoundingBox">
  <animateTransform attributeName="gradientTransform" type="rotate"
                    from="0 0.5 0.5" to="360 0.5 0.5" dur="20s" repeatCount="indefinite"/>
  <stop offset="0%"   stop-color="#3A1A28"/>
  <stop offset="45%"  stop-color="#3A1A28"/>
  <stop offset="50%"  stop-color="{p_primary}" stop-opacity="0.40"/>
  <stop offset="55%"  stop-color="#3A1A28"/>
  <stop offset="100%" stop-color="#3A1A28"/>
</linearGradient>
```

Replace ALL 6 with these EXACT specifications. Each has unique `x1/y1/x2/y2`, `from/to` translate values, and `dur`. The 5 stops are unchanged.

**brainGrad_frontal — horizontal LTR wave, 10s:**
```xml
    <linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="0"
                    gradientUnits="objectBoundingBox" spreadMethod="repeat">
      <animateTransform attributeName="gradientTransform" type="translate"
                        from="0 0" to="1 0" dur="10s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_primary}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

**brainGrad_parietal — vertical TTB wave, 12s:**
```xml
    <linearGradient id="brainGrad_parietal" x1="0" y1="0" x2="0" y2="1"
                    gradientUnits="objectBoundingBox" spreadMethod="repeat">
      <animateTransform attributeName="gradientTransform" type="translate"
                        from="0 0" to="0 1" dur="12s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_accent_d}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

**brainGrad_occipital — horizontal RTL wave, 9s:**
```xml
    <linearGradient id="brainGrad_occipital" x1="1" y1="0" x2="0" y2="0"
                    gradientUnits="objectBoundingBox" spreadMethod="repeat">
      <animateTransform attributeName="gradientTransform" type="translate"
                        from="0 0" to="1 0" dur="9s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_secondary}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

**brainGrad_temporal — diagonal up-right wave, 14s:**
```xml
    <linearGradient id="brainGrad_temporal" x1="0" y1="1" x2="1" y2="0"
                    gradientUnits="objectBoundingBox" spreadMethod="repeat">
      <animateTransform attributeName="gradientTransform" type="translate"
                        from="0 0" to="1 -1" dur="14s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_accent_c}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

**brainGrad_cerebellum — diagonal down-right wave, 11s:**
```xml
    <linearGradient id="brainGrad_cerebellum" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox" spreadMethod="repeat">
      <animateTransform attributeName="gradientTransform" type="translate"
                        from="0 0" to="1 1" dur="11s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_accent_a}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

**brainGrad_brainstem — vertical BTT wave, 13s:**
```xml
    <linearGradient id="brainGrad_brainstem" x1="0" y1="1" x2="0" y2="0"
                    gradientUnits="objectBoundingBox" spreadMethod="repeat">
      <animateTransform attributeName="gradientTransform" type="translate"
                        from="0 0" to="0 1" dur="13s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#3A1A28"/>
      <stop offset="45%"  stop-color="#3A1A28"/>
      <stop offset="50%"  stop-color="{p_accent_b}" stop-opacity="0.40"/>
      <stop offset="55%"  stop-color="#3A1A28"/>
      <stop offset="100%" stop-color="#3A1A28"/>
    </linearGradient>
```

KEY changes per gradient:
1. `type="rotate"` → `type="translate"`
2. `from="0 0.5 0.5" to="360 0.5 0.5"` → unique translate `from`/`to` per lobe
3. `gradientUnits="objectBoundingBox"` keeps + ADD `spreadMethod="repeat"`
4. `x1/y1/x2/y2` updated to set wave direction (each lobe gets a unique direction)
5. `dur` value updated (each lobe gets a unique duration: 10/12/9/14/11/13s)

The 5 STOP elements are unchanged — same colors, same opacity, same offsets.

### Step 2: Verify Python imports cleanly

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
python -c "from cortex.builders.brain import _compose_wrapper; print('IMPORTS OK')"
```

### Step 3: Smoke build + verification

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify in the output SVG:
- `grep -c 'type="rotate"' examples/rendered/extreme/brain-anatomical.svg` should DROP — was ~6+ before (1 unified + 6 per-lobe), now just 1 (the unified gradient still rotates). Could also be more if there are other rotate animations, but the COUNT should decrease by exactly 6.
- `grep -c 'type="translate"' examples/rendered/extreme/brain-anatomical.svg` should INCREASE by 6 (the new lobe wave animations) plus any existing translate animations (aurora bands have 3, nebula has 4, bgAura has 1).
- `grep -c 'spreadMethod="repeat"' examples/rendered/extreme/brain-anatomical.svg` = 6 (one per lobe gradient).
- `grep -c 'from="0 0" to="1 0"' examples/rendered/extreme/brain-anatomical.svg` = 2 (frontal LTR + occipital RTL — same translate values, different x1/x2 give different wave directions)
- `grep -c 'from="0 0" to="0 1"' examples/rendered/extreme/brain-anatomical.svg` = 2 (parietal TTB + brainstem BTT)
- `grep -c 'from="0 0" to="1 -1"' examples/rendered/extreme/brain-anatomical.svg` = 1 (temporal diagonal ↗)
- `grep -c 'from="0 0" to="1 1"' examples/rendered/extreme/brain-anatomical.svg` = 1 (cerebellum diagonal ↘)
- `grep -c 'dur="9s"\|dur="10s"\|dur="11s"\|dur="12s"\|dur="13s"\|dur="14s"' examples/rendered/extreme/brain-anatomical.svg` ≥ 6 (the 6 lobe durations)
- All 6 per-lobe gradient ids still present (`grep -c 'id="brainGrad_frontal"'` etc. = 1 each)
- Stop offsets unchanged (`grep -c 'offset="45%"' = 6`, `grep -c 'offset="55%"' = 6`)
- `grep -c 'stop-opacity="0.40"' examples/rendered/extreme/brain-anatomical.svg` = 6 (unchanged)

Run unit tests:
```bash
python -m pytest -q
```
Expected: 24 passed.

XML well-formed:
```bash
python -c "import xml.etree.ElementTree as ET; ET.parse('examples/rendered/extreme/brain-anatomical.svg'); print('XML OK')"
```

Determinism check:
```bash
python -c "
import yaml, os, filecmp
from cortex.builders.brain import build
from cortex.schema import Config
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml', encoding='utf-8')))
out_a = os.path.expanduser('~/r5-a.svg')
out_b = os.path.expanduser('~/r5-b.svg')
build(cfg, out_a)
build(cfg, out_b)
print('identical:', filecmp.cmp(out_a, out_b, shallow=False))
"
```
Expected: `identical: True`.

### Step 4: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): translate-based wave gradients replace per-lobe spinners"
```

---

## Self-Review

**Spec coverage:** Task 1 implements all 6 per-lobe gradient changes (rotate → translate + spreadMethod=repeat + unique directions/durations). The unified gradient is intentionally NOT changed (per spec rationale).

**Type/name consistency:** All 6 lobe gradient ids stay the same (`brainGrad_<lobe>`). Lobe-color mapping stays the same (`p_primary`, `p_accent_d`, etc.). Stop offsets and opacity stay the same. Only animation type, direction vectors, and durations change.

**Placeholder scan:** No `TBD` / `<insert>` / `TODO` left.

**Cleanup verified:**
- No `type="rotate"` on per-lobe gradients (only on `brainGrad_unified`).
- No leftover `from="0 0.5 0.5"` rotation values on per-lobe gradients.
- All 6 lobe gradients have `spreadMethod="repeat"`.
