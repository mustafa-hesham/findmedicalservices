# Generated by Django 3.1.1 on 2020-12-04 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0005_auto_20201204_2224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='checkIn',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='checkOut',
            field=models.DateField(),
        ),
    ]
