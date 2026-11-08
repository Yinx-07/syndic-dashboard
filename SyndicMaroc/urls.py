from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import (
    CustomLoginView,
    dashboard_dispatch,
    manager_dashboard,
    resident_dashboard,
    building_detail,
    residents_list,
    update_resident_info,
    assign_resident_to_apartment,
    add_expense,
    delete_expense,
    create_announcement,
    print_receipt,
    create_maintenance_ticket,
    update_ticket_status,
    update_payment_status,
    update_opening_balance
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Role Dispatch
    path('', dashboard_dispatch, name='dashboard_dispatch'),
    path('dashboard/', dashboard_dispatch, name='dashboard'),
    
    # Manager & Admin Routes
    path('manager/dashboard/', manager_dashboard, name='manager_dashboard'),
    path('manager/building/<int:building_id>/', building_detail, name='building_detail'),
    path('manager/residents/', residents_list, name='residents_list'),
    path('manager/resident/<int:resident_id>/update/', update_resident_info, name='update_resident_info'),
    path('manager/apartment/<int:apartment_id>/assign-resident/', assign_resident_to_apartment, name='assign_resident_to_apartment'),
    path('manager/apartment/<int:apartment_id>/opening-balance/', update_opening_balance, name='update_opening_balance'),
    path('manager/payment/<int:payment_id>/update/', update_payment_status, name='update_payment_status'),
    path('manager/expense/add/', add_expense, name='add_expense'),
    path('manager/expense/<int:expense_id>/delete/', delete_expense, name='delete_expense'),
    path('manager/ticket/<int:ticket_id>/update/', update_ticket_status, name='update_ticket_status'),
    path('manager/announcement/create/', create_announcement, name='create_announcement'),
    
    # Shared / Receipt Route
    path('payment/<int:payment_id>/receipt/', print_receipt, name='print_receipt'),
    
    # Resident Routes
    path('resident/dashboard/', resident_dashboard, name='resident_dashboard'),
    path('resident/ticket/create/', create_maintenance_ticket, name='create_maintenance_ticket'),
]
