# Development

## Getting the code

```bash
git clone https://github.com/qiyascc/django-cc-admin
cd django-cc-admin
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[all]"
```

## Layout

```text
django-cc-admin/
├── cc_admin/              the package
│   ├── admin.py           ModelAdmin, the mixin and the inlines
│   ├── conf.py            settings and their defaults
│   ├── dashboard.py       dashboard widgets
│   ├── charts.py          SVG charts
│   ├── filters.py         list filters
│   ├── live.py            live updates
│   ├── notify.py          notifications and push
│   ├── themes.py          themes and appearance
│   ├── static/cc_admin/   CSS, JavaScript and fonts
│   └── templates/         admin and cc_admin templates
├── example/               the Northwind shop
├── scripts/build_themes.py
├── tests/
├── docs/                  this documentation
└── runtests.py
```

## Running the tests

```bash
python runtests.py
```

The tests run against the example project with an in memory SQLite database. They render the main admin pages in every theme and dark mode, and cover lists, forms, actions, filters, export, sorting, the dashboard, activity, shortcuts, live updates and notification rules. To run one module or one test:

```bash
python runtests.py tests.test_live
python runtests.py tests.test_admin.AdminPagesTest.test_every_theme_renders_the_main_pages
```

To test against several Django versions, make one virtual environment per version and run the same command in each.

## The example project

```bash
cd example
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Sign in as `admin` / `admin`. See [A shop admin](../examples/shop-admin.md) for what is in it, and run `python manage.py simulate` next to the server to see live updates.

## Themes

The fifteen themes are defined in `scripts/build_themes.py`, which writes `cc_admin/static/cc_admin/css/themes.css`. Edit the script, not the CSS file, and build again:

```bash
python scripts/build_themes.py
```

The theme list shown in the switcher (names, notes, layouts, modes and preview swatches) lives in `cc_admin/themes.py`.

## Building the documentation

```bash
pip install -r docs/requirements.txt
sphinx-build -W -b html docs docs/_build/html
```

Open `docs/_build/html/index.html`. The documentation is written in Markdown with MyST and uses the Furo theme. Read the Docs builds it from `.readthedocs.yaml` on every push.

## Code style

- No comments in the code. Names, tests and these docs carry the meaning.
- Every Python file starts with the signature block of the project.
- Plain, short user facing text, in the tone of the rest of the admin.
- Ruff for linting.

## Reporting a problem

Open an issue on [GitHub](https://github.com/qiyascc/django-cc-admin/issues) with your Django and Python versions, the relevant part of `CC_ADMIN`, the theme you use, and a screenshot if it is a display problem.
