# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-12 07:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmention', '0004_webmentionresponse_status_key'),
    ]

    operations = [
        migrations.AlterField(
            model_name='webmentionresponse',
            name='status_key',
            field=models.CharField(max_length=6, unique=True),
        ),
    ]