# Generated by Django 5.0.2 on 2024-03-03 22:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0009_remove_industry_sector'),
    ]

    operations = [
        migrations.AddField(
            model_name='industry',
            name='sector',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stock.sector'),
        ),
    ]
