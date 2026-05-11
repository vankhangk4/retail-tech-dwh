---
name: DWH Operations Console
description: Operations console for multi-tenant retail data warehouse workflows and dashboard access.
colors:
  signal-blue: "oklch(43% 0.092 210)"
  signal-blue-strong: "oklch(37% 0.099 210)"
  signal-blue-soft: "oklch(92.6% 0.03 210)"
  cool-canvas: "oklch(97.1% 0.006 210)"
  cool-subtle: "oklch(94.8% 0.009 210)"
  panel-white: "oklch(99.1% 0.004 210)"
  panel-cool: "oklch(96.5% 0.008 210)"
  line-soft: "oklch(90.4% 0.011 210)"
  line-strong: "oklch(82.8% 0.015 210)"
  ink-strong: "oklch(24.5% 0.017 222)"
  ink-main: "oklch(33.5% 0.015 220)"
  ink-muted: "oklch(49% 0.013 218)"
  ink-faint: "oklch(63% 0.011 216)"
  success-green: "oklch(56% 0.108 156)"
  success-green-soft: "oklch(93.3% 0.03 156)"
  warning-amber: "oklch(71% 0.14 77)"
  warning-amber-soft: "oklch(95.2% 0.028 80)"
  danger-red: "oklch(57% 0.15 27)"
  danger-red-soft: "oklch(94.1% 0.03 28)"
  info-blue: "oklch(60% 0.08 230)"
  info-blue-soft: "oklch(93% 0.02 228)"
typography:
  display:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'
    fontSize: "clamp(2.4rem, 4vw, 4.2rem)"
    fontWeight: 820
    lineHeight: 0.96
    letterSpacing: "-0.035em"
  headline:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'
    fontSize: "clamp(1.45rem, 2vw, 2rem)"
    fontWeight: 800
    lineHeight: 1.02
    letterSpacing: "-0.03em"
  title:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'
    fontSize: "1.375rem"
    fontWeight: 800
    lineHeight: 1.15
    letterSpacing: "normal"
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "normal"
  label:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif'
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "0.11em"
rounded:
  xs: "10px"
  sm: "14px"
  md: "20px"
  lg: "28px"
  pill: "999px"
spacing:
  "1": "0.25rem"
  "2": "0.5rem"
  "3": "0.75rem"
  "4": "1rem"
  "5": "1.5rem"
  "6": "2rem"
  "7": "3rem"
components:
  button-primary:
    backgroundColor: "{colors.signal-blue}"
    textColor: "{colors.panel-white}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: "0 1rem"
    height: "2.875rem"
  button-secondary:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink-strong}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: "0 1rem"
    height: "2.875rem"
  button-danger:
    backgroundColor: "{colors.danger-red-soft}"
    textColor: "{colors.danger-red}"
    typography: "{typography.body}"
    rounded: "{rounded.pill}"
    padding: "0 1rem"
    height: "2.875rem"
  surface-card:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink-main}"
    rounded: "{rounded.md}"
    padding: "1.15rem"
  input-default:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink-strong}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "0.75rem 0.95rem"
    height: "3rem"
  status-pill-neutral:
    backgroundColor: "{colors.cool-subtle}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0 0.8rem"
    height: "1.85rem"
  context-chip:
    backgroundColor: "{colors.panel-white}"
    textColor: "{colors.ink-strong}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.55rem 0.85rem"
    height: "2.8rem"
  nav-link-active:
    backgroundColor: "{colors.signal-blue-soft}"
    textColor: "{colors.signal-blue-strong}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "0.85rem 0.9rem"
    height: "3.2rem"
  auth-signal:
    backgroundColor: "oklch(30% 0.017 220 / 0.9)"
    textColor: "oklch(97% 0.006 210)"
    rounded: "1.2rem"
    padding: "1rem 1.05rem"
---

# Design System: DWH Operations Console

## Overview

**Creative North Star: "The Signal Room"**

The current interface behaves like a light operations room rather than a marketing surface. It is dense enough to support tenant administration, ETL control, and dashboard access, but it still uses broad spacing, rounded containers, and softened shadows to keep the console readable under daily use. The active implementation is a restrained product system built on cool blue-tinted neutrals, a single action accent, and a standard app-shell vocabulary of rail, command bar, cards, chips, and forms.

This system works best when it feels controlled, legible, and operationally calm. `PRODUCT.md` explicitly rejects generic blue admin-template drift, so the existing blue-tinted palette has to stay disciplined: accent goes to actions and active states, not decorative floods. Admin flows should reveal upload, ETL, tenant scope, and health quickly. Viewer flows should reduce operational noise and move users toward charts with minimal friction.

The live design system today is defined by `frontend/static/css/system.css`, then extended by `auth.css`, `dashboard.css`, and `settings.css`. The legacy `frontend/static/css/login.css` uses a separate hex palette and should not be used as the source of truth for new work.

**Key Characteristics:**
- Restrained product color strategy with one dominant action accent and semantic state colors.
- One-family sans typography with compact hierarchy and tabular numerals for metrics.
- Rounded surfaces and soft ambient lift instead of hard-edged enterprise framing.
- Standard product patterns: side rail, sticky command bar, pill chips, outlined tables, inline forms.
- Auth surfaces are the most atmospheric part of the system, but still remain tied to operational messaging.

## Colors

The palette is a cool, blue-tinted control-room palette: pale neutral surfaces, dark ink, one azure action accent, and clear semantic state colors for operations.

### Primary

- **Signal Blue** (`oklch(43% 0.092 210)`): The primary action color for submit buttons, current selection, and live operational emphasis.
- **Signal Blue Strong** (`oklch(37% 0.099 210)`): The pressed or hovered action state, plus stronger accent text.
- **Signal Blue Soft** (`oklch(92.6% 0.03 210)`): Accent wash for hover states, quiet emphasis, and active navigation backgrounds.

### Neutral

- **Cool Canvas** (`oklch(97.1% 0.006 210)`): The page-level canvas and base background tint.
- **Cool Subtle** (`oklch(94.8% 0.009 210)`): Secondary neutral used for quiet pills, hover backgrounds, and soft separation.
- **Panel White** (`oklch(99.1% 0.004 210)`): The main surface background for cards, panels, inputs, tables, and chips.
- **Panel Cool** (`oklch(96.5% 0.008 210)`): Stronger neutral layer for rail backgrounds and shaded panel variants.
- **Line Soft** (`oklch(90.4% 0.011 210)`): The default border and divider color across nearly every component.
- **Line Strong** (`oklch(82.8% 0.015 210)`): Used when a border needs slightly more authority, especially on hover.
- **Ink Strong** (`oklch(24.5% 0.017 222)`): Headings, high-priority labels, and control titles.
- **Ink Main** (`oklch(33.5% 0.015 220)`): Default UI text.
- **Ink Muted** (`oklch(49% 0.013 218)`): Supporting copy and secondary metadata.
- **Ink Faint** (`oklch(63% 0.011 216)`): Eyebrows, table headers, helper copy, and quiet metadata.

### Operational States

- **Success Green** (`oklch(56% 0.108 156)` with `oklch(93.3% 0.03 156)` background): Healthy API, completed ETL, positive system readiness.
- **Warning Amber** (`oklch(71% 0.14 77)` with `oklch(95.2% 0.028 80)` background): Freshness caution, pending attention, and non-blocking issues.
- **Danger Red** (`oklch(57% 0.15 27)` with `oklch(94.1% 0.03 28)` background): Failing ETL, invalid input, destructive actions, and blocked states.
- **Info Blue** (`oklch(60% 0.08 230)` with `oklch(93% 0.02 228)` background): Informational messaging when a neutral or semantic state is not sufficient.

**The Restraint Rule.** `Signal Blue` is the action voice, not the wallpaper. The blue tint may live in neutrals, but saturated accent belongs on primary actions, active navigation, focus, and meaningful state emphasis only.

## Typography

**Display Font:** `-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`
**Body Font:** `-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`
**Label/Mono Font:** Same UI sans family; metrics and timestamps switch to `font-variant-numeric: tabular-nums` instead of a separate monospace family.

**Character:** The type system is product-native, compact, and familiar. It uses weight and spacing rather than font pairing to create hierarchy, which keeps dense operational screens coherent and easy to scan.

### Hierarchy

- **Display** (`820`, `clamp(2.4rem, 4vw, 4.2rem)`, `0.96`): Reserved for auth hero headlines and the few moments where the product needs a larger emotional hook.
- **Headline** (`800`, `clamp(1.45rem, 2vw, 2rem)`, `1.02`): Used in command-bar titles, auth card titles, and key page-level headings.
- **Title** (`800`, `1.375rem`, `1.15`): Section titles, mission brief headings, modal titles, and stronger panel headers.
- **Body** (`400`, `0.95rem`, `1.55`): General copy, explanatory text, helper content, and supporting descriptions. Prose is typically capped at `65ch`.
- **Label** (`700`, `0.75rem`, `0.11em`): Eyebrows, table headers, status metadata, chip prefixes, and compact control labels. Uppercase is common in this tier.

**The One-Family Rule.** The system earns hierarchy through weight, tracking, and scale, not through introducing a second decorative type family.

## Elevation

The interface uses a hybrid of tonal layering and soft ambient shadows. Most structure is created by pale surface separation, thin borders, and rounded geometry. Shadows are present, but they are diffuse and low-contrast, giving panels lift without pushing the product into glossy or decorative territory.

### Shadow Vocabulary

- **Ambient Low** (`0 14px 28px -24px oklch(22% 0.02 220 / 0.28)`): Default panel, button, and chip lift across the shared system.
- **Ambient Medium** (`0 24px 50px -30px oklch(22% 0.02 220 / 0.24)`): Modal and larger surfaced overlays.
- **Auth Frame Lift** (`0 36px 80px -46px oklch(20% 0.02 220 / 0.3)`): The auth shell's stronger framing shadow.
- **Auth Card Lift** (`0 30px 68px -40px oklch(22% 0.02 220 / 0.28)`): The inner auth card, still soft but more pronounced than dashboard panels.

**The Soft Lift Rule.** Surfaces should feel separated by atmosphere, not by theatrical depth. If a shadow starts reading as gloss or glass, it is too strong.

## Components

### Buttons

- **Shape:** Pill-first shared button geometry (`999px`) with a minimum height of `2.875rem`.
- **Primary:** Filled with `Signal Blue`, white text, soft shadow, and slight upward hover motion. It carries the main action voice for login, navigation, and ETL-related decisions.
- **Hover / Focus:** Hover darkens the fill or shifts the neutral layer; focus uses the global `2px` accent outline with `2px` offset.
- **Secondary / Danger:** Secondary buttons stay panel-white with border framing. Danger buttons invert to a tinted red container instead of a saturated destructive fill.

### Chips

- **Style:** Status pills are small, rounded, uppercase-leaning metadata containers with semantic backgrounds. They are compact enough for tables and rails, but still feel like product controls instead of badges from a marketing site.
- **State:** Neutral, success, warning, and danger variants exist today. Their shape stays constant, while color and adjacent structure provide the state distinction.

### Cards / Containers

- **Corner Style:** Shared system cards use `20px` rounding by default, with dense variants at `14px`. The auth shell stretches beyond the token scale, which should remain a deliberate exception.
- **Background:** Panels are mostly white-to-cool-white gradients over a tinted canvas.
- **Shadow Strategy:** Most cards use Ambient Low. Modals use Ambient Medium. Auth framing uses the strongest lift in the system.
- **Border:** A thin `Line Soft` border is nearly universal and does most of the structural work.
- **Internal Padding:** Panels cluster around `1rem` to `1.35rem`; auth cards go larger, up to `2rem`.

### Inputs / Fields

- **Style:** Fields are pale, outlined, and rounded at `14px`, with a `3rem` minimum height and generous horizontal padding.
- **Focus:** Shared fields change background subtly on focus, while the page-level `:focus-visible` outline provides the stronger accessibility treatment.
- **Error / Disabled:** Error messaging sits below the field at `0.8125rem` and uses `Danger Red`. Disabled treatment relies on opacity and cursor changes rather than a new shape language.

### Navigation

- **Style:** The rail uses icon-plus-copy rows with `14px` rounding, a two-line label system, and restrained hover motion (`translateX(2px)`). The sticky command bar mirrors this tone with pill-shaped context chips and compact metadata.
- **Active State:** Active navigation is tinted, bordered, and softly inset-highlighted rather than heavily saturated.
- **Mobile Treatment:** The rail becomes an off-canvas sheet at `1024px` and below, with a scrim and unchanged component vocabulary.

### Operational Signal Stack

The signature custom pattern is the operational signal stack: health indicators, trust strips, auth signal rows, freshness pills, status boxes, and ETL workflow states. These components mix quiet semantic color, compact uppercase metadata, and explanatory copy so that users can understand both the state and the consequence, not just see a colored badge.

## Do's and Don'ts

### Do:

- **Do** keep `Signal Blue` (`oklch(43% 0.092 210)`) for primary actions, active navigation, focus, and meaningful live-state emphasis.
- **Do** keep shared panel radii inside the core scale of `14px`, `20px`, and `28px`, with pill geometry for buttons and chips.
- **Do** preserve the global `:focus-visible` treatment of `2px solid var(--accent)` with `2px` offset across all interactive controls.
- **Do** use uppercase metadata labels around `0.72rem` to `0.76rem` with spaced tracking for chips, headers, and operational annotations.
- **Do** extend the active system from `system.css`, `auth.css`, `dashboard.css`, and `settings.css`, not from the legacy `login.css` palette.

### Don't:

- **Don't** let the interface slide into the "dashboard SaaS xanh dương kiểu template" failure mode by flooding inactive surfaces with accent blue or treating every card as the same generic block.
- **Don't** use the hero-metric template of big number, small label, supporting stat, and decorative accent as the default dashboard pattern.
- **Don't** revert auth to a split-screen default that is only decorative and does not carry real operational or trust signals.
- **Don't** reduce every state to the same status pill, or rely on color alone to express warning, error, success, or permission scope.
- **Don't** build "bề mặt enterprise chung chung, nhiều card nhưng không có nhịp điều hướng rõ" by repeating identical card grids without clear priority, action order, or next-step cues.
- **Don't** introduce glassmorphism, gradient text, colored side-stripe borders, or non-standard product controls into this system.
