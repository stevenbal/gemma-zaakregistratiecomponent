# Generated by Django 2.0.9 on 2019-01-28 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0051_zaak_relevante_andere_zaken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zaakproductofdienst',
            name='product_of_dienst',
            field=models.URLField(help_text='Het product of de dienst die door de zaak wordt voortgebracht. Dit is de URL naar de resource zoals die door de producten- en dienstencatalogus-API wordt ontsloten.', verbose_name='product of dienst'),
        ),
    ]
