# Generated by Django 2.0.9 on 2019-01-03 13:53

from django.db import migrations, models
import vng_api_common.fields


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0046_zaak_laatste_betaaldatum'),
    ]

    operations = [
        migrations.AddField(
            model_name='zaak',
            name='verlenging_duur',
            field=vng_api_common.fields.DaysDurationField(blank=True, help_text="Het aantal werkbare dagen waarmee de doorlooptijd van de behandeling van de ZAAK is verlengd (of verkort) ten opzichte van de eerder gecommuniceerde doorlooptijd. Specifieer de duur als 'DD 00:00'", max_duration=999, min_duration=1, null=True, verbose_name='duur verlenging'),
        ),
        migrations.AddField(
            model_name='zaak',
            name='verlenging_reden',
            field=models.CharField(blank=True, help_text='Omschrijving van de reden voor het verlengen van de behandeling van de zaak.', max_length=200, verbose_name='reden verlenging'),
        ),
    ]
