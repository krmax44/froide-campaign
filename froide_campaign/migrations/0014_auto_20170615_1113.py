# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-06-15 09:13
from __future__ import unicode_literals

import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0013_auto_20170615_1104'),
    ]

    operations = [
        migrations.AddField(
            model_name='informationobject',
            name='search_text',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='informationobject',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(default=''),
        ),
    ]