# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-08 17:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_campaign', '0006_auto_20160908_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='subject_template',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
