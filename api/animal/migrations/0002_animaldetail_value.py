# Generated by Django 5.1.3 on 2024-12-02 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animal', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='animaldetail',
            name='value',
            field=models.CharField(default=0, max_length=255),
            preserve_default=False,
        ),
    ]
