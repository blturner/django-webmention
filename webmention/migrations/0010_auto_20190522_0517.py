# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-22 05:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webmention', '0009_remove_webmentionresponse_status_key'),
    ]

    operations = [
        migrations.RenameField(
            model_name='webmentionresponse',
            old_name='status',
            new_name='id',
        ),
    ]