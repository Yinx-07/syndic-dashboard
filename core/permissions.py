from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import AccessMixin
from .models import Building, Apartment, User

def manager_required(view_func):
    """
    Decorator for views that checks if the logged-in user is a Manager (or superuser).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_manager or request.user.is_superuser):
            raise PermissionDenied("Accès réservé exclusivement aux gestionnaires de syndic.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def resident_required(view_func):
    """
    Decorator for views that checks if the logged-in user is a Resident (or superuser).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_resident or request.user.is_superuser):
            raise PermissionDenied("Accès réservé exclusivement aux copropriétaires et résidents.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


class ManagerRequiredMixin(AccessMixin):
    """CBV Mixin to enforce Manager role."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_manager or request.user.is_superuser):
            raise PermissionDenied("Accès réservé exclusivement aux gestionnaires de syndic.")
        return super().dispatch(request, *args, **kwargs)


class ResidentRequiredMixin(AccessMixin):
    """CBV Mixin to enforce Resident role."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not (request.user.is_resident or request.user.is_superuser):
            raise PermissionDenied("Accès réservé exclusivement aux copropriétaires et résidents.")
        return super().dispatch(request, *args, **kwargs)


def get_user_scoped_buildings(user):
    """
    Returns buildings scoped to the current manager user.
    Superusers see all buildings.
    Managers see ONLY buildings assigned to them.
    Residents get an empty queryset.
    """
    if user.is_superuser:
        return Building.objects.all().prefetch_related('apartments')
    elif user.is_manager:
        return Building.objects.filter(manager=user).prefetch_related('apartments')
    return Building.objects.none()


def get_user_scoped_apartments(user):
    """
    Returns apartments scoped to the current resident user.
    Superusers see all apartments.
    Residents see ONLY apartments owned by them.
    Managers see apartments belonging to their managed buildings.
    """
    if user.is_superuser:
        return Apartment.objects.all().select_related('building', 'owner')
    elif user.is_resident:
        return Apartment.objects.filter(owner=user).select_related('building', 'owner')
    elif user.is_manager:
        return Apartment.objects.filter(building__manager=user).select_related('building', 'owner')
    return Apartment.objects.none()
