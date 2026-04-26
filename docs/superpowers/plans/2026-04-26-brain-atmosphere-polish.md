# Brain — Atmosphere & Polish Implementation Plan (Round 2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task.

**Goal:** Replace the `feTurbulence` plasma fog with aurora bands (A), add a specular highlight overlay on the brain body for liquid-glass depth (D), polish the lobe cards with traveling edge glow + inner pulse + stacked shadow + typography (B), and make the canvas atmosphere lively via constellation lines + light streaks + animated background aura (C).

**Architecture:** All edits land in `packages/cortex-core/cortex/builders/brain.py`. No new schema fields. Same `feature/brain-professional-visuals` branch as Round 1.

**Tech Stack:** Python 3.10+, SVG 1.1 with SMIL + CSS. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-04-26-brain-atmosphere-polish-design.md`.

---

## Task 1: A — Aurora bands (replace plasma fog)

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Delete the `plasmaFog` filter def and its `<rect>`**

In `_compose_wrapper`, delete the entire `<filter id="plasmaFog">` block (around lines 609-618 — search `id="plasmaFog"`). Also delete the `<rect ... filter="url(#plasmaFog)" .../>` (around line 711 — search `filter="url(#plasmaFog)"`).

- [ ] **Step 2: Add 3 aurora radial gradient defs**

In the `<defs>` block (anywhere is fine — recommended right after `bgAura`), add:

```
    <radialGradient id="aurora_a" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#EC4899" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#EC4899" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#EC4899" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aurora_b" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#7C3AED" stop-opacity="0.10"/>
      <stop offset="60%"  stop-color="#7C3AED" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#7C3AED" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="aurora_c" cx="50%" cy="50%" r="50%">
      <stop offset="0%"   stop-color="#22D3EE" stop-opacity="0.08"/>
      <stop offset="60%"  stop-color="#22D3EE" stop-opacity="0.03"/>
      <stop offset="100%" stop-color="#22D3EE" stop-opacity="0"/>
    </radialGradient>
```

- [ ] **Step 3: Add 3 aurora `<rect>` elements with translate animations**

Replace the deleted `<rect ... filter="url(#plasmaFog)" .../>` with this block (gated by `atm.show_aura`, same as before). The 3 rects sit BELOW everything else and ABOVE the bgAura.

Find the existing line that renders bgAura+plasmaFog. After deleting plasmaFog rect, replace with:

```python
  {('''<!-- Aurora bands: 3 large soft radial gradients drifting across the canvas
       on staggered timers. Replaces feTurbulence plasma fog with smooth color
       flow that reads as atmospheric light, not noise. -->
  <g class="aurora">
    <rect x="-200" y="-200" width="900" height="900" fill="url(#aurora_a)">
      <animateTransform attributeName="transform" type="translate" 
                        values="0,0; 200,150; 0,0" dur="28s" repeatCount="indefinite"/>
    </rect>
    <rect x="700" y="200" width="900" height="900" fill="url(#aurora_b)">
      <animateTransform attributeName="transform" type="translate" 
                        values="0,0; -180,-120; 0,0" dur="35s" repeatCount="indefinite"/>
    </rect>
    <rect x="200" y="500" width="900" height="900" fill="url(#aurora_c)">
      <animateTransform attributeName="transform" type="translate" 
                        values="0,0; 160,-80; 0,0" dur="31s" repeatCount="indefinite"/>
    </rect>
  </g>''') if atm.show_aura else ""}
```

- [ ] **Step 4: Smoke build + verification**

```bash
cd C:/Users/abdul/Projects/cortex/src/.worktrees/brain-pro
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'plasmaFog' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'feTurbulence' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'id="aurora_a"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'class="aurora"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `python -m pytest -q` → 24 passed

- [ ] **Step 5: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): aurora bands replace feTurbulence plasma fog"
```

---

## Task 2: D — Brain specular highlight pass

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Add the specular gradient def**

In the `<defs>` block, immediately AFTER the existing `brainGrad_unified` def, add:

```
    <linearGradient id="brainGrad_specular" x1="0" y1="0" x2="1" y2="1"
                    gradientUnits="objectBoundingBox">
      <animateTransform attributeName="gradientTransform" type="rotate"
                        from="45 0.5 0.5" to="405 0.5 0.5" dur="18s" repeatCount="indefinite"/>
      <stop offset="0%"   stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="42%"  stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="50%"  stop-color="#FFFFFF" stop-opacity="0.40"/>
      <stop offset="58%"  stop-color="#FFFFFF" stop-opacity="0"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
```

- [ ] **Step 2: Bump the diffuse gradient's accent stop**

Find the line in `brainGrad_unified` that says `stop-color="{p_accent_b}" stop-opacity="0.40"` and change `0.40` to `0.55`.

- [ ] **Step 3: Build the specular content (Python side, in `_compose_wrapper`)**

Find the line where `brain_content` is referenced inside the composition. Right before `_compose_wrapper`'s `return f"""..."""`, add a new variable that creates the specular version of the brain content via simple string substitution:

```python
    # Specular highlight overlay: render the brain content again with the
    # diffuse gradient swapped for the specular gradient. The specular gradient
    # is mostly transparent except for one bright thin band at the middle stop;
    # rotating at 18s (vs. 30s for diffuse) on a different start angle gives the
    # brain a "light catching off curved surface" feel — the visual signature
    # of liquid glass / metallic 3D.
    brain_content_specular = brain_content.replace(
        "url(#brainGrad_unified)", "url(#brainGrad_specular)"
    )
```

Place this right after `brain_content` is recolored / available — likely around the same place where `lobe_stroke_overlay` is built.

- [ ] **Step 4: Wire the specular overlay into the SVG composition**

Find the existing brain composition block:

```
  <g transform="translate(332,152) scale(0.7)">
    <g class="brain-pulse" filter="url(#brainGlow)">
      <g class="{brain_3d_class}">
        {brain_content}
        ...
```

Insert the specular layer IMMEDIATELY AFTER `{brain_content}` and BEFORE `{region_glows}`. The new layer:

```
        <g class="brain-specular" style="mix-blend-mode: screen">
        {brain_content_specular}
        </g>
```

Note: `style="mix-blend-mode: screen"` is set inline (CSS-in-attribute) because GitHub's SVG sanitizer is more reliable with inline style than with class+CSS for blend modes.

- [ ] **Step 5: Smoke build + verification**

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'brainGrad_specular' examples/rendered/extreme/brain-anatomical.svg` ≥ 100 (one ref per brain path + 1 def = ~150)
- `grep -c 'class="brain-specular"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'mix-blend-mode: screen' examples/rendered/extreme/brain-anatomical.svg` = 1
- `python -m pytest -q` → 24 passed

- [ ] **Step 6: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): specular highlight pass — liquid-glass depth on body"
```

---

## Task 3: B1 — Card traveling edge glow

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Update the card composition (in `_compose_wrapper`)**

Find the per-region card composition. Currently it produces (paraphrased):

```python
region_blocks.append(
    f'<g transform="translate({lx},{ly})"><g class="label-fade lf{i + 1}">'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardBg)" '
    f'stroke="{color}" stroke-width="1.8" filter="url(#cardShadow)"/>'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardHighlight)"/>'
    f'<rect x="0" y="0" width="320" height="4" rx="2" fill="{color}" class="breathe-stripe"/>'
    ...
)
```

Make these changes:
1. **Drop the `stroke="{color}" stroke-width="1.8"` from the base rect** (no longer needed — the new edge rect provides this).
2. **Delete the `breathe-stripe` rect** entirely.
3. **Add a new edge-glow rect** between the base rect and the highlight rect. The new rect is the colored animated outline.

The new card composition should look like:

```python
region_blocks.append(
    f'<g transform="translate({lx},{ly})"><g class="label-fade lf{i + 1}">'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardBg)" '
    f'filter="url(#cardShadow)"/>'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="none" '
    f'stroke="{color}" stroke-width="2" pathLength="1000" '
    f'class="card-edge ce{i + 1}"/>'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardHighlight)"/>'
    f'<text x="160" y="38" class="t-cat-cap" text-anchor="middle" fill="{color}">{cap}</text>'
    f'<text x="160" y="80" class="t-region" text-anchor="middle">{emoji} {domain}</text>'
    f'<text x="160" y="116" class="t-skill" text-anchor="middle">{tools_preview}</text>'
    f"</g></g>"
)
```

- [ ] **Step 2: Add CSS for `.card-edge`**

In the `<style>` block, find the `.breathe-stripe` rule and **delete** both `.breathe-stripe` and `@keyframes stripeBreathe`. Then add (near the top of the `<style>` block, anywhere before `.lobe-stroke`):

```css
      .card-edge {{
        stroke-dasharray: 80 1000;
        animation: cardEdgeTravel 4s linear infinite;
        filter: url(#electricGlow);
        opacity: 0.95;
      }}
      @keyframes cardEdgeTravel {{ to {{ stroke-dashoffset: -1080; }} }}
      .ce1 {{ animation-delay: 0s; }}
      .ce2 {{ animation-delay: 0.7s; }}
      .ce3 {{ animation-delay: 1.4s; }}
      .ce4 {{ animation-delay: 2.1s; }}
      .ce5 {{ animation-delay: 2.8s; }}
      .ce6 {{ animation-delay: 3.5s; }}
```

- [ ] **Step 3: Smoke build + verify**

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'class="card-edge ce' examples/rendered/extreme/brain-anatomical.svg` = 6
- `grep -c '@keyframes cardEdgeTravel' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'breathe-stripe' examples/rendered/extreme/brain-anatomical.svg` = 0
- `grep -c 'stripeBreathe' examples/rendered/extreme/brain-anatomical.svg` = 0
- `python -m pytest -q` → 24 passed

- [ ] **Step 4: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): card traveling edge glow replaces breathing stripe"
```

---

## Task 4: B2 + B3 — Card inner glow + stacked shadow + typography

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Replace `cardShadow` filter with `cardShadowStacked`**

Find the existing `<filter id="cardShadow">` def in `_compose_wrapper`'s `<defs>` block. Replace its entire body with three layered `feDropShadow` elements, and rename the id:

```
    <filter id="cardShadowStacked" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="0" dy="2"  stdDeviation="4"  flood-color="#000" flood-opacity="0.30"/>
      <feDropShadow dx="0" dy="6"  stdDeviation="12" flood-color="#000" flood-opacity="0.40"/>
      <feDropShadow dx="0" dy="14" stdDeviation="24" flood-color="#000" flood-opacity="0.30"/>
    </filter>
```

Then update the card composition to reference `url(#cardShadowStacked)` instead of `url(#cardShadow)` (one place — the base rect of each card).

- [ ] **Step 2: Add per-card inner-glow radial gradients**

In `_compose_wrapper`, before the per-region composition loop, build a list of per-card inner-glow gradient defs (one per region). After `region_grads` is built (around the existing per-lobe `rgrad_<key>` block), add a parallel block:

```python
    # Per-card inner glow — radial gradient in the lobe color, used by the
    # card-inner-pulse rect inside each card.
    card_inner_grads: list[str] = []
    for key, region_data in region_positions.items():
        color = palette[region_data["color"]]  # type: ignore[index]
        card_inner_grads.append(
            f'<radialGradient id="cardInnerGlow_{key}" cx="50%" cy="50%" r="60%">'
            f'<stop offset="0%"   stop-color="{color}" stop-opacity="0.18"/>'
            f'<stop offset="100%" stop-color="{color}" stop-opacity="0"/>'
            f"</radialGradient>"
        )
```

Then inject `card_inner_grads` into the `<defs>` block right after `region_grads`:

Find the existing line in the `<defs>` block:
```python
    {chr(10).join("    " + g for g in region_grads)}
```
Add immediately after:
```python
    {chr(10).join("    " + g for g in card_inner_grads)}
```

- [ ] **Step 3: Add the inner-glow rect to each card composition**

Update the card composition (from Task 3) to insert a `<rect class="card-inner-pulse">` between the base rect and the edge rect:

```python
region_blocks.append(
    f'<g transform="translate({lx},{ly})"><g class="label-fade lf{i + 1}">'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardBg)" '
    f'filter="url(#cardShadowStacked)"/>'
    f'<rect x="6" y="6" width="308" height="128" rx="10" '
    f'fill="url(#cardInnerGlow_{key})" class="card-inner-pulse"/>'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="none" '
    f'stroke="{color}" stroke-width="2" pathLength="1000" '
    f'class="card-edge ce{i + 1}"/>'
    f'<rect x="0" y="0" width="320" height="140" rx="14" fill="url(#cardHighlight)"/>'
    f'<text x="160" y="38" class="t-cat-cap" text-anchor="middle" fill="{color}">{cap}</text>'
    f'<text x="160" y="80" class="t-region" text-anchor="middle">{emoji} {domain}</text>'
    f'<text x="160" y="116" class="t-skill" text-anchor="middle">{tools_preview}</text>'
    f"</g></g>"
)
```

- [ ] **Step 4: Add CSS for `.card-inner-pulse` + tighten typography**

In the `<style>` block, find `.t-cat-cap` and update:
- `letter-spacing: 0.30em` → `0.30em` (already 0.20em, change to 0.30em)
- `font-weight: 700` → `font-weight: 800`

The full updated rule:
```css
      .t-cat-cap   {{ font-family: 'Inter', sans-serif; font-weight: 800; font-size: 17px; letter-spacing: 0.30em; text-transform: uppercase; }}
```

Add this new rule near the other card animations:
```css
      .card-inner-pulse {{ animation: cardPulse 5s ease-in-out infinite; }}
      @keyframes cardPulse {{ 0%, 100% {{ opacity: 0.6; }} 50% {{ opacity: 1.0; }} }}
```

- [ ] **Step 5: Smoke build + verify**

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'cardShadowStacked' examples/rendered/extreme/brain-anatomical.svg` ≥ 7 (1 def + 6 refs)
- `grep -c 'class="card-inner-pulse"' examples/rendered/extreme/brain-anatomical.svg` = 6
- `grep -c 'cardInnerGlow_' examples/rendered/extreme/brain-anatomical.svg` ≥ 12 (6 defs + 6 refs)
- `grep -c 'letter-spacing: 0.30em' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `grep -c 'font-weight: 800' examples/rendered/extreme/brain-anatomical.svg` ≥ 1
- `python -m pytest -q` → 24 passed

- [ ] **Step 6: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): card inner glow + stacked shadow + typography polish"
```

---

## Task 5: C1 — Particle constellation lines

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Find the existing particle positions**

In `_compose_wrapper`'s f-string return value, locate the ambient particles block. There are 16 `<circle>` elements with hardcoded `cx`/`cy` like `cx="120" cy="180"`, `cx="260" cy="540"`, etc. Each is gated by `atm.show_particles`.

Extract the positions to a Python list at the top of the f-string return (immediately before the `return f"""..."""` if a Python list isn't already there). If the positions are inline-only, add a new list:

```python
    # 16 ambient particle positions (must match the render below).
    particle_positions: list[tuple[int, int]] = [
        (120, 180), (260, 540), (380, 120), (420, 760),
        (560, 380), (700, 220), (780, 700), (900, 160),
        (980, 520), (1080, 340), (1180, 780), (1260, 240),
        (160, 780), (340, 660), (640, 80),  (1320, 500),
    ]
```

(Place this near the other `_compose_wrapper` Python prep, before the `return` statement.)

- [ ] **Step 2: Compute pairs within 220px (deterministic)**

Right after the particle_positions list:

```python
    # Constellation lines: connect particles within 220px. Indices into
    # particle_positions. Deterministic by definition since positions are fixed.
    constellation_pairs: list[tuple[int, int]] = []
    threshold_sq = 220 * 220
    for i in range(len(particle_positions)):
        for j in range(i + 1, len(particle_positions)):
            dx = particle_positions[i][0] - particle_positions[j][0]
            dy = particle_positions[i][1] - particle_positions[j][1]
            if dx * dx + dy * dy <= threshold_sq:
                constellation_pairs.append((i, j))

    constellation_lines: list[str] = []
    for n, (i, j) in enumerate(constellation_pairs):
        x1, y1 = particle_positions[i]
        x2, y2 = particle_positions[j]
        constellation_lines.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{p_accent_b}" stroke-width="0.8" stroke-opacity="0" '
            f'class="constellation-line cl{n + 1}"/>'
        )
```

- [ ] **Step 3: Wire constellation lines into the SVG**

Find the existing ambient particle `<g fill="...">` block in the f-string. Immediately BEFORE that block, add (gated on the same `atm.show_particles` flag):

```
  {('''<!-- Constellation lines: thin links between nearby particles, fading in/out
       on staggered timers. Reads as a neural-web behind the brain. -->
  <g class="constellation">
  ''' + chr(10).join("    " + ln for ln in constellation_lines) + '''
  </g>''') if atm.show_particles else ""}
```

- [ ] **Step 4: Add CSS for `.constellation-line`**

In the `<style>` block, near the other animation definitions, add:

```css
      .constellation-line {{
        animation: clFade 8s ease-in-out infinite;
      }}
      @keyframes clFade {{
        0%, 100% {{ stroke-opacity: 0; }}
        50%      {{ stroke-opacity: 0.30; }}
      }}
      .cl1{{animation-delay:0s}}    .cl2{{animation-delay:0.6s}}
      .cl3{{animation-delay:1.2s}}  .cl4{{animation-delay:1.8s}}
      .cl5{{animation-delay:2.4s}}  .cl6{{animation-delay:3.0s}}
      .cl7{{animation-delay:3.6s}}  .cl8{{animation-delay:4.2s}}
      .cl9{{animation-delay:4.8s}}  .cl10{{animation-delay:5.4s}}
      .cl11{{animation-delay:6.0s}} .cl12{{animation-delay:6.6s}}
      .cl13{{animation-delay:7.2s}} .cl14{{animation-delay:7.8s}}
      .cl15{{animation-delay:0.3s}} .cl16{{animation-delay:1.5s}}
```

(16 entries cover the upper bound — actual `constellation_pairs` count will be smaller.)

- [ ] **Step 5: Smoke build + verify**

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'class="constellation"' examples/rendered/extreme/brain-anatomical.svg` = 1
- `grep -c 'class="constellation-line cl' examples/rendered/extreme/brain-anatomical.svg` ≥ 4 (depends on particle clustering)
- `grep -c '@keyframes clFade' examples/rendered/extreme/brain-anatomical.svg` = 1
- `python -m pytest -q` → 24 passed

- [ ] **Step 6: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): particle constellation lines for neural-web depth"
```

---

## Task 6: C2 — Light streaks (meteors)

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Add light streaks block to the SVG composition**

In `_compose_wrapper`'s f-string return value, find the existing ambient particle block (the `<g fill="...">` with 16 circles). Immediately BEFORE that block (or before the constellation lines block from Task 5), insert:

```
  {('''<!-- Light streaks: 5 thin diagonal lines that traverse the canvas on
       staggered timers, mimicking meteors / lens flares. Each one fires for
       3s then waits 10-13s before repeating. -->
  <g class="streaks">
    <line x1="-100" y1="200"  x2="-50"  y2="220"  stroke="#EC4899" stroke-width="1.5"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="0s;13s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="0s;13s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="0s;13s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="450"  x2="-50"  y2="470"  stroke="#A78BFA" stroke-width="1.5"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="2s;15s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="2s;15s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="2s;15s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="650"  x2="-50"  y2="670"  stroke="#22D3EE" stroke-width="1.5"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="5s;18s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="5s;18s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="5s;18s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="100"  x2="-50"  y2="120"  stroke="#EC4899" stroke-width="1.2"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="8s;21s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="8s;21s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="8s;21s" repeatCount="indefinite"/>
    </line>
    <line x1="-100" y1="780"  x2="-50"  y2="800"  stroke="#A78BFA" stroke-width="1.2"
          stroke-opacity="0" filter="url(#electricGlow)">
      <animate attributeName="x1" values="-100;1500" dur="3s" begin="11s;24s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="-50;1550"  dur="3s" begin="11s;24s" repeatCount="indefinite"/>
      <animate attributeName="stroke-opacity" values="0;0.7;0.7;0" keyTimes="0;0.15;0.85;1"
               dur="3s" begin="11s;24s" repeatCount="indefinite"/>
    </line>
  </g>''') if atm.show_particles else ""}
```

- [ ] **Step 2: Smoke build + verify**

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- `grep -c 'class="streaks"' examples/rendered/extreme/brain-anatomical.svg` = 1
- The 5 streak `<line>` elements appear (search for `stroke-width="1.5"\|stroke-width="1.2"` in the streaks group context)
- `python -m pytest -q` → 24 passed

- [ ] **Step 3: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): light streaks across canvas for atmospheric motion"
```

---

## Task 7: C3 — bgAura motion + final regen

**Files:**
- Modify: `packages/cortex-core/cortex/builders/brain.py`

- [ ] **Step 1: Animate the `bgAura` rect**

Find the line in `_compose_wrapper` that renders the bgAura rect:
```
{('<rect width="1400" height="900" fill="url(#bgAura)"/>') if atm.show_aura else ""}
```

Replace with an animated version:
```
{('''<rect width="1400" height="900" fill="url(#bgAura)">
    <animateTransform attributeName="transform" type="translate"
                      values="0,0; 100,80; -60,40; 0,0" dur="40s" repeatCount="indefinite"/>
  </rect>''') if atm.show_aura else ""}
```

The bgAura now slowly drifts, adding subtle background motion.

- [ ] **Step 2: Smoke build + verify**

```bash
cortex build -c examples/extreme.yml -o examples/rendered/extreme/
```

Verify:
- The bgAura rect now has an `<animateTransform>` child — grep for `fill="url(#bgAura)"` and confirm an animateTransform follows.
- `python -m pytest -q` → 24 passed.

- [ ] **Step 3: Commit**

```bash
git add packages/cortex-core/cortex/builders/brain.py examples/rendered/extreme/brain-anatomical.svg
git commit -m "feat(brain): drift the bgAura for subtle background motion"
```

---

## Self-Review

**Spec coverage:**
- A (aurora bands replacing plasma fog) → Task 1
- D (specular highlight pass on body + diffuse opacity bump) → Task 2
- B1 (card traveling edge glow) → Task 3
- B2 + B3 (card inner glow + stacked shadow + typography) → Task 4
- C1 (particle constellation lines) → Task 5
- C2 (light streaks) → Task 6
- C3 (bgAura motion) → Task 7

**Type/name consistency:**
- `brain_content_specular` (Task 2) is a string (regex-substituted brain content), used in Task 2 only.
- `card_inner_grads` (Task 4) is a list of str gradient defs, injected into `<defs>` block.
- `particle_positions` and `constellation_pairs` (Task 5) are derived from each other deterministically.
- `cardShadowStacked` (Task 4) replaces `cardShadow` (old) — both refs and def update together.

**Placeholder scan:** No `TBD` / `TODO` / `<insert>` in the plan. Every step has the exact code or commands to run.

**Cleanup verified:**
- Task 1 deletes `plasmaFog` filter and its rect (no orphan refs).
- Task 3 deletes `breathe-stripe` rect, `.breathe-stripe` CSS, `@keyframes stripeBreathe`.
- Task 4 renames `cardShadow` → `cardShadowStacked` (def + all refs together).
