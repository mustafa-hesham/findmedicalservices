# Generated by Django 3.1.1 on 2020-12-04 20:24

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0004_auto_20201201_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='email',
            field=models.CharField(error_messages={'unique': 'بريد إليكتروني مكرر'}, max_length=254, unique=True, validators=[django.core.validators.RegexValidator('[a-zA-Z][a-zA-Z0-9_\\.-]+\\@[a-zA-Z]+[a-zA-Z0-9]+\\.[a-z]+(\\.[a-z]+)?', 'ادخل عنوان بريد إليكتروني صحيح')], verbose_name='email address'),
        ),
        migrations.CreateModel(
            name='reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(max_length=20)),
                ('checkIn', models.DateTimeField()),
                ('checkOut', models.DateTimeField()),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='center', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
