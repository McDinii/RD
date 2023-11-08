from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import Employee
from django.shortcuts import get_object_or_404
class IsActiveEmployeePermission(BasePermission):
    """
    Permission check for active Employee or Admin.
    """
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return False
        employee = get_object_or_404(Employee, user=user)
        if not employee.active:
            raise PermissionDenied("Employee is not active.")
        return employee.active
