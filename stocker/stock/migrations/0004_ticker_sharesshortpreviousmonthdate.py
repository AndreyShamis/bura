# Generated by Django 5.0.2 on 2024-03-03 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0003_rename_zip_code_ticker_zipcode_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticker',
            name='sharesShortPreviousMonthDate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
