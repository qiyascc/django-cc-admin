###############
# Qiyas Sadıqov CC
###############

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "example-only-not-for-production")
DEBUG = os.environ.get("DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]

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

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.environ.get("DATABASE_PATH", BASE_DIR / "db.sqlite3")}}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Baku"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CC_ADMIN = {
    "SITE_HEADER": "Northwind",
    "SITE_SUBHEADER": "Store admin",
    "SITE_TITLE": "Northwind admin",
    "SITE_URL": "/",
    "SITE_SYMBOL": "store",
    "SITE_DROPDOWN": [
        {"title": "Northwind store", "icon": "store", "link": "/"},
        {"title": "Warehouse admin", "icon": "warehouse", "link": "#"},
        {"title": "Status page", "icon": "activity", "link": "#"},
    ],
    "THEME": os.environ.get("CC_THEME", "aurora"),
    "ENVIRONMENT": ("Staging", "warning"),
    "ENVIRONMENT_TITLE_PREFIX": True,
    "FORMS": {"switches": True},
    "ACTIVITY": {"view": "staff", "others": "superuser"},
    "SHORTCUTS": {
        "keys": {"delete": "mod+shift+backspace"},
        "custom": [
            {"keys": "g o", "title": "Open orders", "link": "admin:shop_order_changelist"},
            {"keys": "g p", "title": "Open products", "link": "admin:shop_product_changelist"},
            {"keys": "g r", "title": "Reports", "link": "admin:shop_order_reports"},
        ],
    },
    "COMMAND_PALETTE": {
        "commands": [
            {"title": "Weekly reports", "subtitle": "Revenue by channel", "icon": "chart-pie", "link": "admin:shop_order_reports"},
            {"title": "Pending orders", "subtitle": "Orders waiting for payment", "icon": "clock", "link": "/admin/shop/order/?status__in=pending"},
        ],
    },
    "SIDEBAR": {
        "icons": {"shop.category": "folder-tree", "shop.tag": "tag", "shop.note": "sticky-note"},
        "navigation": [
            {
                "title": "Store",
                "items": [
                    {"title": "Orders", "icon": "receipt", "link": "admin:shop_order_changelist", "badge": "shop.dashboard.pending_orders", "badge_variant": "warning"},
                    {"title": "Products", "icon": "package", "link": "admin:shop_product_changelist", "badge": "shop.dashboard.low_stock", "badge_variant": "danger"},
                    {"title": "Customers", "icon": "users", "link": "admin:shop_customer_changelist"},
                    {"title": "Categories", "icon": "folder-tree", "link": "admin:shop_category_changelist"},
                    {"title": "Reports", "icon": "chart-pie", "link": "admin:shop_order_reports"},
                ],
            },
        ],
    },
    "TABS": [
        {
            "models": ["shop.order"],
            "items": [
                {"title": "All orders", "link": "/admin/shop/order/"},
                {"title": "Pending", "link": "/admin/shop/order/?status__in=pending", "badge": "shop.dashboard.pending_orders"},
                {"title": "Shipped", "link": "/admin/shop/order/?status__in=shipped"},
                {"title": "Refunds", "link": "/admin/shop/order/?status__in=refunded"},
            ],
        },
    ],
    "DASHBOARD": {
        "subtitle": "Here is how the store did over the last 30 days.",
        "widgets": [
            {"type": "kpi", "title": "Revenue", "icon": "wallet", "value": "shop.dashboard.revenue", "link": "admin:shop_order_changelist"},
            {"type": "kpi", "title": "Orders", "icon": "receipt", "value": "shop.dashboard.orders"},
            {"type": "kpi", "title": "Average order", "icon": "chart-line", "value": "shop.dashboard.average_order", "decimals": 0},
            {"type": "kpi", "title": "New customers", "icon": "user-plus", "value": "shop.dashboard.new_customers"},
            {"type": "chart", "kind": "area", "title": "Revenue", "subtitle": "Daily, paid orders only", "data": "shop.dashboard.revenue_chart", "summary": "shop.dashboard.revenue_summary", "prefix": "$", "width": 8, "height": 250},
            {"type": "chart", "kind": "donut", "title": "Order status", "subtitle": "All time", "data": "shop.dashboard.status_split", "width": 4, "center_label": "orders"},
            {"type": "table", "title": "Top products", "data": "shop.dashboard.top_products", "width": 7, "link": "admin:shop_product_changelist"},
            {"type": "list", "title": "Latest orders", "items": "shop.dashboard.latest_orders", "width": 5, "link": "admin:shop_order_changelist"},
            {"type": "chart", "kind": "stacked-bar", "title": "Orders by channel", "subtitle": "Last six months", "data": "shop.dashboard.channels", "width": 7, "height": 220},
            {"type": "progress", "title": "Revenue by category", "items": "shop.dashboard.category_share", "width": 5},
            {"type": "heatmap", "title": "Order activity", "subtitle": "Orders per day, last twelve months", "data": "shop.dashboard.order_days", "unit": "orders", "weeks": 52, "width": 12},
            {"type": "contributions", "title": "Your activity", "icon": "activity", "weeks": 30, "width": 8},
            {"type": "team", "title": "Team", "icon": "users", "days": 30, "width": 4},
            {"type": "cohort", "title": "Customer retention", "subtitle": "Share of new customers who ordered again, by signup month", "data": "shop.dashboard.retention", "width": 12},
            {"type": "tracker", "title": "Fulfilment", "subtitle": "Last 60 days", "data": "shop.dashboard.fulfilment", "width": 12},
            {"type": "activity", "title": "Recent changes", "width": 6, "limit": 6},
            {"type": "recent", "title": "Recently opened", "width": 6},
        ],
    },
    "LOGIN": {"title": "Run the whole store from one place.", "text": "Orders, stock and customers, with the numbers that matter on the first screen."},
    "USER_LINKS": [{"title": "Store front", "icon": "store", "link": "/"}],
}
