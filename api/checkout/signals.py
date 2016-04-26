# -*- coding: utf-8 -*-
from django.dispatch.dispatcher import Signal
from account.models import DeviceUser


post_save_order = Signal(providing_args=['order'])

def post_save_order_receiver(sender, order, **kwargs):
    from .models import BALANCE_KIND_CREDIT, ORDER_AUTHORIZED, OPENED, DELIVERING, DELIVERED, CANCELED
    from .models import BalanceOperation
    import decimal

    print 'POST SAVE ORDER - %.2f' % order.total

    if order.status == ORDER_AUTHORIZED and order.payment_type.gain_credit and not order.operations.all():
        value_company = order.total
        tax = 0
        if order.company.commission_value:
            value_company = order.total - order.total * order.company.commission_value / decimal.Decimal(100)
            tax = order.company.commission_value

        BalanceOperation.objects.create(company=order.company, kind=BALANCE_KIND_CREDIT, value=order.total, value_company=value_company, tax=tax, order=order)

    message = None
    if order.status == ORDER_AUTHORIZED and order.situation == OPENED:
        message = 'Pedido #%06d aberto com sucesso.' % order.id
    elif order.status == ORDER_AUTHORIZED and order.situation == DELIVERING:
        message = 'Seu pedido #%06d está a caminho do endereço de entrega.' % order.id
    elif order.status == ORDER_AUTHORIZED and order.situation == DELIVERED:
        message = 'Seu pedido #%06d foi entregue com sucesso. Obrigado pela confiança!' % order.id
    elif order.status == ORDER_AUTHORIZED and order.situation == CANCELED:
        message = 'Seu pedido #%06d foi cancelado pela empresa.' % order.id

    if message:
        # my_phones = DeviceUser.objects.filter(reg_id='cmoM9cprZkE:APA91bFiIHtGqzJhh7rk2dSCyx0Hf-WQXx1IKN3qUzn0APleYTknN8H0fUGeasgsi7en7Au5sPQ42ssxYkr7rANYPqLhbHfmrnVmQE4Ezedzc4ylZUjWH77pzFzMO_4OfhYOTM2Ytavl')
        my_phones = DeviceUser.objects.filter(user=order.user)
        retorno = my_phones.send_message({'message': message}, collapse_key='something')
        print retorno



def post_save_balance_operation_receiver(sender, instance, created, **kwargs):
    from .models import BALANCE_KIND_CREDIT
    if created:
        if instance.kind == BALANCE_KIND_CREDIT:
            instance.company.total += instance.value_company
        else:
            instance.company.total -= instance.value_company
        instance.company.save()
