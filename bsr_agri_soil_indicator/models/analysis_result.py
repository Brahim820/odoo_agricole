# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class AnalysisResult(models.Model):
    """Résultats détaillés pour chaque paramètre d'une analyse"""
    _name = 'bsr.analysis.result'
    _description = 'Résultat d\'analyse'
    _order = 'analysis_id, parameter_id'

    analysis_id = fields.Many2one('bsr.soil.analysis', 'Analyse', ondelete='cascade')
    culture_analysis_id = fields.Many2one('bsr.culture.analysis', 'Analyse Culture', ondelete='cascade')
    parameter_id = fields.Many2one('bsr.analysis.parameter', 'Paramètre', required=True)
    parameter_data_type = fields.Selection(related='parameter_id.data_type', readonly=True)
    
    # Valeurs
    value_float = fields.Float('Valeur numérique')
    value_integer = fields.Integer('Valeur entière')
    value_boolean = fields.Boolean('Valeur booléenne')
    value_text = fields.Text('Valeur texte')
    value_selection = fields.Char('Valeur sélection')
    
    # Valeur formatée pour affichage
    display_value = fields.Char('Valeur affichée', compute='_compute_display_value', store=True)
    
    # Statut par rapport aux seuils
    status = fields.Selection([
        ('normal', 'Normal'),
        ('warning', 'Attention'),
        ('critical', 'Critique'),
        ('optimal', 'Optimal'),
    ], string='Statut', compute='_compute_status', store=True)
    
    # Métadonnées
    notes = fields.Text('Notes')
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)

    @api.depends('parameter_id', 'value_float', 'value_integer', 'value_boolean', 
                 'value_text', 'value_selection')
    def _compute_display_value(self):
        for record in self:
            param = record.parameter_id
            if not param:
                record.display_value = ''
                continue
                
            if param.data_type == 'float':
                value = record.value_float
            elif param.data_type == 'integer':
                value = record.value_integer
            elif param.data_type == 'boolean':
                value = record.value_boolean
            elif param.data_type == 'text':
                value = record.value_text
            elif param.data_type == 'selection':
                value = record.value_selection
            elif param.data_type == 'percentage':
                value = record.value_float
            else:
                value = None
                
            record.display_value = param.format_value(value) if value is not None else ''

    @api.depends('parameter_id', 'value_float', 'value_integer')
    def _compute_status(self):
        for record in self:
            param = record.parameter_id
            if not param:
                record.status = 'normal'
                continue
                
            # Obtenir la valeur numérique
            if param.data_type in ['float', 'percentage']:
                value = record.value_float
            elif param.data_type == 'integer':
                value = record.value_integer
            else:
                record.status = 'normal'
                continue
                
            if value is None:
                record.status = 'normal'
                continue
                
            # Déterminer le statut
            if param.critical_min and value < param.critical_min:
                record.status = 'critical'
            elif param.critical_max and value > param.critical_max:
                record.status = 'critical'
            elif param.optimal_min and param.optimal_max:
                if param.optimal_min <= value <= param.optimal_max:
                    record.status = 'optimal'
                else:
                    record.status = 'warning'
            elif param.min_value and value < param.min_value:
                record.status = 'warning'
            elif param.max_value and value > param.max_value:
                record.status = 'warning'
            else:
                record.status = 'normal'

    def set_value(self, value):
        """Set value according to parameter data type"""
        param = self.parameter_id
        if not param:
            return
            
        if param.data_type == 'float' or param.data_type == 'percentage':
            self.value_float = float(value) if value is not None else 0.0
        elif param.data_type == 'integer':
            self.value_integer = int(value) if value is not None else 0
        elif param.data_type == 'boolean':
            self.value_boolean = bool(value)
        elif param.data_type == 'text':
            self.value_text = str(value) if value is not None else ''
        elif param.data_type == 'selection':
            self.value_selection = str(value) if value is not None else ''

    def get_value(self):
        """Get value according to parameter data type"""
        param = self.parameter_id
        if not param:
            return None
            
        if param.data_type == 'float' or param.data_type == 'percentage':
            return self.value_float
        elif param.data_type == 'integer':
            return self.value_integer
        elif param.data_type == 'boolean':
            return self.value_boolean
        elif param.data_type == 'text':
            return self.value_text
        elif param.data_type == 'selection':
            return self.value_selection
        return None