# Generated by Django 5.0.4 on 2024-06-18 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0034_status_pedido_transportadora_pedido_codigo_rastreio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transportadora',
            name='cnpj',
            field=models.CharField(default='00000000000000', max_length=14),
        ),
    ]