# Guide de Développement - Module BSR Agri Operation

## 📋 Plan de Développement

Ce document détaille les étapes pratiques pour créer le module `bsr_agri_operation` qui étend `bsr_agri_base`.

## 🏗️ Structure du Module

```
bsr_agri_operation/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── culture_operation.py
│   ├── culture_phase.py
│   ├── operation_template.py
│   └── operation_analytics.py
├── views/
│   ├── culture_operation_views.xml
│   ├── culture_phase_views.xml
│   ├── operation_template_views.xml
│   ├── operation_dashboard_views.xml
│   └── menu_views.xml
├── data/
│   ├── operation_types_data.xml
│   ├── phase_templates_data.xml
│   └── ir_cron_data.xml
├── security/
│   ├── security.xml
│   └── ir.model.access.csv
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       ├── css/
│       └── js/
├── wizard/
│   ├── __init__.py
│   ├── mass_operation_wizard.py
│   └── operation_report_wizard.py
└── reports/
    ├── __init__.py
    ├── operation_report.py
    └── templates/
        └── operation_report_template.xml
```

## 🔧 Étape 1 : Fichiers de Base

### __manifest__.py
```python
{
    'name': 'BSR Agri Operation',
    'version': '15.0.1.0.0',
    'category': 'Agriculture',
    'summary': 'Gestion des opérations agricoles',
    'description': '''
Module de gestion des opérations agricoles
=========================================

Fonctionnalités :
* Planification des opérations de culture
* Suivi des interventions en temps réel
* Gestion des ressources (personnel, équipements)
* Analyses et reporting
    ''',
    'author': 'BSR Agriculture',
    'website': 'https://www.bsr.com',
    'depends': [
        'bsr_agri_base',
        'mail',
        'hr',
        'maintenance', 
        'fleet',
        'stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/operation_types_data.xml',
        'data/phase_templates_data.xml',
        'data/ir_cron_data.xml',
        'views/culture_operation_views.xml',
        'views/culture_phase_views.xml',
        'views/operation_template_views.xml',
        'views/operation_dashboard_views.xml',
        'views/menu_views.xml',
        'wizard/mass_operation_wizard_views.xml',
        'wizard/operation_report_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
```

## 📊 Étape 2 : Modèles Principaux

### models/culture_operation.py - Structure de base
```python
# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class CultureOperation(models.Model):
    _name = 'bsr.culture.operation'
    _description = 'Opération de Culture'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'planned_date, priority desc, name'

    # Identification
    name = fields.Char('Nom de l\'opération', required=True, tracking=True)
    sequence = fields.Char('Séquence', default='/')
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Importante'),
        ('2', 'Urgente'),
    ], string='Priorité', default='0')

    # Relations principales
    campaign_id = fields.Many2one(
        'bsr.culture.campaign', 
        string='Campagne',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    culture_id = fields.Many2one(
        related='campaign_id.culture_id',
        string='Culture',
        store=True,
        readonly=True
    )
    farm_id = fields.Many2one(
        related='culture_id.farm_id',
        string='Ferme',
        store=True,
        readonly=True
    )
    parcel_id = fields.Many2one(
        related='culture_id.parcel_id',
        string='Parcelle',
        store=True,
        readonly=True
    )

    # Type et catégorisation
    operation_type = fields.Selection([
        ('soil_preparation', 'Préparation du sol'),
        ('planting', 'Plantation/Semis'),
        ('irrigation', 'Irrigation'),
        ('fertilization', 'Fertilisation'),
        ('pest_control', 'Traitement phytosanitaire'),
        ('pruning', 'Taille'),
        ('weeding', 'Désherbage'),
        ('harvest', 'Récolte'),
        ('post_harvest', 'Post-récolte'),
        ('maintenance', 'Maintenance'),
        ('monitoring', 'Surveillance'),
        ('other', 'Autre'),
    ], string='Type d\'opération', required=True, tracking=True)

    # Planification temporelle
    planned_date = fields.Datetime('Date et heure prévues', required=True, tracking=True)
    planned_duration = fields.Float('Durée prévue (heures)', digits=(8, 2))
    deadline = fields.Datetime('Date limite')
    
    # Réalisation
    actual_start = fields.Datetime('Début effectif', tracking=True)
    actual_end = fields.Datetime('Fin effective', tracking=True)
    actual_duration = fields.Float('Durée réelle (heures)', compute='_compute_actual_duration', store=True)
    
    # État et workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifiée'),
        ('ready', 'Prête'),
        ('in_progress', 'En cours'),
        ('paused', 'En pause'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)

    # Ressources humaines
    responsible_id = fields.Many2one('hr.employee', string='Responsable')
    employee_ids = fields.Many2many('hr.employee', string='Équipe')
    external_contractor = fields.Char('Prestataire externe')

    # Équipements et matériel
    equipment_ids = fields.Many2many('maintenance.equipment', string='Équipements')
    vehicle_ids = fields.Many2many('fleet.vehicle', string='Véhicules')
    tool_ids = fields.Many2many('product.product', string='Outils et matériel')

    # Produits et consommables
    product_line_ids = fields.One2many('bsr.operation.product.line', 'operation_id', string='Produits utilisés')
    
    # Localisation et surface
    work_area = fields.Float('Surface travaillée (ha)', digits=(10, 4))
    gps_coordinates = fields.Char('Coordonnées GPS')
    weather_conditions = fields.Text('Conditions météorologiques')

    # Coûts et finances
    estimated_cost = fields.Float('Coût estimé', digits='Product Price')
    actual_cost = fields.Float('Coût réel', compute='_compute_actual_cost', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Qualité et résultats
    quality_rating = fields.Selection([
        ('1', 'Très mauvais'),
        ('2', 'Mauvais'), 
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent'),
    ], string='Évaluation qualité')
    
    yield_quantity = fields.Float('Quantité produite', digits=(10, 2))
    yield_unit = fields.Many2one('uom.uom', string='Unité de mesure')
    
    # Documentation
    description = fields.Html('Description')
    internal_notes = fields.Text('Notes internes')
    client_notes = fields.Text('Notes client')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')

    # Méta-données
    active = fields.Boolean('Actif', default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Champs calculés et techniques
    delay_days = fields.Integer('Retard (jours)', compute='_compute_delays')
    is_delayed = fields.Boolean('En retard', compute='_compute_delays')
    completion_rate = fields.Float('Taux de completion (%)', compute='_compute_completion_rate')

    @api.depends('actual_start', 'actual_end')
    def _compute_actual_duration(self):
        for operation in self:
            if operation.actual_start and operation.actual_end:
                delta = operation.actual_end - operation.actual_start
                operation.actual_duration = delta.total_seconds() / 3600.0
            else:
                operation.actual_duration = 0.0

    @api.depends('product_line_ids', 'employee_ids', 'equipment_ids')
    def _compute_actual_cost(self):
        for operation in self:
            total_cost = 0.0
            
            # Coût des produits
            for line in operation.product_line_ids:
                total_cost += line.total_cost
                
            # Coût de la main d'œuvre (si configuré)
            if operation.actual_duration and operation.employee_ids:
                # Calcul basé sur le coût horaire des employés
                pass
                
            # Coût des équipements (amortissement)
            # TODO: Implémenter le calcul
            
            operation.actual_cost = total_cost

    def action_plan(self):
        """Passer à l'état planifié"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Seules les opérations en brouillon peuvent être planifiées.'))
        self.state = 'planned'

    def action_start(self):
        """Démarrer l'opération"""
        self.ensure_one()
        if self.state not in ['planned', 'ready']:
            raise ValidationError(_('L\'opération doit être planifiée pour être démarrée.'))
        self.state = 'in_progress'
        if not self.actual_start:
            self.actual_start = fields.Datetime.now()

    def action_complete(self):
        """Terminer l'opération"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_('L\'opération doit être en cours pour être terminée.'))
        self.state = 'completed'
        if not self.actual_end:
            self.actual_end = fields.Datetime.now()

    @api.model
    def create(self, vals):
        if vals.get('sequence', '/') == '/':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('bsr.culture.operation') or '/'
        return super().create(vals)
```

### models/operation_product_line.py
```python
class OperationProductLine(models.Model):
    _name = 'bsr.operation.product.line'
    _description = 'Ligne de produit d\'opération'

    operation_id = fields.Many2one('bsr.culture.operation', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produit', required=True)
    quantity = fields.Float('Quantité', required=True, digits='Product Unit of Measure')
    uom_id = fields.Many2one('uom.uom', string='Unité de mesure', required=True)
    unit_cost = fields.Float('Coût unitaire', digits='Product Price')
    total_cost = fields.Float('Coût total', compute='_compute_total_cost', store=True)
    
    application_rate = fields.Float('Taux d\'application', help="Quantité par hectare")
    application_method = fields.Selection([
        ('spray', 'Pulvérisation'),
        ('granules', 'Granulés'),
        ('injection', 'Injection'),
        ('manual', 'Application manuelle'),
    ], string='Mode d\'application')

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.unit_cost
```

## 📅 Étape 3 : Vues et Interface

### views/culture_operation_views.xml - Vues principales
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <!-- Vue Calendar -->
    <record id="view_culture_operation_calendar" model="ir.ui.view">
        <field name="name">bsr.culture.operation.calendar</field>
        <field name="model">bsr.culture.operation</field>
        <field name="arch" type="xml">
            <calendar string="Calendrier des Opérations" 
                      date_start="planned_date"
                      date_stop="planned_date" 
                      color="operation_type"
                      mode="month"
                      quick_add="True">
                <field name="name"/>
                <field name="operation_type"/>
                <field name="state"/>
                <field name="responsible_id"/>
                <field name="campaign_id"/>
            </calendar>
        </field>
    </record>

    <!-- Vue Kanban -->
    <record id="view_culture_operation_kanban" model="ir.ui.view">
        <field name="name">bsr.culture.operation.kanban</field>
        <field name="model">bsr.culture.operation</field>
        <field name="arch" type="xml">
            <kanban default_group_by="state" class="o_kanban_small_column">
                <field name="name"/>
                <field name="operation_type"/>
                <field name="planned_date"/>
                <field name="state"/>
                <field name="priority"/>
                <field name="responsible_id"/>
                <templates>
                    <t t-name="kanban-box">
                        <div class="oe_kanban_card">
                            <div class="oe_kanban_content">
                                <div><strong><field name="name"/></strong></div>
                                <div class="text-muted">
                                    <field name="operation_type"/>
                                </div>
                                <div class="oe_kanban_bottom_right">
                                    <img t-att-src="kanban_image('hr.employee', 'avatar_128', record.responsible_id.raw_value)"
                                         t-att-title="record.responsible_id.value"
                                         width="24" height="24" class="oe_kanban_avatar"/>
                                </div>
                                <div class="oe_kanban_bottom_left">
                                    <field name="planned_date" widget="date"/>
                                </div>
                            </div>
                        </div>
                    </t>
                </templates>
            </kanban>
        </field>
    </record>

    <!-- Actions -->
    <record id="action_culture_operation" model="ir.actions.act_window">
        <field name="name">Opérations de Culture</field>
        <field name="res_model">bsr.culture.operation</field>
        <field name="view_mode">kanban,calendar,tree,form</field>
        <field name="context">{}</field>
        <field name="help" type="html">
            <p class="o_view_nocontent_smiling_face">
                Créer votre première opération de culture
            </p>
        </field>
    </record>

</odoo>
```

## 🔐 Étape 4 : Sécurité

### security/security.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    
    <!-- Groupes de sécurité pour les opérations -->
    <record id="group_agriculture_operator" model="res.groups">
        <field name="name">Agriculture: Opérateur</field>
        <field name="category_id" ref="bsr_agri_base.module_category_agriculture"/>
        <field name="comment">Saisie des opérations de terrain</field>
    </record>
    
    <record id="group_agriculture_supervisor" model="res.groups">
        <field name="name">Agriculture: Superviseur Opérations</field>
        <field name="category_id" ref="bsr_agri_base.module_category_agriculture"/>
        <field name="implied_ids" eval="[(4, ref('group_agriculture_operator'))]"/>
        <field name="comment">Planification et supervision des opérations</field>
    </record>

</odoo>
```

## 📊 Étape 5 : Données et Configuration

### data/operation_types_data.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        
        <!-- Séquence pour les opérations -->
        <record id="seq_culture_operation" model="ir.sequence">
            <field name="name">Opération de Culture</field>
            <field name="code">bsr.culture.operation</field>
            <field name="prefix">OP</field>
            <field name="padding">6</field>
            <field name="company_id" eval="False"/>
        </record>

    </data>
</odoo>
```

## 🎯 Étapes de Développement Recommandées

### Phase 1 - Core (2-3 semaines)
1. **Semaine 1**
   - [ ] Structure de base du module
   - [ ] Modèle `CultureOperation` principal
   - [ ] Vues de base (form, tree)
   - [ ] Sécurité de base

2. **Semaine 2**
   - [ ] Workflow des états
   - [ ] Relations avec `bsr_agri_base`
   - [ ] Vue calendrier
   - [ ] Tests de base

3. **Semaine 3**
   - [ ] Modèle `OperationProductLine`
   - [ ] Calculs de coûts
   - [ ] Vue kanban
   - [ ] Documentation

### Phase 2 - Avancé (3-4 semaines)
4. **Semaine 4-5**
   - [ ] Modèle `CulturePhase`
   - [ ] Templates d'opérations
   - [ ] Planification automatique
   - [ ] Amélioration des vues

5. **Semaine 6-7**
   - [ ] Analyses et reporting
   - [ ] Tableaux de bord
   - [ ] Optimisation des performances
   - [ ] Tests d'intégration

## 🧪 Tests et Validation

### Tests unitaires à créer
```python
# tests/test_culture_operation.py
from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError

class TestCultureOperation(TransactionCase):
    
    def setUp(self):
        super().setUp()
        # Setup des données de test
        
    def test_operation_workflow(self):
        # Test des transitions d'état
        pass
        
    def test_cost_calculation(self):
        # Test des calculs de coûts
        pass
```

## 📈 Métriques de Succès

### Critères d'acceptation
- [ ] Intégration parfaite avec `bsr_agri_base`
- [ ] Performance : < 2s pour charger 1000 opérations
- [ ] Couverture de tests : > 85%
- [ ] Documentation complète
- [ ] Interface utilisateur intuitive
- [ ] Conformité aux standards Odoo

---

*Document de développement créé le 18 novembre 2025*  
*Version : 1.0*  
*Auteur : Équipe de développement BSR*