# Generated by Django 2.1 on 2019-08-28 09:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_auto_20190826_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='parkproduction',
            name='fluid_netto',
            field=models.FloatField(default=0, verbose_name='Добыча по весам (нетто)'),
        ),
    ]
