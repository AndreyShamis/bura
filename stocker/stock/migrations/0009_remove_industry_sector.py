# Generated by Django 5.0.2 on 2024-03-03 22:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0008_alter_industry_name_alter_industry_sector'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='industry',
            name='sector',
        ),
    ]
