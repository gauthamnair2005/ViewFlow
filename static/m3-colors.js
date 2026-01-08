/**
 * Material 3 Dynamic Color Generation
 * Based on Material You color system
 */

// Convert hex to RGB
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

// Convert RGB to HSL
function rgbToHsl(r, g, b) {
    r /= 255;
    g /= 255;
    b /= 255;
    const max = Math.max(r, g, b), min = Math.min(r, g, b);
    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0;
    } else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
            case g: h = ((b - r) / d + 2) / 6; break;
            case b: h = ((r - g) / d + 4) / 6; break;
        }
    }

    return { h: h * 360, s: s * 100, l: l * 100 };
}

// Convert HSL to RGB
function hslToRgb(h, s, l) {
    h /= 360;
    s /= 100;
    l /= 100;
    let r, g, b;

    if (s === 0) {
        r = g = b = l;
    } else {
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1;
            if (t > 1) t -= 1;
            if (t < 1/6) return p + (q - p) * 6 * t;
            if (t < 1/2) return q;
            if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        };

        const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        const p = 2 * l - q;
        r = hue2rgb(p, q, h + 1/3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1/3);
    }

    return {
        r: Math.round(r * 255),
        g: Math.round(g * 255),
        b: Math.round(b * 255)
    };
}

// RGB to Hex
function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
}

// Generate Material 3 tonal palette from seed color
function generateTonalPalette(seedColor, isDark = true) {
    const rgb = hexToRgb(seedColor);
    if (!rgb) return null;

    const hsl = rgbToHsl(rgb.r, rgb.g, rgb.b);
    
    // Material 3 tonal values
    const tones = {
        0: 0,
        10: 10,
        20: 20,
        30: 30,
        40: 40,
        50: 50,
        60: 60,
        70: 70,
        80: 80,
        90: 90,
        95: 95,
        99: 99,
        100: 100
    };

    const palette = {};
    for (const [key, lightness] of Object.entries(tones)) {
        const rgb = hslToRgb(hsl.h, hsl.s * 0.8, lightness);
        palette[key] = rgbToHex(rgb.r, rgb.g, rgb.b);
    }

    // Generate Material 3 scheme
    if (isDark) {
        return {
            primary: palette[80],
            primaryContainer: palette[30],
            onPrimary: palette[20],
            onPrimaryContainer: palette[90],
            secondary: palette[80],
            secondaryContainer: palette[30],
            onSecondary: palette[20],
            onSecondaryContainer: palette[90],
            tertiary: generateTertiary(hsl, isDark),
            surface: '#1a1c1e',
            surfaceVariant: '#222426',
            surfaceBright: '#2b2d30',
            surfaceDim: '#131416',
            onSurface: '#e3e2e6',
            onSurfaceVariant: '#c4c6d0',
            outline: '#8e9099',
            outlineVariant: '#44464f'
        };
    } else {
        return {
            primary: palette[40],
            primaryContainer: palette[90],
            onPrimary: '#ffffff',
            onPrimaryContainer: palette[10],
            secondary: palette[40],
            secondaryContainer: palette[90],
            onSecondary: '#ffffff',
            onSecondaryContainer: palette[10],
            tertiary: generateTertiary(hsl, isDark),
            surface: '#faf9fd',
            surfaceVariant: '#f0f0f4',
            surfaceBright: '#ffffff',
            surfaceDim: '#dbd9de',
            onSurface: '#1a1c1e',
            onSurfaceVariant: '#43474e',
            outline: '#73777f',
            outlineVariant: '#c3c6cf'
        };
    }
}

// Generate tertiary color (analogous)
function generateTertiary(hsl, isDark) {
    const tertiaryHue = (hsl.h + 60) % 360;
    const rgb = hslToRgb(tertiaryHue, hsl.s * 0.7, isDark ? 80 : 40);
    return rgbToHex(rgb.r, rgb.g, rgb.b);
}

// Apply Material 3 theme
function applyM3Theme(seedColor, isDark = true) {
    const scheme = generateTonalPalette(seedColor, isDark);
    if (!scheme) return;

    const root = document.documentElement;
    
    // Apply colors
    root.style.setProperty('--md-sys-color-primary', scheme.primary);
    root.style.setProperty('--md-sys-color-primary-container', scheme.primaryContainer);
    root.style.setProperty('--md-sys-color-secondary', scheme.secondary);
    root.style.setProperty('--md-sys-color-secondary-container', scheme.secondaryContainer);
    root.style.setProperty('--md-sys-color-tertiary', scheme.tertiary);
    root.style.setProperty('--md-sys-color-surface', scheme.surface);
    root.style.setProperty('--md-sys-color-surface-variant', scheme.surfaceVariant);
    root.style.setProperty('--md-sys-color-surface-bright', scheme.surfaceBright);
    root.style.setProperty('--md-sys-color-surface-dim', scheme.surfaceDim);
    root.style.setProperty('--md-sys-color-on-surface', scheme.onSurface);
    root.style.setProperty('--md-sys-color-on-surface-variant', scheme.onSurfaceVariant);
    root.style.setProperty('--md-sys-color-outline', scheme.outline);
    root.style.setProperty('--md-sys-color-outline-variant', scheme.outlineVariant);

    // Update semantic mappings
    root.style.setProperty('--accent', scheme.primary);
    root.style.setProperty('--accent-hover', scheme.primaryContainer);
    
    // Save to localStorage
    localStorage.setItem('m3-seed-color', seedColor);
    localStorage.setItem('m3-theme', isDark ? 'dark' : 'light');
}

// Load saved theme
function loadSavedTheme() {
    const savedColor = localStorage.getItem('m3-seed-color');
    const savedTheme = localStorage.getItem('m3-theme') || 'dark';
    
    if (savedColor) {
        const isDark = savedTheme === 'dark';
        applyM3Theme(savedColor, isDark);
    }
}

// Preset colors for quick selection
const presetColors = [
    { name: 'Blue', color: '#a8c7fa' },
    { name: 'Green', color: '#a9d18e' },
    { name: 'Purple', color: '#d4b5f7' },
    { name: 'Pink', color: '#f7b5d5' },
    { name: 'Red', color: '#f7b5b5' },
    { name: 'Orange', color: '#f7d5b5' },
    { name: 'Yellow', color: '#f7f5b5' },
    { name: 'Teal', color: '#b5f7e8' }
];

// Initialize on load
if (typeof window !== 'undefined') {
    loadSavedTheme();
}
