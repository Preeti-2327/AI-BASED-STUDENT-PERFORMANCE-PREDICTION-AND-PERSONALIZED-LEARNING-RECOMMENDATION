# Frontend Assets

Brand + UI assets for the Student Performance System. All SVGs — lightweight, offline-friendly, no CDN needed.

## Structure

```
assets/
├── images/
│   ├── logo.svg      # Brand mark (graduation cap, 64×64)
│   ├── favicon.svg   # Browser tab icon (32×32)
│   ├── hero.svg      # Dashboard/landing illustration (480×300)
│   ├── empty.svg     # Empty-state illustration (240×160)
│   └── avatar-1..3.svg  # Placeholder avatars (64×64)
└── icons/            # 24×24 stroke icons (currentColor)
    ├── dashboard.svg, reports.svg, students.svg, teachers.svg
    ├── subjects.svg, home.svg, logout.svg, search.svg
    └── plus.svg, download.svg, edit.svg, trash.svg, menu.svg, close.svg
```

## Usage

```html
<!-- Favicon -->
<link rel="icon" href="../assets/images/favicon.svg" type="image/svg+xml">

<!-- Sidebar brand -->
<img class="logo-img" src="../assets/images/logo.svg" alt="SPS logo">

<!-- Nav / button icon (inherits text color) -->
<img class="ico-img" src="../assets/icons/dashboard.svg" alt="">
```

```css
.logo-img { width: 36px; height: 36px; border-radius: 9px; }
.ico-img { width: 18px; height: 18px; vertical-align: -3px; }
```

Icons use `stroke="currentColor"`, so they automatically match surrounding text color.
