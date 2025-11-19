# 🏗️ Architecture des Modules BSR Agriculture

## 🌐 Vue d'Ensemble de l'Écosystème

L'écosystème BSR Agriculture est conçu comme une architecture modulaire où chaque module a une responsabilité spécifique tout en s'intégrant parfaitement avec les autres.

## 📊 Diagramme des Dépendances

```
                    🌾 bsr_agri_production
                           (Orchestrateur)
                               |
                    ┌─────────┼─────────┐
                    │         │         │
            🏗️ bsr_agri_base   💧 bsr_agri_irrigation
                    │
        ┌───────────┼───────────┬───────────┐
        │           │           │           │
   🌱 pepinaire  🔧 operation  👥 rh   🧪 soil_indicator
```

## 📦 Modules Détaillés

### 🏗️ bsr_agri_base (Module Fondation)

**Rôle** : Module central fournissant les modèles de base

**Modèles Principaux** :
```python
bsr.farm                    # Fermes agricoles
bsr.parcel                  # Parcelles de terrain  
bsr.culture                 # Cultures agricoles
bsr.culture.type            # Types de culture
bsr.culture.campaign        # Campagnes culturales
```

**Relations Clés** :
- Une `Ferme` contient plusieurs `Parcelles`
- Une `Parcelle` peut avoir plusieurs `Cultures`
- Une `Culture` appartient à un `Type de Culture`

**Sécurité** :
- Gestion multi-fermes
- Isolation des données par ferme
- 4 niveaux d'accès utilisateur

### 💧 bsr_agri_irrigation (Systèmes Irrigation)

**Rôle** : Gestion complète de l'irrigation intelligente

**Modèles Principaux** :
```python
bsr.irrigation.system       # Systèmes d'irrigation
bsr.irrigation.zone         # Zones d'irrigation  
bsr.irrigation.program      # Programmes d'arrosage
bsr.irrigation.session      # Sessions d'irrigation
bsr.irrigation.alert        # Alertes et monitoring
```

**Fonctionnalités Avancées** :
- Calculs automatiques de consommation
- Alertes en temps réel
- Rapports QWeb PDF intégrés
- Historique détaillé

**Intégrations** :
- Lien avec `bsr.parcel` (zones par parcelle)
- Consommables via `product.product`

### 🌱 bsr_agri_pepiniere (Pépinières)

**Rôle** : Production et gestion des plants

**Modèles Principaux** :
```python
bsr.espece                  # Espèces végétales
bsr.variete                 # Variétés par espèce
bsr.lot.plant              # Lots de plants
bsr.intervention           # Interventions pépinière
bsr.stock.intrant          # Intrants et fournitures
```

**Workflow de Production** :
1. **Semis** → Création lot de graines
2. **Germination** → Suivi croissance
3. **Repiquage** → Transplantation
4. **Vente/Transfer** → Expédition plants

### 🔧 bsr_agri_operation (Opérations Terrain)

**Rôle** : Gestion des activités culturales

**Modèles Principaux** :
```python
bsr.culture.operation       # Opérations culturales
bsr.operation.product.line  # Produits utilisés
```

**Types d'Opérations** :
- Préparation du sol
- Plantation/Semis
- Traitements phytosanitaires
- Fertilisation
- Irrigation
- Récolte

**Traçabilité** :
- Produits utilisés (quantités)
- Coûts des opérations
- Personnel impliqué
- Dates et durées

### 👥 bsr_agri_rh (Ressources Humaines)

**Rôle** : Gestion du personnel agricole

**Modèles Principaux** :
```python
bsr.agri.skill             # Compétences agricoles
bsr.agri.team              # Équipes de travail
bsr.team.assignment        # Affectations terrain
```

**Compétences Métier** :
- Conduite tracteur
- Traitement phytosanitaire
- Irrigation
- Récolte manuelle/mécanique

### 🧪 bsr_agri_soil_indicator (Analyses Sol)

**Rôle** : Monitoring qualité des sols

**Modèles Principaux** :
```python
bsr.soil.analysis          # Analyses de sol
bsr.analysis.type          # Types d'analyses
bsr.analysis.parameter     # Paramètres analysés
bsr.analysis.result        # Résultats d'analyse
bsr.analysis.alert         # Alertes qualité
```

**Analyses Supportées** :
- pH, conductivité électrique
- NPK (Azote, Phosphore, Potassium)
- Matière organique
- Oligo-éléments

### 🌾 bsr_agri_production (Orchestrateur)

**Rôle** : Chef d'orchestre de l'écosystème

**Modèles Principaux** :
```python
bsr.production.campaign     # Campagnes de production
bsr.production.cycle        # Cycles culturaux
```

**Workflow 10 Phases** :
1. **Planification** → Définition objectifs
2. **Préparation Sol** → Travaux préparatoires
3. **Semis/Plantation** → Mise en place culture
4. **Croissance** → Suivi développement
5. **Entretien** → Opérations culturales
6. **Protection** → Traitements
7. **Irrigation** → Gestion hydrique
8. **Maturation** → Phase finale
9. **Récolte** → Collecte production
10. **Post-Récolte** → Stockage/Commercialisation

## 🔗 Architecture des Données

### Relations Inter-Modules

```sql
-- Exemple de relations croisées
bsr_production_campaign.farm_id → bsr_farm.id
bsr_production_cycle.parcel_id → bsr_parcel.id
bsr_irrigation_zone.parcel_id → bsr_parcel.id
bsr_culture_operation.culture_id → bsr_culture.id
```

### Héritage et Extensions

```python
# Exemple d'héritage
class ProductionCycle(models.Model):
    _name = 'bsr.production.cycle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Relations avec autres modules
    parcel_id = fields.Many2one('bsr.parcel')
    irrigation_program_ids = fields.One2many('bsr.irrigation.program')
    soil_analysis_ids = fields.One2many('bsr.soil.analysis')
```

## 🛡️ Architecture de Sécurité

### Modèle de Sécurité Transversal

```xml
<!-- Exemple de règle de domaine -->
<record id="production_campaign_rule" model="ir.rule">
    <field name="domain_force">
        [('farm_id.partner_id.user_ids', 'in', [user.id])]
    </field>
</record>
```

### Groupes Hérités

```
group_agriculture_manager      # Accès total écosystème
├── group_agriculture_user     # Accès standard
│   ├── group_farm_supervisor  # Gestion ferme
│   └── group_field_operator   # Saisie terrain
└── group_agriculture_analyst  # Lecture seule + rapports
```

## ⚡ Performance et Optimisations

### Index Base de Données

```sql
-- Index critiques pour performance
CREATE INDEX idx_production_cycle_parcel ON bsr_production_cycle(parcel_id);
CREATE INDEX idx_irrigation_session_date ON bsr_irrigation_session(session_date);
CREATE INDEX idx_soil_analysis_parcel_date ON bsr_soil_analysis(parcel_id, analysis_date);
```

### Caching et Computed Fields

```python
# Champs calculés optimisés avec store=True
total_surface = fields.Float(
    compute='_compute_total_surface',
    store=True  # Mise en cache en BDD
)
```

## 🔄 Patterns d'Intégration

### Event-Driven Architecture

```python
@api.model_create_multi
def create(self, vals_list):
    records = super().create(vals_list)
    # Déclenche événements dans autres modules
    records._trigger_irrigation_planning()
    records._update_soil_analysis_schedule()
    return records
```

### Service Layer Pattern

```python
class ProductionService(models.AbstractModel):
    _name = 'bsr.production.service'
    
    def create_full_campaign(self, vals):
        """Service orchestrateur création campagne complète"""
        # Coordination entre modules
        pass
```

## 📈 Évolutivité

### Plugin Architecture

```python
# Interface pour extensions futures
class IrrigationProvider(models.AbstractModel):
    _name = 'bsr.irrigation.provider'
    
    def calculate_water_need(self):
        raise NotImplementedError()
```

### API Hooks

```python
# Points d'extension pour modules tiers
def _get_production_phases(self):
    phases = super()._get_production_phases()
    # Permet extension par modules externes
    return self._extend_phases(phases)
```

---

Cette architecture modulaire garantit **maintenabilité**, **scalabilité** et **extensibilité** de l'écosystème BSR Agriculture.