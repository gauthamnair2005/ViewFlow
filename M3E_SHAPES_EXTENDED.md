# M3E Extended Shape System Documentation

## 🎨 Overview

The extended M3E shape system adds **30+ new expressive shape variations** to create unique, personality-filled UI components.

---

## 📐 New Shape Categories

### 1. Diagonal Asymmetric Shapes
Perfect for dynamic, modern UI elements.

```css
--md-shape-diagonal-sm: 4px 12px 4px 12px
--md-shape-diagonal-md: 8px 16px 8px 16px
--md-shape-diagonal-lg: 12px 24px 12px 24px
```

**Use Cases**: Navigation items, alert boxes, video rows  
**Visual Effect**: Creates diagonal visual flow

### 2. Top-Heavy Shapes
More rounded at the top, sharp at bottom.

```css
--md-shape-top-heavy-sm: 12px 12px 4px 4px
--md-shape-top-heavy-md: 20px 20px 8px 8px
--md-shape-top-heavy-lg: 28px 28px 12px 12px
```

**Use Cases**: Video thumbnails, image cards, player containers  
**Visual Effect**: Soft welcoming top, grounded bottom

### 3. Bottom-Heavy Shapes
Sharp at top, more rounded at bottom.

```css
--md-shape-bottom-heavy-sm: 4px 4px 12px 12px
--md-shape-bottom-heavy-md: 8px 8px 20px 20px
--md-shape-bottom-heavy-lg: 12px 12px 28px 28px
```

**Use Cases**: Dropdowns, tooltips, video metadata  
**Visual Effect**: Anchored appearance

### 4. Wave Pattern Shapes
Alternating corner radii create wave effect.

```css
--md-shape-wave-sm: 12px 4px 12px 4px
--md-shape-wave-md: 20px 8px 20px 8px
--md-shape-wave-lg: 28px 12px 28px 12px
```

**Use Cases**: Navigation buttons, notification items, cards  
**Visual Effect**: Playful, rhythmic appearance

### 5. Unique Asymmetric Combinations
Creative one-of-a-kind shapes for standout elements.

```css
--md-shape-unique-1: 4px 16px 24px 8px
--md-shape-unique-2: 8px 24px 12px 20px
--md-shape-unique-3: 12px 28px 8px 16px
--md-shape-unique-4: 16px 12px 28px 4px
--md-shape-unique-5: 20px 8px 16px 24px
```

**Use Cases**: Featured cards, hero sections, auth boxes  
**Visual Effect**: Strong personality, memorable

### 6. Extreme Expressive Shapes
Bold statements with high contrast corners.

```css
--md-shape-extreme-1: 4px 32px 4px 32px
--md-shape-extreme-2: 32px 4px 32px 4px
--md-shape-extreme-3: 8px 28px 16px 4px
```

**Use Cases**: Special announcements, featured content, CTAs  
**Visual Effect**: Maximum visual impact

### 7. Component-Specific Shapes
Tailored for specific UI components.

```css
--md-shape-modal: 24px 24px 4px 4px
--md-shape-sheet: 28px 28px 0 0
--md-shape-menu: 4px 16px 16px 4px
--md-shape-tooltip: 8px 8px 2px 8px
--md-shape-chip: 8px 16px 16px 8px
```

---

## 🎯 Component Mappings

### Applied Automatically:

| Component | Shape | Token |
|-----------|-------|-------|
| Video Thumbnails | Top-heavy medium | `--md-shape-top-heavy-md` |
| Auth Box | Unique 2 | `--md-shape-unique-2` |
| Alert | Diagonal medium | `--md-shape-diagonal-md` |
| Nav Buttons | Wave small | `--md-shape-wave-sm` |
| Video Rows | Unique 5 | `--md-shape-unique-5` |
| Notifications | Wave medium | `--md-shape-wave-md` |
| Subscriptions | Diagonal large | `--md-shape-diagonal-lg` |
| Search Suggestions | Menu shape | `--md-shape-menu` |
| Tooltips | Tooltip shape | `--md-shape-tooltip` |
| Modals | Modal shape | `--md-shape-modal` |
| Mobile Drawer | Sheet shape | `--md-shape-sheet` |
| Chips | Chip shape | `--md-shape-chip` |

---

## 🎨 Utility Classes

Apply any shape with utility classes:

```html
<!-- Diagonal shapes -->
<div class="shape-diagonal-sm">Small diagonal</div>
<div class="shape-diagonal-md">Medium diagonal</div>
<div class="shape-diagonal-lg">Large diagonal</div>

<!-- Top-heavy shapes -->
<div class="shape-top-heavy-sm">Small top-heavy</div>
<div class="shape-top-heavy-md">Medium top-heavy</div>
<div class="shape-top-heavy-lg">Large top-heavy</div>

<!-- Bottom-heavy shapes -->
<div class="shape-bottom-heavy-sm">Small bottom-heavy</div>
<div class="shape-bottom-heavy-md">Medium bottom-heavy</div>
<div class="shape-bottom-heavy-lg">Large bottom-heavy</div>

<!-- Wave patterns -->
<div class="shape-wave-sm">Small wave</div>
<div class="shape-wave-md">Medium wave</div>
<div class="shape-wave-lg">Large wave</div>

<!-- Unique combinations -->
<div class="shape-unique-1">Unique shape 1</div>
<div class="shape-unique-2">Unique shape 2</div>
<div class="shape-unique-3">Unique shape 3</div>
<div class="shape-unique-4">Unique shape 4</div>
<div class="shape-unique-5">Unique shape 5</div>

<!-- Extreme shapes -->
<div class="shape-extreme-1">Extreme 1</div>
<div class="shape-extreme-2">Extreme 2</div>
<div class="shape-extreme-3">Extreme 3</div>
```

---

## ⚡ Animated Shapes

### Shape Morphing on Hover

```html
<div class="shape-morph-hover">
    Hover to see shape change
</div>
```

Changes from `unique-1` to `unique-5` on hover with smooth transition.

### Continuous Pulsing Shape

```html
<div class="shape-pulse-animation">
    Continuously morphs between shapes
</div>
```

Pulses between `unique-1` and `unique-5` every 3 seconds.

### Loading Shape Animation

```html
<div class="loading-shape">
    4-stage morph cycle
</div>
```

Cycles through 4 different shapes to indicate loading state.

---

## 🎭 Context-Specific Shapes

Different shapes based on content type:

```html
<!-- Video categories -->
<div class="video-card" data-category="music">Music videos</div>
<div class="video-card" data-category="gaming">Gaming content</div>
<div class="video-card" data-category="education">Educational</div>

<!-- Playlist types -->
<div class="playlist-card" data-type="music">Music playlist</div>
<div class="playlist-card" data-type="favorites">Favorites</div>

<!-- User roles -->
<div class="user-badge" data-role="admin">Admin</div>
<div class="user-badge" data-role="creator">Creator</div>
```

Automatically applies appropriate shapes based on data attributes.

---

## 🎨 Design Guidelines

### When to Use Each Shape Type:

**Diagonal Shapes** 🔷
- Use for: Dynamic content, navigation
- Creates: Forward motion, energy
- Best for: Action-oriented UI

**Top-Heavy Shapes** 🔺
- Use for: Media content, images
- Creates: Welcoming, soft entry
- Best for: Content cards, thumbnails

**Bottom-Heavy Shapes** 🔻
- Use for: Grounded elements, forms
- Creates: Stability, foundation
- Best for: Input groups, footers

**Wave Patterns** 〰️
- Use for: Playful elements, lists
- Creates: Rhythm, flow
- Best for: Navigation, notifications

**Unique Shapes** ⭐
- Use for: Featured content, highlights
- Creates: Personality, memorability
- Best for: Hero sections, CTAs

**Extreme Shapes** 💥
- Use for: Special announcements, impact
- Creates: Maximum attention
- Best for: Promotional content, alerts

---

## 📱 Responsive Behavior

Shapes automatically simplify on mobile:

```css
@media (max-width: 768px) {
    /* Complex shapes become simpler diagonal patterns */
    .video-card,
    .recommended-card,
    .auth-box {
        border-radius: var(--md-shape-diagonal-md);
    }
}
```

**Why?** Extreme asymmetry can look distorted on small screens.

---

## 🎯 Best Practices

### DO ✅

- **Mix shape types** - Use different shapes for visual hierarchy
- **Apply shapes logically** - Similar content = similar shapes
- **Use animations sparingly** - Only on key interactive elements
- **Test on all screen sizes** - Ensure shapes look good everywhere
- **Consider content** - Shape should enhance, not distract

### DON'T ❌

- **Use all extreme shapes** - Too chaotic
- **Apply same shape everywhere** - Boring, defeats purpose
- **Ignore mobile** - Test responsive behavior
- **Over-animate** - Motion sickness risk
- **Mix too many types on one screen** - Choose 2-3 shape families

---

## 🎨 Examples by Use Case

### Landing Page Hero
```css
.hero-card {
    border-radius: var(--md-shape-extreme-1);
}
```

### Video Grid
```css
.video-card {
    border-radius: var(--md-shape-top-heavy-md);
}
```

### Navigation Menu
```css
.nav-item {
    border-radius: var(--md-shape-wave-sm);
}
```

### Form Container
```css
.form-box {
    border-radius: var(--md-shape-bottom-heavy-md);
}
```

### Notification Toast
```css
.toast {
    border-radius: var(--md-shape-diagonal-md);
}
```

### Modal Dialog
```css
.modal {
    border-radius: var(--md-shape-modal);
}
```

---

## 🎊 Advanced Techniques

### 1. Shape + Color Combination
```css
.special-card {
    border-radius: var(--md-shape-unique-3);
    background: linear-gradient(135deg, 
        var(--md-sys-color-primary) 0%, 
        var(--md-sys-color-secondary) 100%);
}
```

### 2. Shape + Shadow Synergy
```css
.elevated-unique {
    border-radius: var(--md-shape-extreme-2);
    box-shadow: 
        0 8px 16px rgba(0,0,0,0.15),
        0 0 0 1px var(--md-sys-color-outline-variant);
}
```

### 3. Nested Shape Patterns
```css
.outer {
    border-radius: var(--md-shape-unique-1);
}

.outer .inner {
    border-radius: var(--md-shape-unique-5);
}
```

### 4. 3D Perspective Effects
```css
.shape-3d {
    border-radius: var(--md-shape-extreme-3);
    transform-style: preserve-3d;
}

.shape-3d:hover {
    transform: perspective(1000px) rotateY(2deg);
}
```

---

## 📊 Shape Statistics

**Total New Shapes**: 30+  
**Shape Categories**: 7  
**Utility Classes**: 25  
**Animated Variants**: 3  
**Context-Specific**: 6  
**Component Mappings**: 12+

---

## 🚀 Performance

All shapes use pure CSS:
- ✅ No JavaScript overhead
- ✅ GPU-accelerated animations
- ✅ Efficient rendering
- ✅ Minimal repaints

---

## 🎓 Learn More

- Visit `/m3e-demo` for interactive examples
- Read `M3E_IMPLEMENTATION.md` for full system
- Check `M3E_QUICK_START.md` for basic usage

---

**Ready to create unique designs with 30+ expressive shapes!** ��

*Updated: January 6, 2026*
