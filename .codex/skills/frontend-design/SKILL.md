---
name: frontend-design
description: Modern frontend design system with component library and best practices
---
# Frontend Design Skill

Professional frontend design system with 200+ components, design patterns, and implementation guidelines.

## Quick Start

When user requests frontend work (design, build, create, implement, redesign), follow this workflow:

### 1. Design System Generation (ALWAYS FIRST)

**Run this before writing any code:**

```bash
python .codex/skills/frontend-design/scripts/generate_design_system.py \
  --project "Project Name" \
  --style "style keywords" \
  --industry "industry type" \
  --type "product type"
```

**Style options:**
- `minimal` - Clean, spacious, modern
- `elegant` - Luxury, sophisticated, refined
- `bold` - Strong typography, high contrast
- `playful` - Friendly, rounded, vibrant
- `professional` - Business, corporate, trust
- `tech` - Modern, sharp, futuristic
- `romantic` - Soft, warm, intimate
- `nature` - Organic, earthy, calm

**Industry options:**
- SaaS, e-commerce, portfolio, dashboard, healthcare, fintech, beauty, education, social

**Product types:**
- Landing page, dashboard, app, blog, store, portfolio, admin

### 2. Component Selection

After design system is ready, select components needed:

```bash
python .codex/skills/frontend-design/scripts/list_components.py --category <category>
```

**Categories:**
- `navigation` - Navbars, sidebars, tabs, breadcrumbs
- `hero` - Hero sections, CTAs
- `cards` - Feature, product, profile, testimonial cards
- `forms` - Inputs, selects, checkboxes, radios
- `buttons` - Button variants, sizes, states
- `layouts` - Grids, sections, containers
- `feedback` - Alerts, toasts, modals, loaders
- `tables` - Data tables, pagination
- `typography` - Headings, body, captions

### 3. Generate Implementation

Generate complete page/component with design system applied:

```bash
python .codex/skills/frontend-design/scripts/generate_component.py \
  --type "dashboard" \
  --design-system "path/to/design-system.json"
```

---

## Design System Capabilities

### Color Systems

Each design system includes:
- Primary/Secondary/Accent colors (with 9-shade scales)
- Neutral grays (9 shades)
- Success/Warning/Error semantic colors
- Background gradients
- Dark mode palette
- WCAG contrast ratio verification

### Typography Systems

- Font pairings (display + body combinations)
- Type scale (12 levels, modular)
- Line heights, letter spacing
- Font weights hierarchy
- Google Font CDN links

### Effect Systems

- Shadow scales (6 levels)
- Border radius scales
- Transition timing functions
- Opacity scales
- Blur strengths for glassmorphism

### Spacing Systems

- 4px base grid (16 levels)
- Container max-widths
- Section paddings
- Gutter sizes

---

## Component Library

### Navigation (24 variants)
| Component | Variants |
|-----------|----------|
| Navbar | Centered, left-aligned, right-aligned, full-width |
| Sidebar | Collapsible, mini, drawer, persistent |
| Tabs | Underline, pills, cards, vertical |
| Breadcrumbs | Slash, arrow, chevron |

### Hero Sections (18 variants)
- Split layout (image + text)
- Centered
- Gradient background
- Pattern background
- With stats
- With form
- Video background

### Cards (32 variants)
- Feature cards (icon, image, number)
- Product cards (e-commerce)
- Profile cards (team, testimonial)
- Stats cards (dashboard KPI)
- Blog post cards
- Pricing cards

### Forms (28 variants)
- Input states (default, focus, error, disabled)
- Select dropdowns (native, custom)
- Checkboxes & radios (custom styled)
- Toggle switches
- Date pickers
- File uploads
- Form layouts (inline, stacked, multi-column)

### Buttons (16 variants)
- Solid, outline, ghost, link
- Sizes: xs, sm, md, lg, xl
- States: hover, active, disabled, loading
- Groups, icons, dropdown triggers

### Feedback Components
- Alerts (4 severity levels)
- Toast notifications (with animations)
- Modals & dialogs
- Tooltips & popovers
- Progress bars & spinners
- Skeleton loaders

### Tables & Data
- Basic data tables
- Sortable columns
- Striped rows
- Pagination
- Row selection
- Compact/dense mode

---

## Implementation Stacks

### Vue 3 + Tailwind CSS (THIS PROJECT)
- Composition API syntax
- `<script setup>` SFC format
- Tailwind utility classes
- Lucide Vue icons
- Vue Router integration

**Example component structure:**
```vue
<script setup lang="ts">
// Props first, then composables, then computed
</script>

<template>
  <!-- Semantic HTML structure -->
</template>

<style scoped>
/* Scoped styles only when needed */
</style>
```

### Other Supported Stacks
- React + Tailwind
- Next.js App Router
- Svelte + SvelteKit
- Astro
- HTML + Tailwind

---

## Quality Standards

### Accessibility (ALWAYS CHECK)
- [ ] Semantic HTML elements
- [ ] ARIA labels for icon-only buttons
- [ ] Keyboard navigation support
- [ ] Focus states visible
- [ ] Color contrast >= 4.5:1 for body text
- [ ] `prefers-reduced-motion` respected
- [ ] Form inputs have associated labels

### Visual Polish
- [ ] Consistent icon set (Lucide preferred)
- [ ] No emojis as UI icons (use for content only)
- [ ] Hover states don't cause layout shift
- [ ] Consistent border radius across components
- [ ] Shadow depth matches visual hierarchy
- [ ] Line heights appropriate for text size
- [ ] No "just red" errors - use proper semantic color

### Responsive Design
- [ ] Test at 375px (mobile)
- [ ] Test at 768px (tablet)
- [ ] Test at 1024px (laptop)
- [ ] Test at 1440px (desktop)
- [ ] No horizontal scroll on mobile
- [ ] Touch targets min 44x44px

### Performance
- [ ] Images have width/height attributes
- [ ] Loading="lazy" for below-fold images
- [ ] No unnecessary re-renders (Vue watchers)
- [ ] CSS animations use transform/opacity only

---

## Common UI Patterns

### Card Hover Effect
```css
.card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -8px rgba(0,0,0,0.15);
}
```

### Gradient Text
```css
.gradient-text {
  background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
```

### Glass Morphism
```css
.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Subtle Pattern Background
```css
.pattern-bg {
  background-image: radial-gradient(circle at 1px 1px, rgba(0,0,0,0.05) 1px, transparent 0);
  background-size: 24px 24px;
}
```

---

## For This Project (LoveZS)

### Current Stack
- Vue 3 + TypeScript + Vite
- Tailwind CSS 4
- Vue Router
- Pinia store
- Lucide icons

### Design Direction
User wants: **romantic, elegant, advanced (高级感)**

Apply these principles:
- **Color palette**: Dusty rose, warm taupe, soft gold accents
- **Typography**: Serif headings + sans body for elegant contrast
- **Effects**: Subtle shadows, paper-like textures, gold accent lines
- **Spacing**: Generous whitespace for sophisticated feel
- **Animation**: Slow, gentle transitions (300-400ms)
- **Borders**: Subtle 1px borders, gold dividers

### Files to Modify
1. `frontend_vue/src/style.css` - Global design system
2. `frontend_vue/src/views/Dashboard.vue` - Main dashboard
3. `frontend_vue/src/components/Layout.vue` - Navigation layout
4. All other views for consistency

---

## Pre-Delivery Checklist

Before delivering any code:

### Design System
- [ ] Design system generated first (not skipped)
- [ ] Colors have proper contrast ratios verified
- [ ] Typography scale defined
- [ ] Consistent spacing system used

### Component Quality
- [ ] All interactive elements have cursor-pointer
- [ ] Hover states provide clear feedback
- [ ] Transitions duration 150-300ms
- [ ] No emojis as UI icons (use Lucide)
- [ ] Consistent icon sizing (w-5/h-5 or w-6/h-6)

### Vue Specific
- [ ] `<script setup lang="ts">` used
- [ ] Proper TypeScript types
- [ ] Props with defaults defined
- [ ] No `any` types without comment
- [ ] Vue Router correctly integrated

### Responsive
- [ ] Tested at mobile breakpoint
- [ ] No horizontal overflow
- [ ] Touch targets adequate size

### Accessibility
- [ ] Semantic HTML
- [ ] Focus states visible
- [ ] Images have alt text
- [ ] Color is not sole indicator
