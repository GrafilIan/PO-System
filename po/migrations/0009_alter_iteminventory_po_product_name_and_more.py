# Generated by Django 4.2.1 on 2024-08-14 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('po', '0008_alter_iteminventory_supplier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iteminventory',
            name='po_product_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='iteminventory',
            name='unit',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
