# Generated by Django 3.1.1 on 2020-11-29 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_governorate_services'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='services',
            new_name='service',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='address_gov',
            field=models.CharField(choices=[('', 'إختر محافظة'), ('القاهرة', 'القاهرة'), ('الجيزة', 'الجيزة'), ('الأسكندرية', 'الأسكندرية'), ('الدقهلية', 'الدقهلية'), ('البحر الأحمر', 'البحر الأحمر'), ('البحيرة', 'البحيرة'), ('الفيوم', 'الفيوم'), ('الغربية', 'الغربية'), ('الإسماعلية', 'الإسماعلية'), ('المنوفية', 'المنوفية'), ('المنيا', 'المنيا'), ('القليوبية', 'القليوبية'), ('الوادي الجديد', 'الوادي الجديد'), ('السويس', 'السويس'), ('أسوان', 'أسوان'), ('أسيوط', 'أسيوط'), ('بني سويف', 'بني سويف'), ('بورسعيد', 'بورسعيد'), ('دمياط', 'دمياط'), ('الشرقية', 'الشرقية'), ('جنوب سيناء', 'جنوب سيناء'), ('كفر الشيخ', 'كفر الشيخ'), ('مطروح', 'مطروح'), ('الأقصر', 'الأقصر'), ('قنا', 'قنا'), ('شمال سيناء', 'شمال سيناء'), ('سوهاج', 'سوهاج')], max_length=20),
        ),
    ]
