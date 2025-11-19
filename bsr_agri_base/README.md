# BSR Agri Base

## Description

Application de gestion agricole complète pour la gestion des fermes, parcelles et cultures.

## Fonctionnalités

### Gestion des Fermes
- Création et gestion des fermes
- Informations de contact et localisation
- Calcul automatique des surfaces cultivées
- Vue d'ensemble des parcelles par ferme

### Gestion des Parcelles
- Création de parcelles au sein des fermes
- Informations techniques (surface, type de sol, pente, irrigation)
- Localisation GPS
- Suivi de l'état des parcelles

### Gestion des Cultures
- Planification et suivi des cultures
- Types de cultures prédéfinis (maraîchage, pépinière, arboriculture, etc.)
- Suivi des dates de plantation et de récolte
- Calcul de rentabilité
- États de culture avec workflow

## Types de Culture Inclus

### Maraîchage
- Tomate, Carotte, Laitue, Courgette, Aubergine, Poivron, Radis, Épinard

### Pépinière
- Plants de Tomate, Plants de Salade, Plants Aromatiques, Plants de Fleurs

### Arboriculture
- Olivier, Citronnier, Oranger, Amandier, Vigne

### Céréales
- Blé, Orge, Avoine, Maïs

### Légumineuses
- Lentille, Pois Chiche, Haricot, Fève

### Fourrage
- Luzerne, Ray-grass, Trèfle

### Autres
- Tournesol, Colza, Lavande

## Groupes de Sécurité

### Utilisateur Agriculture
- Consultation des fermes, parcelles et cultures

### Gestionnaire des Opérations
- Gestion des cultures et parcelles
- Consultation des fermes

### Responsable de Ferme
- Gestion complète des fermes, parcelles et cultures

### Administrateur Agriculture
- Tous les droits y compris configuration des types de culture

## Règles de Gestion

- Une ferme peut contenir plusieurs parcelles
- Une parcelle peut contenir une seule culture à la fois
- Workflow de culture avec états (planifiée → plantée → en croissance → prête → récoltée → terminée)

## Installation

1. Copier le module dans le dossier addons d'Odoo
2. Mettre à jour la liste des applications
3. Installer l'application "BSR Agri Base"