from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Building, Apartment, MaintenanceTicket, MonthlyPayment, Expense, BuildingAnnouncement
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = "Populate database with demo users, buildings, apartments, monthly payments, expenses, and maintenance tickets."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Effacement et reinitialisation des donnees de demonstration..."))

        # Clear existing data
        BuildingAnnouncement.objects.all().delete()
        Expense.objects.all().delete()
        MonthlyPayment.objects.all().delete()
        MaintenanceTicket.objects.all().delete()
        Apartment.objects.all().delete()
        Building.objects.all().delete()
        User.objects.all().delete()

        # 1. Create Superuser / Administrator
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@syndicmaroc.ma',
            password='admin123',
            first_name='Administrateur',
            last_name='Plateforme',
            role=User.Role.MANAGER,
            phone='0600000000'
        )
        self.stdout.write(self.style.SUCCESS("[OK] Admin cree: admin / admin123"))

        # 2. Create Managers
        manager_1 = User.objects.create_user(
            username='syndic.alami',
            email='m.alami@syndicmaroc.ma',
            password='password123',
            first_name='Mehdi',
            last_name='Alami',
            role=User.Role.MANAGER,
            phone='0661122334',
            cin='AB123456'
        )
        
        manager_2 = User.objects.create_user(
            username='syndic.bennani',
            email='s.bennani@syndicmaroc.ma',
            password='password123',
            first_name='Sarah',
            last_name='Bennani',
            role=User.Role.MANAGER,
            phone='0662998877',
            cin='CD789012'
        )
        self.stdout.write(self.style.SUCCESS("[OK] Gestionnaires crees: syndic.alami, syndic.bennani"))

        # 3. Create Residents
        resident_1 = User.objects.create_user(
            username='habitant.idrissi',
            email='y.idrissi@gmail.com',
            password='password123',
            first_name='Youssef',
            last_name='Idrissi',
            role=User.Role.RESIDENT,
            phone='0663445566',
            cin='EF345678'
        )

        resident_2 = User.objects.create_user(
            username='habitant.tazi',
            email='fz.tazi@gmail.com',
            password='password123',
            first_name='Fatima-Zohra',
            last_name='Tazi',
            role=User.Role.RESIDENT,
            phone='0664778899',
            cin='GH901234'
        )

        resident_3 = User.objects.create_user(
            username='habitant.chraibi',
            email='o.chraibi@gmail.com',
            password='password123',
            first_name='Omar',
            last_name='Chraibi',
            role=User.Role.RESIDENT,
            phone='0665112233',
            cin='IJ567890'
        )
        self.stdout.write(self.style.SUCCESS("[OK] Coproprietaires crees: habitant.idrissi, habitant.tazi, habitant.chraibi"))

        # 4. Create Buildings
        b1 = Building.objects.create(
            name="Residence Anfa Palms",
            address="145 Boulevard d'Anfa",
            city="Casablanca",
            manager=manager_1,
            total_units=4
        )

        b2 = Building.objects.create(
            name="Residence Majorelle",
            address="88 Avenue Yacoub El Mansour",
            city="Marrakech",
            manager=manager_2,
            total_units=3
        )
        self.stdout.write(self.style.SUCCESS("[OK] Immeubles crees: Residence Anfa Palms (Casablanca), Residence Majorelle (Marrakech)"))

        # 5. Create Apartments
        appt_101 = Apartment.objects.create(
            building=b1,
            number="101",
            floor=1,
            tantiemes=120.00,
            opening_balance=1500.00,
            owner=resident_1
        )

        appt_102 = Apartment.objects.create(
            building=b1,
            number="102",
            floor=1,
            tantiemes=130.00,
            opening_balance=-450.00,
            owner=resident_2
        )

        appt_201 = Apartment.objects.create(
            building=b1,
            number="201",
            floor=2,
            tantiemes=150.00,
            opening_balance=0.00,
            owner=None
        )

        appt_202 = Apartment.objects.create(
            building=b1,
            number="202",
            floor=2,
            tantiemes=150.00,
            opening_balance=300.00,
            owner=None
        )

        appt_maj_201 = Apartment.objects.create(
            building=b2,
            number="201",
            floor=2,
            tantiemes=250.00,
            opening_balance=800.00,
            owner=resident_3
        )

        appt_maj_101 = Apartment.objects.create(
            building=b2,
            number="101",
            floor=1,
            tantiemes=200.00,
            opening_balance=-200.00,
            owner=None
        )
        self.stdout.write(self.style.SUCCESS("[OK] Appartements crees."))

        # 6. Create Monthly Payments Status for Current Month ("Septembre 2026") & Historical 2026
        # Current month Septembre 2026
        MonthlyPayment.objects.create(
            apartment=appt_101,
            month_name="Septembre 2026",
            amount=350.00,
            paid_amount=350.00,
            status=MonthlyPayment.PaymentStatus.PAID,
            payment_date=date(2026, 9, 5)
        )

        MonthlyPayment.objects.create(
            apartment=appt_102,
            month_name="Septembre 2026",
            amount=350.00,
            paid_amount=200.00,
            status=MonthlyPayment.PaymentStatus.PARTIAL,
            payment_date=date(2026, 9, 12)
        )

        MonthlyPayment.objects.create(
            apartment=appt_201,
            month_name="Septembre 2026",
            amount=350.00,
            paid_amount=350.00,
            status=MonthlyPayment.PaymentStatus.PAID,
            payment_date=date(2026, 9, 3)
        )

        MonthlyPayment.objects.create(
            apartment=appt_202,
            month_name="Septembre 2026",
            amount=350.00,
            paid_amount=0.00,
            status=MonthlyPayment.PaymentStatus.UNPAID
        )

        MonthlyPayment.objects.create(
            apartment=appt_maj_201,
            month_name="Septembre 2026",
            amount=500.00,
            paid_amount=500.00,
            status=MonthlyPayment.PaymentStatus.PAID,
            payment_date=date(2026, 9, 2)
        )

        MonthlyPayment.objects.create(
            apartment=appt_maj_101,
            month_name="Septembre 2026",
            amount=500.00,
            paid_amount=0.00,
            status=MonthlyPayment.PaymentStatus.UNPAID
        )

        # Historical payments for cashflow chart (Janvier -> Août 2026)
        months_history = [
            ("Janvier 2026", 1200.0, 1400.0),
            ("Février 2026", 1400.0, 1500.0),
            ("Mars 2026", 1050.0, 1000.0),
            ("Avril 2026", 1400.0, 1500.0),
            ("Mai 2026", 1050.0, 1500.0),
            ("Juin 2026", 1400.0, 1000.0),
            ("Juillet 2026", 1200.0, 1500.0),
            ("Août 2026", 1400.0, 1500.0),
        ]

        for idx, (m_name, amt_b1, amt_b2) in enumerate(months_history, 1):
            MonthlyPayment.objects.create(
                apartment=appt_101,
                month_name=m_name,
                amount=350.00,
                paid_amount=350.00,
                status=MonthlyPayment.PaymentStatus.PAID,
                payment_date=date(2026, idx, 5)
            )
            MonthlyPayment.objects.create(
                apartment=appt_maj_201,
                month_name=m_name,
                amount=500.00,
                paid_amount=500.00,
                status=MonthlyPayment.PaymentStatus.PAID,
                payment_date=date(2026, idx, 4)
            )

        self.stdout.write(self.style.SUCCESS("[OK] Statuts de cotisations mensuelles et historique 2026 crees."))

        # 7. Create Demo Expenses by Category in MAD
        Expense.objects.create(
            building=b1,
            title="Service de Gardiennage et Sécurité 24/7",
            category=Expense.Category.SECURITY,
            amount=4500.00,
            expense_date=date(2026, 9, 1)
        )
        Expense.objects.create(
            building=b1,
            title="Contrat Maintenance Ascenseurs Otis (T3 2026)",
            category=Expense.Category.ELEVATOR,
            amount=2200.00,
            expense_date=date(2026, 9, 5)
        )
        Expense.objects.create(
            building=b1,
            title="Facture Électricité & Éclairage des parties communes",
            category=Expense.Category.UTILITIES,
            amount=1800.00,
            expense_date=date(2026, 9, 10)
        )
        Expense.objects.create(
            building=b1,
            title="Produits et Prestation de Nettoyage des escaliers",
            category=Expense.Category.CLEANING,
            amount=1500.00,
            expense_date=date(2026, 9, 12)
        )

        Expense.objects.create(
            building=b2,
            title="Société de Sécurité et Gardiennage",
            category=Expense.Category.SECURITY,
            amount=3800.00,
            expense_date=date(2026, 9, 2)
        )
        Expense.objects.create(
            building=b2,
            title="Taille des palmiers & Entretien Espaces Verts",
            category=Expense.Category.GARDENING,
            amount=1200.00,
            expense_date=date(2026, 9, 8)
        )
        Expense.objects.create(
            building=b2,
            title="Facture Lydec Électricité du Hall",
            category=Expense.Category.UTILITIES,
            amount=1400.00,
            expense_date=date(2026, 9, 15)
        )
        self.stdout.write(self.style.SUCCESS("[OK] Depenses de demonstration crees en MAD."))

        # 8. Create Maintenance Tickets
        MaintenanceTicket.objects.create(
            building=b1,
            apartment=appt_101,
            resident=resident_1,
            title="Fuite d'eau dans la conduite principale de terrasse",
            description="Une infiltration d'eau est constatee au plafond du 1er etage pres des escaliers.",
            status=MaintenanceTicket.Status.PENDING
        )

        MaintenanceTicket.objects.create(
            building=b1,
            apartment=appt_102,
            resident=resident_2,
            title="Panne d'eclairage dans le hall principal",
            description="Le minuteur du hall d'entree ne s'allume plus la nuit.",
            status=MaintenanceTicket.Status.IN_PROGRESS
        )

        MaintenanceTicket.objects.create(
            building=b2,
            apartment=appt_maj_201,
            resident=resident_3,
            title="Reparation du portail automatique d'entree",
            description="Telecommande n'activait plus l'ouverture du garage. Telecommande remplacee.",
            status=MaintenanceTicket.Status.RESOLVED
        )

        # 9. Create Building Announcements
        BuildingAnnouncement.objects.create(
            building=b1,
            author=manager_1,
            title="Assemblée Générale Ordinaire de la Résidence",
            content="Chers copropriétaires, l'assemblée générale annuelle se tiendra le samedi 10 Octobre à 16h00 dans la salle de réunion."
        )

        self.stdout.write(self.style.SUCCESS("[OK] Annonces et Tickets de maintenance crees."))
        self.stdout.write(self.style.SUCCESS("=== Seeding termine avec succes ! ==="))
