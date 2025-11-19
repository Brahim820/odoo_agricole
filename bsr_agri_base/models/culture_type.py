# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CultureType(models.Model):
    _name = 'bsr.culture.type'
    _description = 'Type de Culture'
    _order = 'name'

    name = fields.Char('Nom du type de culture', required=True)
    code = fields.Char('Code', required=True)
    description = fields.Text('Description')
    category = fields.Selection([
        ('maraichage', 'Maraîchage'),
        ('pepiniere', 'Pépinière'),
        ('arboriculture', 'Arboriculture'),
        ('cereales', 'Céréales'),
        ('legumineuses', 'Légumineuses'),
        ('fourrage', 'Fourrage'),
        ('autres', 'Autres'),
    ], string='Catégorie', required=True, default='maraichage')
    
    # Gestion des cycles
    is_cyclical = fields.Boolean('Culture cyclique', default=False, 
                                 help="Cochez si cette culture a des cycles répétitifs (ex: arboriculture)")
    cycle_type = fields.Selection([
        ('annual', 'Annuel'),
        ('biannual', 'Bi-annuel'), 
        ('seasonal', 'Saisonnier'),
        ('perennial', 'Pérenne'),
    ], string='Type de cycle', help="Fréquence des cycles pour cette culture")
    cycle_duration_months = fields.Integer('Durée du cycle (mois)', default=12,
                                         help="Durée moyenne d'un cycle en mois")
    harvest_frequency = fields.Selection([
        ('once', 'Une fois par cycle'),
        ('multiple', 'Plusieurs fois par cycle'),
        ('continuous', 'Continue'),
    ], string='Fréquence de récolte', default='once')
    
    # Phases du cycle
    has_planting_phase = fields.Boolean('Phase de plantation', default=True)
    has_growing_phase = fields.Boolean('Phase de croissance', default=True) 
    has_flowering_phase = fields.Boolean('Phase de floraison', default=False)
    has_fruiting_phase = fields.Boolean('Phase de fructification', default=False)
    has_harvest_phase = fields.Boolean('Phase de récolte', default=True)
    has_dormancy_phase = fields.Boolean('Phase de dormance', default=False)
    
    active = fields.Boolean('Actif', default=True)

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code du type de culture doit être unique.'),
    ]