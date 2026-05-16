---
name: Institutional Minimalist
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#444650'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#757682'
  outline-variant: '#c5c6d2'
  surface-tint: '#435b9f'
  primary: '#00113a'
  on-primary: '#ffffff'
  primary-container: '#002366'
  on-primary-container: '#758dd5'
  inverse-primary: '#b3c5ff'
  secondary: '#585f66'
  on-secondary: '#ffffff'
  secondary-container: '#dce3ec'
  on-secondary-container: '#5e656c'
  tertiary: '#2d0700'
  on-tertiary: '#ffffff'
  tertiary-container: '#501300'
  on-tertiary-container: '#d37758'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dbe1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#00174a'
  on-primary-fixed-variant: '#2a4386'
  secondary-fixed: '#dce3ec'
  secondary-fixed-dim: '#c0c7cf'
  on-secondary-fixed: '#151c22'
  on-secondary-fixed-variant: '#41484e'
  tertiary-fixed: '#ffdbd0'
  tertiary-fixed-dim: '#ffb59e'
  on-tertiary-fixed: '#390b00'
  on-tertiary-fixed-variant: '#783018'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Newsreader
    fontSize: 64px
    fontWeight: '400'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.08em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 32px
  margin-desktop: 64px
  margin-mobile: 20px
  stack-xl: 80px
  stack-md: 40px
---

## Brand & Style
The design system embodies "Institutional Minimalism," a philosophy tailored for high-net-worth wealth management. It projects an image of stability, precision, and intellectual rigor. The aesthetic avoids the clichés of "fintech" brightness in favor of an editorial, "financial journal" atmosphere. 

The visual language is characterized by extreme whitespace, which serves as a canvas for high-contrast typography and precise data visualization. The emotional goal is to provide a sense of calm authority, making complex financial landscapes feel navigable and serene. The style utilizes a modern take on Swiss design principles—prioritizing clarity, hierarchy, and a structured grid over decorative elements.

## Colors
The palette is rooted in archival neutrals and deep institutional tones.
- **Primary (Navy Blue):** Used for primary actions, navigation markers, and brand-heavy moments to signal trust and heritage.
- **Secondary (Slate):** Applied to supporting UI elements, metadata, and iconography to maintain a sophisticated, low-vibrancy environment.
- **Neutral Base:** The interface utilizes `#F8F9FA` for the main canvas and `#E9ECEF` for subtle sectioning. This off-white approach reduces eye strain compared to pure white and feels more like premium stationery.
- **Strict Adherence:** Avoid all neon, vibrant gradients, or "gold" luxury tropes. Contrast is achieved through value (light vs. dark) rather than hue.

## Typography
This design system employs a dual-typeface strategy to bridge the gap between traditional publishing and modern software.
- **The Anchor (Inter):** A clean, Swiss-inspired sans-serif used for all functional data, body text, and primary headings. Use massive weight contrast (Bold for headers vs. Regular for body) to create hierarchy.
- **The Accent (Newsreader):** A high-end serif reserved for display moments, editorial insights, and large quote-style callouts. This provides the "financial journal" feel.
- **Leading & Kerning:** Keep leading tight for headlines to maintain a compact, "inked" look. Use generous letter spacing for all-caps labels to ensure legibility and a sense of luxury.

## Layout & Spacing
The layout follows a strict 12-column fixed grid for desktop, prioritizing immense margins to signify premium exclusivity.
- **The "Breath" Rule:** Spacing is the primary separator. Use `stack-xl` (80px) between major sections instead of horizontal rules.
- **Grid Alignment:** All elements must align to the baseline grid. Text-heavy columns should occupy the center 8 columns to maximize the whitespace on the flanks.
- **Responsive Behavior:** On mobile, margins shrink to 20px, and the grid collapses to a single column, but the "vertical air" remains high to maintain the brand's premium feel.

## Elevation & Depth
In this design system, borders are strictly forbidden for layout separation. Depth is conveyed through subtle tonal shifts and ambient shadows.
- **The Shadow Signature:** Use extremely soft, high-diffusion shadows (e.g., `0 20px 40px rgba(0, 0, 0, 0.04)`). The goal is for the shadow to be felt, not seen as a distinct shape.
- **Tonal Layering:** Use the off-white background (#F8F9FA) for the base and the light grey (#E9ECEF) for "container" elements like cards or sidebars.
- **Interaction Depth:** On hover, elements should not lift aggressively; instead, a subtle increase in shadow spread or a slight color shift in the background is preferred.

## Shapes
The shape language is "Soft-Institutional." 
- **Base Radius:** A subtle 0.25rem (4px) radius is applied to buttons and inputs. This prevents the UI from feeling "sharp" or aggressive while maintaining a professional, structured silhouette.
- **Containers:** Larger cards or modal containers may use a slightly more pronounced 0.5rem (8px) radius, but never exceed this.
- **Icons:** Use sharp, 2px stroke-width icons. Rounded terminals in iconography should be avoided to maintain the "pixel-perfect" precision required for wealth management.

## Components
- **Buttons:** Primary buttons are solid Navy (#002366) with white Inter Bold text. Secondary buttons are transparent with a thin Slate (#495057) label—no border, just the text.
- **Input Fields:** Use a subtle background fill (#E9ECEF) with no border. The label should be in `label-caps` style above the field.
- **Cards:** Cards are defined solely by their ambient shadow and white background. Do not use borders to define card edges.
- **Data Visualization:** Charts should use the primary Navy Blue as the main data line, with Slate for axes and grids. Use thin, 1px lines for all graphing elements.
- **Chips:** Small, rectangular tags with a light grey fill and Slate text. Used sparingly for status indicators.
- **Lists:** High-density lists (e.g., transaction history) use generous vertical padding (16px - 24px) between items rather than dividers.