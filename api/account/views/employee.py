# encoding: utf-8

from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializers import EmployeeSerializer
from ..models import Employee
from ..permissions import CompanyPermission, AdmPermission


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = (IsAuthenticated, CompanyPermission)

    def get_queryset(self):
        return Employee.objects.filter(deleted=0, company=self.request.user.get_user().company).order_by('-date_joined')

    def destroy(self, request, pk=None):
        if Employee.objects.filter(pk=pk).update(deleted=1):
            return Response({'detail': 'Registro removido com sucesso'})
        return Response({'detail': 'Erro ao tentar remover registro'})

    def perform_create(self, serializer):
        serializer.save(company=self.request.user.get_user().company)

    def perform_update(self, serializer):
        serializer.save(company=self.request.user.get_user().company)


class EmployeeCreateView(generics.CreateAPIView):
    serializer_class = EmployeeSerializer
    permission_classes = (IsAuthenticated, AdmPermission)