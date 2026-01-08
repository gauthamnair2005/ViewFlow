# 🎨 M3E Shape Quick Reference

## Visual Guide to All Shape Tokens

```
┌─────────────────────────────────────────────────────────┐
│          M3E EXPRESSIVE SHAPE SYSTEM                    │
│          30+ Asymmetric Shape Variations                │
└─────────────────────────────────────────────────────────┘
```

---

## 📐 Shape Patterns Visualized

### Original M3E Shapes
```
┌────────┐      ╭─────────╮      ╭──────────╮
│ CARD   │      │ BUTTON  │      │   FAB    │
│  16px  │      │  20px   │      │   16px   │
│        │      │         │      │          │
│    28px│      │     4px │      │      4px │
└──────4px      ╰─────────┘      ╰──────────┘
16 16 28 4      20 20 20 4       16 16 16 4
```

### Diagonal Asymmetric
```
╭──────╮        ╭────────╮        ╭──────────╮
│  SM  │        │   MD   │        │    LG    │
│ 4px  │        │  8px   │        │   12px   │
│  12px│        │   16px │        │    24px  │
╰────4px        ╰──────8px        ╰────────12px
4 12 4 12       8 16 8 16         12 24 12 24
```

### Top-Heavy (Soft Top, Sharp Bottom)
```
╭──────╮        ╭────────╮        ╭──────────╮
│  SM  │        │   MD   │        │    LG    │
│ 12px │        │  20px  │        │   28px   │
│      │        │        │        │          │
└────4px        └──────8px        └────────12px
12 12 4 4       20 20 8 8         28 28 12 12
```

### Bottom-Heavy (Sharp Top, Soft Bottom)
```
┌────────┐      ┌──────────┐      ┌────────────┐
│   SM   │      │    MD    │      │     LG     │
│   4px  │      │   8px    │      │    12px    │
│        │      │          │      │            │
╰──────12px     ╰────────20px     ╰──────────28px
4 4 12 12       8 8 20 20         12 12 28 28
```

### Wave Pattern (Alternating)
```
╭────╮          ╭──────╮          ╭────────╮
│ SM │          │  MD  │          │   LG   │
│12px│          │ 20px │          │  28px  │
│  4px          │  8px            │  12px
╰──12px         ╰────20px         ╰──────28px
12 4 12 4       20 8 20 8         28 12 28 12
```

### Unique Combinations
```
╭─────╮         ╭───────╮         ╭────────╮
│  1  │         │   2   │         │   3    │
│ 4px │         │  8px  │         │  12px  │
│ 16px│         │  24px │         │  28px  │
│  24px         │   12px          │   8px
╰───8px         ╰─────20px        ╰──────16px
4 16 24 8       8 24 12 20        12 28 8 16

╭──────╮        ╭────────╮
│  4   │        │   5    │
│ 16px │        │  20px  │
│ 12px │        │   8px  │
│  28px         │   16px
╰────4px        ╰──────24px
16 12 28 4      20 8 16 24
```

### Extreme Shapes
```
╭──╮            ╭────────╮        ╭──────╮
│1 │            │   2    │        │  3   │
│4px            │  32px  │        │ 8px  │
│  32px         │   4px  │        │ 28px │
│  4px          │  32px  │        │ 16px │
╰──32px         ╰────4px          ╰────4px
4 32 4 32       32 4 32 4         8 28 16 4
```

---

## 🎯 Quick Selection Guide

### By Visual Effect:

**Need ENERGY?** → Diagonal shapes
```css
shape-diagonal-md
```

**Need SOFTNESS?** → Top-heavy shapes
```css
shape-top-heavy-lg
```

**Need STABILITY?** → Bottom-heavy shapes
```css
shape-bottom-heavy-md
```

**Need PLAYFULNESS?** → Wave patterns
```css
shape-wave-md
```

**Need PERSONALITY?** → Unique shapes
```css
shape-unique-2
```

**Need IMPACT?** → Extreme shapes
```css
shape-extreme-1
```

---

## 🎨 Component Selection Chart

```
┌─────────────────┬──────────────────┬─────────────────┐
│   Component     │   Best Shape     │   Reasoning     │
├─────────────────┼──────────────────┼─────────────────┤
│ Video Thumb     │ Top-Heavy MD     │ Soft welcome    │
│ Auth Box        │ Unique 2         │ Memorable       │
│ Navigation      │ Wave SM          │ Rhythmic        │
│ Alert/Toast     │ Diagonal MD      │ Dynamic         │
│ Modal           │ Modal Shape      │ Specific        │
│ Tooltip         │ Tooltip Shape    │ Subtle          │
│ Card            │ Original Card    │ Balanced        │
│ Button          │ Wave SM          │ Playful         │
│ Hero Section    │ Extreme 1        │ Impact          │
│ Footer          │ Bottom-Heavy     │ Grounded        │
│ Video Row       │ Unique 5         │ List flow       │
│ Notification    │ Wave MD          │ Attention       │
└─────────────────┴──────────────────┴─────────────────┘
```

---

## 💡 Usage Examples

### HTML with Utility Classes
```html
<!-- Quick application -->
<div class="shape-diagonal-md">Content</div>
<div class="shape-wave-lg">Content</div>
<div class="shape-unique-3">Content</div>
```

### CSS with Tokens
```css
/* Custom component */
.my-card {
    border-radius: var(--md-shape-diagonal-md);
}

.my-button {
    border-radius: var(--md-shape-wave-sm);
}

.my-hero {
    border-radius: var(--md-shape-extreme-1);
}
```

---

## 🎭 Shape Families

### Family 1: Symmetry Variations
- `shape-card` (asymmetric)
- `shape-button` (mostly symmetric)
- `shape-fab` (subtle asymmetry)

### Family 2: Diagonal Flow
- `shape-diagonal-sm/md/lg`
- Creates forward motion

### Family 3: Vertical Bias
- `shape-top-heavy` (soft entry)
- `shape-bottom-heavy` (grounded)

### Family 4: Alternating Rhythm
- `shape-wave-sm/md/lg`
- Visual musicality

### Family 5: Unique Signatures
- `shape-unique-1` through `-5`
- Maximum personality

### Family 6: Maximum Impact
- `shape-extreme-1` through `-3`
- Bold statements

---

## 📊 Shape Metrics

```
Shape Complexity Scale (1-5):
═══════════════════════════════

Uniform (8px)           ░░░░░ 1
Diagonal (8 16 8 16)    ░░░░░ 2
Card (16 16 28 4)       ████░ 3
Unique (8 24 12 20)     ████░ 4
Extreme (4 32 4 32)     █████ 5
```

**Recommendation**: Use complexity 3-4 for most UI, 5 for special elements.

---

## 🎨 Color + Shape Combinations

```
Primary Color      →  Diagonal/Wave shapes
Secondary Color    →  Top-Heavy shapes
Tertiary Color     →  Unique shapes
Error/Warning      →  Extreme shapes (attention!)
Success            →  Bottom-Heavy (stable)
```

---

## 🔧 Customization

### Create Your Own Shape:
```css
:root {
    --my-shape: 6px 18px 12px 24px;
}

.my-element {
    border-radius: var(--my-shape);
}
```

**Formula**: Pick 4 values between 4px-32px with variety!

---

## ⚡ Performance Tips

✅ **DO**: Use CSS variables  
✅ **DO**: Group similar shapes  
✅ **DO**: Test on mobile  
❌ **DON'T**: Animate border-radius rapidly  
❌ **DON'T**: Use extreme shapes everywhere  
❌ **DON'T**: Mix 5+ shape families on one page  

---

## 🎯 Decision Tree

```
Need to style an element?
    │
    ├─ Is it interactive? → Wave/Diagonal
    ├─ Is it media content? → Top-Heavy
    ├─ Is it a form? → Bottom-Heavy
    ├─ Is it featured? → Unique/Extreme
    ├─ Is it navigation? → Wave
    ├─ Is it a modal? → Modal shape
    └─ Default? → Card shape
```

---

## 📱 Mobile Considerations

On screens < 768px:
- Extreme shapes → Diagonal
- Complex unique → Simplified
- Large radii → Medium radii

```css
@media (max-width: 768px) {
    .my-element {
        /* Simplify from extreme-1 to diagonal-md */
        border-radius: var(--md-shape-diagonal-md);
    }
}
```

---

## 🎊 Complete Token List

```css
/* Core M3E */
--md-shape-card
--md-shape-button  
--md-shape-fab

/* Diagonal */
--md-shape-diagonal-sm/md/lg

/* Top-Heavy */
--md-shape-top-heavy-sm/md/lg

/* Bottom-Heavy */
--md-shape-bottom-heavy-sm/md/lg

/* Wave */
--md-shape-wave-sm/md/lg

/* Unique */
--md-shape-unique-1/2/3/4/5

/* Extreme */
--md-shape-extreme-1/2/3

/* Component-Specific */
--md-shape-modal
--md-shape-sheet
--md-shape-menu
--md-shape-tooltip
--md-shape-chip

/* Standard Corners */
--md-shape-corner-xs/sm/md/lg/xl/full
```

**Total: 33 shape tokens!**

---

## 🚀 Start Using

1. **Visit**: `/m3e-demo` to see all shapes
2. **Pick**: Choose shape family that fits
3. **Apply**: Use utility class or CSS variable
4. **Test**: Check on all screen sizes
5. **Refine**: Adjust based on content

---

**Master expressive shapes for unique, personality-filled designs!** 🎨

*Quick Reference v1.0 - January 6, 2026*
