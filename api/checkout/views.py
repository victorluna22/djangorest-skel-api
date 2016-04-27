# encoding: utf-8

from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import generics
from .serializers import OrderWriteSerializer, OrderCashWriteSerializer, OrderReadSerializer, \
    OrderChangeSituationSerializer, ProductItemSerializer, ProductItemWriteSerializer, DischargeSerializer, \
    DischargeStatusSerializer, BalanceOperationSerializer, DischargeReadSerializer, \
    RevenuesSerializer
from .models import Order, ProductItem, Discharge, BalanceOperation, ORDER_AUTHORIZED, BALANCE_KIND_CREDIT
from .signals import post_save_order
from account.permissions import ConsumerPermission, CompanyPermission, AdmPermission
from product.models import Product


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-id')
    serializer_class = OrderReadSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def update(self, request, pk=None):
        self.serializer_class = OrderChangeSituationSerializer
        return super(OrderViewSet, self).update(request, pk)

class ProductItemViewSet(viewsets.ModelViewSet):
    queryset = ProductItem.objects.all().order_by('-id')
    serializer_class = ProductItemSerializer


class OrderUserListView(generics.ListAPIView):
    serializer_class = OrderReadSerializer
    permission_classes = (IsAuthenticated, ConsumerPermission)

    def get_queryset(self):
        user = self.request.user.get_user()
        orders = Order.objects.filter(user=user)
        return orders

class OrderCompanyListView(generics.ListAPIView):
    serializer_class = OrderReadSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def get_queryset(self):
        user = self.request.user.get_user()

        orders = Order.objects.filter(company=user.company).order_by('-purchase_time')

        if self.request.GET.get('start_date'):
            orders = orders.filter(purchase_time__gte=self.request.GET.get('start_date'))
        if self.request.GET.get('end_date'):
            orders = orders.filter(purchase_time__lte=self.request.GET.get('end_date'))
        if self.request.GET.get('payment_type'):
            orders = orders.filter(payment_type=self.request.GET.get('payment_type'))
        if self.request.GET.get('status'):
            orders = orders.filter(status=self.request.GET.get('status'))
        if self.request.GET.get('q'):
            orders = orders.filter(user__full_name__icontains=self.request.GET.get('q'))

        return orders

class OrderLastCompanyListView(generics.ListAPIView):
    serializer_class = OrderReadSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def get_queryset(self):
        user = self.request.user.get_user()

        orders = Order.objects.filter(company=user.company).order_by('-purchase_time')[:10]
        return orders

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderWriteSerializer
    permission_classes = (IsAuthenticated, ConsumerPermission)

    # @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = OrderWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user.get_user(), total=0)
        print request.data
        if order:
            total_order = 0
            ids = request.data.get('products[][id]')
            if type(ids) == unicode:
                ids = [ids]
            for i, id in enumerate(ids):
                product = Product.objects.get(id=id)
                serializer_p = ProductItemWriteSerializer(data={'order': order.id, 'product': product.id, 'qtd': request.data.get('products[][qtd]')[i], 'price': product.price})
                serializer_p.is_valid(raise_exception=True)
                serializer_p.save()
                total_order += product.price * int(request.data.get('products[][qtd]')[i])
            order.total = total_order
            order.save()
            data = order.pay_credcard()
            post_save_order.send(sender=Order, order=order)
            return Response({'detail': data.msgret})
        else:
            raise APIException('Ocorreu um erro em sua transação. Tente novamente mais tarde.')

        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        

class OrderCashCreateView(generics.CreateAPIView):
    serializer_class = OrderCashWriteSerializer
    permission_classes = (IsAuthenticated, ConsumerPermission)

    def post(self, request, *args, **kwargs):
        serializer = OrderCashWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user.get_user(), total=0)
        print request.data
        if order:
            total_order = 0
            ids = request.data.get('products[][id]')
            if type(ids) == unicode:
                ids = [ids]
            for i, id in enumerate(ids):
                product = Product.objects.get(id=id)
                serializer_p = ProductItemWriteSerializer(data={'order': order.id, 'product': product.id, 'qtd': request.data.get('products[][qtd]')[i], 'price': product.price})
                serializer_p.is_valid(raise_exception=True)
                serializer_p.save()
                total_order += product.price * int(request.data.get('products[][qtd]')[i])
            order.total = total_order
            order.status = 0
            order.save()
            post_save_order.send(sender=Order, order=order)
        # headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response(serializer.data)

class DischargeListView(generics.ListAPIView):
    serializer_class = DischargeReadSerializer
    queryset = Discharge.objects.all().order_by('-id')
    permission_classes = (IsAuthenticated, AdmPermission)

    def get_queryset(self):
        discharges = Discharge.objects.all().order_by('-created_at')

        if self.request.GET.get('start_date'):
            discharges = discharges.filter(created_at__gte=self.request.GET.get('start_date'))
        if self.request.GET.get('end_date'):
            discharges = discharges.filter(created_at__lte=self.request.GET.get('end_date'))
        if self.request.GET.get('company'):
            discharges = discharges.filter(company=self.request.GET.get('company'))
        if self.request.GET.get('city'):
            discharges = discharges.filter(company__address__city__id=self.request.GET.get('city'))
        if self.request.GET.get('status'):
            discharges = discharges.filter(status=self.request.GET.get('status'))
        return discharges



class DischargeCompanyListView(generics.ListAPIView):
    serializer_class = DischargeSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def get_queryset(self):
        user = self.request.user.get_user()
        discharges = Discharge.objects.filter(company=user.company)
        if self.request.GET.get('start_date'):
            discharges = discharges.filter(created_at__gte=self.request.GET.get('start_date'))
        if self.request.GET.get('end_date'):
            discharges = discharges.filter(created_at__lte=self.request.GET.get('end_date'))
        return discharges

class DischargeCreateView(generics.CreateAPIView):
    serializer_class = DischargeSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def post(self, request, *args, **kwargs):
        user = request.user.get_user()
        request.data['value'] = user.company.total
        serializer = DischargeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(pharmacist=user, company=user.company)
        return Response(serializer.data)

class DischargeChangeStatusView(generics.UpdateAPIView):
    serializer_class = DischargeStatusSerializer
    permission_classes = (IsAuthenticated,)
    queryset = Discharge.objects.all()


class FinanceDataView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user.get_user()
        data = {}
        data['liquid_gain'] = self.request.user.get_user().company.total
        data['discharge_available'] = Discharge.objects.total_discharge_available(user.company)
        data['discharge_requested'] = Discharge.objects.total_discharged_requested(user.company)

        return Response(data)


class OperationsCompanyListView(generics.ListAPIView):
    serializer_class = RevenuesSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user.get_user()

        operations = BalanceOperation.objects.filter(company=user.company, kind=BALANCE_KIND_CREDIT)

        if self.request.GET.get('start_date'):
            operations = operations.filter(created_at__gte=self.request.GET.get('start_date'))
        if self.request.GET.get('end_date'):
            operations = operations.filter(created_at__lte=self.request.GET.get('end_date'))

        operations = operations.extra({'date_created':"date(created_at)"}).values('date_created').annotate(transactions=Count('id'), total=Sum('value'), receive=Sum('value_company'))
        return operations
