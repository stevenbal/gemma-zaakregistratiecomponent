# Generated by Django 2.0.6 on 2018-06-11 13:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0009_klantcontact'),
    ]

    operations = [
        migrations.AddField(
            model_name='klantcontact',
            name='zaak',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='datamodel.Zaak'),
            preserve_default=False,
        ),
    ]
