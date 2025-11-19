# BSR Agriculture - Modules Odoo 15
# ===============================

Ce repository contient l'écosystème complet des modules BSR Agriculture pour Odoo 15.

## 🌾 Modules Inclus

### 🏗️ **bsr_agri_base**
- **Description** : Module de base pour l'écosystème agricole BSR
- **Fonctionnalités** : Fermes, parcelles, cultures, types de culture
- **Statut** : ✅ Stable

### 💧 **bsr_agri_irrigation** 
- **Description** : Gestion complète des systèmes d'irrigation
- **Fonctionnalités** : Systèmes, zones, programmes, sessions, alertes
- **Statut** : ✅ Stable + Rapports QWeb

### 🌱 **bsr_agri_pepinaire**
- **Description** : Gestion des pépinières et plants
- **Fonctionnalités** : Production de plants, semis, transplantation
- **Statut** : ✅ Stable

### 📊 **bsr_agri_production**
- **Description** : Gestion de la production agricole
- **Fonctionnalités** : Campagnes, cycles, planification, suivi récoltes
- **Statut** : ✅ Phase 1 Complète (Fondations)

### 🔧 **bsr_agri_operation**
- **Description** : Gestion des opérations culturales
- **Fonctionnalités** : Activités terrain, traitements, interventions
- **Statut** : ✅ Stable

### 👥 **bsr_agri_rh**
- **Description** : Ressources humaines agricoles
- **Fonctionnalités** : Personnel agricole, planning, compétences
- **Statut** : ✅ Stable

### 🧪 **bsr_agri_soil_indicator**
- **Description** : Analyses et indicateurs de sol
- **Fonctionnalités** : Analyses physico-chimiques, recommandations
- **Statut** : ✅ Stable

## 🚀 Installation

### Prérequis
- Odoo 15.0
- PostgreSQL
- Python 3.8+

### Installation des Modules
```bash
# 1. Cloner le repository
git clone https://github.com/Brahim820/odoo_agricole.git

# 2. Copier les modules dans addons
cp -r odoo_agricole/* /path/to/odoo/addons/

# 3. Installer les modules (ordre recommandé)
python odoo-bin -d database_name -i bsr_agri_base
python odoo-bin -d database_name -i bsr_agri_soil_indicator
python odoo-bin -d database_name -i bsr_agri_irrigation
python odoo-bin -d database_name -i bsr_agri_pepinaire
python odoo-bin -d database_name -i bsr_agri_operation
python odoo-bin -d database_name -i bsr_agri_rh
python odoo-bin -d database_name -i bsr_agri_production
```

## 📋 Dépendances

```
bsr_agri_base (base)
    ├── bsr_agri_soil_indicator
    ├── bsr_agri_irrigation
    ├── bsr_agri_pepinaire
    ├── bsr_agri_operation
    ├── bsr_agri_rh
    └── bsr_agri_production (orchestre tout)
```

## 🔄 Workflow de Développement

### Phase 1 ✅ : Fondations
- [x] bsr_agri_base : Modèles de base
- [x] Tous modules : Fonctionnalités core
- [x] bsr_agri_production : Campagnes et cycles

### Phase 2 🚧 : Planification Avancée
- [ ] Calendriers culturaux automatisés
- [ ] Optimisation planning multi-contraintes
- [ ] Intégrations IoT et capteurs

### Phase 3 📊 : Analytics & BI
- [ ] Tableaux de bord avancés
- [ ] Prédictions ML rendements
- [ ] Analyses de rentabilité

## 🛡️ Sécurité

### Groupes d'Utilisateurs
- **Production Manager** : Accès complet
- **Farm Supervisor** : Gestion de sa ferme
- **Field Operator** : Saisie terrain
- **Analyst** : Consultation rapports

## 📈 Fonctionnalités Clés

### 🎯 Gestion de Production
- Planification campagnes agricoles
- Suivi cycles de production (10 phases)
- Gestion des récoltes
- Analyses de performance

### 💧 Irrigation Intelligente
- Systèmes et zones d'irrigation
- Programmes automatisés
- Sessions avec consommation
- Alertes temps réel

### 🧪 Analyses de Sol
- Analyses physico-chimiques
- Recommandations automatiques
- Historique et tendances
- Intégration planning

### 👥 Ressources Humaines
- Personnel spécialisé agricole
- Planning des équipes
- Compétences et formations
- Suivi performance

## 📊 Rapports et Analyses

- Rapports de production PDF
- Analyses de rentabilité
- Tableaux de bord interactifs
- Exports Excel/CSV

## 🔧 Configuration

### Variables d'Environnement
```python
# Configuration optionnelle dans odoo.conf
[options]
addons_path = /path/to/addons,/path/to/bsr_modules
```

## 📞 Support

- **Développeur** : BSR Agriculture Team
- **Email** : support@bsr-agriculture.com
- **Documentation** : [Wiki GitHub](https://github.com/Brahim820/odoo_agricole/wiki)

## 📝 Changelog

### v1.0.0 (2025-11-19)
- ✅ Release initiale écosystème complet
- ✅ 7 modules intégrés
- ✅ Système de sécurité robuste
- ✅ Rapports QWeb intégrés

---

**🌾 BSR Agriculture - Digitalisation de l'agriculture** 🌾