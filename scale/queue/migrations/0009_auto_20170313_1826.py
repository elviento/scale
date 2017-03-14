# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-13 18:26
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('queue', '0008_auto_20160421_1648'),
    ]

    operations = [
        migrations.AlterField(
            model_name='queue',
            name='configuration',
            field=django.contrib.postgres.fields.jsonb.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='queue',
            name='job_exe',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, primary_key=True, serialize=False, to='job.JobExecution'),
        ),
    ]
