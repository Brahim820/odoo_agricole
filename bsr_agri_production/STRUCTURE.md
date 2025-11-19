# BSR AGRI PRODUCTION - STRUCTURE DU MODULE
# ==========================================

## STRUCTURE DE FICHIERS PRÉVUE

```
bsr_agri_production/
│
├── __init__.py
├── __manifest__.py
│
├── models/
│   ├── __init__.py
│   ├── production_campaign.py      # Campagnes agricoles
│   ├── production_cycle.py         # Cycles de production
│   ├── production_activity.py      # Activités culturales
│   ├── production_task.py          # Tâches de production
│   ├── harvest_record.py           # Enregistrements récolte
│   ├── production_analysis.py      # Analyses performance
│   ├── cultural_calendar.py        # Calendrier cultural
│   └── production_forecast.py      # Prévisions production
│
├── views/
│   ├── production_campaign_views.xml
│   ├── production_cycle_views.xml
│   ├── production_activity_views.xml
│   ├── harvest_record_views.xml
│   ├── production_dashboard_views.xml
│   ├── cultural_calendar_views.xml
│   └── menus.xml
│
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
│
├── data/
│   ├── production_sequences.xml
│   ├── cultural_templates.xml
│   ├── activity_types.xml
│   └── production_data.xml
│
├── reports/
│   ├── production_reports.xml
│   ├── campaign_report.xml
│   ├── cycle_report.xml
│   ├── harvest_report.xml
│   └── performance_report.xml
│
├── wizards/
│   ├── __init__.py
│   ├── campaign_wizard.py          # Assistant création campagne
│   ├── harvest_wizard.py           # Assistant saisie récolte
│   └── analysis_wizard.py          # Assistant analyses
│
├── static/
│   ├── src/
│   │   ├── js/
│   │   │   ├── production_calendar.js
│   │   │   └── production_dashboard.js
│   │   └── css/
│   │       └── production_styles.css
│   └── description/
│       ├── icon.png
│       └── index.html
│
└── tests/
    ├── __init__.py
    ├── test_production_campaign.py
    ├── test_production_cycle.py
    └── test_harvest_record.py
```

## MODÈLES DÉTAILLÉS

### 1. PRODUCTION CAMPAIGN (Campagne)
```python
class ProductionCampaign(models.Model):
    _name = 'bsr.production.campaign'
    
    # Champs principaux
    name = fields.Char('Nom campagne')
    season = fields.Selection([...])
    start_date = fields.Date()
    end_date = fields.Date()
    farm_ids = fields.Many2many('bsr.farm')
    
    # Relations
    cycle_ids = fields.One2many('bsr.production.cycle')
    
    # Computed
    total_surface = fields.Float(compute='_compute_surface')
    expected_production = fields.Float()
```

### 2. PRODUCTION CYCLE (Cycle)
```python
class ProductionCycle(models.Model):
    _name = 'bsr.production.cycle'
    
    # Références
    campaign_id = fields.Many2one('bsr.production.campaign')
    parcel_id = fields.Many2one('bsr.parcel')
    culture_id = fields.Many2one('bsr.culture')
    
    # Dates importantes
    sowing_date = fields.Date()
    harvest_date_planned = fields.Date()
    harvest_date_actual = fields.Date()
    
    # États
    state = fields.Selection([
        ('planned', 'Planifié'),
        ('sowing', 'Semis'),
        ('growing', 'Croissance'),
        ('mature', 'Maturation'),
        ('harvest', 'Récolte'),
        ('completed', 'Terminé')
    ])
```

### 3. PRODUCTION ACTIVITY (Activité)
```python
class ProductionActivity(models.Model):
    _name = 'bsr.production.activity'
    
    # Référence cycle
    cycle_id = fields.Many2one('bsr.production.cycle')
    
    # Type activité
    activity_type = fields.Selection([
        ('preparation', 'Préparation sol'),
        ('sowing', 'Semis'),
        ('fertilization', 'Fertilisation'),
        ('treatment', 'Traitement'),
        ('irrigation', 'Irrigation'),
        ('harvest', 'Récolte')
    ])
    
    # Planning
    planned_date = fields.Datetime()
    actual_date = fields.Datetime()
    duration_planned = fields.Float()
    duration_actual = fields.Float()
    
    # Resources
    operator_ids = fields.Many2many('res.users')
    equipment_ids = fields.Many2many('maintenance.equipment')
```

## INTÉGRATIONS PRÉVUES

### AVEC BSR_AGRI_BASE
- Récupération fermes, parcelles, cultures
- Synchronisation données de base
- Hérite des structures géographiques

### AVEC BSR_AGRI_IRRIGATION
- Import sessions d'irrigation dans activités
- Synchronisation planning irrigation
- Données consommation eau

### AVEC BSR_AGRI_SOIL_INDICATOR
- Import recommandations fertilisation
- Prise en compte analyses sol
- Adaptation cycles selon indicateurs

## WORKFLOWS AUTOMATISÉS

### CRÉATION AUTOMATIQUE ACTIVITÉS
1. Sélection template cultural selon culture
2. Génération activités selon calendrier
3. Adaptation dates selon conditions météo
4. Assignment automatique ressources

### SUIVI AVANCEMENT
1. Mise à jour état cycle selon activités
2. Calcul pourcentage avancement
3. Alertes retards ou anomalies
4. Notifications équipes terrain

---
*Document vivant - À maintenir à jour*