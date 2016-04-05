from rest_framework import permissions

class ConsumerPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user.get_user()
        if user and user.is_consumer():
            return True
        return False


class CompanyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user.get_user()
        if user and user.is_company():
            return True
        return False


class AdmPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        user = request.user.get_user()
        if user and user.is_adm():
            return True
        return False