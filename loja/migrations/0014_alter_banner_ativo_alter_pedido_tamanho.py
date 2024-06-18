# Generated by Django 5.0.4 on 2024-06-02 02:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0013_pedido_id_pagamento_pedido_pagamento_aprovado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='ativo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='pedido',
            name='tamanho',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='loja.tamanho'),
        ),
    ]
