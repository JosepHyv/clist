# Generated by Django 2.2.10 on 2020-02-18 02:10

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clist', '0028_contest_insert_or_update_trigger'),
    ]

    operations = [
        migrations.AddField(
            model_name='resource',
            name='ratings',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list),
        ),
    ]
