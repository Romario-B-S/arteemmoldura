# Generated by Django 5.0.4 on 2024-06-04 15:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0031_alter_pedido_tamanho'),
    ]

    operations = [
        migrations.AddField(
            model_name='endereco',
            name='telefone',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AlterField(
            model_name='endereco',
            name='cep',
            field=models.CharField(blank=True, max_length=9, null=True),
        ),
    ]