# Generated by Django 5.1.3 on 2024-12-02 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0002_animaldetail_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalmeasurement',
            name='height',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
            preserve_default=False,
        ),
    ]