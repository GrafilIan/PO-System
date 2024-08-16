# Generated by Django 4.2.1 on 2024-08-14 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('po', '0010_alter_iteminventory_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iteminventory',
            name='quantity_in',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='iteminventory',
            name='quantity_out',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='iteminventory',
            name='stock',
            field=models.IntegerField(default=0),
        ),
    ]
