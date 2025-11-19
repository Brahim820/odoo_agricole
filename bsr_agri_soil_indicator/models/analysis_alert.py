# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class AnalysisAlert(models.Model):
    """Alertes générées par les analyses"""
    _name = 'bsr.analysis.alert'
    _description = 'Alerte d\'analyse'
    _order = 'priority desc, create_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Nom', compute='_compute_name', store=True)
    
    # Analyse source
    soil_analysis_id = fields.Many2one('bsr.soil.analysis', 'Analyse de sol', ondelete='cascade')
    culture_analysis_id = fields.Many2one('bsr.culture.analysis', 'Analyse de culture', ondelete='cascade')
    parameter_id = fields.Many2one('bsr.analysis.parameter', 'Paramètre', required=True)
    
    # Détails de l'alerte
    alert_type = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('critical', 'Critique'),
    ], string='Type d\'alerte', required=True, default='warning', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('urgent', 'Urgent'),
    ], string='Priorité', compute='_compute_priority', store=True, tracking=True)
    
    message = fields.Text('Message', required=True)
    value = fields.Char('Valeur mesurée')
    threshold_exceeded = fields.Boolean('Seuil dépassé', store=True)
    
    # Statut
    state = fields.Selection([
        ('new', 'Nouvelle'),
        ('acknowledged', 'Prise en compte'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolue'),
        ('dismissed', 'Ignorée'),
    ], string='Statut', default='new', tracking=True)
    
    # Actions
    recommended_action = fields.Text('Action recommandée')
    action_taken = fields.Text('Action réalisée')
    resolution_notes = fields.Text('Notes de résolution')
    
    # Assignation
    assigned_to_id = fields.Many2one('res.users', 'Assigné à')
    acknowledged_by_id = fields.Many2one('res.users', 'Pris en compte par')
    acknowledged_date = fields.Datetime('Date de prise en compte')
    resolved_by_id = fields.Many2one('res.users', 'Résolu par')
    resolved_date = fields.Datetime('Date de résolution')
    
    # Délais
    deadline = fields.Datetime('Échéance')
    is_overdue = fields.Boolean('En retard', compute='_compute_is_overdue', store=True)
    
    # Localisation (héritée de l'analyse)
    farm_id = fields.Many2one('bsr.farm', 'Ferme', compute='_compute_location_fields', store=True)
    parcel_id = fields.Many2one('bsr.parcel', 'Parcelle', compute='_compute_location_fields', store=True)
    culture_id = fields.Many2one('bsr.culture', 'Culture', compute='_compute_location_fields', store=True)
    
    # Métadonnées
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)

    @api.depends('parameter_id', 'soil_analysis_id', 'culture_analysis_id')
    def _compute_name(self):
        for record in self:
            param_name = record.parameter_id.name if record.parameter_id else ''
            
            if record.soil_analysis_id:
                analysis_ref = record.soil_analysis_id.name
                location = record.soil_analysis_id.parcel_id.name if record.soil_analysis_id.parcel_id else ''
            elif record.culture_analysis_id:
                analysis_ref = record.culture_analysis_id.name
                location = record.culture_analysis_id.culture_id.name if record.culture_analysis_id.culture_id else ''
            else:
                analysis_ref = ''
                location = ''
            
            record.name = f"{param_name} - {location} ({analysis_ref})"

    @api.depends('alert_type')
    def _compute_priority(self):
        for record in self:
            if record.alert_type == 'critical':
                record.priority = 'urgent'
            elif record.alert_type == 'warning':
                record.priority = 'high'
            else:
                record.priority = 'medium'

    @api.depends('deadline')
    def _compute_is_overdue(self):
        now = datetime.now()
        for record in self:
            record.is_overdue = (record.deadline and record.deadline < now and 
                               record.state not in ['resolved', 'dismissed'])

    @api.depends('soil_analysis_id', 'culture_analysis_id')
    def _compute_location_fields(self):
        for record in self:
            if record.soil_analysis_id:
                record.farm_id = record.soil_analysis_id.farm_id
                record.parcel_id = record.soil_analysis_id.parcel_id
                record.culture_id = record.soil_analysis_id.culture_id
            elif record.culture_analysis_id:
                record.farm_id = record.culture_analysis_id.farm_id
                record.parcel_id = record.culture_analysis_id.parcel_id
                record.culture_id = record.culture_analysis_id.culture_id
            else:
                record.farm_id = False
                record.parcel_id = False
                record.culture_id = False

    def action_acknowledge(self):
        """Prendre en compte l'alerte"""
        self.write({
            'state': 'acknowledged',
            'acknowledged_by_id': self.env.user.id,
            'acknowledged_date': datetime.now(),
        })

    def action_start_resolution(self):
        """Commencer la résolution"""
        self.write({
            'state': 'in_progress',
            'assigned_to_id': self.env.user.id,
        })

    def action_resolve(self):
        """Marquer comme résolue"""
        self.write({
            'state': 'resolved',
            'resolved_by_id': self.env.user.id,
            'resolved_date': datetime.now(),
        })

    def action_dismiss(self):
        """Ignorer l'alerte"""
        self.state = 'dismissed'

    def action_view_analysis(self):
        """Voir l'analyse source"""
        if self.soil_analysis_id:
            return {
                'name': 'Analyse de sol',
                'type': 'ir.actions.act_window',
                'res_model': 'bsr.soil.analysis',
                'res_id': self.soil_analysis_id.id,
                'view_mode': 'form',
            }
        elif self.culture_analysis_id:
            return {
                'name': 'Analyse de culture',
                'type': 'ir.actions.act_window',
                'res_model': 'bsr.culture.analysis',
                'res_id': self.culture_analysis_id.id,
                'view_mode': 'form',
            }

    @api.model
    def create(self, vals):
        """Auto-assign based on alert type and location"""
        alert = super().create(vals)
        
        # Auto-assignment logic could be added here
        # For example, assign critical alerts to farm manager
        if alert.alert_type == 'critical' and alert.farm_id:
            # Could look for farm manager or responsible user
            pass
            
        return alert