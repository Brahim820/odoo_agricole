# Guide de mise à jour du module BSR Gestion Pépinière Agricole

## Migration vers la version 15.0.1.0.0

Cette version remplace le module de vente personnalisé (`pepiniere.vente`) par une intégration avec le module de vente standard d'Odoo (`sale.order`).

### Option 1 : Mise à jour automatique (Recommandé)

Le script de migration automatique supprimera les anciens modèles et leurs données.

**⚠️ ATTENTION : Cette opération supprimera toutes les ventes existantes du module pépinière !**

1. **Sauvegardez votre base de données** avant de procéder
2. Mettez à jour le module via l'interface Odoo
3. Le script de migration s'exécutera automatiquement

### Option 2 : Désinstallation/Réinstallation (Si la migration échoue)

Si la mise à jour automatique échoue :

1. **Sauvegardez votre base de données**
2. Désinstallez le module "BSR Gestion Pépinière Agricole"
3. Redémarrez le serveur Odoo
4. Réinstallez le module

**Note :** Cette méthode supprimera toutes les données du module (espèces, variétés, lots, interventions, etc.)

### Option 3 : Migration manuelle des données

Si vous souhaitez conserver vos données de vente :

1. **Avant la mise à jour**, exportez vos ventes depuis le menu Pépinière > Ventes
2. Suivez l'Option 1 ou 2
3. Recréez les ventes dans le nouveau système via Pépinière > Ventes (qui utilise maintenant sale.order)

### Nouvelles fonctionnalités après migration

- Intégration complète avec le module de vente Odoo
- Accès à toutes les fonctionnalités de vente (remises, taxes, conditions de paiement)
- Workflow complet : Devis → Commande → Livraison → Facture
- Intégration native avec la comptabilité
- Rapports de vente standard d'Odoo

### Support

Pour toute question, contactez BSR.
