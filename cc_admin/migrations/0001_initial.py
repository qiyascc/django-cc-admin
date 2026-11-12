###############
# Qiyas Sadıqov CC
###############

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PushSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.TextField(verbose_name='endpoint')),
                ('endpoint_hash', models.CharField(editable=False, max_length=64, unique=True)),
                ('p256dh', models.CharField(max_length=200)),
                ('auth', models.CharField(max_length=100)),
                ('user_agent', models.CharField(blank=True, max_length=300, verbose_name='browser')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('last_used_at', models.DateTimeField(blank=True, null=True, verbose_name='last used')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cc_push_subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'push subscription',
                'verbose_name_plural': 'push subscriptions',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('body', models.TextField(blank=True, verbose_name='body')),
                ('link', models.CharField(blank=True, max_length=500, verbose_name='link')),
                ('level', models.CharField(choices=[('info', 'Info'), ('success', 'Success'), ('warning', 'Warning'), ('danger', 'Danger'), ('accent', 'Accent'), ('neutral', 'Neutral')], default='info', max_length=16, verbose_name='level')),
                ('icon', models.CharField(blank=True, max_length=64, verbose_name='icon')),
                ('sound', models.CharField(blank=True, max_length=32, verbose_name='sound')),
                ('key', models.CharField(blank=True, max_length=120, verbose_name='key')),
                ('data', models.JSONField(blank=True, default=dict, verbose_name='data')),
                ('created_at', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='created at')),
                ('read_at', models.DateTimeField(blank=True, null=True, verbose_name='read at')),
                ('actor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='actor')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cc_notifications', to=settings.AUTH_USER_MODEL, verbose_name='recipient')),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'ordering': ['-id'],
                'indexes': [models.Index(fields=['recipient', 'read_at'], name='cc_notif_unread')],
            },
        ),
    ]
