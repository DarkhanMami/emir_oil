# Generated by Django 2.1 on 2019-09-06 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_parkproduction_fluid_netto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='production',
            name='timestamp',
            field=models.DateField(blank=True, verbose_name='Дата'),
        ),
    ]
