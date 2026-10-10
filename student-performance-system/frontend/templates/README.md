# Templates Folder (Flask Jinja2)

Rendered by `backend/app.py` (`template_folder=frontend/templates`).
Static assets resolve via `url_for('static', ...)` → `frontend/static/`.

```
templates/
├── base.html        # Shared layout (head, .container, footer, script)
├── index.html       # Prediction form (30 fields) + result + history
└── errors/
    ├── 404.html     # Page-not-found (wired in app.py)
    └── 500.html     # Server-error (wired in app.py)
```

## Conventions

- Every page `{% extends "base.html" %}` and fills `title` + `content`.
- Element IDs used by `static/js/script.js` (do not rename):
  `predictionForm`, `loading`, `result`, `grade`, `level`,
  `interpretation`, `recommendations`, `histRows`, `histCount`,
  `refreshHist` + one input ID per model feature
  (`school`, `sex`, `age`, … `absences`).
- Form field names/IDs must match `REQUIRED_FIELDS` in `backend/app.py`.
