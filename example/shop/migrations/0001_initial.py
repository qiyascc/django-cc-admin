###############
# Qiyas Sadıqov CC
###############

import django.db.models.deletion
import django.utils.timezone
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('slug', models.SlugField(unique=True)),
                ('color', models.CharField(default='accent', max_length=20)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone', models.CharField(blank=True, max_length=30)),
                ('country', models.CharField(max_length=60)),
                ('city', models.CharField(blank=True, max_length=60)),
                ('tier', models.CharField(choices=[('standard', 'Standard'), ('silver', 'Silver'), ('gold', 'Gold'), ('vip', 'VIP')], default='standard', max_length=10)),
                ('is_active', models.BooleanField(default=True)),
                ('marketing_opt_in', models.BooleanField(default=False)),
                ('notes', models.TextField(blank=True)),
                ('joined_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('shipped', 'Shipped'), ('delivered', 'Delivered'), ('refunded', 'Refunded'), ('cancelled', 'Cancelled')], default='pending', max_length=12)),
                ('channel', models.CharField(choices=[('web', 'Web'), ('mobile', 'Mobile app'), ('instagram', 'Instagram'), ('store', 'In store')], default='web', max_length=12)),
                ('total', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=12)),
                ('tracking_code', models.CharField(blank=True, max_length=40)),
                ('shipped_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('is_gift', models.BooleanField(default=False)),
                ('gift_message', models.CharField(blank=True, max_length=200)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='shop.customer')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=60)),
                ('body', models.TextField()),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='timeline', to='shop.order')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(unique=True)),
                ('sku', models.CharField(max_length=32, unique=True, verbose_name='SKU')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cost', models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('archived', 'Archived')], default='draft', max_length=12)),
                ('is_featured', models.BooleanField(default=False, verbose_name='featured')),
                ('has_discount', models.BooleanField(default=False)),
                ('discount_percent', models.PositiveSmallIntegerField(default=0)),
                ('description', models.TextField(blank=True)),
                ('launched_on', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='shop.category')),
                ('tags', models.ManyToManyField(blank=True, to='shop.tag')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('position', models.PositiveIntegerField(default=0)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='shop.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shop.product')),
            ],
            options={
                'ordering': ['position', 'id'],
            },
        ),
    ]
