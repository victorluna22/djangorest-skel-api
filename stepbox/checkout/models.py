#encoding: utf-8

import decimal
from StringIO import StringIO
from datetime import datetime, timedelta
from decimal import Decimal
from pyrcws import GetAuthorizedException, PaymentAttempt
from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.conf import settings
from rest_framework.exceptions import APIException
from account.models import ConsumerUser, Employee, Address
from company.models import Company
from product.models import Product
from .signals import post_save_order, post_save_order_receiver, post_save_balance_operation_receiver
from django.utils.translation import ugettext as _

# Pedido
# Item de pedido
# Boleto
# Resgate

ORDER_AUTHORIZED = 0

STATUS_CHOICES = (
    (ORDER_AUTHORIZED, u'Aprovada'),
    (1, u'Negada'),
    (2, u'Negada por Fraude'),
    (5, u'Em Revisão (Análise Manual de Fraude)'),
    (1022, u'Erro na operadora de cartão'),
    (1024, u'Erro nos parâmetros enviados'),
    (1025, u'Erro nas credenciais'),
    (2048, u'Erro interno na maxiPago!'),
    (4097, u'Timeout com a adquirente')
)

OPENED = 1;DELIVERING = 2; DELIVERED = 3; CANCELED = 4;
ORDER_SITUATIONS = (
    (OPENED, u'Em aberto'),
    (DELIVERING, u'Em rota'),
    (DELIVERED, u'Entregue'),
    (CANCELED, u'Cancelado'),
)

class PaymentType(models.Model):
    name = models.CharField('Nome', max_length=255)
    credit_ipill = models.BooleanField(default=1)
    obligatory = models.BooleanField(default=0)
    

class Order(models.Model):
    """
        Representação de um pedido.
    """
    user = models.ForeignKey(ConsumerUser, verbose_name=u'usuario', related_name='orders_user')
    company = models.ForeignKey(Company, verbose_name=u'empresa', related_name='orders_company')
    billing_name = models.CharField(max_length=200, null=True, blank=True, verbose_name=u'nome completo')
    billing_number = models.CharField(max_length=16, verbose_name=u'Número')
    billing_cpf = models.CharField(max_length=14, verbose_name=u'CPF')
    billing_expiration = models.CharField(verbose_name=u'validade', max_length=16)
    billing_cvc = models.CharField(verbose_name=u'CVC', max_length=4)
    situation = models.CharField(max_length=100, choices=ORDER_SITUATIONS, default=OPENED)
    payment_type = models.ForeignKey(PaymentType)
    return_cash_from = models.DecimalField(decimal_places=2, max_digits=30, verbose_name=u'troco para', null=True, blank=True)
    total = models.DecimalField(decimal_places=2, max_digits=30, verbose_name=u'valor pago')

    status = models.PositiveSmallIntegerField(default=1000, verbose_name=u'situação')
    processor_reply_dump = models.TextField(null=True, blank=True, verbose_name=u'retorno do gateway')
    address = models.ForeignKey(Address, verbose_name=u'Endereço', blank=True, null=True)
    # number_installments = models.PositiveSmallIntegerField(null=True, blank=True, default=0, verbose_name=u'parcelas')

    purchase_time = models.DateTimeField(auto_now=True, verbose_name=u'data')

    @property
    def authorized(self):
        return self.status == ORDER_AUTHORIZED

    @property
    def get_situation(self):
        return dict(ORDER_SITUATIONS)[int(self.situation)]

    def pay_credcard(self):
        params = {
            'affiliation_id': '123456789',
            'total': self.total,
            'order_id': self.id, # strings are allowed here
            'card_number': self.billing_number,
            'cvc2': self.billing_cvc,
            'exp_month': self.billing_expiration.split('-')[1],
            'exp_year': self.billing_expiration.split('-')[0],
            'card_holders_name': self.billing_name,
            'installments': 1,
            'debug': settings.DEBUG,
        }

        attempt = PaymentAttempt(**params)
        try:
            attempt.get_authorized(conftxn='S')
        except GetAuthorizedException, e:
            self.status = attempt.codret
            self.processor_reply_dump = attempt.msgret
            self.save()
            raise APIException(u'Erro %s: %s' % (e.codret, e.msg))
        else:
            attempt.capture()
            
        if attempt.msgret:
            self.status = attempt.codret
            self.processor_reply_dump = attempt.msgret
            self.save()
        return attempt

    def save(self, *args, **kwargs):
        if self.pk is not None:
            old_order = Order.objects.get(pk=self.pk)
            if old_order.situation != self.situation:
                OrderChangeSituation.objects.create(order=self, old_situation=old_order.situation, current_situation=self.situation)
        return super(Order, self).save(*args, **kwargs)

class ProductItemManager(models.Manager):
    def get_best_seller(self, company):
        result = self.filter(order__company=company, order__status=0).values('product__name').annotate(selled_count=models.Count('product')).order_by('-selled_count')[0]
        return result


class ProductItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'pedido', related_name='items')
    product = models.ForeignKey(Product, verbose_name=u'produto')
    qtd = models.IntegerField("Quantidade", default=1)
    price = models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name=u'Preço')

    objects = ProductItemManager()


class OrderChangeSituation(models.Model):
    order = models.ForeignKey(Order, verbose_name=u'pedido', related_name='changes')
    old_situation = models.CharField(max_length=100, choices=ORDER_SITUATIONS, default=OPENED)
    current_situation = models.CharField(max_length=100, choices=ORDER_SITUATIONS, default=OPENED)
    created_at = models.DateTimeField(auto_now_add=True)

TYPES = (
    (1, 'Conta Corrente'),
    (2, 'Conta Poupança'),
    )

DISCHARGE_STATUS_REQUESTED = 0
DISCHARGE_STATUS_DONE = 1
DISCHARGE_STATUS_FAIL = 2
DISCHARGE_STATUS_CHOICES = (
    (DISCHARGE_STATUS_REQUESTED, u'Solicitado'),
    (DISCHARGE_STATUS_DONE, u'Efetuado'),
    (DISCHARGE_STATUS_FAIL, u'Falha'),
)

BALANCE_KIND_DEBIT = 0
BALANCE_KIND_CREDIT = 1
BALANCE_KIND_CHOICES = (
    (BALANCE_KIND_DEBIT, u'Débito'),
    (BALANCE_KIND_CREDIT, u'Crédito'),
)

class DischargeManager(models.Manager):
    def total_discharged(self, company):
        return super(DischargeManager, self).filter(company=company, status=DISCHARGE_STATUS_DONE).aggregate(
            total=Sum('value'))['total'] or 0

    def total_discharged_requested(self, company):
        return super(DischargeManager, self).filter(company=company, status=DISCHARGE_STATUS_REQUESTED).aggregate(
            total=Sum('value'))['total'] or 0

    def total_discharge_available(self, company):
        total_available = Order.objects.filter(company=company, status=ORDER_AUTHORIZED, payment_type=2, purchase_time__lt=datetime.now()-timedelta(days=30)).aggregate(
            total=Sum('total'))['total'] or 0
        total_discharged = self.total_discharged(company)
        return total_available - total_discharged

class Discharge(models.Model):
    company = models.ForeignKey(Company)
    pharmacist = models.ForeignKey(Employee)
    value = models.DecimalField(_(u'Valor resgate'), max_digits=9, decimal_places=2, default=0)
    status = models.IntegerField(_(u'Situação do Resgate'), choices=DISCHARGE_STATUS_CHOICES, default=DISCHARGE_STATUS_REQUESTED)
    owner_name = models.CharField(_(u'Titular'), max_length=255)
    bank = models.CharField(_(u'Banco'), max_length=255)
    agency = models.CharField(_(u'Agência'), max_length=10)
    account = models.CharField(_(u'Número da conta'), max_length=10)
    cpf = models.CharField(_(u'CPF'), max_length=255)
    type_account = models.IntegerField(verbose_name=_(u'Tipo'), choices=TYPES, default=1)
    created_at = models.DateTimeField(_(u'Data resgate'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Data modificação'), auto_now=True)

    objects = DischargeManager()

    def save(self, *args, **kwargs):
        create_balance = False
        if self.pk is not None:
            discharge_old = Discharge.objects.get(pk=self.pk)
            if (discharge_old.status == DISCHARGE_STATUS_DONE or discharge_old.status == DISCHARGE_STATUS_REQUESTED) and self.status == DISCHARGE_STATUS_FAIL:
                create_balance = True
                kind = BALANCE_KIND_CREDIT
            elif discharge_old.status == DISCHARGE_STATUS_FAIL and (self.status == DISCHARGE_STATUS_DONE or self.status == DISCHARGE_STATUS_REQUESTED):
                create_balance = True
                kind = BALANCE_KIND_DEBIT
        else:
            create_balance = True
            kind = BALANCE_KIND_DEBIT

        data = super(Discharge, self).save(*args, **kwargs)

        if create_balance:
            value = Discharge.objects.total_discharge_available(self.company)
            BalanceOperation.objects.create(company=self.company, kind=kind, value=value, value_company=value, discharge=self)
        return data





class BalanceManager(models.Manager):
    def total_gross_gain(self, company):
        credits = \
            super(BalanceManager, self).filter(company=company, kind=BALANCE_KIND_CREDIT).aggregate(total=Sum('value'))[
                'total'] or 0
        debits = \
            super(BalanceManager, self).filter(company=company, kind=BALANCE_KIND_DEBIT).aggregate(total=Sum('value'))[
                'total'] or 0
        return credits - debits

    def total_liquid_gain(self, company):
        credits = \
            super(BalanceManager, self).filter(company=company, kind=BALANCE_KIND_CREDIT).aggregate(total=Sum('value_company'))[
                'total'] or 0
        debits = \
            super(BalanceManager, self).filter(company=company, kind=BALANCE_KIND_DEBIT).aggregate(total=Sum('value_company'))[
                'total'] or 0
        return credits - debits


class BalanceOperation(models.Model):
    company = models.ForeignKey(Company)
    order = models.ForeignKey(Order, related_name='operations', null=True, blank=True)
    discharge = models.ForeignKey(Discharge, null=True, blank=True)
    kind = models.IntegerField(_(u'Tipo da operação'), choices=BALANCE_KIND_CHOICES)
    value = models.DecimalField(_(u'Valor da operação'), max_digits=9, decimal_places=2, default=0)
    value_company = models.DecimalField(_(u'Valor da empresa'), max_digits=9, decimal_places=2, default=0)
    tax = models.DecimalField(_(u'Taxa'), max_digits=9, decimal_places=2, default=0)
    created_at = models.DateTimeField(_(u'Data operação'), auto_now_add=True)
    updated_at = models.DateTimeField(_(u'Data modificação'), auto_now=True)

    objects = BalanceManager()

    class Meta:
        verbose_name = _(u'operação no saldo')
        verbose_name_plural = _(u'operações no saldo')

    def __unicode__(self):
        return u'{0:.3g}'.format(self.value)



post_save_order.connect(post_save_order_receiver, sender=Order, dispatch_uid='ipill.checkout.signals.post_save_order')
post_save.connect(post_save_balance_operation_receiver, sender=BalanceOperation, dispatch_uid='ipill.checkout.signals.post_save_balance')