# Brain — Vibrant Lobes & Atmospheric Depth Implementation Plan (Round 3)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Kill the metallic specular pass, restore per-lobe color identity via 6 desaturated tinted gradients (not the saturated paint-by-numbers from before), add three new background depth layers (star field + perspective grid + nebula clouds), and fix card text overflow.

**Architecture:** All edits land in `packages/cortex-core/cortex/builders/brain.py`. Per-lobe gradient substitution happens in `_compose_wrapper` via regex on `paths_by_lobe` (existing data), not in `_recolor` (which stays simple). No new schema fields.

**Spec:** `docs/superpowers/specs/2026-04-26-brain-vibrant-lobes-design.md`.

---

## Task 1: Remove specular + revive per-lobe tinted gradients

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 1.1: Delete the specular gradient def

In `_compose_wrapper`'s `<defs>` block, find and DELETE the entire `<linearGradient id="brainGrad_specular">` block. It's adjacent to `brainGrad_unified`. Confirm with:
```bash
grep -n "brainGrad_specular" packages/cortex-core/cortex/builders/brain.py
```

After deletion, the only hits should be 0.

### Step 1.2: Bump diffuse opacity back down

Find the `brainGrad_unified` def's middle stop. Change `stop-opacity="0.55"` back to `stop-opacity="0.30"`. The unified gradient is now a fallback for unclassified paths only (rare); per-lobe gradients carry the color.

### Step 1.3: Add 6 per-lobe gradient defs

Immediately AFTER `brainGrad_unified`'s closing `</linearGradient>`, ADD these 6 gradient defs (matching template format, indented 4 spaces):

```
    <linearGradient id="brainGrad_frontal" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="20s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="40%"  stop-color="{p_primary}"   stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="{p_primary}"   stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
    <linearGradient id="brainGrad_parietal" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="23s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="40%"  stop-color="{p_accent_d}"  stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="{p_accent_d}"  stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
    <linearGradient id="brainGrad_occipital" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="17s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="40%"  stop-color="{p_secondary}" stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="{p_secondary}" stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
    <linearGradient id="brainGrad_temporal" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="25s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="40%"  stop-color="{p_accent_c}"  stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="{p_accent_c}"  stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
    <linearGradient id="brainGrad_cerebellum" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="19s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="40%"  stop-color="{p_accent_a}"  stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="{p_accent_a}"  stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
    <linearGradient id="brainGrad_brainstem" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="0 0.5 0.5" to="360 0.5 0.5" dur="27s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#0E0820"/>
      <stop offset="40%"  stop-color="{p_accent_b}"  stop-opacity="0.45"/>
      <stop offset="60%"  stop-color="{p_accent_b}"  stop-opacity="0.45"/>
      <stop offset="100%" stop-color="#0E0820"/>
    </linearGradient>
```

### Step 1.4: Add per-lobe substitution in `_compose_wrapper`

In `_compose_wrapper`, find where `paths_by_lobe` is unpacked from `_ensure_classification()` (set in R1 Task 5). After `paths_by_lobe` is in scope, AND BEFORE `brain_content` is referenced in the f-string, ADD the substitution loop:

```python
    # Per-lobe fill substitution: paths that classify into a lobe get that
    # lobe's gradient (e.g., brainGrad_frontal). Unclassified paths keep
    # url(#brainGrad_unified) from _recolor's global pass — the unified
    # gradient is now just a fallback. Each lobe rotates on its own period
    # (frontal=20s, parietal=23s, etc.) so the 6 networks are never visually
    # synced.
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

### Step 1.5: Replace `brain_content` with `brain_content_lobed` in the SVG composition

Find the line in the f-string composition that renders `{brain_content}`. There should be exactly ONE such reference (the brain body fill, inside the wobble group). Change it to `{brain_content_lobed}`.

DO NOT change the lobe-stroke-layer or any other layer that uses `brain_content` derivatives — they don't exist as separate references; the overlay layer uses different data.

### Step 1.6: Delete the `brain_content_specular` block

Find and DELETE:
- The `brain_content_specular = brain_content.replace(...)` line in `_compose_wrapper`
- The `<g class="brain-specular" style="mix-blend-mode: screen">{brain_content_specular}</g>` block in the SVG composition

### Step 1.7: Smoke build + verification

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'brainGrad_specular' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'brain-specular' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'mix-blend-mode: screen' examples/rendered/extreme/brain-anatomical.svg` should drop to ≤2 (was 3 with specular; the remaining 2 are pre-existing `.region-glow` and the constellation/streaks may also reference it — actually let me re-check; the only `mix-blend-mode: screen` left should be the `.region-glow` rule's CSS = 1 or 2 instances).
- `grep -c 'id="brainGrad_frontal"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainGrad_parietal"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainGrad_occipital"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainGrad_temporal"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainGrad_cerebellum"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'id="brainGrad_brainstem"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'url(#brainGrad_frontal)' examples/rendered/extreme/brain-anatomical.svg` ≥ 20 (one per frontal-lobe path)
- `grep -c 'url(#brainGrad_unified)' examples/rendered/extreme/brain-anatomical.svg` ≤ 5 (the def itself + maybe a few unclassified paths; was ~150 before)
- `python -m pytest -q` → 24 passed
- Two builds → byte-identical (`build twice; diff -q`)

### Step 1.8: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): per-lobe tinted gradients replace silver specular"
```

---

## Task 2: Background depth layers — far stars + perspective grid + nebula clouds

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 2.1: Generate far star field (Python side)

In `_compose_wrapper`, near the other prep code (e.g., after `particle_positions` from R2-5), add:

```python
    # Far star field — 30 dim points spread deterministically across the canvas.
    # Smaller and dimmer than ambient particles; reads as deep-space depth.
    star_rng = random.Random(_seed_from_name(config.identity.name) ^ 0xDEADBEEF)
    far_stars: list[str] = []
    for _ in range(30):
        sx = star_rng.randint(40, 1360)
        sy = star_rng.randint(40, 860)
        sr = round(star_rng.uniform(0.6, 1.2), 1)
        s_op = round(star_rng.uniform(0.20, 0.50), 2)
        s_dur = star_rng.choice([8, 10, 12, 14])
        far_stars.append(
            f'<circle cx="{sx}" cy="{sy}" r="{sr}" fill="#FFFFFF" '
            f'opacity="{s_op}" class="far-star fs{s_dur}"/>'
        )
```

The `fs{s_dur}` class will be styled with a unique twinkle keyframes for each duration variant — explained in Step 2.5.

### Step 2.2: Add far-star CSS

In `_compose_wrapper`'s `<style>` block, add:

```
      .far-star {{
        animation-name: starTwinkle;
        animation-iteration-count: infinite;
        animation-timing-function: ease-in-out;
      }}
      .fs8  {{ animation-duration:  8s; }}
      .fs10 {{ animation-duration: 10s; }}
      .fs12 {{ animation-duration: 12s; }}
      .fs14 {{ animation-duration: 14s; }}
      @keyframes starTwinkle {{
        0%, 100% {{ opacity: 0.20; }}
        50%      {{ opacity: 0.85; }}
      }}
```

### Step 2.3: Generate perspective grid (Python side)

In `_compose_wrapper`, after `far_stars`, add:

```python
    # Perspective grid — thin lines forming a 80px grid across the canvas,
    # faded at edges via a radial mask. Slow diagonal drift evokes data space.
    grid_lines: list[str] = []
    for x in range(80, 1400, 80):
        grid_lines.append(
            f'<line x1="{x}" y1="0" x2="{x}" y2="900" '
            f'stroke="{p_accent_b}" stroke-width="0.5" stroke-opacity="0.06"/>'
        )
    for y in range(80, 900, 80):
        grid_lines.append(
            f'<line x1="0" y1="{y}" x2="1400" y2="{y}" '
            f'stroke="{p_accent_b}" stroke-width="0.5" stroke-opacity="0.06"/>'
        )
```

### Step 2.4: Add the gridFade radial mask def

In the `<defs>` block, add:

```
    <radialGradient id="gridFade" cx="50%" cy="50%" r="55%">
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="1"/>
      <stop offset="80%"  stop-color="#FFFFFF" stop-opacity="0.4"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
    <mask id="gridMask">
      <rect width="1400" height="900" fill="url(#gridFade)"/>
    </mask>
```

### Step 2.5: Generate nebula clouds (Python side)

In `_compose_wrapper`, after `grid_lines`, add:

```python
    # Nebula clouds — 4 large soft blurred radial gradients drifting on
    # staggered phases. More organic than aurora bands (which are flat
    # circles); these have feGaussianBlur for amorphous edges.
    nebula_blocks: list[str] = []
    nebula_specs = [
        ("#EC4899", -100, -100, 38),  # pink, top-left, 38s
        ("#7C3AED", 700, -100, 44),   # purple, top-right, 44s
        ("#22D3EE", -100, 500, 41),   # cyan, bottom-left, 41s
        ("#34D399", 700, 500, 47),    # green, bottom-right, 47s
    ]
    for n, (ncolor, nx, ny, ndur) in enumerate(nebula_specs):
        nebula_blocks.append(
            f'<g class="nebula" filter="url(#nebulaBlur)">'
            f'<rect x="{nx}" y="{ny}" width="1100" height="1100" fill="url(#nebula_{n})">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0,0; {-50 if n%2==0 else 50},{-30 if n<2 else 30}; 0,0" '
            f'dur="{ndur}s" repeatCount="indefinite"/>'
            f'</rect></g>'
        )
```

### Step 2.6: Add nebula gradient defs + nebulaBlur filter

In the `<defs>` block, add:

```
    <radialGradient id="nebula_0" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#EC4899" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#EC4899" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_1" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#7C3AED" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_2" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#22D3EE" stop-opacity="0.08"/>
      <stop offset="60%"  stop-color="#22D3EE" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="nebula_3" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#34D399" stop-opacity="0.08"/>
      <stop offset="60%"  stop-color="#34D399" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#34D399" stop-opacity="0"/>
    </radialGradient>
    <filter id="nebulaBlur" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="40"/>
    </filter>
```

### Step 2.7: Wire all 3 layers into the SVG composition

Find the existing aurora `<g class="aurora">` block in the f-string. The new layers go BETWEEN bgRadial/bgAura (background) and aurora (which is already a midground layer). Insert these blocks in this order, all gated by `atm.show_aura`:

```
  {('''<!-- Far star field: 30 dim points twinkling at deep-space distance.
       Each star uses a CSS class fs8/fs10/fs12/fs14 for varied twinkle speed. -->
  <g class="stars">
  ''' + chr(10).join("    " + s for s in far_stars) + '''
  </g>''') if atm.show_aura else ""}

  {('''<!-- Perspective grid: 80px grid lines, edge-faded via radial mask, slow drift. -->
  <g class="grid" mask="url(#gridMask)">
    <g>
      <animateTransform attributeName="transform" type="translate"
                        values="0,0; 40,30; 0,0" dur="50s" repeatCount="indefinite"/>
  ''' + chr(10).join("      " + ln for ln in grid_lines) + '''
    </g>
  </g>''') if atm.show_aura else ""}

  {('''<!-- Nebula clouds: 4 large blurred radial gradients drifting slowly.
       More organic than aurora bands; adds color depth behind the brain. -->
  <g class="nebulae">
  ''' + chr(10).join("    " + n for n in nebula_blocks) + '''
  </g>''') if atm.show_aura else ""}
```

Place this block AFTER the existing bgAura rect rendering, BEFORE the aurora `<g class="aurora">` block (the 3 aurora bands from R2-1).

### Step 2.8: Smoke build + verification

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'class="far-star fs' examples/rendered/extreme/brain-anatomical.svg` = 30
- `grep -c '@keyframes starTwinkle' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c '<line x1=.*stroke="#' examples/rendered/extreme/brain-anatomical.svg` ≥ 28 (16 vertical + 11 horizontal grid lines)
- `grep -c 'class="grid"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'mask="url(#gridMask)"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'class="nebula"' examples/rendered/extreme/brain-anatomical.svg` = 4
- `grep -c 'id="nebula_0"\|id="nebula_1"\|id="nebula_2"\|id="nebula_3"' examples/rendered/extreme/brain-anatomical.svg` = 4
- `grep -c 'id="nebulaBlur"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `python -m pytest -q` → 24 passed
- XML well-formed
- Two builds → byte-identical

### Step 2.9: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): far stars + perspective grid + nebula clouds — atmospheric depth"
```

---

## Task 3: Fix card text overflow

**Files:** Modify `packages/cortex-core/cortex/builders/brain.py`

### Step 3.1: Update typography in `<style>` block

Find the existing CSS rules:

```css
.t-cat-cap   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: 0.30em; text-transform: uppercase; }}
.t-region    {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 24px; fill: #FFFFFF; }}
.t-skill     {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 18px; fill: #E5E7EB; }}
```

Update to:

```css
.t-cat-cap   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: 0.25em; text-transform: uppercase; }}
.t-region    {{ font-family: 'Inter', sans-serif; font-weight: 700; font-size: 22px; fill: #FFFFFF; }}
.t-skill     {{ font-family: 'JetBrains Mono', monospace; font-weight: 500; font-size: 16px; fill: #E5E7EB; }}
```

Three changes: cap letter-spacing 0.30em → 0.25em; region font-size 24px → 22px; skill font-size 18px → 16px.

### Step 3.2: Smoke build + verification

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'letter-spacing: 0.25em' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `grep -c 'letter-spacing: 0.30em' examples/rendered/extreme/brain-anatomical.svg` = 0 (the old setting is gone)
- `grep -c 'font-size: 22px' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `grep -c 'font-size: 16px' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `python -m pytest -q` → 24 passed

### Step 3.3: Commit

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "fix(brain): tighten card typography to prevent text overflow"
```

---

## Task 4: Final regen + visual eyeball

This task verifies the complete Round 3 result.

- [ ] **Step 4.1: Final regen + lint sweep**

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
python -m ruff check packages/cortex-core/cortex/builders/brain.py
python -m pytest
```

Expected:
- Build succeeds.
- Ruff clean.
- 24 tests pass.

- [ ] **Step 4.2: Determinism final check**

```bash
python -c "
import yaml
from cortex.builders.brain import build
from cortex.schema import Config
cfg = Config.model_validate(yaml.safe_load(open('examples/extreme.yml', encoding='utf-8')))
build(cfg, '/tmp/r3-final-a.svg')
build(cfg, '/tmp/r3-final-b.svg')
"
diff -q /tmp/r3-final-a.svg /tmp/r3-final-b.svg
```
Expected: empty output (files identical).

- [ ] **Step 4.3: Final structural verification**

Check the rendered SVG has all expected layers:
- `grep -c 'class="brain-3d"\|class="brain-pulse"\|class="lobe-stroke-layer"\|class="arc-network"' examples/rendered/extreme/brain-anatomical.svg` = 4
- `grep -c 'class="aurora"\|class="grid"\|class="nebulae"\|class="stars"\|class="constellation"\|class="streaks"' examples/rendered/extreme/brain-anatomical.svg` = 6
- `grep -c 'brainGrad_unified\|brainGrad_frontal\|brainGrad_parietal\|brainGrad_occipital\|brainGrad_temporal\|brainGrad_cerebellum\|brainGrad_brainstem' examples/rendered/extreme/brain-anatomical.svg` ≥ 7 (one def per name)
- `grep -c 'brainGrad_specular\|class="brain-specular"' examples/rendered/extreme/brain-anatomical.svg` = 0

If anything fails, fix on the same branch before reporting done.

- [ ] **Step 4.4: No commit needed** (Task 1–3 already regenerated the showcase as part of their commits; if Step 4.1 produces a diff, run it now and commit as a no-op fix).

---

## Self-Review

**Spec coverage:**
- Kill specular + revive per-lobe gradients → Task 1
- Background depth (stars + grid + nebula) → Task 2
- Text overflow fix → Task 3
- Final verification → Task 4

**Type/name consistency:**
- `brain_content_lobed` (Task 1) is a string used in the SVG composition (replaces the old `brain_content` reference).
- `far_stars`, `grid_lines`, `nebula_blocks` (Task 2) are `list[str]` joined into the f-string composition.
- All 6 lobe gradient ids match `brainGrad_<lobe>` for the 6 keys in `_LOBE_KEYS`.
- All 4 nebula gradient ids `nebula_0..nebula_3` map to the 4 entries in `nebula_specs`.

**Placeholder scan:** No `TBD` / `<insert>` / `TODO` left.

**Cleanup verified:**
- Specular gradient def + variable + composition block all deleted in Task 1.
- Old `mix-blend-mode: screen` count drops from 3 → 1 (only `.region-glow` keeps it).
