# MediTrack - Système de Suivi de Médicaments

##  Présentation

MediTrack est une application web développée avec Django qui permet aux utilisateurs de suivre leur prise de médicaments quotidienne. L'application offre une interface intuitive pour gérer les médicaments, planifier les doses et suivre l'adhérence au traitement médical.

##  Fonctionnalités

### Gestion des Médicaments
- Ajout, modification et suppression de médicaments
- Suivi des informations détaillées (nom, dosage, instructions, dates de début/fin)

### Suivi des Doses
- Tableau de bord quotidien organisé par période (Matin, Midi, Soir, Coucher)
- Enregistrement manuel du statut des doses (Prise, Manquée, Sautée)
- Marquage automatique des doses manquées

### Historique et Statistiques
- Historique complet des prises de médicaments avec filtrage
- Statistiques d'adhérence (pourcentage global, tendance hebdomadaire)

### Authentification et Sécurité
- Système complet d'inscription et de connexion
- Protection des données par utilisateur
- Interface d'administration pour les gestionnaires du système

### Interface Utilisateur
- Design professionnel avec thème vert utilisant Bootstrap
- Interface responsive adaptée aux mobiles et ordinateurs
- Messages de notification pour les actions importantes

## 🛠️ Architecture Technique

### Structure du Projet
meditrack_project/
├── meditrack/            # Configuration principale du projet
│   ├── settings.py       # Paramètres Django
│   ├── urls.py           # URLs principales
│   └── wsgi.py           # Configuration WSGI
├── tracker/              # Application principale
│   ├── models.py         # Modèles de données
│   ├── views.py          # Logique de l'application
│   ├── forms.py          # Formulaires
│   ├── urls.py           # URLs de l'application
│   ├── admin.py          # Configuration admin
│   ├── templates/        # Templates HTML
│   └── static/           # Fichiers statiques (CSS, JS)
├── manage.py             # Script de gestion Django
└── db.sqlite3            # Base de données SQLite

### Modèles de Données

#### Utilisateur
- Utilise le modèle User intégré de Django
- Gère l'authentification et les informations personnelles

#### Médicament (Medication)
- Lié à un utilisateur spécifique
- Stocke les informations sur le médicament (nom, dosage, instructions)
- Dates de début et de fin optionnelles

#### Dose
- Liée à un utilisateur et à un médicament
- Enregistre l'heure prévue et l'heure effective de prise
- Statut (En attente, Prise, Manquée, Sautée)
- Notes optionnelles

## 🔒 Installation pour le Développement

1. **Cloner le repository**
```bash
git clone https://github.com/your-username/meditrack.git
cd meditrack
```

2. **Créer et activer l'environnement virtuel**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
# Copier le fichier d'exemple
cp .env.example .env

# Éditer .env avec vos paramètres
# Voici les variables requises:
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True  # Mettre False en production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

5. **Appliquer les migrations**
```bash
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

## 🔒 Notes de Sécurité

1. **Variables d'Environnement**
   - Ne jamais commiter le fichier `.env`
   - Toujours utiliser des variables d'environnement pour les informations sensibles
   - Générer une nouvelle `SECRET_KEY` pour chaque installation

2. **Base de Données**
   - Le fichier `db.sqlite3` est ignoré par git
   - Faire des sauvegardes régulières en production
   - Ne jamais commiter de données sensibles

3. **Déploiement**
   - Toujours définir `DEBUG=False` en production
   - Configurer correctement `ALLOWED_HOSTS`
   - Utiliser HTTPS en production

## 🤝 Contribution

1. Fork le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request#   M e d i T r a c k  
 