# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-26 16:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('account', '0002_employee_company'),
        ('company', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BalanceOperation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.IntegerField(choices=[(0, 'D\xe9bito'), (1, 'Cr\xe9dito')], verbose_name='Tipo da opera\xe7\xe3o')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Valor da opera\xe7\xe3o')),
                ('value_company', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Valor da empresa')),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Taxa')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data opera\xe7\xe3o')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Data modifica\xe7\xe3o')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
            ],
            options={
                'verbose_name': 'opera\xe7\xe3o no saldo',
                'verbose_name_plural': 'opera\xe7\xf5es no saldo',
            },
        ),
        migrations.CreateModel(
            name='Discharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='Valor resgate')),
                ('status', models.IntegerField(choices=[(0, 'Solicitado'), (1, 'Efetuado'), (2, 'Falha')], default=0, verbose_name='Situa\xe7\xe3o do Resgate')),
                ('owner_name', models.CharField(max_length=255, verbose_name='Titular')),
                ('bank', models.CharField(max_length=255, verbose_name='Banco')),
                ('agency', models.CharField(max_length=10, verbose_name='Ag\xeancia')),
                ('account', models.CharField(max_length=10, verbose_name='N\xfamero da conta')),
                ('cpf', models.CharField(max_length=255, verbose_name='CPF')),
                ('type_account', models.IntegerField(choices=[(1, b'Conta Corrente'), (2, b'Conta Poupan\xc3\xa7a')], default=1, verbose_name='Tipo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Data resgate')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Data modifica\xe7\xe3o')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
                ('pharmacist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='nome completo')),
                ('billing_number', models.CharField(max_length=16, verbose_name='N\xfamero')),
                ('billing_cpf', models.CharField(max_length=14, verbose_name='CPF')),
                ('billing_expiration', models.CharField(max_length=16, verbose_name='validade')),
                ('billing_cvc', models.CharField(max_length=4, verbose_name='CVC')),
                ('situation', models.CharField(choices=[(1, 'Em aberto'), (2, 'Em rota'), (3, 'Entregue'), (4, 'Cancelado')], default=1, max_length=100)),
                ('return_cash_from', models.DecimalField(blank=True, decimal_places=2, max_digits=30, null=True, verbose_name='troco para')),
                ('total', models.DecimalField(decimal_places=2, max_digits=30, verbose_name='valor pago')),
                ('status', models.PositiveSmallIntegerField(default=1000, verbose_name='situa\xe7\xe3o')),
                ('processor_reply_dump', models.TextField(blank=True, null=True, verbose_name='retorno do gateway')),
                ('purchase_time', models.DateTimeField(auto_now=True, verbose_name='data')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.Address', verbose_name='Endere\xe7o')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_company', to='company.Company', verbose_name='empresa')),
            ],
        ),
        migrations.CreateModel(
            name='OrderChangeSituation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_situation', models.CharField(choices=[(1, 'Em aberto'), (2, 'Em rota'), (3, 'Entregue'), (4, 'Cancelado')], default=1, max_length=100)),
                ('current_situation', models.CharField(choices=[(1, 'Em aberto'), (2, 'Em rota'), (3, 'Entregue'), (4, 'Cancelado')], default=1, max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='changes', to='checkout.Order', verbose_name='pedido')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name=b'Nome')),
                ('credit_ipill', models.BooleanField(default=1)),
                ('obligatory', models.BooleanField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ProductItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qtd', models.IntegerField(default=1, verbose_name=b'Quantidade')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Pre\xe7o')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='checkout.Order', verbose_name='pedido')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.Product', verbose_name='produto')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='payment_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='checkout.PaymentType'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders_user', to='account.ConsumerUser', verbose_name='usuario'),
        ),
        migrations.AddField(
            model_name='balanceoperation',
            name='discharge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='checkout.Discharge'),
        ),
        migrations.AddField(
            model_name='balanceoperation',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='operations', to='checkout.Order'),
        ),
    ]