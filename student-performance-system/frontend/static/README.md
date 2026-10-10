# Static Folder (Flask-served)

Flask serves this directory at `/static/` (`backend/app.py`:
`static_folder=frontend/static`). Only files inside `static/` and
`templates/` are reachable when running `python backend/app.py`.

```
static/
├── css/
│   └── style.css   # Prediction page theme (indigo)
├── js/
│   └── script.js   # /predict form → result card
└── images/
    ├── logo.svg    # Brand mark (mirrors assets/images)
    ├── favicon.svg # Browser tab icon
    ├── hero.svg    # Landing/prediction illustration
    └── empty.svg   # Empty-state illustration
```

> `assets/` is the design source for static mockups; `static/images/`
> holds the copies Flask can actually serve. Keep both in sync.

## Usage in templates

```html
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
<link rel="icon" href="{{ url_for('static', filename='images/favicon.svg') }}" type="image/svg+xml">
<img class="brand-logo" src="{{ url_for('static', filename='images/logo.svg') }}" alt="SPS logo">
<script src="{{ url_for('static', filename='js/script.js') }}"></script>
```
