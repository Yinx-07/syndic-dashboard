from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        MANAGER = 'MANAGER', 'Gestionnaire / Syndic'
        RESIDENT = 'RESIDENT', 'Copropriétaire / Résident'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT,
        verbose_name="Rôle"
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    cin = models.CharField(max_length=20, blank=True, verbose_name="N° CIN")

    @property
    def is_manager(self):
        return self.role == self.Role.MANAGER or self.is_superuser

    @property
    def is_resident(self):
        return self.role == self.Role.RESIDENT

    def __str__(self):
        full_name = self.get_full_name()
        name = full_name if full_name else self.username
        return f"{name} ({self.get_role_display()})"


class Building(models.Model):
    name = models.CharField(max_length=150, verbose_name="Nom de l'immeuble / Résidence")
    address = models.CharField(max_length=255, verbose_name="Adresse")
    city = models.CharField(max_length=100, default="Casablanca", verbose_name="Ville")
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_buildings",
        verbose_name="Syndic / Gestionnaire"
    )
    total_units = models.PositiveIntegerField(default=0, verbose_name="Nombre d'appartements")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Immeuble"
        verbose_name_plural = "Immeubles"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} - {self.city}"


class Apartment(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="apartments",
        verbose_name="Immeuble"
    )
    number = models.CharField(max_length=30, verbose_name="N° d'appartement")
    floor = models.IntegerField(default=0, verbose_name="Étage")
    tantiemes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=100.00,
        verbose_name="Tantièmes / Millièmes"
    )
    opening_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        verbose_name="Solde d'ouverture (MAD)"
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="apartments",
        verbose_name="Copropriétaire / Résident"
    )

    class Meta:
        verbose_name = "Appartement"
        verbose_name_plural = "Appartements"
        ordering = ['building', 'number']

    def __str__(self):
        return f"{self.building.name} - Appt {self.number}"


class MonthlyPayment(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = 'PAID', 'Payé'
        UNPAID = 'UNPAID', 'Non payé'
        PARTIAL = 'PARTIAL', 'Partiel'

    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name="monthly_payments",
        verbose_name="Appartement"
    )
    month_name = models.CharField(max_length=50, default="Septembre 2026", verbose_name="Mois / Période")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=350.00, verbose_name="Montant Total Cotisation (MAD)")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Montant Payé / Versé (MAD)")
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.UNPAID,
        verbose_name="Statut du paiement"
    )
    payment_date = models.DateField(null=True, blank=True, verbose_name="Date de paiement")
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def actual_paid_amount(self):
        if self.status == self.PaymentStatus.PAID:
            return self.amount
        elif self.status == self.PaymentStatus.PARTIAL:
            return self.paid_amount if self.paid_amount > 0 else (self.amount / 2)
        return 0.00

    @property
    def remaining_amount(self):
        if self.status == self.PaymentStatus.PAID:
            return 0.00
        elif self.status == self.PaymentStatus.PARTIAL:
            rem = self.amount - self.actual_paid_amount
            return rem if rem > 0 else 0.00
        return self.amount

    class Meta:
        verbose_name = "Cotisation Mensuelle"
        verbose_name_plural = "Cotisations Mensuelles"

    def __str__(self):
        return f"{self.apartment} - {self.month_name} : {self.get_status_display()}"


class Expense(models.Model):
    class Category(models.TextChoices):
        SECURITY = 'SECURITY', 'Gardiennage & Sécurité'
        CLEANING = 'CLEANING', 'Nettoyage & Propreté'
        UTILITIES = 'UTILITIES', 'Électricité & Eau commune'
        ELEVATOR = 'ELEVATOR', 'Maintenance Ascenseurs & Pompes'
        GARDENING = 'GARDENING', 'Espaces Verts & Jardinage'
        REPAIRS = 'REPAIRS', 'Travaux & Réparations'
        OTHER = 'OTHER', 'Autres charges divers'

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="expenses", verbose_name="Immeuble")
    title = models.CharField(max_length=200, verbose_name="Libellé / Titre de la dépense")
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.UTILITIES,
        verbose_name="Catégorie"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant (MAD)")
    expense_date = models.DateField(verbose_name="Date de la dépense")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dépense Immeuble"
        verbose_name_plural = "Dépenses Immeuble"
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.title} - {self.amount} MAD ({self.building.name})"


class BuildingAnnouncement(models.Model):
    building = models.ForeignKey(
        Building,
        on_delete=models.CASCADE,
        related_name="announcements",
        verbose_name="Immeuble"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Auteur / Syndic")
    title = models.CharField(max_length=200, verbose_name="Titre de l'annonce")
    content = models.TextField(verbose_name="Contenu de l'annonce")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de publication")

    class Meta:
        verbose_name = "Annonce Immeuble"
        verbose_name_plural = "Annonces Immeuble"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.building.name}"


class MaintenanceTicket(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        IN_PROGRESS = 'IN_PROGRESS', 'En cours de traitement'
        RESOLVED = 'RESOLVED', 'Résolu'
        REJECTED = 'REJECTED', 'Rejeté'

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="tickets")
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    resident = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submitted_tickets")
    title = models.CharField(max_length=200, verbose_name="Sujet / Titre")
    description = models.TextField(verbose_name="Description du problème")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Statut"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de signalement")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")

    class Meta:
        verbose_name = "Demande de maintenance"
        verbose_name_plural = "Demandes de maintenance"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} - {self.building.name}"
