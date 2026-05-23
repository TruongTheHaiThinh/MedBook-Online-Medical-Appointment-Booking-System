# 🏛️ MEDBOOK ENTERPRISE - THE ULTIMATE FLYING UI/UX PROMPT
## Gửi cho Claude AI để thiết kế Landing Page + Design System

---

## [CONTEXT & ROLE]

You are a world-class Senior UI/UX Engineer and Creative Director with 15 years of experience designing award-winning healthcare platforms. Your mission is to create the **Landing Page** (index.html + style.css) for **"MedBook Enterprise"** — a premium medical appointment booking system.

This is NOT a generic medical website. It must look like a **masterpiece** — extraordinary, "flying," and ethereal. Think: the love child of **Stripe.com**, **Linear.app**, and a futuristic hospital from the year 2035. Every pixel must evoke trust, innovation, and calm.

---

## [1. CORE AESTHETIC: THE "FLYING & ETHEREAL" SYSTEM]

### 1.1 Aurora Mesh Backdrop
- The `<body>` background must be a **dynamic, slow-moving Aurora Mesh Gradient** using CSS `@keyframes`.
- Colors: shifting between soft Mint (#f0fdf4), Sky (#eff6ff), Lavender (#fdf2f8), and Pearl (#f8fafc).
- `background-size: 400% 400%` with `animation: aurora 20s ease infinite`.
- It should feel like **liquid silk** slowly moving behind a frosted glass pane.

### 1.2 Zero-Gravity Glassmorphism
- Every container, card, navbar, and modal must use **deep glassmorphism**:
  - `background: rgba(255, 255, 255, 0.15)` to `rgba(255, 255, 255, 0.4)`
  - `backdrop-filter: blur(40px)` and `-webkit-backdrop-filter: blur(40px)`
  - `border: 1px solid rgba(255, 255, 255, 0.25)`
  - Soft, ethereal box-shadows: `0 8px 32px rgba(0, 0, 0, 0.08)`
- Cards should feel like they are **floating in midair** over the aurora.

### 1.3 3D Perspective Transforms
- The Hero Section must use `perspective: 2000px`.
- The main hero card/container should have `transform: rotateY(-8deg) rotateX(5deg)` by default.
- On hover, it should smoothly animate to `rotateY(0) rotateX(0)` using `transition: 0.8s cubic-bezier(0.23, 1, 0.32, 1)`.
- This creates a sense of **physical depth** — like the card is tilting towards you.

### 1.4 Cinematic Motion & Scroll-Reveal
- Use "Ease-Out-Expo" transitions: `cubic-bezier(0.16, 1, 0.3, 1)` with duration 0.8s to 1.2s.
- Implement **Scroll-Reveal**: elements start with `opacity: 0; transform: translateY(60px)` and animate to `opacity: 1; transform: translateY(0)` when they enter the viewport.
- Use `IntersectionObserver` for performance.
- Key UI elements should have **asynchronous floating animations** (`@keyframes float` with different delays).

### 1.5 Decoration Blobs
- Add 2-3 large blurred color blobs (`filter: blur(120px)`, `border-radius: 50%`, `opacity: 0.2-0.3`) positioned absolutely behind content.
- Colors: One Emerald (#10b981), one Blue (#3b82f6), one Purple (#8b5cf6).
- They should add a **dreamy, atmospheric depth** without distracting from content.

---

## [2. DYNAMIC ROLE-BASED COLOR BRANDING]

The entire UI must adapt its **color "soul"** based on the logged-in user's role. Use a centralized **CSS Custom Properties** system on `:root` and override via body classes:

| Role | Body Class | Color Name | HEX | HSL Hue |
|------|-----------|------------|-----|---------|
| **Patient** | `theme-patient` | Emerald Green | #10b981 | 162 |
| **Doctor** | `theme-doctor` | Cyber Blue | #3b82f6 | 217 |
| **HR Admin** | `theme-hr-admin` | Royal Purple | #8b5cf6 | 262 |
| **Cashier** | `theme-cashier-admin` | Golden Amber | #f59e0b | 38 |

**Implementation:**
```css
:root {
    --primary-h: 162;
    --primary-s: 84%;
    --primary-l: 39%;
    --primary: hsl(var(--primary-h), var(--primary-s), var(--primary-l));
    --primary-light: hsl(var(--primary-h), var(--primary-s), 95%);
    --primary-dark: hsl(var(--primary-h), var(--primary-s), 28%);
}
body.theme-patient  { --primary-h: 162; }
body.theme-doctor   { --primary-h: 217; }
body.theme-hr-admin { --primary-h: 262; }
body.theme-cashier-admin { --primary-h: 38; }
```

**Requirement:** ALL primary buttons, glows, shadows, accent text, icon backgrounds, and gradient stops must reference `var(--primary)` so they **automatically switch colors** when the body class changes.

---

## [3. LANDING PAGE STRUCTURE (index.html)]

### 3.1 Floating Pill Navbar
- `position: fixed; top: 20px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 1200px;`
- `border-radius: 9999px;` (full pill shape)
- Deep glass effect with `backdrop-filter: blur(30px)`
- On scroll (past 80px), shrink padding and increase background opacity.
- Contains: Logo (left), Nav Links (center), Auth Buttons (right).

### 3.2 Hero Section (THE SHOWPIECE)
- Wrap in a `perspective: 2000px` container.
- Inside: a **3D glass card** with the title, subtitle, and CTA buttons.
- **Title:** "Trải nghiệm Y Tế Số chưa bao giờ mượt mà đến thế." — Use `font-size: clamp(3rem, 6vw, 5.5rem)`, `font-weight: 900`, `letter-spacing: -0.04em`.
- The words "Y Tế Số" must use `background: linear-gradient(135deg, var(--primary), #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;`.
- **CTA Buttons:** Two buttons — Primary ("Bắt đầu trải nghiệm") with glow effect, and Outline ("Tìm hiểu thêm").
- Add 2-3 **floating medical icons** (stethoscope, heartbeat, DNA) positioned absolutely around the card with `animation: float 8s ease-in-out infinite`.

### 3.3 Specialties/Services Section
- Section title with gradient text effect.
- **Bento Grid** (`display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem;`).
- Each specialty card: glass card with icon-box, name, and short description.
- Cards should have `hover: translateY(-12px)` with a glowing border.
- **Data is loaded dynamically** via `api.get('/admin/specialties')` — see API section below.

### 3.4 Footer
- Minimal, elegant footer with glass background.
- Logo, copyright, and brief tagline.

### 3.5 Auth Modal (Login/Register)
- Uses the `.modal-overlay` with `backdrop-filter: blur(20px)` for the backdrop.
- The modal card itself: glass effect, large border-radius (2rem+), smooth scale-in animation.
- Login form: Email/Phone input, Password input, Submit button, Toggle to Register.
- Register form: Full name, Phone, Password, Submit button, Toggle to Login.
- Input fields: `border-radius: 1rem`, glowing focus states with `box-shadow: 0 0 0 4px var(--primary-light)`.

---

## [4. EXISTING JAVASCRIPT LOGIC TO PRESERVE]

The landing page uses 3 external JS files that are ALREADY BUILT. Do NOT rewrite them. Just reference them:

```html
<script src="js/config.js"></script>  <!-- Contains CONFIG.API_URL = 'http://localhost:8000' -->
<script src="js/api.js"></script>     <!-- Contains api.get(), api.post(), api.patch(), api.delete() -->
<script src="js/auth.js"></script>    <!-- Contains isAuthenticated(), getUser(), logout(), initAuthUI(), handleLogin(), handleRegister(), guardRoute() -->
```

### Key Functions Available:
- `isAuthenticated()` — returns true if user is logged in (checks localStorage).
- `getUser()` — returns `{ id, full_name, email, phone, role }` from localStorage.
- `logout()` — clears localStorage and redirects to index.html.
- `initAuthUI()` — updates navbar to show user name + Dashboard button if logged in.
- `handleLogin(event)` — sends POST to `/auth/login` with `{ identifier, password }`.
- `handleRegister(event)` — sends POST to `/auth/register` with `{ full_name, phone, password, role: 'patient' }`.
- `api.get(endpoint)` — fetch with JWT auth header.
- `escapeHTML(str)` — XSS-safe string escaping.

### Inline Script Logic Needed:
```javascript
// 1. Navbar scroll effect
window.addEventListener('scroll', () => {
    const nav = document.getElementById('main-nav');
    if (window.scrollY > 80) nav.classList.add('scrolled');
    else nav.classList.remove('scrolled');
    
    // 2. Scroll-Reveal trigger
    document.querySelectorAll('.reveal').forEach(el => {
        if (el.getBoundingClientRect().top < window.innerHeight - 100) {
            el.classList.add('active');
        }
    });
});

// 3. On load: init auth, apply role theme, load specialties
document.addEventListener('DOMContentLoaded', async () => {
    initAuthUI();
    
    if (isAuthenticated()) {
        const user = getUser();
        document.body.className = 'theme-' + (user.role === 'cashier_admin' ? 'cashier-admin' : user.role.replace('_', '-'));
    }

    try {
        const specialties = await api.get('/admin/specialties');
        const grid = document.getElementById('specialties-grid');
        if (grid && specialties.length > 0) {
            grid.innerHTML = specialties.map(s => `
                <div class="card glass hover-float text-center reveal">
                    <div class="icon-box"><i class="fa-solid fa-stethoscope"></i></div>
                    <h3>${escapeHTML(s.name)}</h3>
                    <p class="text-gray text-sm">${escapeHTML(s.description || 'Chuyên khoa uy tín.')}</p>
                </div>
            `).join('');
        }
    } catch (e) { console.error(e); }
});

// 4. Dashboard redirect based on role
function goToDashboard() {
    if (!isAuthenticated()) { openLoginModal(); return; }
    const user = getUser();
    const routes = {
        patient: 'patient/dashboard.html',
        doctor: 'doctor/dashboard.html',
        hr_admin: 'admin/hr_dashboard.html',
        cashier_admin: 'admin/cashier_dashboard.html'
    };
    window.location.href = routes[user.role] || 'patient/dashboard.html';
}

// 5. Modal open/close/toggle
function openLoginModal() { /* show auth-modal, display login-section */ }
function openRegisterModal() { /* show auth-modal, display register-section */ }
function closeAuthModal() { /* hide auth-modal */ }
function toggleAuthForms() { /* toggle between login/register sections */ }
```

---

## [5. EXTERNAL DEPENDENCIES]

```html
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<!-- Font Awesome 6 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<!-- Custom CSS -->
<link rel="stylesheet" href="css/style.css">
```

---

## [6. CSS REQUIREMENTS CHECKLIST]

The `style.css` must include ALL of the following. This is the complete Design System used across ALL pages (dashboards, booking, etc.):

- [x] CSS Reset (*, html, body)
- [x] Aurora animated background on body
- [x] Role-based CSS variables (`:root` + `body.theme-*`)
- [x] `.glass` class (glassmorphism)
- [x] `.container`, `.flex`, `.grid`, `.grid-2`, `.grid-3` utilities
- [x] `.text-center`, `.text-primary`, `.text-gray`, `.text-sm`, `.text-xs`, `.font-bold`
- [x] `.mb-2`, `.mb-4`, `.mb-8`, `.mt-4`, `.w-100`, `.gap-2`, `.gap-4`
- [x] `.navbar` (floating pill) + `.navbar.scrolled`
- [x] `.logo`, `.nav-links`, `.auth-buttons`
- [x] `.hero-title` (with gradient text `span`)
- [x] `.btn`, `.btn-primary` (gradient + glow), `.btn-outline`, `.btn-sm`
- [x] `.card`, `.hover-float`, `.icon-box`
- [x] `.modal-overlay`, `.modal-overlay.active`, `.modal-content`, `.close-btn`
- [x] `.form-group`, `.form-label`, `.form-control` (with glowing focus)
- [x] `.table-container`, `table`, `th`, `td`, `tr:hover`
- [x] `.dashboard-container`, `.sidebar`, `.sidebar-logo`, `.side-link`, `.content-area`
- [x] `.badge`, `.badge-success`, `.badge-danger`, `.badge-warning`, `.badge-info`
- [x] `.toast-container`, `.toast`
- [x] `.reveal` + `.reveal.active` (scroll animation)
- [x] `@keyframes float`, `.floating`, `.floating-delayed`
- [x] `.blob`, `.blob-1`, `.blob-2` (decoration)
- [x] `@keyframes aurora` (background)
- [x] `@keyframes slideIn` (toast)
- [x] `.footer`, `.footer-bottom`
- [x] Responsive: `@media (max-width: 1024px)` and `@media (max-width: 768px)`

---

## [7. DELIVERABLE]

Please provide **TWO complete files**:

1. **`style.css`** — The FULL Design System (must include ALL items from Section 6 checklist). This CSS powers the entire MedBook app (landing page + all dashboards).

2. **`index.html`** — The complete Landing Page with:
   - Floating pill navbar
   - 3D perspective hero section with floating medical icons
   - Specialties bento grid (data loaded via JS)
   - Elegant glass footer
   - Auth modal (login + register toggle)
   - All inline JS logic from Section 4
   - References to external JS files (config.js, api.js, auth.js)

**Quality Standard:** The result must look like it belongs on **Awwwards.com** — breathtaking at first glance, silky-smooth in motion, and pixel-perfect in every detail. The user should feel an immediate wave of **calm, trust, and technological excellence** upon landing.

---

*End of Prompt. Good luck, Claude! Make it legendary.* 🚀
