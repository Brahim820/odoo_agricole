# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AnalysisType(models.Model):
    """Types d'analyses (Sol, Culture, etc.)"""
    _name = 'bsr.analysis.type'
    _description = 'Types d\'analyse'
    _order = 'sequence, name'

    name = fields.Char('Nom', required=True, translate=True)
    code = fields.Char('Code', required=True, size=10)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Séquence', default=10)
    active = fields.Boolean('Actif', default=True)
    
    # Classification
    category = fields.Selection([
        ('soil', 'Analyse de Sol'),
        ('culture', 'Analyse de Culture'),
        ('water', 'Analyse d\'Eau'),
        ('harvest', 'Analyse de Récolte'),
        ('pest', 'Analyse Parasitaire'),
    ], string='Catégorie', required=True)
    
    analysis_class = fields.Selection([
        ('physical', 'Physique'),
        ('chemical', 'Chimique'),
        ('biological', 'Biologique'),
        ('nutritional', 'Nutritionnel'),
        ('environmental', 'Environnemental'),
    ], string='Classe d\'analyse', required=True)
    
    # Configuration
    parameter_ids = fields.One2many('bsr.analysis.parameter', 'analysis_type_id', 'Paramètres')
    parameter_count = fields.Integer('Nombre de paramètres', compute='_compute_parameter_count')
    
    # Fréquence recommandée
    recommended_frequency = fields.Selection([
        ('weekly', 'Hebdomadaire'),
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('biannual', 'Semestriel'),
        ('annual', 'Annuel'),
        ('biennial', 'Bisannuel'),
        ('on_demand', 'À la demande'),
    ], string='Fréquence recommandée', default='quarterly')
    
    # Coûts et durée
    estimated_cost = fields.Float('Coût estimé', digits=(10, 2))
    currency_id = fields.Many2one('res.currency', string='Devise',
                                 default=lambda self: self.env.company.currency_id)
    estimated_duration_days = fields.Integer('Durée estimée (jours)')
    
    # Métadonnées
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)
    color = fields.Integer('Couleur', default=0)

    @api.depends('parameter_ids')
    def _compute_parameter_count(self):
        for record in self:
            record.parameter_count = len(record.parameter_ids)
    
    def action_view_parameters(self):
        """Action pour voir les paramètres de ce type d'analyse"""
        return {
            'name': f'Paramètres - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.analysis.parameter',
            'view_mode': 'tree,form',
            'domain': [('analysis_type_id', '=', self.id)],
            'context': {'default_analysis_type_id': self.id},
        }

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Le code du type d\'analyse doit être unique!'),
    ]