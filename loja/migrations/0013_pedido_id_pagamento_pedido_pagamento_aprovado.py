# Generated by Django 5.0.4 on 2024-05-27 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0012_rename_adicheckaut_pedido_adicheckout'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='id_pagamento',
            field=models.CharField(default=0, max_length=400),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pedido',
            name='pagamento_aprovado',
            field=models.BooleanField(default=False),
        ),
    ]
