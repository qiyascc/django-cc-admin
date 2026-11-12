###############
# Qiyas Sadıqov CC
###############

from django.contrib import admin, messages
from django.db.models import Count, Sum
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html

from cc_admin.admin import ModelAdmin, StackedInline, TabularInline
from cc_admin.decorators import action, display
from cc_admin.filters import (
    AllValuesCheckboxFilter,
    ChoicesCheckboxFilter,
    FieldTextFilter,
    RangeDateFilter,
    RelatedDropdownFilter,
    SliderNumericFilter,
)
from cc_admin.sections import TableSection
from cc_admin.views import AdminPageView
from cc_admin.widgets import ColorWidget, RichTextWidget, SegmentedWidget

from .models import Category, Customer, Note, Order, OrderItem, Product, Tag

ORDER_TONES = {
    "pending": "warning",
    "paid": "info",
    "shipped": "accent",
    "delivered": "success",
    "refunded": "neutral",
    "cancelled": "danger",
}


class CategoryProducts(TableSection):
    verbose_name = "Products"
    related_name = "products"
    fields = ["name", "sku", "price", "stock"]
    limit = 6


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["name", "swatch", "slug", "product_count"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name"]
    ordering_field = "position"
    list_sections = [CategoryProducts]
    exclude = ["position", "color"]

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "hex_color":
            kwargs["widget"] = ColorWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @display(description="Colour")
    def swatch(self, obj):
        return format_html('<span class="cc-badge" style="--tone:{}">{}</span>', obj.hex_color, obj.hex_color)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(n=Count("products"))

    @display(description="Products", ordering="n")
    def product_count(self, obj):
        return obj.n


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ["product", "sku", "category", "price", "stock_level", "status_label", "is_featured"]
    list_filter = [
        ("status", ChoicesCheckboxFilter),
        ("category", RelatedDropdownFilter),
        ("price", SliderNumericFilter),
        "is_featured",
        ("launched_on", RangeDateFilter),
    ]
    search_fields = ["name", "sku"]
    prepopulated_fields = {"slug": ["name"]}
    autocomplete_fields = ["category"]
    filter_horizontal = ["tags"]
    list_per_page = 25
    actions_list = ["sync_inventory", {"title": "Reports", "icon": "file-chart-column", "items": ["stock_report", "price_report"]}]
    actions_row = ["duplicate", "archive"]
    actions_detail = ["preview"]
    conditional_fields = {"discount_percent": "has_discount"}
    fieldsets = [
        (None, {"fields": ["name", ("slug", "sku"), "category", "description"]}),
        ("Pricing", {"fields": [("price", "cost"), "has_discount", "discount_percent"], "classes": ["tab"]}),
        ("Inventory", {"fields": [("stock", "launched_on"), "tags", "specs"], "classes": ["tab"]}),
        ("Publishing", {"fields": ["status", "is_featured", "created_at"], "classes": ["sidebar"]}),
    ]

    @display(description="Product", header=True, ordering="name")
    def product(self, obj):
        return obj.name, obj.category.name

    @display(description="Status", label=ORDER_TONES | {"draft": "neutral", "active": "success", "archived": "warning"}, ordering="status")
    def status_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(description="Stock", ordering="stock", progress=True)
    def stock_level(self, obj):
        return obj.stock, 240

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "description":
            kwargs["widget"] = RichTextWidget
        if db_field.name == "status":
            kwargs["widget"] = SegmentedWidget(choices=db_field.choices)
        return super().formfield_for_dbfield(db_field, request, **kwargs)

    @action(description="Stock report", icon="boxes")
    def stock_report(self, request):
        messages.info(request, "Stock report is on its way to your inbox.")

    @action(description="Price history", icon="chart-line")
    def price_report(self, request):
        messages.info(request, "Price history exported.")

    @action(description="Sync inventory", icon="refresh-cw")
    def sync_inventory(self, request):
        messages.success(request, "Inventory synced with the warehouse.")

    @action(description="Duplicate", icon="copy")
    def duplicate(self, request, obj):
        messages.info(request, f"Made a copy of {obj}.")

    @action(description="Archive", icon="archive", variant="danger", confirm="Archive this product? It will be hidden from the store.")
    def archive(self, request, obj):
        obj.status = Product.Status.ARCHIVED
        obj.save(update_fields=["status"])
        messages.warning(request, f"{obj} archived.")

    @action(description="Preview", icon="eye")
    def preview(self, request, obj):
        messages.info(request, f"Preview link for {obj} copied.")


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ["product"]
    ordering_field = "position"
    fields = ["product", "quantity", "unit_price", "position"]


class OrderLines(TableSection):
    verbose_name = "Items"
    related_name = "items"
    fields = ["product", "quantity", "unit_price", "line_total"]

    def line_total(self, item):
        return f"${item.quantity * item.unit_price:,.2f}"

    line_total.short_description = "Line total"


class OrderNotes(TableSection):
    verbose_name = "Notes"
    related_name = "timeline"
    fields = ["author", "body", "created_at"]
    empty_text = "No notes on this order."


class CustomerOrders(TableSection):
    verbose_name = "Latest orders"
    related_name = "orders"
    fields = ["number", "status", "total", "created_at"]
    limit = 8

    def get_queryset(self):
        return self.obj.orders.order_by("-created_at")


class ReportsView(AdminPageView):
    title = "Reports"
    subtitle = "Numbers the team asks for every Monday."
    template_name = "shop/reports.html"
    permission_required = "shop.view_order"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rows = Order.objects.values("channel").annotate(n=Count("id"), revenue=Sum("total")).order_by("-revenue")
        context["rows"] = rows
        return context


class NoteInline(StackedInline):
    model = Note
    extra = 0
    tab = True
    fields = ["author", "body"]


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ["person", "email_address", "country", "tier_label", "orders_count", "is_active", "joined_at"]
    list_filter = ["tier", "is_active", ("country", FieldTextFilter), ("joined_at", RangeDateFilter)]
    search_fields = ["name", "email", "city"]
    date_hierarchy = "joined_at"
    list_per_page = 30
    compressed_fields = True
    actions_row = ["send_reset"]
    form_sections = [CustomerOrders]
    fieldsets = [
        (None, {"fields": ["name", "email", ("phone", "country", "city")]}),
        ("Account", {"fields": ["tier", "is_active", "marketing_opt_in", "joined_at"]}),
        ("Notes", {"fields": ["notes"], "classes": ["collapse"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(n_orders=Count("orders"))

    @display(description="Customer", header=True, ordering="name")
    def person(self, obj):
        return obj.name, obj.city or obj.country

    @display(description="Email", copy=True, ordering="email")
    def email_address(self, obj):
        return obj.email

    @display(description="Tier", label={"standard": "neutral", "silver": "info", "gold": "warning", "vip": "accent"}, ordering="tier")
    def tier_label(self, obj):
        return obj.tier, obj.get_tier_display()

    @display(description="Orders", ordering="n_orders")
    def orders_count(self, obj):
        return obj.n_orders

    @action(description="Send password reset", icon="mail")
    def send_reset(self, request, obj):
        messages.success(request, f"Reset link sent to {obj.email}.")


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer_link", "status_label", "channel", "items_count", "total", "created_at"]
    list_filter = [("status", ChoicesCheckboxFilter), ("channel", AllValuesCheckboxFilter), ("total", SliderNumericFilter), ("created_at", RangeDateFilter), "is_gift"]
    search_fields = ["number", "customer__name", "customer__email", "tracking_code"]
    autocomplete_fields = ["customer"]
    date_hierarchy = "created_at"
    inlines = [OrderItemInline, NoteInline]
    list_sections = [OrderLines, OrderNotes]
    list_horizontal_scrollbar_top = True
    readonly_fields = ["total"]
    list_select_related = ["customer"]
    actions = ["mark_shipped"]
    actions_detail = ["print_invoice"]
    actions_submit_line = ["save_and_notify"]
    conditional_fields = {"gift_message": "is_gift", "tracking_code": "status in ['shipped', 'delivered']", "shipped_at": "status in ['shipped', 'delivered']"}
    fieldsets = [
        (None, {"fields": [("number", "customer"), ("status", "channel"), "is_gift", "gift_message", "notes"]}),
        ("Shipping", {"fields": ["tracking_code", "shipped_at"]}),
        ("Summary", {"fields": ["total", "created_at"], "classes": ["sidebar"]}),
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(n_items=Sum("items__quantity"))

    @display(description="Customer", header=True, ordering="customer__name")
    def customer_link(self, obj):
        return obj.customer.name, obj.customer.email

    @display(description="Status", label=ORDER_TONES, ordering="status")
    def status_label(self, obj):
        return obj.status, obj.get_status_display()

    @display(description="Items", ordering="n_items")
    def items_count(self, obj):
        return obj.n_items or 0

    def get_urls(self):
        view = self.admin_site.admin_view(ReportsView.as_view(model_admin=self))
        return [path("reports/", view, name="shop_order_reports")] + super().get_urls()

    @admin.action(description="Mark selected as shipped")
    def mark_shipped(self, request, queryset):
        n = queryset.update(status=Order.Status.SHIPPED, shipped_at=timezone.now())
        messages.success(request, f"{n} orders marked as shipped.")

    @action(description="Print invoice", icon="printer")
    def print_invoice(self, request, obj):
        messages.info(request, f"Invoice for {obj} sent to the printer.")

    @action(description="Save and email customer", icon="send", variant="default")
    def save_and_notify(self, request, obj):
        messages.success(request, f"Saved. {obj.customer.email} got an update.")
