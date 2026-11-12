###############
# Qiyas Sadıqov CC
###############

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("shop", "0001_initial")]

    operations = [
        migrations.AlterModelOptions(name="category", options={"ordering": ["position", "name"], "verbose_name_plural": "categories"}),
        migrations.AddField(model_name="category", name="hex_color", field=models.CharField(default="#5b5bd6", max_length=9, verbose_name="colour")),
        migrations.AddField(model_name="category", name="position", field=models.PositiveIntegerField(default=0)),
        migrations.AddField(model_name="product", name="specs", field=models.JSONField(blank=True, default=dict)),
    ]
