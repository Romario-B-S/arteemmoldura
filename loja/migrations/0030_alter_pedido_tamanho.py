# Generated by Django 5.0.4 on 2024-06-03 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0029_pedido_tamanho'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='tamanho',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
