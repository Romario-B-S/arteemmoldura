# Generated by Django 5.0.4 on 2024-06-02 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0015_alter_pedido_tamanho'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='tamanho',
        ),
    ]
