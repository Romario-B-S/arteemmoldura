# Generated by Django 5.0.4 on 2024-06-02 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0022_pedido_adicional_alter_pedido_tamanho'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='tamanho',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]