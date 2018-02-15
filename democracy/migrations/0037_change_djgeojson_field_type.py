# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-12-19 12:41
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations
import djgeojson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('democracy', '0036_migrate_geojson_to_postgis'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hearing',
            name='geojson',
            field=djgeojson.fields.GeoJSONField(blank=True, null=True, verbose_name='area'),
        ),
        migrations.AlterField(
            model_name='hearing',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326, verbose_name='area geometry'),
        ),
        migrations.AlterField(
            model_name='sectioncomment',
            name='geojson',
            field=djgeojson.fields.GeoJSONField(blank=True, null=True, verbose_name='location'),
        ),
        migrations.AlterField(
            model_name='sectioncomment',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(blank=True, null=True, srid=4326, verbose_name='location geometry'),
        ),
    ]
