# BSR Gestion Pépinière Agricole

## Description

Module Odoo complet pour la gestion de pépinière agricole, développé pour optimiser la production, le suivi des ressources, la traçabilité, la gestion financière et l'organisation du travail.

## Fonctionnalités principales

### 1. Gestion des cultures et plants
- Base de données des espèces et variétés
- Suivi du cycle de vie des plants (semis, germination, repiquage, croissance)
- Planification des interventions culturales
- Traçabilité complète des lots

### 2. Gestion des stocks
- Gestion des intrants (semences, substrats, pots, engrais, produits phytosanitaires)
- Alertes de seuils minimums
- Suivi des mouvements d'entrée/sortie
- Historique complet

### 3. Traçabilité et contrôle qualité
- Traçabilité des lots de plants
- Historique des interventions
- Suivi des traitements
- Calcul automatique des taux de germination

### 4. Gestion commerciale
- Gestion des clients
- Devis et commandes
- Facturation intégrée avec le module comptabilité
- Bons de livraison
- Suivi des paiements

### 5. Gestion des ressources humaines
- Planning des interventions par employé
- Traçabilité des tâches
- Calcul des coûts de main d'œuvre

### 6. Suivi financier
- Suivi des coûts par lot
- Calcul automatique du coût unitaire
- Analyse des marges
- Rapports financiers

## Installation

1. Copier le module dans le dossier addons d'Odoo
2. Mettre à jour la liste des applications
3. Installer le module "BSR Gestion Pépinière Agricole"

## Configuration

### Étape 1 : Configuration de base
1. Aller dans Pépinière > Configuration > Serres
2. Créer vos serres et emplacements

### Étape 2 : Catalogue
1. Créer les espèces (Pépinière > Catalogue > Espèces)
2. Créer les variétés pour chaque espèce

### Étape 3 : Stock
1. Créer les intrants (Pépinière > Stock > Intrants)
2. Enregistrer les stocks initiaux

### Étape 4 : Production
1. Créer des lots de plants (Pépinière > Production > Lots de plants)
2. Planifier les interventions

## Utilisation

### Créer un nouveau lot de plants
1. Aller dans Pépinière > Production > Lots de plants
2. Cliquer sur "Créer"
3. Renseigner l'espèce, la variété, la date de semis et la quantité
4. Suivre l'évolution du lot avec les boutons d'état

### Enregistrer une intervention
1. Depuis un lot, cliquer sur "Interventions"
2. Créer une nouvelle intervention
3. Renseigner le type, l'employé, les produits utilisés et les coûts

### Créer une vente
1. Aller dans Pépinière > Ventes
2. Créer une nouvelle vente
3. Sélectionner le client et ajouter les lignes de vente
4. Confirmer, livrer et facturer

## Rapports disponibles

- Fiche de lot de plants
- Bon de commande
- Fiche d'intervention

## Dépendances

- base
- stock
- sale_management
- purchase
- account
- hr
- product

## Support

Pour toute question ou assistance, contactez BSR.

## Licence

LGPL-3

## Auteur

BSR - https://www.bsr.ma

## Version

15.0.1.0.0
