# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-14 07:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webmention', '0006_webmentionresponse_status_code'),
    ]

    operations = [
        migrations.DeleteModel(
            name='SentWebMention',
        ),
    ]