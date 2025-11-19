# 🚀 Guide de Démarrage Rapide

Ce guide vous permet de démarrer rapidement avec BSR Agriculture.

## 📋 Prérequis

- **Odoo 15.0** installé et fonctionnel
- **PostgreSQL** 12+ configuré
- **Python 3.8+** avec pip
- Accès administrateur à votre instance Odoo

## ⚡ Installation en 5 minutes

### 1. 📥 Cloner le Repository
```bash
git clone https://github.com/Brahim820/odoo_agricole.git
cd odoo_agricole
```

### 2. 📁 Copier les Modules
```bash
# Linux/Mac
cp -r * /path/to/odoo/addons/

# Windows
xcopy /E /I * "C:\Program Files\Odoo 15.0\server\addons\"
```

### 3. 🔄 Redémarrer Odoo
```bash
# Arrêter Odoo
sudo systemctl stop odoo

# Redémarrer avec mise à jour des modules
sudo systemctl start odoo
```

### 4. 📦 Installation des Modules (Ordre Important)

Connectez-vous à votre interface Odoo et installez dans cet ordre :

1. ✅ **bsr_agri_base** (module fondation)
2. ✅ **bsr_agri_soil_indicator** (analyses de sol)
3. ✅ **bsr_agri_irrigation** (systèmes irrigation)
4. ✅ **bsr_agri_pepinaire** (pépinières)
5. ✅ **bsr_agri_operation** (opérations terrain)
6. ✅ **bsr_agri_rh** (ressources humaines)
7. ✅ **bsr_agri_production** (orchestrateur)

## 🎯 Premier Projet Agricole

### Étape 1 : Créer une Ferme
1. **Navigation** : `Agriculture > Configuration > Fermes`
2. **Nouveau** : Cliquer "Créer"
3. **Informations** :
   - Nom : "Ma Ferme BSR"
   - Adresse complète
   - Contact responsable

### Étape 2 : Définir les Parcelles
1. **Navigation** : `Agriculture > Configuration > Parcelles`
2. **Créer** une parcelle :
   - Nom : "Parcelle Nord"
   - Superficie : 10 hectares
   - Type de sol : Argileux

### Étape 3 : Configurer les Cultures
1. **Navigation** : `Agriculture > Configuration > Types de Culture`
2. **Ajouter** : Blé, Maïs, Tomate, etc.

### Étape 4 : Lancer une Campagne de Production
1. **Navigation** : `Agriculture > Production > Campagnes`
2. **Nouvelle campagne** :
   - Nom : "Campagne Blé 2025"
   - Ferme : Ma Ferme BSR
   - Culture : Blé
   - Superficie : 5 hectares

## 🎨 Interface Utilisateur

### 🏠 Menu Principal
- **Agriculture** : Point d'entrée principal
- **Production** : Campagnes et cycles
- **Configuration** : Paramètres de base
- **Rapports** : Analyses et exports

### 📊 Tableaux de Bord
- **Vue Ferme** : État global des fermes
- **Production** : Suivi en temps réel
- **Irrigation** : Monitoring des systèmes
- **Analyses** : Indicateurs de sol

## ⚙️ Configuration de Base

### 🔒 Groupes d'Utilisateurs
```
Production Manager    → Accès total
Farm Supervisor      → Gestion de sa ferme
Field Operator       → Saisie terrain uniquement
Analyst             → Consultation rapports
```

### 📧 Notifications
- Alertes irrigation automatiques
- Rappels opérations culturales
- Notifications de récolte

## 🔧 Personnalisation Rapide

### Séquences
Modifiez les séquences dans `Configuration > Séquences` :
- Campagnes : CAMP-2025-001
- Parcelles : PARC-001
- Analyses : ANA-2025-001

### Données Maître
Ajoutez vos propres :
- Types de culture spécifiques
- Variétés locales
- Équipements de la ferme

## 🚨 Dépannage Express

### ❌ Module ne s'installe pas
```bash
# Vérifier les dépendances
python odoo-bin -d database --check
```

### ❌ Erreur de permission
```bash
# Vérifier les groupes utilisateur
Paramètres > Utilisateurs et Sociétés > Groupes
```

### ❌ Données manquantes
```bash
# Réinitialiser les données de démonstration
Paramètres > Base de données > Réinitialiser données démo
```

## 📞 Support Rapide

- **Issues GitHub** : [Créer une issue](https://github.com/Brahim820/odoo_agricole/issues/new)
- **Email** , brahim820@gmail.com
- **Documentation** : [Wiki complet](Home)

---

✅ **En 15 minutes, vous devriez avoir un système agricole fonctionnel !** 

👉 **Prochaine étape** : [Guide Utilisateur](User-Guide) pour découvrir toutes les fonctionnalités.