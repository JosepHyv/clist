# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-06 05:45


from django.db import migrations
import django_enumfield.db.fields
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_auto_20180206_0545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='tshirt_size',
            field=django_enumfield.db.fields.EnumField(blank=True, default=1, enum=events.models.TshirtSize, null=True),
        ),
    ]
