# Generated by Django 3.2.12 on 2022-03-29 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ml_project', '0007_auto_20220329_1522'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='uploadedFile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ml_project.uploadedfile'),
        ),
    ]
