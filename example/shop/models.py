###############
# Qiyas Sadıqov CC
###############

from decimal import Decimal

from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=20, default="accent")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        ARCHIVED = "archived", "Archived"

    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    sku = models.CharField("SKU", max_length=32, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField("featured", default=False)
    has_discount = models.BooleanField(default=False)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True)
    launched_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def margin(self):
        if not self.price:
            return 0
        return float((self.price - self.cost) / self.price * 100)


class Customer(models.Model):
    class Tier(models.TextChoices):
        STANDARD = "standard", "Standard"
        SILVER = "silver", "Silver"
        GOLD = "gold", "Gold"
        VIP = "vip", "VIP"

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30, blank=True)
    country = models.CharField(max_length=60)
    city = models.CharField(max_length=60, blank=True)
    tier = models.CharField(max_length=10, choices=Tier.choices, default=Tier.STANDARD)
    is_active = models.BooleanField(default=True)
    marketing_opt_in = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    joined_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        REFUNDED = "refunded", "Refunded"
        CANCELLED = "cancelled", "Cancelled"

    class Channel(models.TextChoices):
        WEB = "web", "Web"
        MOBILE = "mobile", "Mobile app"
        INSTAGRAM = "instagram", "Instagram"
        STORE = "store", "In store"

    number = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    channel = models.CharField(max_length=12, choices=Channel.choices, default=Channel.WEB)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    tracking_code = models.CharField(max_length=40, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_gift = models.BooleanField(default=False)
    gift_message = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return f"{self.quantity} × {self.product}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity


class Note(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="timeline")
    author = models.CharField(max_length=60)
    body = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.body[:40]
