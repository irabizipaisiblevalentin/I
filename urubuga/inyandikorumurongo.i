shyiramo "json"

# ═══════════════════════════════════════════════════════════════════
# URUBUGA DESIGN SYSTEM — Modern CSS Framework
# ═══════════════════════════════════════════════════════════════════

shyira_ko URUBUGA_CSS = "
/* ═══ URUBUGA DESIGN SYSTEM ═══ */
:root {
    /* Primary Colors */
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --primary-light: #818cf8;
    --primary-50: #eef2ff;
    --primary-100: #e0e7ff;
    --primary-900: #312e81;

    /* Accent Colors */
    --accent: #f59e0b;
    --accent-dark: #d97706;
    --accent-light: #fbbf24;

    /* Success / Error / Warning */
    --success: #10b981;
    --success-dark: #059669;
    --error: #ef4444;
    --error-dark: #dc2626;
    --warning: #f59e0b;
    --warning-dark: #d97706;
    --info: #3b82f6;

    /* Neutrals */
    --white: #ffffff;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    --black: #030712;

    /* Background */
    --bg: #ffffff;
    --bg-secondary: #f9fafb;
    --bg-dark: #111827;
    --bg-card: #ffffff;

    /* Text */
    --text: #111827;
    --text-secondary: #6b7280;
    --text-muted: #9ca3af;
    --text-inverse: #ffffff;

    /* Borders */
    --border: #e5e7eb;
    --border-dark: #d1d5db;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    --shadow-2xl: 0 25px 50px -12px rgb(0 0 0 / 0.25);
    --shadow-glow: 0 0 20px rgb(99 102 241 / 0.3);

    /* Radius */
    --radius-sm: 0.375rem;
    --radius: 0.5rem;
    --radius-md: 0.75rem;
    --radius-lg: 1rem;
    --radius-xl: 1.5rem;
    --radius-2xl: 2rem;
    --radius-full: 9999px;

    /* Spacing */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;
    --space-16: 4rem;
    --space-20: 5rem;
    --space-24: 6rem;

    /* Typography */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    --font-serif: 'Playfair Display', Georgia, serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

    /* Font Sizes */
    --text-xs: 0.75rem;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.5rem;
    --text-3xl: 1.875rem;
    --text-4xl: 2.25rem;
    --text-5xl: 3rem;
    --text-6xl: 3.75rem;
    --text-7xl: 4.5rem;

    /* Line Heights */
    --leading-tight: 1.25;
    --leading-snug: 1.375;
    --leading-normal: 1.5;
    --leading-relaxed: 1.625;
    --leading-loose: 2;

    /* Font Weights */
    --font-light: 300;
    --font-normal: 400;
    --font-medium: 500;
    --font-semibold: 600;
    --font-bold: 700;
    --font-extrabold: 800;

    /* Transitions */
    --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition: 200ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
    --transition-spring: 500ms cubic-bezier(0.34, 1.56, 0.64, 1);

    /* Z-Index */
    --z-dropdown: 1000;
    --z-sticky: 1020;
    --z-fixed: 1030;
    --z-modal-backdrop: 1040;
    --z-modal: 1050;
    --z-popover: 1060;
    --z-tooltip: 1070;

    /* Container */
    --container-max: 1200px;
    --container-narrow: 800px;
    --container-wide: 1400px;
}

/* Dark Mode */
@media (prefers-color-scheme: dark) {
    :root {
        --bg: #0f172a;
        --bg-secondary: #1e293b;
        --bg-dark: #020617;
        --bg-card: #1e293b;
        --text: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --border: #334155;
        --border-dark: #475569;
    }
}

[data-theme='dark'] {
    --bg: #0f172a;
    --bg-secondary: #1e293b;
    --bg-dark: #020617;
    --bg-card: #1e293b;
    --text: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border: #334155;
    --border-dark: #475569;
}

/* ═══ RESET ═══ */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html {
    scroll-behavior: smooth;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

body {
    font-family: var(--font-sans);
    font-size: var(--text-base);
    line-height: var(--leading-normal);
    color: var(--text);
    background: var(--bg);
    min-height: 100vh;
}

img, video, svg {
    display: block;
    max-width: 100%;
    height: auto;
}

a {
    color: var(--primary);
    text-decoration: none;
    transition: color var(--transition);
}
a:hover {
    color: var(--primary-dark);
}

/* ═══ UTILITIES ═══ */
.container {
    width: 100%;
    max-width: var(--container-max);
    margin-left: auto;
    margin-right: auto;
    padding-left: var(--space-6);
    padding-right: var(--space-6);
}
.container-narrow { max-width: var(--container-narrow); }
.container-wide { max-width: var(--container-wide); }

/* Flexbox */
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.items-start { align-items: flex-start; }
.items-end { align-items: flex-end; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.justify-end { justify-content: flex-end; }
.flex-1 { flex: 1; }
.gap-1 { gap: var(--space-1); }
.gap-2 { gap: var(--space-2); }
.gap-3 { gap: var(--space-3); }
.gap-4 { gap: var(--space-4); }
.gap-6 { gap: var(--space-6); }
.gap-8 { gap: var(--space-8); }

/* Grid */
.grid { display: grid; }
.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }
@media (max-width: 768px) {
    .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
}

/* Text */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }
.text-xs { font-size: var(--text-xs); }
.text-sm { font-size: var(--text-sm); }
.text-base { font-size: var(--text-base); }
.text-lg { font-size: var(--text-lg); }
.text-xl { font-size: var(--text-xl); }
.text-2xl { font-size: var(--text-2xl); }
.text-3xl { font-size: var(--text-3xl); }
.text-4xl { font-size: var(--text-4xl); }
.text-5xl { font-size: var(--text-5xl); }
.text-6xl { font-size: var(--text-6xl); }
.text-7xl { font-size: var(--text-7xl); }
.font-light { font-weight: var(--font-light); }
.font-normal { font-weight: var(--font-normal); }
.font-medium { font-weight: var(--font-medium); }
.font-semibold { font-weight: var(--font-semibold); }
.font-bold { font-weight: var(--font-bold); }
.font-extrabold { font-weight: var(--font-extrabold); }
.text-primary { color: var(--primary); }
.text-secondary { color: var(--text-secondary); }
.text-muted { color: var(--text-muted); }
.text-white { color: var(--white); }
.text-success { color: var(--success); }
.text-error { color: var(--error); }
.uppercase { text-transform: uppercase; }
.tracking-wide { letter-spacing: 0.05em; }

/* Spacing */
.p-1 { padding: var(--space-1); }
.p-2 { padding: var(--space-2); }
.p-3 { padding: var(--space-3); }
.p-4 { padding: var(--space-4); }
.p-6 { padding: var(--space-6); }
.p-8 { padding: var(--space-8); }
.px-4 { padding-left: var(--space-4); padding-right: var(--space-4); }
.px-6 { padding-left: var(--space-6); padding-right: var(--space-6); }
.px-8 { padding-left: var(--space-8); padding-right: var(--space-8); }
.py-2 { padding-top: var(--space-2); padding-bottom: var(--space-2); }
.py-4 { padding-top: var(--space-4); padding-bottom: var(--space-4); }
.py-6 { padding-top: var(--space-6); padding-bottom: var(--space-6); }
.py-8 { padding-top: var(--space-8); padding-bottom: var(--space-8); }
.py-12 { padding-top: var(--space-12); padding-bottom: var(--space-12); }
.py-16 { padding-top: var(--space-16); padding-bottom: var(--space-16); }
.py-20 { padding-top: var(--space-20); padding-bottom: var(--space-20); }
.py-24 { padding-top: var(--space-24); padding-bottom: var(--space-24); }
.mt-1 { margin-top: var(--space-1); }
.mt-2 { margin-top: var(--space-2); }
.mt-4 { margin-top: var(--space-4); }
.mt-6 { margin-top: var(--space-6); }
.mt-8 { margin-top: var(--space-8); }
.mb-1 { margin-bottom: var(--space-1); }
.mb-2 { margin-bottom: var(--space-2); }
.mb-4 { margin-bottom: var(--space-4); }
.mb-6 { margin-bottom: var(--space-6); }
.mb-8 { margin-bottom: var(--space-8); }
.mx-auto { margin-left: auto; margin-right: auto; }

/* Borders & Radius */
.rounded { border-radius: var(--radius); }
.rounded-md { border-radius: var(--radius-md); }
.rounded-lg { border-radius: var(--radius-lg); }
.rounded-xl { border-radius: var(--radius-xl); }
.rounded-2xl { border-radius: var(--radius-2xl); }
.rounded-full { border-radius: var(--radius-full); }
.border { border: 1px solid var(--border); }
.border-2 { border: 2px solid var(--border); }

/* Shadows */
.shadow-sm { box-shadow: var(--shadow-sm); }
.shadow { box-shadow: var(--shadow); }
.shadow-md { box-shadow: var(--shadow-md); }
.shadow-lg { box-shadow: var(--shadow-lg); }
.shadow-xl { box-shadow: var(--shadow-xl); }
.shadow-2xl { box-shadow: var(--shadow-2xl); }
.shadow-glow { box-shadow: var(--shadow-glow); }

/* Backgrounds */
.bg { background-color: var(--bg); }
.bg-secondary { background-color: var(--bg-secondary); }
.bg-dark { background-color: var(--bg-dark); }
.bg-primary { background-color: var(--primary); }
.bg-primary-dark { background-color: var(--primary-dark); }
.bg-gradient {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
}
.bg-gradient-accent {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
}
.bg-gradient-dark {
    background: linear-gradient(135deg, var(--gray-900) 0%, var(--gray-800) 100%);
}
.bg-gradient-hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Display */
.hidden { display: none; }
.block { display: block; }
.inline-block { display: inline-block; }
.inline { display: inline; }
.inline-flex { display: inline-flex; }

/* Position */
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; top: 0; }

/* Overflow */
.overflow-hidden { overflow: hidden; }
.overflow-auto { overflow: auto; }
.truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* Width/Height */
.w-full { width: 100%; }
.h-full { height: 100%; }
.min-h-screen { min-height: 100vh; }
.max-w-full { max-width: 100%; }

/* Opacity */
.opacity-0 { opacity: 0; }
.opacity-50 { opacity: 0.5; }
.opacity-100 { opacity: 1; }

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-30px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeInRight {
    from { opacity: 0; transform: translateX(30px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideIn {
    from { transform: translateX(-100%); }
    to { transform: translateX(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
    to { opacity: 1; transform: scale(1); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@keyframes bounce {
    0%, 100% { transform: translateY(-25%); animation-timing-function: cubic-bezier(0.8, 0, 1, 1); }
    50% { transform: translateY(0); animation-timing-function: cubic-bezier(0, 0, 0.2, 1); }
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
@keyframes glow {
    0%, 100% { box-shadow: 0 0 5px var(--primary); }
    50% { box-shadow: 0 0 20px var(--primary), 0 0 40px var(--primary); }
}

.animate-fade-in { animation: fadeIn 0.5s ease-out; }
.animate-fade-in-up { animation: fadeInUp 0.6s ease-out; }
.animate-fade-in-down { animation: fadeInDown 0.6s ease-out; }
.animate-fade-in-left { animation: fadeInLeft 0.6s ease-out; }
.animate-fade-in-right { animation: fadeInRight 0.6s ease-out; }
.animate-scale-in { animation: scaleIn 0.3s ease-out; }
.animate-pulse { animation: pulse 2s infinite; }
.animate-spin { animation: spin 1s linear infinite; }
.animate-bounce { animation: bounce 1s infinite; }
.animate-float { animation: float 3s ease-in-out infinite; }
.animate-glow { animation: glow 2s ease-in-out infinite; }

/* Hover Effects */
.hover-lift { transition: transform var(--transition), box-shadow var(--transition); }
.hover-lift:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.hover-scale { transition: transform var(--transition); }
.hover-scale:hover { transform: scale(1.05); }
.hover-glow { transition: box-shadow var(--transition); }
.hover-glow:hover { box-shadow: var(--shadow-glow); }

/* Stagger Animations */
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
.stagger-3 { animation-delay: 0.3s; }
.stagger-4 { animation-delay: 0.4s; }
.stagger-5 { animation-delay: 0.5s; }
"

# ═══════════════════════════════════════════════════════════════════
# COMPONENT STYLES
# ═══════════════════════════════════════════════════════════════════

shyira_ko COMPONENT_CSS = "
/* ═══ BUTTONS ═══ */
.btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    line-height: 1.5;
    border-radius: var(--radius-lg);
    border: none;
    cursor: pointer;
    transition: all var(--transition);
    text-decoration: none;
    white-space: nowrap;
}
.btn:active { transform: scale(0.97); }

.btn-primary {
    background: var(--primary);
    color: var(--white);
    box-shadow: 0 1px 2px rgb(0 0 0 / 0.05);
}
.btn-primary:hover {
    background: var(--primary-dark);
    box-shadow: 0 4px 12px rgb(99 102 241 / 0.4);
    transform: translateY(-1px);
    color: var(--white);
}

.btn-secondary {
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--border);
}
.btn-secondary:hover {
    background: var(--gray-50);
    border-color: var(--gray-300);
}

.btn-accent {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
    color: var(--white);
}
.btn-accent:hover {
    box-shadow: 0 4px 12px rgb(245 158 11 / 0.4);
    transform: translateY(-1px);
    color: var(--white);
}

.btn-ghost {
    background: transparent;
    color: var(--text-secondary);
}
.btn-ghost:hover {
    background: var(--gray-100);
    color: var(--text);
}

.btn-danger {
    background: var(--error);
    color: var(--white);
}
.btn-danger:hover {
    background: var(--error-dark);
    color: var(--white);
}

.btn-success {
    background: var(--success);
    color: var(--white);
}
.btn-success:hover {
    background: var(--success-dark);
    color: var(--white);
}

.btn-lg {
    padding: 0.875rem 1.75rem;
    font-size: var(--text-base);
    border-radius: var(--radius-xl);
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: var(--text-xs);
}

.btn-icon {
    width: 2.5rem;
    height: 2.5rem;
    padding: 0;
    border-radius: var(--radius);
}

/* ═══ NAVBAR ═══ */
.navbar {
    position: sticky;
    top: 0;
    z-index: var(--z-sticky);
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 0;
    transition: all var(--transition);
}
[data-theme='dark'] .navbar {
    background: rgba(15, 23, 42, 0.8);
}
.navbar.scrolled {
    box-shadow: var(--shadow-md);
}
.navbar-inner {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
}
.navbar-brand {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: var(--text-xl);
    font-weight: var(--font-bold);
    color: var(--text);
    text-decoration: none;
}
.navbar-brand:hover { color: var(--primary); }
.navbar-brand img {
    height: 2rem;
}
.navbar-nav {
    display: flex;
    align-items: center;
    gap: 0.25rem;
    list-style: none;
}
.navbar-link {
    display: flex;
    align-items: center;
    padding: 0.5rem 1rem;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    color: var(--text-secondary);
    border-radius: var(--radius-md);
    transition: all var(--transition);
    text-decoration: none;
}
.navbar-link:hover {
    color: var(--primary);
    background: var(--primary-50);
}
.navbar-link.active {
    color: var(--primary);
    background: var(--primary-50);
}
.navbar-actions {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.navbar-toggle {
    display: none;
    padding: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
}
@media (max-width: 768px) {
    .navbar-nav { display: none; }
    .navbar-toggle { display: flex; }
    .navbar-nav.active {
        display: flex;
        flex-direction: column;
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--bg);
        border-bottom: 1px solid var(--border);
        padding: 1rem;
        box-shadow: var(--shadow-lg);
    }
}

/* ═══ HERO ═══ */
.hero {
    position: relative;
    overflow: hidden;
    padding: 6rem 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: var(--white);
}
.hero::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><circle cx=\"50\" cy=\"50\" r=\"40\" fill=\"none\" stroke=\"white\" stroke-width=\"0.5\" opacity=\"0.1\"/></svg>') repeat;
    background-size: 100px 100px;
    opacity: 0.3;
}
.hero-content {
    position: relative;
    z-index: 1;
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}
.hero-title {
    font-size: var(--text-6xl);
    font-weight: var(--font-extrabold);
    line-height: var(--leading-tight);
    margin-bottom: var(--space-6);
    letter-spacing: -0.025em;
}
.hero-subtitle {
    font-size: var(--text-xl);
    opacity: 0.9;
    margin-bottom: var(--space-8);
    line-height: var(--leading-relaxed);
}
.hero-buttons {
    display: flex;
    gap: var(--space-4);
    justify-content: center;
    flex-wrap: wrap;
}
.hero .btn-primary {
    background: var(--white);
    color: var(--primary-dark);
}
.hero .btn-primary:hover {
    box-shadow: 0 8px 25px rgb(0 0 0 / 0.2);
}
.hero .btn-secondary {
    background: rgba(255, 255, 255, 0.1);
    color: var(--white);
    border-color: rgba(255, 255, 255, 0.3);
}
.hero .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.2);
}
.hero-shapes {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
    pointer-events: none;
}
.hero-shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.1);
}
.hero-shape-1 {
    width: 300px;
    height: 300px;
    top: -100px;
    right: -100px;
    animation: float 6s ease-in-out infinite;
}
.hero-shape-2 {
    width: 200px;
    height: 200px;
    bottom: -50px;
    left: -50px;
    animation: float 8s ease-in-out infinite reverse;
}
.hero-shape-3 {
    width: 150px;
    height: 150px;
    top: 50%;
    left: 10%;
    animation: float 7s ease-in-out infinite 1s;
}

/* ═══ CARDS ═══ */
.card {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    border: 1px solid var(--border);
    overflow: hidden;
    transition: all var(--transition);
}
.card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-2px);
}
.card-body {
    padding: var(--space-6);
}
.card-header {
    padding: var(--space-6);
    border-bottom: 1px solid var(--border);
}
.card-footer {
    padding: var(--space-4) var(--space-6);
    border-top: 1px solid var(--border);
    background: var(--bg-secondary);
}
.card-image {
    width: 100%;
    height: 200px;
    object-fit: cover;
}
.card-title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    margin-bottom: var(--space-2);
    color: var(--text);
}
.card-text {
    color: var(--text-secondary);
    line-height: var(--leading-relaxed);
}
.card-flat { border: none; box-shadow: var(--shadow); }
.card-gradient {
    border: none;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: var(--white);
}
.card-gradient .card-title,
.card-gradient .card-text { color: var(--white); }

/* ═══ FEATURES ═══ */
.features {
    padding: 6rem 0;
    background: var(--bg);
}
.feature-card {
    text-align: center;
    padding: var(--space-8);
    border-radius: var(--radius-xl);
    transition: all var(--transition);
}
.feature-card:hover {
    background: var(--bg-secondary);
    transform: translateY(-4px);
}
.feature-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 4rem;
    height: 4rem;
    border-radius: var(--radius-lg);
    background: var(--primary-50);
    color: var(--primary);
    font-size: 1.5rem;
    margin-bottom: var(--space-4);
}
.feature-title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    margin-bottom: var(--space-2);
}
.feature-text {
    color: var(--text-secondary);
    line-height: var(--leading-relaxed);
}

/* ═══ SECTION ═══ */
.section {
    padding: 6rem 0;
}
.section-alt {
    background: var(--bg-secondary);
}
.section-dark {
    background: var(--bg-dark);
    color: var(--white);
}
.section-header {
    text-align: center;
    max-width: 700px;
    margin: 0 auto var(--space-16);
}
.section-badge {
    display: inline-block;
    padding: 0.375rem 1rem;
    background: var(--primary-50);
    color: var(--primary);
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    border-radius: var(--radius-full);
    margin-bottom: var(--space-4);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.section-title {
    font-size: var(--text-4xl);
    font-weight: var(--font-bold);
    margin-bottom: var(--space-4);
    letter-spacing: -0.025em;
    line-height: var(--leading-tight);
}
.section-subtitle {
    font-size: var(--text-lg);
    color: var(--text-secondary);
    line-height: var(--leading-relaxed);
}
.section-dark .section-subtitle { color: var(--gray-400); }

/* ═══ PRICING ═══ */
.pricing-card {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    border: 1px solid var(--border);
    padding: var(--space-8);
    text-align: center;
    transition: all var(--transition);
    position: relative;
}
.pricing-card.featured {
    border-color: var(--primary);
    box-shadow: var(--shadow-glow);
    transform: scale(1.05);
}
.pricing-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    padding: 0.25rem 1rem;
    background: var(--primary);
    color: var(--white);
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    border-radius: var(--radius-full);
    text-transform: uppercase;
}
.pricing-name {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
    margin-bottom: var(--space-2);
}
.pricing-price {
    font-size: var(--text-5xl);
    font-weight: var(--font-extrabold);
    color: var(--primary);
    margin-bottom: var(--space-4);
}
.pricing-price span {
    font-size: var(--text-base);
    font-weight: var(--font-normal);
    color: var(--text-secondary);
}
.pricing-features {
    list-style: none;
    margin: var(--space-8) 0;
    text-align: left;
}
.pricing-features li {
    padding: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: var(--text-secondary);
}
.pricing-features li::before {
    content: '✓';
    display: flex;
    align-items: center;
    justify-content: center;
    width: 1.25rem;
    height: 1.25rem;
    background: var(--success);
    color: var(--white);
    border-radius: var(--radius-full);
    font-size: 0.75rem;
    flex-shrink: 0;
}

/* ═══ TESTIMONIALS ═══ */
.testimonial {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    padding: var(--space-8);
    border: 1px solid var(--border);
}
.testimonial-quote {
    font-size: var(--text-lg);
    font-style: italic;
    color: var(--text);
    margin-bottom: var(--space-6);
    line-height: var(--leading-relaxed);
}
.testimonial-quote::before {
    content: '"';
    font-size: var(--text-5xl);
    color: var(--primary);
    line-height: 0;
    vertical-align: -0.5em;
    margin-right: 0.25em;
}
.testimonial-author {
    display: flex;
    align-items: center;
    gap: var(--space-4);
}
.testimonial-avatar {
    width: 3rem;
    height: 3rem;
    border-radius: var(--radius-full);
    background: var(--primary-50);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: var(--font-bold);
    color: var(--primary);
}
.testimonial-name {
    font-weight: var(--font-semibold);
}
.testimonial-role {
    font-size: var(--text-sm);
    color: var(--text-secondary);
}

/* ═══ STATS ═══ */
.stat {
    text-align: center;
}
.stat-value {
    font-size: var(--text-5xl);
    font-weight: var(--font-extrabold);
    color: var(--primary);
    line-height: 1;
    margin-bottom: var(--space-2);
}
.stat-label {
    font-size: var(--text-sm);
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ═══ CTA ═══ */
.cta {
    padding: 6rem 0;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: var(--white);
    text-align: center;
}
.cta-title {
    font-size: var(--text-4xl);
    font-weight: var(--font-bold);
    margin-bottom: var(--space-4);
}
.cta-text {
    font-size: var(--text-lg);
    opacity: 0.9;
    margin-bottom: var(--space-8);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}
.cta .btn-primary {
    background: var(--white);
    color: var(--primary-dark);
}

/* ═══ FOOTER ═══ */
.footer {
    background: var(--bg-dark);
    color: var(--gray-400);
    padding: 4rem 0 2rem;
}
.footer-grid {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 3rem;
    margin-bottom: 3rem;
}
@media (max-width: 768px) {
    .footer-grid { grid-template-columns: 1fr; }
}
.footer-brand {
    font-size: var(--text-xl);
    font-weight: var(--font-bold);
    color: var(--white);
    margin-bottom: var(--space-4);
}
.footer-text {
    line-height: var(--leading-relaxed);
    max-width: 300px;
}
.footer-heading {
    font-size: var(--text-sm);
    font-weight: var(--font-semibold);
    color: var(--white);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: var(--space-4);
}
.footer-links {
    list-style: none;
}
.footer-links li {
    margin-bottom: var(--space-2);
}
.footer-links a {
    color: var(--gray-400);
    transition: color var(--transition);
    text-decoration: none;
}
.footer-links a:hover {
    color: var(--white);
}
.footer-bottom {
    padding-top: var(--space-8);
    border-top: 1px solid var(--gray-800);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-4);
}
.footer-copyright {
    font-size: var(--text-sm);
}
.footer-social {
    display: flex;
    gap: var(--space-4);
}
.footer-social a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.5rem;
    height: 2.5rem;
    border-radius: var(--radius-full);
    background: var(--gray-800);
    color: var(--gray-400);
    transition: all var(--transition);
}
.footer-social a:hover {
    background: var(--primary);
    color: var(--white);
}

/* ═══ FORMS ═══ */
.form-group {
    margin-bottom: var(--space-4);
}
.form-label {
    display: block;
    font-size: var(--text-sm);
    font-weight: var(--font-medium);
    margin-bottom: var(--space-2);
    color: var(--text);
}
.form-input {
    width: 100%;
    padding: 0.625rem 1rem;
    font-size: var(--text-sm);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    background: var(--bg);
    color: var(--text);
    transition: all var(--transition);
}
.form-input:focus {
    outline: none;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-100);
}
.form-input::placeholder {
    color: var(--text-muted);
}
textarea.form-input {
    min-height: 120px;
    resize: vertical;
}
.form-hint {
    font-size: var(--text-xs);
    color: var(--text-muted);
    margin-top: var(--space-1);
}
.form-error {
    font-size: var(--text-xs);
    color: var(--error);
    margin-top: var(--space-1);
}
.form-input.error {
    border-color: var(--error);
}
.form-input.error:focus {
    box-shadow: 0 0 0 3px rgb(239 68 68 / 0.1);
}

/* ═══ TABLE ═══ */
.table-wrapper {
    overflow-x: auto;
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
}
.table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--text-sm);
}
.table th {
    background: var(--bg-secondary);
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: var(--font-semibold);
    color: var(--text);
    border-bottom: 1px solid var(--border);
}
.table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    color: var(--text-secondary);
}
.table tr:last-child td { border-bottom: none; }
.table tr:hover td { background: var(--bg-secondary); }

/* ═══ BADGES ═══ */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    font-size: var(--text-xs);
    font-weight: var(--font-semibold);
    border-radius: var(--radius-full);
}
.badge-primary { background: var(--primary-50); color: var(--primary); }
.badge-success { background: rgb(16 185 129 / 0.1); color: var(--success); }
.badge-error { background: rgb(239 68 68 / 0.1); color: var(--error); }
.badge-warning { background: rgb(245 158 11 / 0.1); color: var(--warning); }

/* ═══ ALERTS ═══ */
.alert {
    display: flex;
    align-items: flex-start;
    gap: var(--space-3);
    padding: var(--space-4);
    border-radius: var(--radius-lg);
    font-size: var(--text-sm);
}
.alert-success { background: rgb(16 185 129 / 0.1); color: var(--success-dark); border: 1px solid rgb(16 185 129 / 0.2); }
.alert-error { background: rgb(239 68 68 / 0.1); color: var(--error-dark); border: 1px solid rgb(239 68 68 / 0.2); }
.alert-warning { background: rgb(245 158 11 / 0.1); color: var(--warning-dark); border: 1px solid rgb(245 158 11 / 0.2); }
.alert-info { background: rgb(59 130 246 / 0.1); color: var(--info); border: 1px solid rgb(59 130 246 / 0.2); }

/* ═══ MODAL ═══ */
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: var(--z-modal);
    opacity: 0;
    pointer-events: none;
    transition: opacity var(--transition);
}
.modal-overlay.active {
    opacity: 1;
    pointer-events: all;
}
.modal {
    background: var(--bg);
    border-radius: var(--radius-xl);
    box-shadow: var(--shadow-2xl);
    width: 90%;
    max-width: 500px;
    max-height: 90vh;
    overflow: auto;
    transform: scale(0.9) translateY(20px);
    transition: transform var(--transition-spring);
}
.modal-overlay.active .modal {
    transform: scale(1) translateY(0);
}
.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: var(--space-6);
    border-bottom: 1px solid var(--border);
}
.modal-title {
    font-size: var(--text-xl);
    font-weight: var(--font-semibold);
}
.modal-close {
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    background: none;
    cursor: pointer;
    border-radius: var(--radius);
    color: var(--text-muted);
    transition: all var(--transition);
}
.modal-close:hover {
    background: var(--gray-100);
    color: var(--text);
}
.modal-body { padding: var(--space-6); }
.modal-footer {
    padding: var(--space-4) var(--space-6);
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: flex-end;
    gap: var(--space-3);
}

/* ═══ TOAST ═══ */
.toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: var(--z-tooltip);
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}
.toast {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    background: var(--bg);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border);
    animation: slideIn 0.3s ease-out;
    min-width: 300px;
}

/* ═══ SCROLL REVEAL ═══ */
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s ease-out;
}
.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}
"

shyira_ko URUBUGA_JS = "
/* ═══ URUBUGA INTERACTIVE JS ═══ */
(function() {
    'use strict';

    // Dark Mode Toggle
    const theme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', theme);

    window.toggleTheme = function() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    };

    // Navbar Scroll Effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            navbar.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // Mobile Menu Toggle
    const toggle = document.querySelector('.navbar-toggle');
    const nav = document.querySelector('.navbar-nav');
    if (toggle && nav) {
        toggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }

    // Scroll Reveal
    const reveals = document.querySelectorAll('.reveal');
    if (reveals.length > 0) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, { threshold: 0.1 });
        reveals.forEach(function(el) { observer.observe(el); });
    }

    // Smooth Scroll
    document.querySelectorAll('a[href^=\"#\"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Counter Animation
    const counters = document.querySelectorAll('[data-count]');
    if (counters.length > 0) {
        const counterObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const target = parseInt(entry.target.getAttribute('data-count'));
                    let current = 0;
                    const increment = target / 50;
                    const timer = setInterval(function() {
                        current += increment;
                        if (current >= target) {
                            entry.target.textContent = target.toLocaleString();
                            clearInterval(timer);
                        } else {
                            entry.target.textContent = Math.floor(current).toLocaleString();
                        }
                    }, 30);
                    counterObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        counters.forEach(function(el) { counterObserver.observe(el); });
    }

    // Modal
    window.openModal = function(id) {
        document.getElementById(id).classList.add('active');
        document.body.style.overflow = 'hidden';
    };
    window.closeModal = function(id) {
        document.getElementById(id).classList.remove('active');
        document.body.style.overflow = '';
    };

    // Toast
    window.showToast = function(message, type) {
        type = type || 'info';
        var container = document.querySelector('.toast-container') || (function() {
            var c = document.createElement('div');
            c.className = 'toast-container';
            document.body.appendChild(c);
            return c;
        })();
        var toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        toast.innerHTML = '<span>' + message + '</span>';
        container.appendChild(toast);
        setTimeout(function() { toast.remove(); }, 3000);
    };

    // Typing Effect
    window.typeEffect = function(element, text, speed) {
        speed = speed || 50;
        var i = 0;
        element.textContent = '';
        function type() {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        type();
    };
})();
"

# ═══════════════════════════════════════════════════════════════════
# COMPONENT FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

urwego UrubugaCSS kora
    umurimo __init__(self)
        self.css = URUBUGA_CSS
        self.components = COMPONENT_CSS
        self.js = URUBUGA_JS
    iherezo

    umurimo get_full_css(self)
        subira self.css + self.components
    iherezo

    umurimo get_js(self)
        subira self.js
    iherezo
iherezo

urwego UrubugaInyandikorumurongoAdvanced kora
    umurimo __init__(self)
        self.css = UrubugaCSS.nshya()
    iherezo

    umurimo base_page(self, params)
        shyiramo title = params.get("title", "Urubuga")
        shyiramo body = params.get("body", "")
        shyiramo nav = params.get("nav", "")
        shyiramo footer = params.get("footer", "")
        shyiramo scripts = params.get("scripts", "")

        subira "<!DOCTYPE html>" + chr(10) +
            "<html lang=\"rw\">" + chr(10) +
            "<head>" + chr(10) +
            "  <meta charset=\"UTF-8\">" + chr(10) +
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">" + chr(10) +
            "  <title>" + title + "</title>" + chr(10) +
            "  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">" + chr(10) +
            "  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap\" rel=\"stylesheet\">" + chr(10) +
            "  <style>" + self.css.get_full_css() + "</style>" + chr(10) +
            "</head>" + chr(10) +
            "<body>" + chr(10) +
            nav + chr(10) +
            body + chr(10) +
            footer + chr(10) +
            "<script>" + self.css.get_js() + "</script>" + chr(10) +
            scripts + chr(10) +
            "</body>" + chr(10) +
            "</html>"
    iherezo

    umurimo navbar(self, params)
        shyiramo brand = params.get("brand", "Urubuga")
        shyiramo links = params.get("links", [])
        shyiramo cta = params.get("cta", none)

        shyiramo links_html = ""
        buri link in links kora
            links_html = links_html + "<a href=\"" + link.get("href", "#") + "\" class=\"navbar-link\">" + link.get("izina", "") + "</a>"
        iherezo

        shyiramo cta_html = ""
        niba cta != none kora
            cta_html = "<a href=\"" + cta.get("href", "#") + "\" class=\"btn btn-primary btn-sm\">" + cta.get("izina", "Get Started") + "</a>"
        iherezo

        subira "<nav class=\"navbar\">" + chr(10) +
            "  <div class=\"container flex items-center justify-between\">" + chr(10) +
            "    <a href=\"/\" class=\"navbar-brand\">" + brand + "</a>" + chr(10) +
            "    <div class=\"navbar-nav\">" + links_html + "</div>" + chr(10) +
            "    <div class=\"navbar-actions\">" + cta_html + "</div>" + chr(10) +
            "    <button class=\"navbar-toggle\" aria-label=\"Menu\">☰</button>" + chr(10) +
            "  </div>" + chr(10) +
            "</nav>"
    iherezo

    umurimo hero(self, params)
        shyiramo umutwe = params.get("umutwe", "Murakaza neza")
        shyiramo inkuru = params.get("inkuru", "")
        shyiramo buttons = params.get("buttons", [])
        shyiramo bg = params.get("bg", "")

        shyiramo bg_style = ""
        niba bg != "" kora
            bg_style = " style=\"background: " + bg + ";\""
        iherezo

        shyiramo btns = ""
        buri btn in buttons kora
            shyiramo cls = "btn " + btn.get("class", "btn-primary")
            btns = btns + "<a href=\"" + btn.get("href", "#") + "\" class=\"" + cls + "\">" + btn.get("izina", "") + "</a>"
        iherezo

        subira "<section class=\"hero\"" + bg_style + ">" + chr(10) +
            "  <div class=\"hero-shapes\">" + chr(10) +
            "    <div class=\"hero-shape hero-shape-1\"></div>" + chr(10) +
            "    <div class=\"hero-shape hero-shape-2\"></div>" + chr(10) +
            "    <div class=\"hero-shape hero-shape-3\"></div>" + chr(10) +
            "  </div>" + chr(10) +
            "  <div class=\"container\">" + chr(10) +
            "    <div class=\"hero-content animate-fade-in-up\">" + chr(10) +
            "      <h1 class=\"hero-title\">" + umutwe + "</h1>" + chr(10) +
            "      <p class=\"hero-subtitle\">" + inkuru + "</p>" + chr(10) +
            "      <div class=\"hero-buttons\">" + btns + "</div>" + chr(10) +
            "    </div>" + chr(10) +
            "  </div>" + chr(10) +
            "</section>"
    iherezo

    umurimo card(self, params)
        shyiramo umutwe = params.get("umutwe", "")
        shyiramo inkuru = params.get("inkuru", "")
        shyiramo icon = params.get("icon", "")
        shyiramo link = params.get("link", "")
        shyiramo image = params.get("image", "")
        shyiramo ubwoko = params.get("ubwoko", "")

        shyiramo classes = "card"
        niba ubwoko == "flat" kora
            classes = classes + " card-flat"
        iherezo
        niba ubwoko == "gradient" kora
            classes = classes + " card-gradient"
        iherezo

        shyiramo image_html = ""
        niba image != "" kora
            image_html = "<img src=\"" + image + "\" alt=\"" + umutwe + "\" class=\"card-image\">"
        iherezo

        shyiramo icon_html = ""
        niba icon != "" kora
            icon_html = "<div class=\"feature-icon\">" + icon + "</div>"
        iherezo

        shyiramo link_html = ""
        niba link != "" kora
            link_html = "<a href=\"" + link + "\" class=\"btn btn-primary btn-sm mt-4\">Menya byinshi</a>"
        iherezo

        subira "<div class=\"" + classes + " hover-lift animate-fade-in-up\">" + chr(10) +
            image_html + chr(10) +
            "  <div class=\"card-body text-center\">" + chr(10) +
            icon_html + chr(10) +
            "    <h3 class=\"card-title\">" + umutwe + "</h3>" + chr(10) +
            "    <p class=\"card-text\">" + inkuru + "</p>" + chr(10) +
            link_html + chr(10) +
            "  </div>" + chr(10) +
            "</div>"
    iherezo

    umurimo section(self, params)
        shyiramo umutwe = params.get("umutwe", "")
        shyiramo inkuru = params.get("inkuru", "")
        shyiramo badge = params.get("badge", "")
        shyiramo content = params.get("content", "")
        shyiramo ubwoko = params.get("ubwoko", "")

        shyiramo classes = "section"
        niba ubwoko == "alt" kora
            classes = classes + " section-alt"
        iherezo
        niba ubwoko == "dark" kora
            classes = classes + " section-dark"
        iherezo

        shyiramo badge_html = ""
        niba badge != "" kora
            badge_html = "<span class=\"section-badge\">" + badge + "</span>"
        iherezo

        shyiramo header_html = ""
        niba umutwe != "" kora
            header_html = "<div class=\"section-header reveal\">" + chr(10) +
                badge_html + chr(10) +
                "<h2 class=\"section-title\">" + umutwe + "</h2>" + chr(10) +
                "<p class=\"section-subtitle\">" + inkuru + "</p>" + chr(10) +
                "</div>"
        iherezo

        subira "<section class=\"" + classes + "\">" + chr(10) +
            "  <div class=\"container\">" + chr(10) +
            header_html + chr(10) +
            content + chr(10) +
            "  </div>" + chr(10) +
            "</section>"
    iherezo

    umurimo features_grid(self, params)
        shyiramo items = params.get("items", [])

        shyiramo items_html = ""
        buri item in items kora
            items_html = items_html + "<div class=\"feature-card reveal\">" + chr(10) +
                "<div class=\"feature-icon\">" + item.get("icon", "") + "</div>" + chr(10) +
                "<h3 class=\"feature-title\">" + item.get("umutwe", "") + "</h3>" + chr(10) +
                "<p class=\"feature-text\">" + item.get("inkuru", "") + "</p>" + chr(10) +
                "</div>"
        iherezo

        subira "<div class=\"grid grid-3 gap-8\">" + items_html + "</div>"
    iherezo

    umurimo pricing_grid(self, params)
        shyiramo plans = params.get("plans", [])

        shyiramo plans_html = ""
        buri plan in plans kora
            shyiramo featured = plan.get("featured", ubusa)
            shyiramo classes = "pricing-card"
            niba featured kora
                classes = classes + " featured"
            iherezo

            shyiramo badge_html = ""
            niba featured kora
                badge_html = "<span class=\"pricing-badge\">Best Value</span>"
            iherezo

            shyiramo features_html = ""
            buri feature in plan.get("features", []) kora
                features_html = features_html + "<li>" + feature + "</li>"
            iherezo

            plans_html = plans_html + "<div class=\"" + classes + " reveal\">" + chr(10) +
                badge_html + chr(10) +
                "<div class=\"pricing-name\">" + plan.get("name", "") + "</div>" + chr(10) +
                "<div class=\"pricing-price\">" + plan.get("price", "") + "<span>/mo</span></div>" + chr(10) +
                "<ul class=\"pricing-features\">" + features_html + "</ul>" + chr(10) +
                "<a href=\"#\" class=\"btn btn-primary w-full\">Tangira</a>" + chr(10) +
                "</div>"
        iherezo

        subira "<div class=\"grid grid-3 gap-8\">" + plans_html + "</div>"
    iherezo

    umurimo testimonial_grid(self, params)
        shyiramo items = params.get("items", [])

        shyiramo items_html = ""
        buri item in items kora
            shyiramo initials = item.get("izina", "U").slice(0, 1)
            items_html = items_html + "<div class=\"testimonial reveal\">" + chr(10) +
                "<p class=\"testimonial-quote\">" + item.get("quote", "") + "</p>" + chr(10) +
                "<div class=\"testimonial-author\">" + chr(10) +
                "<div class=\"testimonial-avatar\">" + initials + "</div>" + chr(10) +
                "<div>" + chr(10) +
                "<div class=\"testimonial-name\">" + item.get("izina", "") + "</div>" + chr(10) +
                "<div class=\"testimonial-role\">" + item.get("role", "") + "</div>" + chr(10) +
                "</div>" + chr(10) +
                "</div>" + chr(10) +
                "</div>"
        iherezo

        subira "<div class=\"grid grid-3 gap-8\">" + items_html + "</div>"
    iherezo

    umurimo stats(self, params)
        shyiramo items = params.get("items", [])

        shyiramo items_html = ""
        buri item in items kora
            items_html = items_html + "<div class=\"stat reveal\">" + chr(10) +
                "<div class=\"stat-value\" data-count=\"" + shobora_umuntu(item.get("value", 0)) + "\">0</div>" + chr(10) +
                "<div class=\"stat-label\">" + item.get("label", "") + "</div>" + chr(10) +
                "</div>"
        iherezo

        subira "<div class=\"grid grid-4 gap-8\">" + items_html + "</div>"
    iherezo

    umurimo cta_section(self, params)
        shyiramo umutwe = params.get("umutwe", "")
        shyiramo inkuru = params.get("inkuru", "")
        shyiramo button = params.get("button", {})

        subira "<section class=\"cta\">" + chr(10) +
            "  <div class=\"container text-center\">" + chr(10) +
            "    <h2 class=\"cta-title\">" + umutwe + "</h2>" + chr(10) +
            "    <p class=\"cta-text\">" + inkuru + "</p>" + chr(10) +
            "    <a href=\"" + button.get("href", "#") + "\" class=\"btn btn-primary btn-lg\">" + button.get("izina", "Get Started") + "</a>" + chr(10) +
            "  </div>" + chr(10) +
            "</section>"
    iherezo

    umurimo footer(self, params)
        shyiramo brand = params.get("brand", "Urubuga")
        shyiramo inkuru = params.get("inkuru", "")
        shyiramo columns = params.get("columns", [])
        shyiramo copyright = params.get("copyright", "")

        shyiramo columns_html = ""
        buri col in columns kora
            shyiramo links_html = ""
            buri link in col.get("links", []) kora
                links_html = links_html + "<li><a href=\"" + link.get("href", "#") + "\">" + link.get("izina", "") + "</a></li>"
            iherezo
            columns_html = columns_html + "<div>" + chr(10) +
                "<h4 class=\"footer-heading\">" + col.get("umutwe", "") + "</h4>" + chr(10) +
                "<ul class=\"footer-links\">" + links_html + "</ul>" + chr(10) +
                "</div>"
        iherezo

        subira "<footer class=\"footer\">" + chr(10) +
            "  <div class=\"container\">" + chr(10) +
            "    <div class=\"footer-grid\">" + chr(10) +
            "      <div>" + chr(10) +
            "        <div class=\"footer-brand\">" + brand + "</div>" + chr(10) +
            "        <p class=\"footer-text\">" + inkuru + "</p>" + chr(10) +
            "      </div>" + chr(10) +
            columns_html + chr(10) +
            "    </div>" + chr(10) +
            "    <div class=\"footer-bottom\">" + chr(10) +
            "      <p class=\"footer-copyright\">" + copyright + "</p>" + chr(10) +
            "    </div>" + chr(10) +
            "  </div>" + chr(10) +
            "</footer>"
    iherezo
iherezo

umurimo gukora_template_engine()
    subira UrubugaInyandikorumurongoAdvanced.nshya()
iherezo
