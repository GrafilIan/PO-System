# Generated by Django 5.0.7 on 2024-09-10 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('po', '0049_inventorysupplierfolder_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryhistory',
            name='remarks',
            field=models.TextField(blank=True, null=True, verbose_name='Remarks'),
        ),
    ]
