# Generated by Django 5.1.4 on 2025-04-12 17:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_record_date_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='finance.category', verbose_name='Kategorie'),
        ),
    ]
