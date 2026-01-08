# M3E UI Quick Start Guide

## 🎨 What Was Implemented

Your ViewFlow app now has a complete **Material Design 3 Expressive** UI system!

## ✨ Key Visual Changes

### Before vs After
- **Cards**: Flat rectangles → Asymmetric rounded corners with hover effects
- **Buttons**: Basic rounded → Expressive shapes with ripple effects
- **Forms**: Simple inputs → Elevated focus states with glow
- **Interactions**: Static → Dynamic state layers on hover/press

## 🚀 Quick Usage Guide

### 1. Buttons
```html
<!-- Primary button with ripple -->
<button class="btn btn-accent">Click Me</button>

<!-- Icon button with state layer -->
<button class="icon-btn">
    <svg>...</svg>
</button>
```

### 2. Floating Action Button (FAB)
```html
<!-- Standard FAB -->
<button class="fab">
    <svg>...</svg>
</button>

<!-- Extended FAB with label -->
<button class="fab fab-extended">
    <svg>...</svg>
    <span class="fab-label">Create</span>
</button>
```

### 3. Chips
```html
<span class="chip">Default</span>
<span class="chip chip-filled">Filled</span>
<span class="chip chip-selected">Selected</span>
```

### 4. Badges
```html
<span class="badge">3</span>
<span class="badge badge-primary">New</span>
```

### 5. List Items
```html
<div class="list-item">
    <div class="list-item-leading">
        <svg>...</svg>
    </div>
    <div class="list-item-content">
        <div class="list-item-title">Title</div>
        <div class="list-item-subtitle">Subtitle</div>
    </div>
</div>
```

### 6. Progress Bars
```html
<!-- Linear progress -->
<div class="progress-linear">
    <div class="progress-linear-bar" style="width: 50%;"></div>
</div>

<!-- Indeterminate -->
<div class="progress-linear progress-linear-indeterminate">
    <div class="progress-linear-bar"></div>
</div>
```

### 7. Snackbar
```html
<div id="snackbar" class="snackbar">
    <span class="snackbar-message">Message here</span>
    <button class="snackbar-action">Action</button>
</div>

<script>
document.getElementById('snackbar').classList.add('show');
</script>
```

## 🎭 Automatic Enhancements

These elements automatically have M3E styling:
- All `.video-card` → State layers + expressive borders
- All `.recommended-card` → Enhanced hover effects
- All `.btn` → Ripple effects
- All `.icon-btn` → State layer overlays
- All form inputs → Focus animations
- All `.search-input` → Scale transform on focus

## 🎨 Color System

Use M3 color tokens in your custom CSS:
```css
.my-element {
    background: var(--md-sys-color-primary-container);
    color: var(--md-sys-color-on-primary-container);
    border-radius: var(--md-shape-card); /* Asymmetric! */
}
```

## 📐 Shape System

Available shape tokens:
- `--md-shape-card` → `16px 16px 28px 4px` (expressive asymmetric)
- `--md-shape-button` → `20px 20px 20px 4px` (playful)
- `--md-shape-fab` → `16px 16px 16px 4px` (FAB style)
- `--md-shape-corner-sm` → `8px` (small uniform)
- `--md-shape-corner-full` → `9999px` (fully rounded)

## ⚡ Animation System

Available animation classes:
```html
<div class="animate-in">Fade + scale in</div>
<div class="slide-in-up">Slide from bottom</div>
<div class="slide-in-down">Slide from top</div>
```

Motion timing tokens:
- `--md-motion-duration-short4` → 200ms
- `--md-motion-duration-medium2` → 300ms
- `--md-motion-easing-emphasized` → smooth emphasized curve

## 🎯 Demo Page

**Visit `/m3e-demo` to see all components in action!**

This interactive demo shows:
- All button variants
- FAB components
- Form elements
- Cards with expressive shapes
- Chips and badges
- Progress indicators
- List items
- Typography scale
- Color palette
- And more!

## 🔧 Customization

### Change a card's shape:
```css
.my-custom-card {
    border-radius: var(--md-shape-card);
}
```

### Add state layer to custom element:
```css
.my-element {
    position: relative;
}

.my-element::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--md-sys-color-primary);
    opacity: 0;
    transition: opacity 200ms;
}

.my-element:hover::before {
    opacity: 0.08;
}
```

## 📱 Mobile Optimized

All components are responsive:
- FABs adjust position on mobile
- Snackbars adapt to screen width
- Cards stack properly
- Touch targets are 48px minimum

## 🎨 Theme Support

M3E works with both light and dark themes automatically!
The theme toggle in the navbar switches between:
- Dark theme (default)
- Light theme (with adjusted colors)

## 🔥 What Makes This "Expressive"?

1. **Asymmetric shapes** - Not boring uniform corners!
2. **State layers** - Visual feedback on every interaction
3. **Emphasized motion** - Smooth, personality-filled animations
4. **Rich color system** - Tonal palettes instead of flat colors
5. **Playful details** - Ripples, glows, transforms, and more

## 📊 Performance

- All animations use GPU-accelerated properties (transform, opacity)
- State layers use pseudo-elements (no extra DOM nodes)
- CSS-only implementations (no JavaScript overhead)
- Minimal repaints and reflows

## ✅ Testing Checklist

To see M3E in action:
1. ✅ Hover over video cards (see state layer + border color change)
2. ✅ Click buttons (see ripple effect)
3. ✅ Focus on inputs (see glow + lift animation)
4. ✅ Hover icon buttons (see circular state layer)
5. ✅ Visit `/m3e-demo` (see all components)

## 🎓 Learn More

- [Material Design 3](https://m3.material.io/)
- [M3 Color System](https://m3.material.io/styles/color/overview)
- [M3 Motion](https://m3.material.io/styles/motion/overview)

---

**Happy designing with M3E!** 🎨✨
