###############
# Qiyas Sadıqov CC
###############

import random
import time
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from shop.models import Customer, Order, OrderItem, Product


class Command(BaseCommand):
    help = "Keep placing fake orders so you can watch the admin update live."

    def add_arguments(self, parser):
        parser.add_argument("--every", type=float, default=8.0)
        parser.add_argument("--count", type=int, default=0)

    def handle(self, *args, **options):
        rnd = random.Random()
        made = 0
        customers = list(Customer.objects.filter(is_active=True))
        products = list(Product.objects.filter(status="active"))
        while not options["count"] or made < options["count"]:
            last = Order.objects.order_by("-id").values_list("number", flat=True).first() or "NW-24000"
            number = f"NW-{int(last.split('-')[1]) + rnd.randint(1, 3)}"
            order = Order(number=number, customer=rnd.choice(customers), status="pending", channel=rnd.choice(["web", "mobile", "instagram"]), created_at=timezone.now())
            picked = rnd.sample(products, rnd.randint(1, 3))
            order.total = sum((p.price for p in picked), Decimal("0"))
            order.save()
            for i, product in enumerate(picked):
                OrderItem.objects.create(order=order, product=product, quantity=1, unit_price=product.price, position=i + 1)
            made += 1
            self.stdout.write(f"{order.number} for {order.customer} · ${order.total}")
            if not options["count"] or made < options["count"]:
                time.sleep(options["every"])
