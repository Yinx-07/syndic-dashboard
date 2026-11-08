import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.core.exceptions import PermissionDenied

from .models import Building, Apartment, MaintenanceTicket, MonthlyPayment, Expense, BuildingAnnouncement, User
from .permissions import (
    manager_required,
    resident_required,
    get_user_scoped_buildings,
    get_user_scoped_apartments
)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        if user.is_manager or user.is_superuser:
            return '/manager/dashboard/'
        elif user.is_resident:
            return '/resident/dashboard/'
        return '/dashboard/'


def get_building_expenses_chart_data(building):
    """
    Helper function to aggregate expenses by category in MAD for Chart.js rendering.
    """
    expenses = Expense.objects.filter(building=building).values('category').annotate(total=Sum('amount'))
    category_labels_map = dict(Expense.Category.choices)

    labels = []
    data = []
    for item in expenses:
        cat_code = item['category']
        labels.append(category_labels_map.get(cat_code, cat_code))
        data.append(float(item['total'] or 0))

    if not labels:
        labels = ["Aucune dépense"]
        data = [0]

    return json.dumps(labels), json.dumps(data)


def get_recouvrement_chart_data(buildings):
    """
    Returns JSON serialized labels, data, and colors for current month recovery rate chart.
    Colors: 🟢 Vert (#059669), 🔴 Rouge (#dc2626), 🟠 Orange (#d97706)
    """
    payments = MonthlyPayment.objects.filter(apartment__building__in=buildings, month_name__icontains="Septembre 2026")
    if not payments.exists():
        payments = MonthlyPayment.objects.filter(apartment__building__in=buildings)

    paid_count = payments.filter(status=MonthlyPayment.PaymentStatus.PAID).count()
    unpaid_count = payments.filter(status=MonthlyPayment.PaymentStatus.UNPAID).count()
    partial_count = payments.filter(status=MonthlyPayment.PaymentStatus.PARTIAL).count()

    labels = ["Cotisations Réglées", "Cotisations Non Réglées", "Paiements Partiels"]
    data = [paid_count, unpaid_count, partial_count]
    colors = ["#059669", "#dc2626", "#d97706"]

    return json.dumps(labels), json.dumps(data), json.dumps(colors)


def get_monthly_cashflow_chart_data(buildings):
    """
    Returns JSON serialized labels and data (MAD amounts collected) over 12 months (Jan - Dec).
    """
    months = [
        "Janvier 2026", "Février 2026", "Mars 2026", "Avril 2026",
        "Mai 2026", "Juin 2026", "Juillet 2026", "Août 2026",
        "Septembre 2026", "Octobre 2026", "Novembre 2026", "Décembre 2026"
    ]
    labels = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
    
    payments = MonthlyPayment.objects.filter(apartment__building__in=buildings)
    
    data = []
    for month in months:
        m_payments = payments.filter(month_name=month)
        total_collected = 0.0
        for p in m_payments:
            total_collected += float(p.actual_paid_amount)
        data.append(round(total_collected, 2))

    return json.dumps(labels), json.dumps(data)


@login_required
def dashboard_dispatch(request):
    """Redirect user to appropriate dashboard based on their role."""
    if request.user.is_manager or request.user.is_superuser:
        return redirect('manager_dashboard')
    elif request.user.is_resident:
        return redirect('resident_dashboard')
    return redirect('login')


@login_required
@manager_required
def manager_dashboard(request):
    """
    Manager Dashboard: Shows assigned buildings, apartments, monthly payment stats, and expense charts.
    """
    buildings = get_user_scoped_buildings(request.user)
    
    total_buildings = buildings.count()
    apartments = Apartment.objects.filter(building__in=buildings).select_related('owner', 'building').prefetch_related('monthly_payments')
    total_apartments = apartments.count()
    
    total_opening_balance = apartments.aggregate(total=Sum('opening_balance'))['total'] or 0.00
    
    current_payments = MonthlyPayment.objects.filter(apartment__building__in=buildings)
    paid_count = current_payments.filter(status=MonthlyPayment.PaymentStatus.PAID).count()
    unpaid_count = current_payments.filter(status=MonthlyPayment.PaymentStatus.UNPAID).count()

    tickets = MaintenanceTicket.objects.filter(building__in=buildings)
    pending_tickets_count = tickets.filter(status=MaintenanceTicket.Status.PENDING).count()
    in_progress_tickets_count = tickets.filter(status=MaintenanceTicket.Status.IN_PROGRESS).count()

    expenses = Expense.objects.filter(building__in=buildings)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0.00

    # Format chart data for first building or primary building
    primary_building = buildings.first()
    chart_labels, chart_data = ("[]", "[]")
    if primary_building:
        chart_labels, chart_data = get_building_expenses_chart_data(primary_building)

    recouvrement_labels, recouvrement_data, recouvrement_colors = get_recouvrement_chart_data(buildings)
    cashflow_labels, cashflow_data = get_monthly_cashflow_chart_data(buildings)

    announcements = BuildingAnnouncement.objects.filter(building__in=buildings)[:5]

    context = {
        'buildings': buildings,
        'primary_building': primary_building,
        'apartments': apartments,
        'total_buildings': total_buildings,
        'total_apartments': total_apartments,
        'total_opening_balance': total_opening_balance,
        'paid_count': paid_count,
        'unpaid_count': unpaid_count,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'recouvrement_labels': recouvrement_labels,
        'recouvrement_data': recouvrement_data,
        'recouvrement_colors': recouvrement_colors,
        'cashflow_labels': cashflow_labels,
        'cashflow_data': cashflow_data,
        'tickets': tickets[:10],
        'pending_tickets_count': pending_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'announcements': announcements,
        'expense_categories': Expense.Category.choices,
        'role_title': 'Espace Syndic & Gestionnaire',
    }
    return render(request, 'core/manager_dashboard.html', context)


@login_required
@manager_required
def building_detail(request, building_id):
    """
    Detailed building view showing expenses, chart, and roster.
    """
    if request.user.is_superuser:
        building = get_object_or_404(Building, pk=building_id)
    else:
        building = get_object_or_404(Building, pk=building_id, manager=request.user)
        
    apartments = building.apartments.select_related('owner').prefetch_related('monthly_payments').all()
    tickets = building.tickets.all()
    announcements = building.announcements.all()
    expenses = building.expenses.all()
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0.00

    chart_labels, chart_data = get_building_expenses_chart_data(building)
    all_residents = User.objects.filter(role=User.Role.RESIDENT)
    
    context = {
        'building': building,
        'apartments': apartments,
        'tickets': tickets,
        'announcements': announcements,
        'expenses': expenses,
        'total_expenses': total_expenses,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'all_residents': all_residents,
        'expense_categories': Expense.Category.choices,
    }
    return render(request, 'core/building_detail.html', context)


@login_required
@manager_required
def add_expense(request):
    """
    Allow manager to record a new building expense.
    """
    if request.method == 'POST':
        building_id = request.POST.get('building_id')
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category')
        amount_raw = request.POST.get('amount')
        expense_date = request.POST.get('expense_date')

        if building_id and title and category and amount_raw and expense_date:
            if request.user.is_superuser:
                building = get_object_or_404(Building, pk=building_id)
            else:
                building = get_object_or_404(Building, pk=building_id, manager=request.user)

            try:
                amount = float(amount_raw)
                Expense.objects.create(
                    building=building,
                    title=title,
                    category=category,
                    amount=amount,
                    expense_date=expense_date
                )
                messages.success(request, f"La dépense '{title}' ({amount:,.2f} MAD) a été enregistrée avec succès. Le graphique des dépenses s'est mis à jour.")
            except ValueError:
                messages.error(request, "Saisie du montant invalide.")
        else:
            messages.error(request, "Veuillez remplir tous les champs obligatoires du formulaire de dépense.")

    next_url = request.META.get('HTTP_REFERER', '/manager/dashboard/')
    return redirect(next_url)


@login_required
@manager_required
def delete_expense(request, expense_id):
    """
    Allow manager to delete an expense entry.
    """
    if request.user.is_superuser:
        expense = get_object_or_404(Expense, pk=expense_id)
    else:
        expense = get_object_or_404(Expense, pk=expense_id, building__manager=request.user)

    if request.method == 'POST':
        title = expense.title
        expense.delete()
        messages.info(request, f"La dépense '{title}' a été supprimée. Le graphique a été actualisé.")

    next_url = request.META.get('HTTP_REFERER', '/manager/dashboard/')
    return redirect(next_url)


@login_required
@manager_required
def create_announcement(request):
    """
    Allow manager to publish an announcement for a building.
    """
    if request.method == 'POST':
        building_id = request.POST.get('building_id')
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()

        if building_id and title and content:
            if request.user.is_superuser:
                building = get_object_or_404(Building, pk=building_id)
            else:
                building = get_object_or_404(Building, pk=building_id, manager=request.user)

            BuildingAnnouncement.objects.create(
                building=building,
                author=request.user,
                title=title,
                content=content
            )
            messages.success(request, f"L'annonce pour la résidence '{building.name}' a été publiée avec succès à tous les copropriétaires.")
        else:
            messages.error(request, "Veuillez remplir tous les champs du formulaire d'annonce.")

    next_url = request.META.get('HTTP_REFERER', '/manager/dashboard/')
    return redirect(next_url)


@login_required
@manager_required
def residents_list(request):
    """
    List residents grouped by Building.
    """
    if request.user.is_superuser:
        buildings = Building.objects.all().prefetch_related(
            'apartments__owner',
            'apartments__monthly_payments'
        )
        unassigned_residents = User.objects.filter(role=User.Role.RESIDENT, apartments__isnull=True)
    else:
        buildings = get_user_scoped_buildings(request.user).prefetch_related(
            'apartments__owner',
            'apartments__monthly_payments'
        )
        unassigned_residents = User.objects.none()

    all_residents = User.objects.filter(role=User.Role.RESIDENT)

    context = {
        'buildings': buildings,
        'unassigned_residents': unassigned_residents,
        'all_residents': all_residents,
        'role_title': 'Gestion des Copropriétaires par Immeuble',
    }
    return render(request, 'core/residents_list.html', context)


@login_required
@manager_required
def assign_resident_to_apartment(request, apartment_id):
    """
    Assign a resident to an apartment.
    """
    if request.user.is_superuser:
        apartment = get_object_or_404(Apartment, pk=apartment_id)
    else:
        apartment = get_object_or_404(Apartment, pk=apartment_id, building__manager=request.user)

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'existing':
            resident_id = request.POST.get('existing_resident_id')
            if resident_id:
                resident = get_object_or_404(User, pk=resident_id, role=User.Role.RESIDENT)
                apartment.owner = resident
                apartment.save()
                messages.success(request, f"Le copropriétaire {resident.get_full_name() or resident.username} a été rattaché à l'Appt {apartment.number} ({apartment.building.name}).")
            else:
                messages.error(request, "Veuillez sélectionner un copropriétaire existant.")

        elif action_type == 'new':
            username = request.POST.get('username', '').strip()
            password = request.POST.get('password', '').strip() or 'password123'
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            cin = request.POST.get('cin', '').strip()

            if username:
                if User.objects.filter(username=username).exists():
                    messages.error(request, f"Le nom d'utilisateur '{username}' existe déjà.")
                else:
                    new_resident = User.objects.create_user(
                        username=username,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        phone=phone,
                        cin=cin,
                        role=User.Role.RESIDENT
                    )
                    apartment.owner = new_resident
                    apartment.save()
                    messages.success(request, f"Le nouveau copropriétaire {new_resident.get_full_name() or username} a été créé et rattaché à l'Appt {apartment.number}.")
            else:
                messages.error(request, "Veuillez saisir un nom d'utilisateur pour le nouveau copropriétaire.")

        elif action_type == 'remove':
            old_name = apartment.owner.get_full_name() if apartment.owner else "Copropriétaire"
            apartment.owner = None
            apartment.save()
            messages.info(request, f"L'Appt {apartment.number} est désormais vacant.")

    next_url = request.META.get('HTTP_REFERER', '/manager/residents/')
    return redirect(next_url)


@login_required
@manager_required
def update_resident_info(request, resident_id):
    """
    Allow manager to edit a resident's info.
    """
    if request.user.is_superuser:
        resident = get_object_or_404(User, pk=resident_id, role=User.Role.RESIDENT)
    else:
        buildings = get_user_scoped_buildings(request.user)
        resident = get_object_or_404(User, pk=resident_id, role=User.Role.RESIDENT, apartments__building__in=buildings)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        cin = request.POST.get('cin', '').strip()

        resident.first_name = first_name
        resident.last_name = last_name
        resident.email = email
        resident.phone = phone
        resident.cin = cin
        resident.save()

        messages.success(request, f"Les informations du copropriétaire {resident.get_full_name() or resident.username} ont été mises à jour avec succès.")

    next_url = request.META.get('HTTP_REFERER', '/manager/residents/')
    return redirect(next_url)


@login_required
@manager_required
def update_payment_status(request, payment_id):
    """
    Allow manager to change monthly payment status and optional paid_amount for partial payments.
    """
    if request.user.is_superuser:
        payment = get_object_or_404(MonthlyPayment, pk=payment_id)
    else:
        payment = get_object_or_404(MonthlyPayment, pk=payment_id, apartment__building__manager=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        paid_amount_raw = request.POST.get('paid_amount')

        if new_status in MonthlyPayment.PaymentStatus.values:
            payment.status = new_status
            from django.utils import timezone
            if not payment.payment_date:
                payment.payment_date = timezone.now().date()

            if paid_amount_raw:
                try:
                    payment.paid_amount = float(paid_amount_raw)
                except ValueError:
                    pass
            elif new_status == MonthlyPayment.PaymentStatus.PAID:
                payment.paid_amount = payment.amount
            elif new_status == MonthlyPayment.PaymentStatus.PARTIAL and payment.paid_amount == 0:
                payment.paid_amount = payment.amount / 2

            payment.save()
            messages.success(request, f"Le statut de la cotisation de l'Appt {payment.apartment.number} ({payment.month_name}) a été mis à jour : {payment.get_status_display()}.")

    next_url = request.META.get('HTTP_REFERER', '/manager/dashboard/')
    return redirect(next_url)


@login_required
@manager_required
def update_opening_balance(request, apartment_id):
    """
    Allow manager to update opening balance in MAD.
    """
    if request.user.is_superuser:
        apartment = get_object_or_404(Apartment, pk=apartment_id)
    else:
        apartment = get_object_or_404(Apartment, pk=apartment_id, building__manager=request.user)

    if request.method == 'POST':
        raw_balance = request.POST.get('opening_balance')
        try:
            new_balance = float(raw_balance)
            apartment.opening_balance = new_balance
            apartment.save()
            messages.success(request, f"Le solde d'ouverture de l'Appt {apartment.number} ({apartment.building.name}) a été mis à jour à {new_balance:,.2f} MAD.")
        except (ValueError, TypeError):
            messages.error(request, "Veuillez saisir un montant numérique valide pour le solde d'ouverture.")

    next_url = request.META.get('HTTP_REFERER', '/manager/dashboard/')
    return redirect(next_url)


@login_required
def print_receipt(request, payment_id):
    """
    Render official printable PDF receipt in French for paid or partially paid monthly fees.
    Contains total amount, actual paid amount, and remaining balance to pay in MAD.
    """
    payment = get_object_or_404(MonthlyPayment, pk=payment_id)
    user = request.user

    if payment.status == MonthlyPayment.PaymentStatus.UNPAID:
        raise PermissionDenied("Le reçu n'est pas disponible pour une cotisation non réglée.")

    if not user.is_superuser:
        if user.is_manager and payment.apartment.building.manager != user:
            raise PermissionDenied("Accès refusé au reçu de paiement d'un autre syndic.")
        elif user.is_resident and payment.apartment.owner != user:
            raise PermissionDenied("Accès refusé au reçu de paiement d'un autre copropriétaire.")

    context = {
        'payment': payment,
        'apartment': payment.apartment,
        'building': payment.apartment.building,
        'owner': payment.apartment.owner,
        'syndic': payment.apartment.building.manager,
        'receipt_number': f"REC-2026-{payment.id:04d}",
    }
    return render(request, 'core/receipt.html', context)


@login_required
@resident_required
def resident_dashboard(request):
    """
    Resident Dashboard: Shows ONLY apartments owned by the resident + Building Expenses Chart!
    """
    apartments = get_user_scoped_apartments(request.user).prefetch_related('monthly_payments')
    
    total_balance = apartments.aggregate(total=Sum('opening_balance'))['total'] or 0.00
    total_tantiemes = apartments.aggregate(total=Sum('tantiemes'))['total'] or 0.00

    tickets = MaintenanceTicket.objects.filter(resident=request.user)

    buildings = Building.objects.filter(apartments__in=apartments).distinct()
    announcements = BuildingAnnouncement.objects.filter(building__in=buildings)

    # Expenses chart data for resident's primary building
    primary_building = buildings.first()
    chart_labels, chart_data = ("[]", "[]")
    building_expenses = []
    total_building_expenses = 0.00

    if primary_building:
        chart_labels, chart_data = get_building_expenses_chart_data(primary_building)
        building_expenses = primary_building.expenses.all()[:5]
        total_building_expenses = primary_building.expenses.aggregate(total=Sum('amount'))['total'] or 0.00

    recouvrement_labels, recouvrement_data, recouvrement_colors = get_recouvrement_chart_data(buildings)
    cashflow_labels, cashflow_data = get_monthly_cashflow_chart_data(buildings)

    context = {
        'apartments': apartments,
        'total_balance': total_balance,
        'total_tantiemes': total_tantiemes,
        'tickets': tickets,
        'buildings': buildings,
        'primary_building': primary_building,
        'announcements': announcements,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'recouvrement_labels': recouvrement_labels,
        'recouvrement_data': recouvrement_data,
        'recouvrement_colors': recouvrement_colors,
        'cashflow_labels': cashflow_labels,
        'cashflow_data': cashflow_data,
        'building_expenses': building_expenses,
        'total_building_expenses': total_building_expenses,
        'role_title': 'Espace Copropriétaire',
    }
    return render(request, 'core/resident_dashboard.html', context)


@login_required
@resident_required
def create_maintenance_ticket(request):
    """Allow resident to submit a maintenance request."""
    if request.method == 'POST':
        apartment_id = request.POST.get('apartment_id')
        title = request.POST.get('title')
        description = request.POST.get('description')

        if apartment_id and title and description:
            apartment = get_object_or_404(Apartment, pk=apartment_id, owner=request.user)
            MaintenanceTicket.objects.create(
                building=apartment.building,
                apartment=apartment,
                resident=request.user,
                title=title,
                description=description
            )
            messages.success(request, "Votre demande de maintenance a été transmise avec succès au syndic.")
        else:
            messages.error(request, "Veuillez remplir tous les champs du formulaire.")
    return redirect('resident_dashboard')


@login_required
@manager_required
def update_ticket_status(request, ticket_id):
    """Allow manager to update maintenance status."""
    if request.user.is_superuser:
        ticket = get_object_or_404(MaintenanceTicket, pk=ticket_id)
    else:
        ticket = get_object_or_404(MaintenanceTicket, pk=ticket_id, building__manager=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in MaintenanceTicket.Status.values:
            ticket.status = new_status
            ticket.save()
            messages.success(request, f"Le statut du ticket #{ticket.id} a été mis à jour.")
    
    return redirect('manager_dashboard')
