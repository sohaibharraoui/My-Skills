---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
license: Complete terms in LICENSE.txt
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Action Buttons & Component Surface Rules

- **No Primary Color on Action Buttons**: Do NOT use `primary` color for buttons.
- **Main Action Buttons**: MUST use `variant="elevated"`.
  - **Success Actions** (Save, Update, Confirm, Create, Connect): Use `color="success"`.
  - **Neutral Main Actions**: Use `color="accent"`.
  - **Destructive Actions**: Use `color="error"`.
- **Secondary Action Buttons**: MUST use `variant="outlined"`.
- **Cancel & Clear Buttons**: MUST use a **neutral color** (e.g. `variant="outlined"` with `color="grey-darken-1"` / neutral grey styling). Avoid saturated or vibrant colors for cancel/clear.
- **Neutral Actions**: Use `color="accent"` or neutral outlined styling.
- **Steve Jobs / Apple Minimalist Philosophy**:
  - **Unclutter the UI**: Eliminate unnecessary decorations, gratuitous containers, and visual noise.
  - **Avoid Too Many Colors**: Keep palettes restrained, clean, and monochromatic. Reserve color strictly for semantic status and key actions.
  - **Unified Neutral Iconography**: Avoid noisy multicolored pastel avatar circles. Use crisp, monochromatic icons.
- **Limited Card Rounding**: Cards must **not** be rounded a lot (avoid excessive rounding like `rounded-xl`, `rounded-2xl`, `16px+`). Use limited rounding tokens: **`6px` (`rounded-md`) / max `8px` (`rounded-lg`)**.

## Spatial Rhythm & Proximity Architecture

Avoid ambiguous, uniform spacing (e.g. putting 16px between everything). Apply the **3-Tier Spatial Rhythm** derived from a strict 4px/8px grid:

- **1. Micro-Spacing (2px – 8px)**: Inside atomic elements.
  - Title to subtitle micro-gap: `2px - 4px`
  - Icon to text gap: `4px - 6px`
  - Form label to input field: `4px - 6px` (tight proximity forms a single cognitive unit)
  - Badge and button internal padding: `4px 8px` / `8px 16px`
- **2. Meso-Spacing (12px – 20px)**: Between related sibling elements.
  - Form field to next form field: `16px - 20px` (signals a new input item)
  - Card internal padding: `16px - 20px`
  - List item vertical padding: `10px - 14px`
- **3. Macro-Spacing (24px – 48px)**: Between independent containers and sections.
  - Card-to-card gap: `16px - 24px`
  - Section-to-section gap: `32px - 48px`
  - Page container boundary padding: `24px - 32px`

> [!IMPORTANT]
> **The Law of Proximity ($Micro < Meso < Macro$)**: The gap between related items inside a group must ALWAYS be significantly smaller than the gap separating independent groups.
> - **Component Spacing Encapsulation**: Components manage their own internal padding (`p-*`), but NEVER set outer margins (`m-*`). Parent layout stacks control external gutters.
> - **No Border Inception**: Avoid nesting cards inside cards inside panels. Use subtle background tone shifts (`#f8fafc` on `#ffffff`) and negative space instead of redundant borders.

## Multi-Variable Visual Hierarchy & Layout Physics

Do NOT rely solely on huge font sizes to establish visual hierarchy. Balance the **Hierarchy Triad**:

1. **Size Scale**: Keep scales compact and controlled (`11px` tertiary/badge, `12-13px` secondary/metadata, `13.5-14px` body/data, `15-16px` section/card title, `20-24px` page header).
2. **Font Weight**: Use `700` (Bold) sparingly for key headers, `600` (Semi-bold) for primary data/labels, `500` (Medium) for controls, and `400` (Regular) for descriptions.
3. **Tonal Contrast**:
   - Primary content: High-contrast Slate 900 (`#0f172a` / `#1e293b`).
   - Secondary metadata / subtitles: Slate 600 (`#475569` / `#64748b`).
   - Tertiary / borders / placeholders: Slate 400 (`#94a3b8` / `#cbd5e1` / `#e2e8f0`).
4. **De-emphasize to Emphasize**: To make a CTA or critical status pop, tone down the surrounding borders and secondary labels rather than over-saturating the entire view.
5. **Labels as a Last Resort**: Drop redundant `Label: Value` prefixes when data context is clear from formatting or layout.
6. **Optical Alignment & Tabular Figures**:
   - Numeric metrics, latencies, dates, and amounts must be right-aligned with `tabular-nums`.
   - In flex rows with multi-line text, align icons to the top (`align-self: flex-start; margin-top: 2px`) rather than center.
7. **The 7-State Component Lifecycle**:
   - Account for all 7 states in every component: Ideal, Zero-Data Empty, Filter Zero, Loading Skeleton, Error/Failure, Partial Syncing, and Extreme Overflow (`max-w: 65ch` / `line-clamp-2`).
8. **Form Ergonomics**:
   - Validate on `blur` or submit; re-validate on `input` only after error. Helper/error text sits `4px` beneath inputs.
9. **Action Safety (Transient Undo vs Blocking Modals)**:
   - For non-destructive actions (archiving, unassigning, filter dismissal), execute immediately with a 5-second floating "Undo" toast. Reserve blocking confirmation modals strictly for catastrophic/irreversible actions.
10. **Poka-Yoke & Single-Column Form Cadence**:
   - Design mistake-proofing constraints (disabled invalid date ranges, masked inputs). Keep form fields strictly in a single vertical column to preserve natural vertical eye scanning.

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.