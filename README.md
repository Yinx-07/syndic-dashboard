# 🇲🇦 SyndicMaroc - Prototype Local (Étape 1)

**SyndicMaroc** est une application web Django de gestion de copropriété adaptée aux normes et usages au Maroc (Interface en Français, devises en MAD / Dirham Marocain).

---

## 🚀 Fonctionnalités Réalisées (Étape 1)

1. **Initialisation de l'Application** :
   - Structure Django 6.0 / Python 3.12 avec base de données **SQLite**.
   - Modèle utilisateur personnalisé avec gestion des rôles : `MANAGER` (Syndic / Gestionnaire) et `RESIDENT` (Copropriétaire / Résident).
   - Architecture pour les immeubles, appartements, tantièmes et soldes d'ouverture en **MAD**.

2. **Système de Sécurité & Droits d'Accès Sécurisés sur le Serveur** :
   - **Isolation Gestionnaire (Syndic)** : Un syndic accède **exclusivement** aux immeubles qu'il gère directement.
   - **Isolation Copropriétaire (Résident)** : Un copropriétaire accède **uniquement** aux données de ses propres appartements.
   - Contrôle strict côté serveur (`@manager_required`, `@resident_required`, filtrage des QuerySets) avec gestion des tentatives d'accès non autorisées (Page 403 personnalisée).

3. **Tableaux de Bord Dédiés** :
   - **Tableau de Bord Syndic** (`/manager/dashboard/`) : Métriques globales (Immeubles gérés, appartements, solde d'ouverture global en MAD, demandes de maintenance), liste des résidences et suivi des tickets avec mise à jour du statut.
   - **Tableau de Bord Résident** (`/resident/dashboard/`) : Fiche appartement, solde d'ouverture personnel en MAD, formulaire de signalement de maintenance et annonces partagées de l'immeuble.

4. **Comptes & Données de Démonstration Fictives** :
   - Commande automatique de seeding `python manage.py seed_demo_data` créant deux résidences (*Résidence Anfa Palms* à Casablanca et *Résidence Majorelle* à Marrakech), des appartements, des soldes d'ouverture et des tickets de démonstration.

---

## 🔑 Comptes de Démonstration (Déjà Configurés)

Tous les comptes ont pour mot de passe par défaut : `password123` *(sauf admin)*.

| Rôle | Nom d'utilisateur | Nom Complet | Périmètre / Périmètre visible |
| :--- | :--- | :--- | :--- |
| **Syndic 1** | `syndic.alami` | Mehdi Alami | *Résidence Anfa Palms* (Casablanca) |
| **Syndic 2** | `syndic.bennani` | Sarah Bennani | *Résidence Majorelle* (Marrakech) |
| **Résident 1** | `habitant.idrissi` | Youssef Idrissi | Appt 101 (*Anfa Palms*, Casa) - Solde: +1,500.00 MAD |
| **Résident 2** | `habitant.tazi` | Fatima-Zohra Tazi | Appt 102 (*Anfa Palms*, Casa) - Solde: -450.00 MAD |
| **Résident 3** | `habitant.chraibi` | Omar Chraibi | Appt 201 (*Majorelle*, MKE) - Solde: +800.00 MAD |
| **Admin** | `admin` | Administrateur | Tous les accès (Mot de passe: `admin123`) |

---

## 🛠️ Instructions pour Lancer l'Application Localement

### 1. Cloner / Se placer dans le répertoire du projet
```bash
cd d:\syndic
```

### 2. Effectuer les migrations de base de données
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Charger les données de démonstration
```bash
python manage.py seed_demo_data
```

### 4. Démarrer le serveur de développement Django
```bash
python manage.py runserver
```

### 5. Accéder à l'application
Ouvrez votre navigateur sur : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📌 Architecture des Fichiers Clés

- [models.py](file:///d:/syndic/core/models.py) : Modèles `User`, `Building`, `Apartment`, `MaintenanceTicket`.
- [permissions.py](file:///d:/syndic/core/permissions.py) : Mixins, décorateurs et fonctions de scoping pour l'isolation stricte des données.
- [views.py](file:///d:/syndic/core/views.py) : Vues `manager_dashboard`, `resident_dashboard`, `building_detail`, `create_maintenance_ticket`, `update_ticket_status`.
- [seed_demo_data.py](file:///d:/syndic/core/management/commands/seed_demo_data.py) : Commande de géneration du jeu de données de test.
- [templates/](file:///d:/syndic/templates/) : Modèles HTML Bootstrap 5 en Français avec devises en MAD.
