---
name: Alpine Expedition
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf3'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d5e3fc'
  on-surface: '#0d1c2e'
  on-surface-variant: '#434843'
  inverse-surface: '#233144'
  inverse-on-surface: '#eaf1ff'
  outline: '#737973'
  outline-variant: '#c3c8c1'
  surface-tint: '#4d6453'
  primary: '#061b0e'
  on-primary: '#ffffff'
  primary-container: '#1b3022'
  on-primary-container: '#819986'
  inverse-primary: '#b4cdb8'
  secondary: '#904d00'
  on-secondary: '#ffffff'
  secondary-container: '#fe932c'
  on-secondary-container: '#663500'
  tertiary: '#141817'
  on-tertiary: '#ffffff'
  tertiary-container: '#292c2b'
  on-tertiary-container: '#909392'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d0e9d4'
  primary-fixed-dim: '#b4cdb8'
  on-primary-fixed: '#0b2013'
  on-primary-fixed-variant: '#364c3c'
  secondary-fixed: '#ffdcc3'
  secondary-fixed-dim: '#ffb77d'
  on-secondary-fixed: '#2f1500'
  on-secondary-fixed-variant: '#6e3900'
  tertiary-fixed: '#e1e3e1'
  tertiary-fixed-dim: '#c5c7c5'
  on-tertiary-fixed: '#191c1b'
  on-tertiary-fixed-variant: '#444746'
  background: '#f8f9ff'
  on-background: '#0d1c2e'
  surface-variant: '#d5e3fc'
typography:
  headline-xl:
    fontFamily: Montserrat
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  headline-md:
    fontFamily: Montserrat
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 64px
  max-width: 1280px
---

## Brand & Style

The design system is built on a foundation of **Rugged Minimalism**. It balances the reliability of high-end technical outdoor equipment with the clarity of professional enterprise software. The aesthetic is clean and high-performance, avoiding unnecessary decoration in favor of functional precision.

The target audience consists of outdoor professionals and enthusiasts who value durability, clarity, and trustworthiness. The UI should evoke a sense of calm under pressure—like a topographical map or a high-quality compass. We utilize a "Professional-Outdoor" style: heavy whitespace, precise typography, and tactile UI elements that feel like physical gear.

## Colors

The palette is inspired by the transition from the forest floor to the mountain peak.

- **Primary (Deep Forest):** Used for navigation, primary headers, and core brand elements. It conveys stability and depth.
- **Accent (Safety Orange):** Reserved for high-priority calls to action, notifications, and "Quick Action" buttons. It mimics the high-visibility fabrics used in survival gear.
- **Background (Mist):** An off-white `primary-container` that reduces screen glare and provides a soft, organic canvas for content.
- **Surface (Pristine):** Pure white is used sparingly for cards and input fields to create a clear visual hierarchy against the tinted background.

## Typography

Typography follows a utilitarian hierarchy. **Montserrat** provides a bold, architectural feel for headlines, reminiscent of trail markers and equipment branding. **Inter** is used for all body and UI text to ensure maximum legibility and a professional, systematic appearance.

Labels and small metadata should use `label-md` with uppercase styling and increased letter spacing to emulate the stamped labels found on technical gear.

## Layout & Spacing

The design system utilizes a **Fixed Grid** model for desktop and a **Fluid Grid** for mobile. 

- **Desktop:** 12-column grid with a 1280px max-width. Generous margins (64px) ensure the content feels focused and un-cluttered.
- **Mobile:** 4-column fluid grid with 16px margins. 
- **Vertical Rhythm:** All spacing is derived from a base 8px unit. Components should use 16px or 24px padding to maintain a "breathable" feel. Large sections should be separated by at least 80px to reinforce the minimalist aesthetic.

## Elevation & Depth

This design system uses **Tonal Layers** combined with **Ambient Shadows**. 

- **Level 0 (Background):** `tertiary_color_hex` (Mist).
- **Level 1 (Cards/Surfaces):** White background with a very soft, diffused shadow (15% opacity, 12px blur, 4px Y-offset) tinted with the Primary color.
- **Level 2 (Interactive):** Elements like "Quick Actions" use a more pronounced shadow upon hover to simulate a physical button being ready for use.
- **Outlines:** Subtle 1px borders in a light grey-green (#E2E8F0) are used to define boundaries on white surfaces without adding visual weight.

## Shapes

The shape language is **Soft**. A 0.25rem (4px) base radius is applied to most UI elements (inputs, small buttons) to keep the feel professional and precise. Larger containers and cards use `rounded-lg` (8px) to soften the overall interface and make it approachable. 

Buttons specifically use `rounded-lg` to differentiate them from functional input fields.

## Components

- **Quick Action Buttons:** These are the primary navigation triggers. They use the Accent (Safety Orange) color with white text. On hover, the shadow deepens.
- **Chat Bubbles:** 
    - *Bot:* Deep Forest background with white text, aligned left. 
    - *User:* Light Grey-Green tint with Primary text, aligned right.
    - Bubbles use 12px rounded corners, but the corner pointing to the speaker is sharper (4px).
- **Input Fields:** Pure white background, 1px Primary-tinted border, with `label-md` floating above the field.
- **Chips:** Used for tags or categories. They feature a light version of the Primary color with a 1px solid border.
- **Cards:** White surfaces with 8px radius. They should feature a "header" area with a subtle 1px bottom border to separate titles from content.
- **Progress Indicators:** Use a thick (4px) track in light grey with the Primary color indicating completion, mimicking the look of a topographical map scale.