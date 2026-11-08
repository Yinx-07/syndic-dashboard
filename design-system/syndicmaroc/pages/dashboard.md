# SyndicMaroc — Dashboard Design System Specification (ui-ux-pro-max)

> **Context:** Property management & co-ownership (Syndic de copropriété au Maroc).
> **Target Audience:** Syndic managers & co-owners / residents viewing financial health, payments, receipts, and maintenance.
> **Archetype:** Bento Grid Data-Dense Fintech / Real Estate Operations.

---

## 1. Visual Foundation & Design Tokens

### 1.1 Color Palette (WCAG AAA/AA Contrast Compliant)
| Token | Hex | Role & Usage |
|-------|-----|--------------|
| `--syn-brand` | `#0F766E` | Brand Primary: Deep Moroccan Emerald / Teal |
| `--syn-brand-dark` | `#115E59` | Active & hover states for primary buttons |
| `--syn-brand-light` | `#CCFBF1` | Soft tint background for badges and KPI icons |
| `--syn-navy` | `#0F172A` | Slate 900: Header, navbar gradient base, primary text |
| `--syn-navy-surface` | `#1E293B` | Slate 800: Secondary dark elements |
| `--syn-bg` | `#F8FAFC` | Slate 50: Dashboard main canvas background |
| `--syn-card` | `#FFFFFF` | Card surface, pure white with soft border |
| `--syn-border` | `#E2E8F0` | 1px border for clean separation |
| `--syn-text-main` | `#0F172A` | Primary typography (contrast 12.6:1 on white) |
| `--syn-text-muted` | `#64748B` | Secondary details, captions, meta info |
| `--syn-success` | `#059669` | Paid status, positive treasury (+MAD) |
| `--syn-success-light` | `#ECFDF5` | Soft green background for status badges |
| `--syn-warning` | `#D97706` | Partial payments (acompte), in-progress tickets |
| `--syn-warning-light` | `#FFFBEB` | Soft amber background for warning pills |
| `--syn-danger` | `#DC2626` | Unpaid dues, debts, urgent alerts |
| `--syn-danger-light` | `#FEF2F2` | Soft red/rose background |
| `--syn-info` | `#0284C7` | Treasury evolution, announcements, reports |
| `--syn-info-light` | `#F0F9FF` | Soft sky blue background |

### 1.2 Typography
- **Primary Font Family:** `'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- **Google Fonts Import:**
  `https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap`
- **Rhythm & Scale:**
  - H1 / Page Titles: `1.5rem` (24px) - `1.75rem` (28px), weight 800, tracking `-0.025em`
  - H2 / Section Headers: `1.125rem` (18px) - `1.25rem` (20px), weight 700
  - KPI Big Numbers: `1.75rem` (28px) - `2rem` (32px), weight 800, tabular figures
  - Body Text: `0.875rem` (14px), weight 400/500, line-height 1.5
  - Small / Micro Badges: `0.75rem` (12px), weight 600, tracking `0.02em`

### 1.3 Shadows & Elevation
- `--syn-shadow-card`: `0 1px 3px 0 rgba(15, 23, 42, 0.03), 0 4px 12px -2px rgba(15, 23, 42, 0.05)`
- `--syn-shadow-hover`: `0 8px 24px -4px rgba(15, 23, 42, 0.08), 0 2px 6px -1px rgba(15, 23, 42, 0.04)`
- `--syn-shadow-modal`: `0 20px 40px -12px rgba(15, 23, 42, 0.2)`

### 1.4 Radius System
- Cards & Bento Tiles: `16px` (`border-radius: 1rem`)
- KPI Icons: `12px` (`border-radius: 0.75rem`)
- Buttons & Inputs: `10px` (`border-radius: 0.625rem`)
- Badges & Pills: `9999px` (`rounded-pill`)

---

## 2. Component System Guidelines

1. **Top Navigation Bar:**
   - Deep slate-900 with emerald glow accent (`linear-gradient(135deg, #0F172A 0%, #134E4A 100%)`).
   - Clean brand mark with Moroccan flag badge & active route indicator pill.
   - User profile dropdown with role pill ("Syndic" emerald, "Copropriétaire" blue).

2. **Bento KPI Cards:**
   - 4-column responsive grid on desktop, 2-column on tablet, single column stack on mobile.
   - Distinct icon badges with micro-gradients.
   - Metric comparison subtitle & secondary indicator pill.

3. **Charts & Data Visualizations:**
   - Styled cards with header icon, title, and time filter badge.
   - Chart.js styled with brand palette:
     - Recouvrement: Green (`#059669`), Red (`#DC2626`), Amber (`#D97706`).
     - Cashflow: Gradient Teal-to-Slate bars with subtle rounded tops.
     - Dépenses: Harmonious categorical palette.

4. **Interactive Data Tables:**
   - Subtle zebra hover (`rgba(241, 245, 249, 0.6)`).
   - Sticky header feel, clean borders, crisp action buttons.
   - Responsive horizontal swipe with touch indicators.

5. **Accessibility & Interaction:**
   - `cursor: pointer` on all interactive triggers.
   - Smooth 150-250ms transitions (`all 0.2s cubic-bezier(0.16, 1, 0.3, 1)`).
   - High contrast ratios (all body text > 7:1 against card background).
   - Mobile touch targets ≥ 44px height.
