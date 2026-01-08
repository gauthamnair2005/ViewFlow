# M3E Player - Quick Visual Reference

## 🎮 Button Shape Guide

```
╔════════════════════════════════════════════════════════════╗
║  M3E VIDEO PLAYER - UNIQUE BUTTON SHAPES                  ║
╚════════════════════════════════════════════════════════════╝

┌─ PLAY/PAUSE ──────────────────────┐
│  ╔═══╗     Top-Heavy Shape        │
│  ║ ▶ ║     12px 12px 4px 4px      │
│  ╚═══╝     Welcoming, soft entry   │
└───────────────────────────────────┘

┌─ MUTE/VOLUME ─────────────────────┐
│  ╔═══╗     Bottom-Heavy Shape     │
│  ║ 🔊 ║     4px 4px 12px 12px      │
│  ╚═══╝     Grounded, stable        │
└───────────────────────────────────┘

┌─ QUALITY/SETTINGS ────────────────┐
│  ╔═╗       Wave Shape              │
│  ║⚙║       12px 4px 12px 4px      │
│  ╚═╝       Rhythmic, playful       │
└───────────────────────────────────┘

┌─ SPEED ───────────────────────────┐
│  ╔═╗       Diagonal Shape          │
│  ║1x║      4px 12px 4px 12px      │
│  ╚═╝       Forward motion          │
└───────────────────────────────────┘

┌─ THEATRE MODE ────────────────────┐
│  ╔═══╗     Unique-1 Shape          │
│  ║ ⛶ ║     16px 4px 16px 4px      │
│  ╚═══╝     Personality + identity  │
└───────────────────────────────────┘

┌─ FULLSCREEN ──────────────────────┐
│  ╔═══╗     Unique-2 Shape          │
│  ║ ▢ ║     4px 16px 4px 16px      │
│  ╚═══╝     Distinctive asymmetry   │
└───────────────────────────────────┘
```

---

## 📊 Seek Bar (Progress Bar)

```
╔══════════════════════════════════════════════════════════╗
║  SEEK BAR - Interactive Anatomy                          ║
╚══════════════════════════════════════════════════════════╝

DEFAULT STATE (6px height):
├────────────────────────────────────────┤
│██████████████████░░░░░░░░░░░░░░░░░░░░│
└────────────────────────────────────────┘
 ↑                ↑                     ↑
 Filled (Primary) Scrubber (Hidden)    Track (Muted)


HOVER STATE (8px height):
├─────────────────────────────────────────┤
│████████████████████◆░░░░░░░░░░░░░░░░░░│
│                    │                    │
│                [0:42]                   │
└─────────────────────────────────────────┘
                     ↑
              Scrubber (16px)
           Diagonal 4-8-4-8
         + Tooltip above


GRADIENT FILL:
┌─────────────────────────────────────────┐
│ Primary ──────────▶ Tertiary            │
│ (Blue) ────────────▶ (Purple/Teal)      │
└─────────────────────────────────────────┘


SCRUBBER HANDLE:
     ◢◣      ← Asymmetric Diamond
    ◢──◣        4px 8px 4px 8px
   ◢────◣       Diagonal shape
  ◢──────◣   
  ◤──────◥      With elevation shadow
   ◥────◤       + 3px surface border
    ◥──◤
     ◥◤
```

---

## 🔊 Volume Slider

```
╔══════════════════════════════════════════════════════════╗
║  VOLUME SLIDER - Wave Pattern Design                     ║
╚══════════════════════════════════════════════════════════╝

TRACK (6px height, wave shape 8-4-8-4):
┌─────────────────────────────────┐
│ ∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿│  ← Wave border-radius
└─────────────────────────────────┘

FILLED PORTION (Primary gradient):
├─────────────────┤
│████████████████░░░░░░░░░░░░░░░│
└─────────────────┘
 ↑               ↑               ↑
 0%            50%             100%


THUMB (16px, Unique-3 shape 8-16-8-4):
     ╔═══╗
     ║   ║      ← Extreme asymmetry
     ║ ● ║         8px 16px 8px 4px
     ╚═══╝         
      ↑
   Unique-3
 + 3px border
 + Elevation-2


HOVER STATE:
     ╔═══╗
     ║   ║  
     ║ ● ║  ← Scale 1.2x
     ╚═══╝     Elevation-3
      ⬆
   Enlarged
```

---

## 🎬 Big Play Button

```
╔══════════════════════════════════════════════════════════╗
║  BIG PLAY BUTTON - Extreme Asymmetry                     ║
╚══════════════════════════════════════════════════════════╝

SHAPE (80px × 80px, Extreme-1: 4-32-4-32):

      ╔════════════════════════╗
      ║                        ║
      ║                        ║
      ║          ▶             ║
      ║      40px icon         ║
      ║                        ║
      ║                        ║
      ╚════════════════════════╝
       ↑                      ↑
    4px corner          32px corner
    
    ↑                          ↑
 32px corner              4px corner


STATES:
┌─────────────────────────────────────────┐
│ DEFAULT   : 80×80px, Elevation-3        │
│ HOVER     : Scale 1.1x, Elevation-4     │
│ ACTIVE    : Scale 1.05x, Elevation-1    │
│ STATE     : 8% hover, 12% press overlay │
└─────────────────────────────────────────┘


CENTER POSITIONING:
        Parent Container
    ┌─────────────────────┐
    │                     │
    │        ╔═══╗        │
    │        ║ ▶ ║        │
    │        ╚═══╝        │
    │   50% / 50% + translate  │
    └─────────────────────┘
```

---

## 📦 Controls Container

```
╔══════════════════════════════════════════════════════════╗
║  CONTROLS CONTAINER - Unique-4 Shape                     ║
╚══════════════════════════════════════════════════════════╝

SHAPE (16-16-4-4 - Top-Rounded Expressive):

┌───────────────────────────────────────────────────┐
│  ╔▶╗  ══════════════  ╚🔊╝ ╔⚙╗ ╚1x╝ ⬡⛶⬢ ▢          │
│   ↑       ↑          ↑    ↑   ↑   ↑  ↑  ↑       │
└───────────────────────────────────────────────────┘
 ↑                                                 ↑
16px rounded                                    16px rounded
     ↓                                         ↓
     4px sharp                              4px sharp


FEATURES:
├─ Backdrop Filter: blur(20px)
├─ Padding: 12px
├─ Gap: 12px between buttons
├─ Border: 1px outline-variant
├─ Elevation: 3 (default) → 4 (hover)
└─ Semi-transparent background


LAYOUT:
┌───────────────────────────────────────────────┐
│ [Play] [Progress────────────] [Time]          │
│        [Volume] [Settings] [Speed]            │
│        [Theatre] [Fullscreen]                 │
└───────────────────────────────────────────────┘
  ← 12px gap between all elements →
```

---

## 🎛️ Quality Menu

```
╔══════════════════════════════════════════════════════════╗
║  QUALITY/SETTINGS MENU - Bottom-Heavy                    ║
╚══════════════════════════════════════════════════════════╝

MENU CONTAINER (Bottom-Heavy: 4-4-12-12):

       [Settings Button ⚙]
              ↓
      ╔════════════╗  ← 4px corners
      ║  Auto      ║
      ║  1080p     ║
      ║  720p      ║
      ║  480p      ║
      ║  360p      ║
      ╚════════════╝  ← 12px corners


MENU ITEMS (Diagonal-SM: 2-6-2-6):

  ╔─ Auto ───╗  ← Each item
  ║          ║    Diagonal shape
  ╚─────────╝     for consistency


STATES:
┌────────────────────────────────┐
│ DEFAULT  : Transparent bg      │
│ HOVER    : Surface-highest bg  │
│          : 8% state layer      │
│ ACTIVE   : 12% state layer     │
└────────────────────────────────┘
```

---

## 📱 Responsive Changes (< 700px)

```
╔══════════════════════════════════════════════════════════╗
║  MOBILE OPTIMIZATIONS                                    ║
╚══════════════════════════════════════════════════════════╝

DESKTOP                    MOBILE
┌─────────┐               ┌──────┐
│ ╔═══╗   │               │ ╔═╗  │
│ ║ ▶ ║   │   ──────▶     │ ║▶║  │
│ ╚═══╝   │               │ ╚═╝  │
│ 40×40px │               │36×36px│
└─────────┘               └──────┘
 Complex                   Simple
 Extreme-1                 Diagonal-XL


BIG PLAY:
┌─────────┐               ┌──────┐
│  ╔═══╗  │               │ ╔═╗  │
│  ║ ▶ ║  │   ──────▶     │ ║▶║  │
│  ╚═══╝  │               │ ╚═╝  │
│  80×80  │               │64×64 │
└─────────┘               └──────┘


VOLUME:
├──────────┤              ├────────┤
│90px wide │   ──────▶    │60px    │
└──────────┘              └────────┘


SEEK BAR:
├─ 6px ──┤                ├─ 8px ──┤
          ──────▶         (Thicker for touch)
```

---

## 🎨 Color Modes

```
╔══════════════════════════════════════════════════════════╗
║  DARK MODE vs LIGHT MODE                                 ║
╚══════════════════════════════════════════════════════════╝

DARK MODE:
┌────────────────────────────────────────┐
│ ████████████████████████████████████████│ ← Video
│ ████████████████████████████████████████│
│ ████████████████████████████████████████│
│                                        │
│ ╔▶╗ ═══════════ ╚🔊╝ ⚙ 1x ⛶ ▢        │ ← Controls
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓│ ← Semi-trans dark
└────────────────────────────────────────┘
  ↑
  White icons (#f5f5f7)
  Blur backdrop


LIGHT MODE:
┌────────────────────────────────────────┐
│ ████████████████████████████████████████│ ← Video
│ ████████████████████████████████████████│
│ ████████████████████████████████████████│
│                                        │
│ ╔▶╗ ═══════════ ╚🔊╝ ⚙ 1x ⛶ ▢        │ ← Controls
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│ ← Semi-trans light
└────────────────────────────────────────┘
  ↑
  Dark icons (#1b1b1f)
  Blur backdrop
```

---

## ⚡ Animation Timing

```
╔══════════════════════════════════════════════════════════╗
║  M3E MOTION SYSTEM                                       ║
╚══════════════════════════════════════════════════════════╝

DURATION SCALE:
├─ 100ms (short2)   : Scrubber, volume thumb
├─ 150ms (short3)   : State layers, button hover
├─ 200ms (short4)   : Ripple fade out
├─ 250ms (medium1)  : Container elevation
└─ 300ms (medium2)  : Big play scale


EASING CURVES:
┌────────────────────────────────────────┐
│ Standard     : Default transitions     │
│              : Cubic-bezier ease-in-out│
│                                        │
│ Emphasized   : Interactive elements    │
│              : Quick start, slow end   │
│              : More personality        │
└────────────────────────────────────────┘


TIMELINE EXAMPLE (Button Click):
─────────────────────────────────────────────▶ Time
0ms   : Click detected
0ms   : Ripple starts (scale 0 → 10)
0ms   : State layer → 12% opacity
300ms : Ripple complete (scale 10)
350ms : Ripple fades out
500ms : State layer → 0% opacity
```

---

## 📏 Touch Targets

```
╔══════════════════════════════════════════════════════════╗
║  ACCESSIBILITY - Minimum 48px Touch Areas                ║
╚══════════════════════════════════════════════════════════╝

DESKTOP BUTTONS (40px visible):
    ┌────────────┐
    │ ┌────────┐ │  ← 40px visible button
    │ │  Icon  │ │
    │ └────────┘ │
    └────────────┘  ← 48px touch area (with padding)


MOBILE BUTTONS (36px visible):
    ┌──────────┐
    │ ┌──────┐ │    ← 36px visible
    │ │ Icon │ │    ← 48px touch area
    │ └──────┘ │      (with padding)
    └──────────┘


SEEK BAR (8px on mobile):
────────────────────────────  ← 8px tall
↑                            ↑
Easier to tap on touchscreen
```

---

## 🎯 Shape Token Reference

```
╔══════════════════════════════════════════════════════════╗
║  ALL SHAPES USED IN PLAYER                               ║
╚══════════════════════════════════════════════════════════╝

--md-shape-card              16-16-28-4   Player container
--md-shape-corner-full       50%          Seek bar, volume
--md-shape-corner-xs         4px          Tooltips
--md-shape-corner-lg         12px         Base buttons
--md-shape-top-heavy-lg      12-12-4-4    Play button
--md-shape-bottom-heavy-lg   4-4-12-12    Mute, menu
--md-shape-wave-md           8-4-8-4      Volume track
--md-shape-wave-lg           12-4-12-4    Quality button
--md-shape-diagonal-sm       2-6-2-6      Menu items
--md-shape-diagonal-md       4-8-4-8      Scrubber
--md-shape-diagonal-lg       4-12-4-12    Speed, mobile
--md-shape-diagonal-xl       8-20-8-20    Big play mobile
--md-shape-unique-1          16-4-16-4    Theatre button
--md-shape-unique-2          4-16-4-16    Fullscreen
--md-shape-unique-3          8-16-8-4     Volume thumb
--md-shape-unique-4          16-16-4-4    Controls container
--md-shape-extreme-1         4-32-4-32    Big play button
```

---

*Visual Reference Guide - M3E Player Implementation*  
*January 6, 2026*
