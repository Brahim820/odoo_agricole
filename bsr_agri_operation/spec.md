# Spécification Module BSR Agri Operation

## 📋 Vue d'ensemble

**Nom du module :** `bsr_agri_operation`  
**Version :** 15.0.1.0.0  
**Catégorie :** Agriculture  
**Dépendances :** `bsr_agri_base`, `mail`, `hr`, `maintenance`, `fleet`, `stock`

## 🎯 Objectif

Le module `bsr_agri_operation` étend le module `bsr_agri_base` pour fournir une gestion détaillée des opérations agricoles. Il permet de planifier, suivre et analyser toutes les activités liées aux campagnes de culture.

## 🔗 Lien avec BSR Agri Base

Ce module s'appuie sur l'infrastructure fournie par `bsr_agri_base` :
- **Fermes** : Contexte géographique des opérations
- **Parcelles** : Localisation précise des interventions
- **Cultures** : Type de production concerné
- **Campagnes de Culture** : Cycles de production auxquels sont rattachées les opérations
- **Types de Culture** : Configuration des phases et cycles

## 📦 Modèles principaux

### 1. Opération de Culture (`bsr.culture.operation`)
Modèle central pour la gestion des interventions agricoles.

**Champs principaux :**
- `name` : Nom de l'opération
- `campaign_id` : Lien vers la campagne de culture
- `operation_type` : Type d'intervention (plantation, irrigation, etc.)
- `planned_date` : Date prévue
- `actual_date` : Date réelle d'exécution
- `state` : État (planifiée, en cours, terminée, annulée)
- `duration` : Durée en heures
- `description` : Description détaillée

**Relations :**
- Campagne de culture (Many2one vers `bsr.culture.campaign`)
- Équipements utilisés (Many2many vers `maintenance.equipment`)
- Véhicules (Many2many vers `fleet.vehicle`)
- Employés (Many2many vers `hr.employee`)
- Consommables (Many2many vers produits ou consommables spécialisés)

### 2. Phase de Culture (`bsr.culture.phase`)
Gestion des phases dans le cycle de vie des cultures.

**Phases standard :**
- Préparation du sol
- Plantation/Semis
- Croissance
- Floraison
- Fructification
- Récolte
- Post-récolte
- Dormance (pour les cultures pérennes)

### 3. Modèle d'Opération (`bsr.operation.template`)
Templates d'opérations réutilisables selon le type de culture.

**Fonctionnalités :**
- Templates par type de culture
- Séquencement automatique des opérations
- Paramètres configurables (durée, ressources, etc.)

## 🔧 Fonctionnalités

### Planning et Planification
- **Calendrier des opérations** : Vue calendrier avec filtres par type, parcelle, culture
- **Planification automatique** : Génération d'opérations basée sur des modèles
- **Gestion des conflits** : Détection des conflits de ressources (équipements, personnel)
- **Prévisions météo** : Intégration possible avec services météo pour planification

### Suivi et Traçabilité
- **Suivi en temps réel** : État d'avancement des opérations
- **Géolocalisation** : Enregistrement GPS des interventions
- **Photos et documentation** : Pièces jointes par opération
- **Traçabilité complète** : Historique des interventions par parcelle

### Gestion des Ressources
- **Allocation des équipements** : Réservation et suivi d'utilisation
- **Planning du personnel** : Attribution des tâches aux employés
- **Consommation de produits** : Suivi des intrants utilisés
- **Coûts d'intervention** : Calcul automatique des coûts par opération

### Analyses et Reporting
- **Tableaux de bord** : KPIs opérationnels et financiers
- **Analyses de performance** : Comparaison prévu/réalisé
- **Rapports de productivité** : Efficacité par équipe, équipement, parcelle
- **Historiques** : Archivage et recherche dans l'historique

## 🎨 Interface Utilisateur

### Vues principales
1. **Vue Calendrier** : Planning hebdomadaire/mensuel des opérations
2. **Vue Kanban** : Suivi par état d'avancement
3. **Vue Liste** : Table détaillée avec filtres avancés
4. **Vue Formulaire** : Saisie/modification détaillée
5. **Vue Gantt** : Planification projet avec dépendances

### Tableaux de bord
- Dashboard opérationnel avec KPIs temps réel
- Analyses graphiques (courbes, histogrammes)
- Alertes et notifications automatiques

## 📱 Fonctionnalités Mobiles

### Application Mobile (optionnelle)
- **Saisie terrain** : Enregistrement direct depuis les parcelles
- **Mode hors-ligne** : Synchronisation ultérieure
- **Scanner codes** : Lecture QR codes équipements/parcelles
- **Photos géolocalisées** : Documentation automatique

## 🔐 Sécurité et Droits

### Groupes de sécurité
- **Opérateur agricole** : Saisie des interventions terrain
- **Superviseur** : Validation et planification
- **Gestionnaire** : Administration complète du module
- **Administrateur** : Configuration système

### Règles d'accès
- Restriction par ferme/parcelle selon l'affectation
- Visibilité limitée selon le rôle
- Audit trail complet des modifications

## 🔌 Intégrations

### Modules Odoo
- **HR** : Gestion du personnel et planning
- **Maintenance** : Équipements et maintenance préventive
- **Fleet** : Véhicules et carburant
- **Stock** : Gestion des intrants et consommables
- **Purchase** : Achat de produits phytosanitaires
- **Accounting** : Comptabilité analytique par culture

### APIs externes (futures)
- Services météorologiques
- Systèmes IoT (capteurs, drones)
- Applications de géolocalisation
- Plateformes de vente en ligne

## 📊 KPIs et Métriques

### Indicateurs opérationnels
- Taux de réalisation des opérations planifiées
- Respect des délais d'intervention
- Utilisation des équipements
- Productivité du personnel

### Indicateurs financiers
- Coût par hectare et par culture
- Rentabilité par campagne
- Écarts budgétaires
- ROI des investissements équipements

### Indicateurs qualité
- Respect des protocoles
- Taux de réussite des cultures
- Traçabilité documentaire
- Conformité réglementaire

## 🚀 Roadmap de développement

### Phase 1 - Core (v1.0)
- [ ] Modèles de base (opérations, phases)
- [ ] Vues principales (liste, form, calendrier)
- [ ] Workflow de base (planifié → en cours → terminé)
- [ ] Intégration avec bsr_agri_base

### Phase 2 - Avancé (v1.1)
- [ ] Templates d'opérations
- [ ] Planification automatique
- [ ] Gestion des conflits de ressources
- [ ] Tableaux de bord

### Phase 3 - Optimisation (v1.2)
- [ ] Vue Gantt
- [ ] Analyses avancées
- [ ] Optimisation mobile
- [ ] APIs externes

### Phase 4 - Intelligence (v2.0)
- [ ] IA pour recommandations
- [ ] Prédictions basées sur l'historique
- [ ] Optimisation automatique des plannings
- [ ] Intégration IoT

## 📝 Notes techniques

### Architecture
- Modularité : Chaque fonctionnalité dans des fichiers séparés
- Extensibilité : Hooks pour modules complémentaires
- Performance : Optimisation requêtes et caching
- Tests : Couverture complète avec tests unitaires

### Standards
- PEP 8 pour le code Python
- Guidelines Odoo pour la structure
- Documentation inline complète
- Logs détaillés pour debugging

---

*Document créé le 18 novembre 2025*  
*Version : 1.0*  
*Auteur : BSR Agriculture Team*