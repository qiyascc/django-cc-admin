###############
# Qiyas Sadıqov CC
###############

import json
from urllib.parse import quote

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from cc_admin import charts, themes
from shop.models import Customer, Order, Product


class AdminPagesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", orders=120, verbosity=0)
        cls.user = get_user_model().objects.get(username="admin")

    def setUp(self):
        self.client.force_login(self.user)

    def get(self, url, **kwargs):
        response = self.client.get(url, **kwargs)
        self.assertEqual(response.status_code, 200, url)
        return response

    def test_every_theme_renders_the_main_pages(self):
        order = Order.objects.first()
        pages = [
            reverse("admin:index"),
            reverse("admin:app_list", args=["shop"]),
            reverse("admin:shop_order_changelist"),
            reverse("admin:shop_order_change", args=[order.pk]),
            reverse("admin:shop_product_add"),
            reverse("admin:shop_customer_changelist") + "?q=a&tier__exact=gold",
            reverse("admin:auth_user_changelist"),
            reverse("admin:shop_order_history", args=[order.pk]),
            reverse("admin:shop_order_delete", args=[order.pk]),
        ]
        for key in themes.registry():
            self.client.cookies["cc_admin_prefs"] = quote(json.dumps({"theme": key, "scheme": "dark"}))
            for url in pages:
                response = self.get(url)
                self.assertContains(response, f'data-skin="{key}"')

    def test_login_page(self):
        self.client.logout()
        response = self.get(reverse("admin:login"))
        self.assertContains(response, "cc-login-wrap")

    def test_dashboard_widgets(self):
        response = self.get(reverse("admin:index"))
        for name in ("cc-kpi", "cc-chart-line", "cc-donut", "cc-chart-bar", "cc-heat", "cc-timeline"):
            self.assertContains(response, name)

    def test_filters_and_chips(self):
        url = reverse("admin:shop_product_changelist")
        response = self.get(url + "?status__in=active&status__in=draft&price__gte=20&price__lte=&launched_on__gte=2020-01-01")
        self.assertContains(response, "cc-chip")
        expected = Product.objects.filter(status__in=["active", "draft"], price__gte=20, launched_on__gte="2020-01-01").count()
        self.assertEqual(response.context["cl"].result_count, expected)

    def test_text_filter(self):
        url = reverse("admin:shop_customer_changelist")
        response = self.get(url + "?country__icontains=azer")
        self.assertEqual(response.context["cl"].result_count, Customer.objects.filter(country__icontains="azer").count())

    def test_export_respects_filters(self):
        url = reverse("admin:shop_order_cc_export")
        response = self.client.get(url + "?status__in=pending&_format=json")
        self.assertEqual(response.status_code, 200)
        rows = json.loads(response.content)
        self.assertEqual(len(rows), Order.objects.filter(status="pending").count())
        csv = b"".join(self.client.get(url + "?_format=csv").streaming_content).decode()
        self.assertIn("Number", csv.splitlines()[0])

    def test_export_selected_action(self):
        ids = list(Order.objects.values_list("pk", flat=True)[:3])
        response = self.client.post(
            reverse("admin:shop_order_changelist"),
            {"action": "cc_export_csv", "_selected_action": ids, "index": 0},
        )
        self.assertEqual(response.status_code, 200)
        body = b"".join(response.streaming_content).decode()
        self.assertEqual(len(body.strip().splitlines()), 4)

    def test_list_row_and_detail_actions(self):
        product = Product.objects.first()
        response = self.client.post(reverse("admin:shop_product_cc_action", args=["sync-inventory"]))
        self.assertEqual(response.status_code, 302)
        response = self.client.post(reverse("admin:shop_product_cc_object_action", args=[product.pk, "archive"]))
        self.assertEqual(response.status_code, 302)
        product.refresh_from_db()
        self.assertEqual(product.status, "archived")
        response = self.client.post(reverse("admin:shop_product_cc_object_action", args=[product.pk, "nope"]))
        self.assertEqual(response.status_code, 403)

    def test_row_actions_render(self):
        response = self.get(reverse("admin:shop_product_changelist"))
        self.assertContains(response, "cc-row-menu")
        self.assertContains(response, "/cc-action/archive/")

    def test_submit_line_action(self):
        order = Order.objects.first()
        url = reverse("admin:shop_order_change", args=[order.pk])
        response = self.get(url)
        form = response.context["adminform"].form
        data = {k: v for k, v in form.initial.items() if v is not None}
        data.update({"customer": order.customer_id, "created_at_0": "2026-01-01", "created_at_1": "10:00:00", "shipped_at_0": "", "shipped_at_1": ""})
        for prefix, formset in (("items", order.items), ("timeline", order.timeline)):
            data[f"{prefix}-TOTAL_FORMS"] = formset.count()
            data[f"{prefix}-INITIAL_FORMS"] = formset.count()
            data[f"{prefix}-MIN_NUM_FORMS"] = 0
            data[f"{prefix}-MAX_NUM_FORMS"] = 1000
            for i, obj in enumerate(formset.all()):
                data[f"{prefix}-{i}-id"] = obj.pk
                data[f"{prefix}-{i}-order"] = order.pk
                for field in ("product", "quantity", "unit_price", "position", "author", "body"):
                    if hasattr(obj, field):
                        value = getattr(obj, field)
                        data[f"{prefix}-{i}-{field}"] = getattr(value, "pk", value)
        data["_cc_action"] = "save-and-notify"
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "got an update")

    def test_palette_search(self):
        order = Order.objects.first()
        response = self.client.get(reverse("admin:cc_search"), {"q": order.number})
        results = response.json()["results"]
        self.assertTrue(any(r["title"] == order.number for r in results))
        self.assertEqual(self.client.get(reverse("admin:cc_search"), {"q": "a"}).json()["results"], [])

    def test_search_needs_staff(self):
        self.client.logout()
        response = self.client.get(reverse("admin:cc_search"), {"q": "NW"})
        self.assertEqual(response.status_code, 302)

    def test_tabs_and_badges(self):
        Order.objects.filter(pk=Order.objects.first().pk).update(status="pending")
        response = self.get(reverse("admin:shop_order_changelist"))
        self.assertContains(response, "cc-tabs-page")
        self.assertContains(response, "cc-badge cc-tone-warning")

    @override_settings(CC_ADMIN={"THEME": "classic", "THEME_SWITCHER": False, "DASHBOARD": {"widgets": []}, "TOKENS": {"accent": "#ff0000", "dark": {"accent": "#00ff00"}}})
    def test_settings_override(self):
        response = self.get(reverse("admin:index"))
        self.assertContains(response, 'data-skin="classic"')
        self.assertContains(response, "--cc-accent:#ff0000")
        self.assertNotContains(response, "cc-theme-panel")
        self.assertContains(response, "Nothing on the dashboard yet")

    @override_settings(CC_ADMIN={"THEMES": {"acme": {"extends": "midnight", "label": "Acme", "tokens": {"accent": "#e11d48"}}}, "THEME": "acme"})
    def test_custom_theme(self):
        response = self.get(reverse("admin:index"))
        self.assertContains(response, 'data-theme="midnight"')
        self.assertContains(response, 'data-skin="acme"')
        self.assertContains(response, 'html.cc[data-skin=acme]{--cc-accent:#e11d48}')

    def test_plain_model_admin_still_works(self):
        self.get(reverse("admin:auth_group_add"))
        self.get(reverse("admin:shop_tag_changelist"))


class ChartsTest(TestCase):
    def test_nice_max(self):
        self.assertEqual(charts.nice_max(7300)[0], 8000)
        self.assertEqual(charts.nice_max(0)[0], 1.0)

    def test_compact(self):
        self.assertEqual(charts.compact(73386, "$"), "$73.4k")
        self.assertEqual(charts.compact(2_500_000), "2.5M")
        self.assertEqual(charts.compact(12), "12")

    def test_render(self):
        self.assertIn("cc-chart-line", charts.line(["a", "b"], [[1, 2]]))
        self.assertIn("cc-chart-bar", charts.bar(["a", "b"], [{"name": "x", "values": [1, 2]}], stacked=True))
        self.assertIn("<circle", charts.donut([("a", 1), ("b", 3)]))
        self.assertIn("<svg", charts.spark([1, 4, 2]))
        self.assertEqual(charts.spark([]), "")
