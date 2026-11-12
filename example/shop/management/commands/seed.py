###############
# Qiyas Sadıqov CC
###############

import datetime
import random
from decimal import Decimal

from django.contrib.admin.models import ADDITION, CHANGE, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from shop.models import Category, Customer, Note, Order, OrderItem, Product, Tag

CATEGORIES = {
    "Audio": ["Studio Headphones", "Wireless Earbuds", "Desk Speaker", "Bluetooth Speaker", "USB Microphone", "Noise Cancelling Headset"],
    "Workspace": ["Standing Desk", "Ergonomic Chair", "Monitor Arm", "Desk Mat", "Cable Tray", "Laptop Stand", "Footrest"],
    "Lighting": ["Desk Lamp", "Light Bar", "Smart Bulb Pack", "LED Strip", "Floor Lamp"],
    "Keyboards": ["Mechanical Keyboard", "Low Profile Keyboard", "Split Keyboard", "Keycap Set", "Wrist Rest"],
    "Accessories": ["USB-C Hub", "Travel Charger", "Braided Cable", "Laptop Sleeve", "Webcam Cover", "Card Reader", "Phone Stand"],
    "Coffee": ["Pour Over Kit", "Burr Grinder", "Gooseneck Kettle", "Espresso Cups", "Cold Brew Jar"],
}
TAGS = ["new", "bestseller", "limited", "eco", "bundle", "gift", "pro", "sale"]
FIRST = ["Aylin", "Murad", "Leyla", "Kamran", "Nigar", "Elvin", "Sevda", "Rashad", "Aysel", "Tural", "Emma", "Liam", "Olivia", "Noah", "Mia", "Lucas", "Sofia", "Mateo", "Hana", "Yusuf", "Zeynep", "Emir", "Ines", "Jonas", "Clara", "Arda", "Lea", "Omar", "Nora", "Felix"]
LAST = ["Aliyev", "Mammadova", "Huseynov", "Karimova", "Ismayilov", "Yilmaz", "Demir", "Schmidt", "Rossi", "Novak", "Silva", "Kowalski", "Larsen", "Moreau", "Haddad", "Tanaka", "Park", "Costa", "Weber", "Jansen"]
PLACES = [("Azerbaijan", "Baku"), ("Turkey", "Istanbul"), ("Germany", "Berlin"), ("Italy", "Milan"), ("Netherlands", "Amsterdam"), ("Poland", "Warsaw"), ("Georgia", "Tbilisi"), ("United Kingdom", "London"), ("France", "Lyon"), ("Japan", "Osaka"), ("Portugal", "Lisbon"), ("Spain", "Valencia")]
NOTES = ["Customer asked for gift wrap.", "Called to confirm the address.", "Courier picked up the parcel.", "Swapped the colour on request.", "Paid by bank transfer, confirmed."]


class Command(BaseCommand):
    help = "Fill the example shop with demo data."

    def add_arguments(self, parser):
        parser.add_argument("--orders", type=int, default=2200)
        parser.add_argument("--seed", type=int, default=7)

    @transaction.atomic
    def handle(self, *args, **options):
        rnd = random.Random(options["seed"])
        for model in (Note, OrderItem, Order, Customer, Product, Tag, Category):
            model.objects.all().delete()
        LogEntry.objects.all().delete()
        now = timezone.now()
        tags = [Tag.objects.create(name=t) for t in TAGS]
        products = []
        sku = 1000
        for cat_name, names in CATEGORIES.items():
            category = Category.objects.create(name=cat_name, slug=slugify(cat_name), description=f"Everything in {cat_name.lower()}.")
            for name in names:
                sku += rnd.randint(3, 17)
                price = Decimal(rnd.choice([19, 24, 29, 39, 49, 59, 79, 99, 129, 149, 199, 249, 349, 499])) - Decimal("0.01")
                product = Product.objects.create(
                    name=name,
                    slug=slugify(name),
                    sku=f"NW-{sku}",
                    category=category,
                    price=price,
                    cost=(price * Decimal(rnd.uniform(0.35, 0.7))).quantize(Decimal("0.01")),
                    stock=rnd.choice([0, 4, 8, 12, 25, 40, 60, 85, 120, 240]),
                    status=rnd.choices(["active", "draft", "archived"], [8, 1, 1])[0],
                    is_featured=rnd.random() < 0.25,
                    has_discount=rnd.random() < 0.2,
                    discount_percent=rnd.choice([0, 10, 15, 20]),
                    description=f"{name} from the {cat_name.lower()} range.",
                    launched_on=(now - datetime.timedelta(days=rnd.randint(20, 900))).date(),
                    created_at=now - datetime.timedelta(days=rnd.randint(20, 900)),
                )
                product.tags.set(rnd.sample(tags, rnd.randint(0, 3)))
                products.append(product)
        weights = [rnd.uniform(0.3, 3) for _ in products]
        customers = []
        used = set()
        for i in range(320):
            first, last = rnd.choice(FIRST), rnd.choice(LAST)
            email = f"{first}.{last}{'' if (first, last) not in used else i}@example.com".lower()
            used.add((first, last))
            country, city = rnd.choice(PLACES)
            customers.append(
                Customer(
                    name=f"{first} {last}",
                    email=email,
                    phone=f"+{rnd.randint(30, 99)} {rnd.randint(100, 999)} {rnd.randint(100, 999)} {rnd.randint(10, 99)}",
                    country=country,
                    city=city,
                    tier=rnd.choices(["standard", "silver", "gold", "vip"], [12, 5, 2, 1])[0],
                    is_active=rnd.random() > 0.08,
                    marketing_opt_in=rnd.random() > 0.5,
                    joined_at=now - datetime.timedelta(days=rnd.uniform(0, 420)),
                )
            )
        Customer.objects.bulk_create(customers)
        customers = list(Customer.objects.all())
        orders, items = [], []
        number = 24000
        total_orders = options["orders"]
        for i in range(total_orders):
            age = rnd.betavariate(1.1, 2.4) * 365
            created = now - datetime.timedelta(days=age, minutes=rnd.randint(0, 1440))
            if created.weekday() >= 5 and rnd.random() < 0.35:
                created -= datetime.timedelta(days=2)
            number += rnd.randint(1, 3)
            if age < 2:
                status = rnd.choices(["pending", "paid"], [3, 2])[0]
            elif age < 6:
                status = rnd.choices(["paid", "shipped", "pending"], [2, 4, 1])[0]
            else:
                status = rnd.choices(["delivered", "shipped", "refunded", "cancelled"], [30, 2, 2, 1])[0]
            orders.append(
                Order(
                    number=f"NW-{number}",
                    customer=rnd.choice(customers),
                    status=status,
                    channel=rnd.choices(["web", "mobile", "instagram", "store"], [6, 4, 2, 1])[0],
                    tracking_code=f"TRK{rnd.randint(10**8, 10**9)}" if status in ("shipped", "delivered") else "",
                    shipped_at=created + datetime.timedelta(days=rnd.uniform(0.5, 3)) if status in ("shipped", "delivered") else None,
                    is_gift=rnd.random() < 0.08,
                    created_at=created,
                )
            )
        Order.objects.bulk_create(orders)
        orders = list(Order.objects.all())
        for order in orders:
            chosen = rnd.choices(products, weights, k=rnd.choices([1, 2, 3, 4], [6, 3, 2, 1])[0])
            total = Decimal("0")
            for pos, product in enumerate(dict.fromkeys(chosen)):
                qty = rnd.choices([1, 2, 3], [8, 2, 1])[0]
                items.append(OrderItem(order=order, product=product, quantity=qty, unit_price=product.price, position=pos + 1))
                total += product.price * qty
            order.total = total
        OrderItem.objects.bulk_create(items)
        Order.objects.bulk_update(orders, ["total"], batch_size=500)
        for order in rnd.sample(orders, 60):
            Note.objects.create(order=order, author=rnd.choice(["Aylin", "Murad", "Support"]), body=rnd.choice(NOTES), created_at=order.created_at + datetime.timedelta(hours=3))
        user, _ = get_user_model().objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "first_name": "Qiyas", "last_name": "Sadıqov", "is_staff": True, "is_superuser": True})
        user.first_name, user.last_name, user.is_staff, user.is_superuser = "Qiyas", "Sadıqov", True, True
        user.set_password("admin")
        user.save()
        order_ct = ContentType.objects.get_for_model(Order)
        product_ct = ContentType.objects.get_for_model(Product)
        entries = []
        for i, order in enumerate(sorted(orders, key=lambda o: o.created_at, reverse=True)[:5]):
            entries.append(LogEntry(user=user, content_type=order_ct, object_id=str(order.pk), object_repr=str(order), action_flag=CHANGE, change_message="Changed status.", action_time=now - datetime.timedelta(minutes=7 + i * 23)))
        for i, product in enumerate(rnd.sample(products, 3)):
            entries.append(LogEntry(user=user, content_type=product_ct, object_id=str(product.pk), object_repr=str(product), action_flag=ADDITION if i == 0 else CHANGE, change_message="Updated price.", action_time=now - datetime.timedelta(hours=3 + i * 5)))
        LogEntry.objects.bulk_create(entries)
        self.stdout.write(self.style.SUCCESS(f"{len(products)} products, {len(customers)} customers, {len(orders)} orders, {len(items)} items. Log in as admin / admin."))
