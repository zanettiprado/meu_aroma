# Generated by Django 4.2.8 on 2024-01-12 19:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_remove_inventory_quantity_allocated_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventory',
            old_name='is_in_stock',
            new_name='is_available',
        ),
    ]
