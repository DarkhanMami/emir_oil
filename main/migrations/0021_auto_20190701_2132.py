# Generated by Django 2.1 on 2019-07-01 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20190701_1947'),
    ]

    operations = [
        migrations.AddField(
            model_name='fieldbalance',
            name='agzu_fluid',
            field=models.FloatField(db_index=True, default=0, verbose_name='Замер жидкости по скважинам'),
        ),
        migrations.AddField(
            model_name='fieldbalance',
            name='agzu_oil',
            field=models.FloatField(db_index=True, default=0, verbose_name='Замер нефти по скважинам'),
        ),
        migrations.AddField(
            model_name='fieldbalance',
            name='teh_rej_fluid',
            field=models.FloatField(db_index=True, default=0, verbose_name='Замер по Тех. жидкости'),
        ),
        migrations.AddField(
            model_name='fieldbalance',
            name='teh_rej_oil',
            field=models.FloatField(db_index=True, default=0, verbose_name='Замер по Тех. нефти'),
        ),
    ]
