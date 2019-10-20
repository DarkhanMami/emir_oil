# Generated by Django 2.1 on 2019-10-20 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_parkoil'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parkoil',
            name='end',
            field=models.TimeField(blank=True, null=True, verbose_name='Конец налива'),
        ),
        migrations.AlterField(
            model_name='parkoil',
            name='go_out',
            field=models.TimeField(blank=True, null=True, verbose_name='Время выезда из ГУ'),
        ),
        migrations.AlterField(
            model_name='parkoil',
            name='go_to',
            field=models.TimeField(blank=True, null=True, verbose_name='Время заезда на ГУ'),
        ),
        migrations.AlterField(
            model_name='parkoil',
            name='start',
            field=models.TimeField(blank=True, null=True, verbose_name='Начало налива'),
        ),
    ]
