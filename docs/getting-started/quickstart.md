# Quickstart

In this walkthrough you build a small back office for a corner shop from an empty folder. It takes about fifteen minutes. At the end you have a themed admin with your own name in the corner, a sidebar with a live badge, a dashboard with four numbers and a chart, and a product list with badges, filters and a row action.

Every file is shown in full, so you can copy each block as it is. The commands are for Linux and macOS; on Windows CMD use `py` instead of `python3` and `.venv\Scripts\activate` to activate the environment, as shown on the [installation](installation.md) page.

## 1. Create the project

```bash
mkdir cornershop
cd cornershop
python3 -m venv .venv
source .venv/bin/activate
pip install django-cc-admin
django-admin startproject mysite .
python manage.py startapp shop
```

You now have this layout:

```text
cornershop/
├── manage.py
├── mysite/
│   ├── settings.py
│   └── urls.py
└── shop/
    ├── admin.py
    └── models.py
```

## 2. Register the apps

Open `mysite/settings.py`. Add `cc_admin` as the very first app and your `shop` app at the end:

```python
INSTALLED_APPS = [
    "cc_admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]
```

`mysite/urls.py` already contains `path("admin/", admin.site.urls)`. Leave it as it is.

## 3. Write two models

Replace `shop/models.py` with:

```python
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

Create the tables, including the two small ones django-cc-admin needs for notifications, and a user to sign in with:

```bash
python manage.py makemigrations shop
python manage.py migrate
python manage.py createsuperuser
```

## 4. Look at the admin as it is now

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/admin/`. Even with no admin classes yet you get the new sign in page, the dashboard, the sidebar, the command palette and the theme switcher. Stop the server with {kbd}`Ctrl+C` and carry on.

## 5. Register the models with the extended ModelAdmin

Replace `shop/admin.py` with:

```python
from django.contrib import admin, messages

from cc_admin.admin import ModelAdmin
from cc_admin.decorators import action, display
from cc_admin.filters import ChoicesCheckboxFilter, RangeNumericFilter, RelatedDropdownFilter

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["product", "price", "stock", "status_badge"]
    list_filter = [
        ("status", ChoicesCheckboxFilter),
        ("category", RelatedDropdownFilter),
        ("price", RangeNumericFilter),
    ]
    search_fields = ["name"]
    actions_row = ["archive"]

    @display(description="Product", header=True, ordering="name")
    def product(self, obj):
        return obj.name, obj.category.name

    @display(description="Status", label={"draft": "neutral", "active": "success", "archived": "warning"}, ordering="status")
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @action(description="Archive", icon="archive", variant="danger", confirm="Archive this product?")
    def archive(self, request, obj):
        obj.status = Product.Status.ARCHIVED
        obj.save(update_fields=["status"])
        messages.success(request, f"{obj} archived.")
```

What each part does:

`cc_admin.admin.ModelAdmin`
: A drop in replacement for `django.contrib.admin.ModelAdmin`. Everything Django supports still works. It adds the options described in [ModelAdmin extras](../guides/model-admin.md).

`@display(header=True)`
: The column shows a title, a subtitle and an avatar with initials. The method returns a tuple of `(title, subtitle)`.

`@display(label={...})`
: The column shows a coloured badge. The method returns `(value, text)`, and the dict maps each value to a tone.

`ChoicesCheckboxFilter`, `RelatedDropdownFilter`, `RangeNumericFilter`
: Pick several statuses at once, pick a category from a dropdown, and type a price range. Filters open in a side panel. See [Filters](../guides/filters.md).

`actions_row` and `@action`
: Every row gets a menu with an "Archive" item. Because of `confirm`, the user is asked first. The method receives the request and the object. See [Actions](../guides/actions.md).

## 6. Name the admin and pick a theme

Add this at the bottom of `mysite/settings.py`:

```python
CC_ADMIN = {
    "SITE_HEADER": "Corner Shop",
    "SITE_SUBHEADER": "Back office",
    "SITE_SYMBOL": "store",
    "THEME": "nord",
    "ENVIRONMENT": ("Local", "info"),
}
```

`SITE_HEADER` and `SITE_SUBHEADER` appear in the top left corner. `SITE_SYMBOL` puts the Lucide `store` icon in the brand square instead of initials. `THEME` sets the default theme for people who have not picked one. `ENVIRONMENT` shows a small "Local" badge in the top bar, so nobody mistakes this admin for production.

## 7. Add the sidebar group and the dashboard

Create `shop/dashboard.py`. These are plain functions that take the request and return numbers or lists. django-cc-admin calls them when it draws the page.

```python
from django.db.models import Count, F, Sum

from .models import Category, Product


def product_count(request):
    return Product.objects.count()


def stock_value(request):
    total = Product.objects.aggregate(v=Sum(F("price") * F("stock")))["v"] or 0
    return {"value": total, "prefix": "$"}


def low_stock(request):
    return Product.objects.filter(stock__lt=5, status="active").count()


def category_count(request):
    return Category.objects.count()


def by_category(request):
    rows = Category.objects.annotate(n=Count("products")).order_by("-n")
    return [{"label": row.name, "value": row.n} for row in rows]
```

Now extend `CC_ADMIN` so it uses them:

```python
CC_ADMIN = {
    "SITE_HEADER": "Corner Shop",
    "SITE_SUBHEADER": "Back office",
    "SITE_SYMBOL": "store",
    "THEME": "nord",
    "ENVIRONMENT": ("Local", "info"),
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Shop",
                "items": [
                    {
                        "title": "Products",
                        "icon": "package",
                        "link": "admin:shop_product_changelist",
                        "badge": "shop.dashboard.low_stock",
                        "badge_variant": "danger",
                    },
                    {"title": "Categories", "icon": "folder-tree", "link": "admin:shop_category_changelist"},
                ],
            },
        ],
    },
    "DASHBOARD": {
        "subtitle": "Stock and prices at a glance.",
        "widgets": [
            {"type": "kpi", "title": "Products", "icon": "package", "value": "shop.dashboard.product_count", "link": "admin:shop_product_changelist"},
            {"type": "kpi", "title": "Stock value", "icon": "wallet", "value": "shop.dashboard.stock_value"},
            {"type": "kpi", "title": "Low stock", "icon": "triangle-exclamation-point", "value": "shop.dashboard.low_stock", "tone": "warning"},
            {"type": "kpi", "title": "Categories", "icon": "folder-tree", "value": "shop.dashboard.category_count"},
            {"type": "chart", "kind": "donut", "title": "Products by category", "data": "shop.dashboard.by_category", "width": 5, "center_label": "products"},
            {"type": "activity", "title": "Recent changes", "width": 7},
        ],
    },
}
```

A few things to notice:

- Values such as `"shop.dashboard.low_stock"` are dotted paths. django-cc-admin imports the function and calls it with the request. You can also pass the function itself, or any plain value.
- Links such as `"admin:shop_product_changelist"` are URL names. A path like `"/admin/shop/product/"` or a full URL works too.
- Icons are [Lucide](https://lucide.dev/icons) names. A name the bundled set does not know falls back to a small dot, so if an icon does not show up, check the spelling. The [FAQ](../reference/faq.md) shows how to list the names that ship with the package.
- The four KPIs have no `width`, so they take the default of 3 columns each and fill one row of the 12 column grid.

## 8. Run it

Add a few categories and products in the admin, or paste some in `python manage.py shell`, then open the dashboard:

```bash
python manage.py runserver
```

```{image} ../screenshots/quickstart-dashboard.jpg
:alt: The quickstart dashboard in the Nord theme
```

The greeting changes with the time of day. The red badge next to "Products" in the sidebar is the number of active products with fewer than five in stock, and it updates on its own while the page is open.

Click "Products":

```{image} ../screenshots/quickstart-list.jpg
:alt: The product list with avatars, badges and row menus
```

Try these on the list:

- Press {kbd}`f` to open the filters, tick two statuses and apply.
- Press {kbd}`j` and {kbd}`k` to move between rows and {kbd}`Enter` to open one.
- Open the menu at the end of a row and pick "Archive".
- Open "Export" at the top and download the filtered list as CSV.
- Press {kbd}`?` to see every shortcut.

## Where to go from here

- Make the sidebar and the dashboard your own: [Navigation](../guides/navigation.md) and [Dashboard](../guides/dashboard.md).
- Group form fields into tabs, add a sticky side column and show fields only when they matter: [ModelAdmin extras](../guides/model-admin.md).
- Tell the team when something happens: [Notifications](../guides/notifications.md).
- See a bigger version of the same idea: [A shop admin](../examples/shop-admin.md).
