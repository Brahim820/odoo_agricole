# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class SoilAnalysis(models.Model):
    """Analyses de sol"""
    _name = 'bsr.soil.analysis'
    _description = 'Analyse de Sol'
    _order = 'analysis_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    # Informations générales
    name = fields.Char('Référence', required=True, copy=False, readonly=True,
                      default=lambda self: self.env['ir.sequence'].next_by_code('bsr.soil.analysis'))
    display_name = fields.Char('Nom', compute='_compute_display_name', store=True)
    
    # Localisation
    farm_id = fields.Many2one('bsr.farm', 'Ferme', required=True, tracking=True)
    parcel_id = fields.Many2one('bsr.parcel', 'Parcelle', required=True, tracking=True,
                               domain="[('farm_id', '=', farm_id)]")
    culture_id = fields.Many2one('bsr.culture', 'Culture', tracking=True,
                                domain="[('parcel_id', '=', parcel_id)]")
    
    # Échantillonnage
    sampling_date = fields.Datetime('Date d\'échantillonnage', required=True, tracking=True,
                                   default=fields.Datetime.now)
    sampling_depth_from = fields.Float('Profondeur de (cm)', default=0)
    sampling_depth_to = fields.Float('Profondeur à (cm)', default=30)
    sampling_method = fields.Selection([
        ('grid', 'Échantillonnage en grille'),
        ('zigzag', 'Échantillonnage en zigzag'),
        ('composite', 'Échantillon composite'),
        ('targeted', 'Échantillonnage ciblé'),
        ('random', 'Échantillonnage aléatoire'),
    ], string='Méthode d\'échantillonnage', default='composite')
    
    sample_points = fields.Integer('Nombre de points de prélèvement', default=1)
    sample_weight = fields.Float('Poids échantillon (kg)')
    
    # Coordonnées GPS (optionnel)
    sampling_latitude = fields.Float('Latitude échantillonnage', digits=(16, 6))
    sampling_longitude = fields.Float('Longitude échantillonnage', digits=(16, 6))
    
    # Analyse
    analysis_type_id = fields.Many2one('bsr.analysis.type', 'Type d\'analyse', required=True,
                                      domain=[('category', '=', 'soil')], tracking=True)
    analysis_date = fields.Datetime('Date d\'analyse', required=True, tracking=True)
    laboratory_id = fields.Many2one('res.partner', 'Laboratoire',
                                   domain=[('is_company', '=', True)], tracking=True)
    laboratory_reference = fields.Char('Référence laboratoire')
    
    # Résultats
    result_ids = fields.One2many('bsr.analysis.result', 'analysis_id', 'Résultats')
    result_count = fields.Integer('Nombre de résultats', compute='_compute_result_count', store=True)
    
    # Statut global
    overall_status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('average', 'Moyen'),
        ('poor', 'Médiocre'),
        ('critical', 'Critique'),
    ], string='Statut global', compute='_compute_overall_status', store=True)
    
    # Workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sampled', 'Échantillonné'),
        ('analyzed', 'Analysé'),
        ('validated', 'Validé'),
        ('archived', 'Archivé'),
    ], string='Statut', default='draft', tracking=True)
    
    # Coûts
    analysis_cost = fields.Float('Coût d\'analyse', digits=(10, 2))
    currency_id = fields.Many2one('res.currency', string='Devise',
                                 default=lambda self: self.env.company.currency_id)
    
    # Recommandations
    recommendations = fields.Text('Recommandations')
    next_analysis_date = fields.Date('Prochaine analyse recommandée',
                                    compute='_compute_next_analysis_date', store=True)
    
    # Documents
    report_file = fields.Binary('Rapport d\'analyse')
    report_filename = fields.Char('Nom du fichier rapport')
    
    # Métadonnées
    technician_id = fields.Many2one('res.users', 'Technicien', default=lambda self: self.env.user)
    responsible_id = fields.Many2one('res.users', 'Responsable')
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)
    
    # Alertes générées
    alert_ids = fields.One2many('bsr.analysis.alert', 'soil_analysis_id', 'Alertes')
    alert_count = fields.Integer('Nombre d\'alertes', compute='_compute_alert_count', store=True)

    @api.depends('name', 'parcel_id', 'analysis_date')
    def _compute_display_name(self):
        for record in self:
            parcel_name = record.parcel_id.name if record.parcel_id else ''
            date_str = record.analysis_date.strftime('%d/%m/%Y') if record.analysis_date else ''
            record.display_name = f"{record.name} - {parcel_name} ({date_str})"

    @api.depends('result_ids')
    def _compute_result_count(self):
        for record in self:
            record.result_count = len(record.result_ids)

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        for record in self:
            record.alert_count = len(record.alert_ids)

    @api.depends('result_ids.status')
    def _compute_overall_status(self):
        for record in self:
            if not record.result_ids:
                record.overall_status = 'average'
                continue
                
            status_counts = {
                'critical': 0,
                'warning': 0,
                'normal': 0,
                'optimal': 0
            }
            
            for result in record.result_ids:
                status_counts[result.status] += 1
            
            total = len(record.result_ids)
            
            if status_counts['critical'] > 0:
                record.overall_status = 'critical'
            elif status_counts['warning'] > total * 0.3:
                record.overall_status = 'poor'
            elif status_counts['optimal'] > total * 0.7:
                record.overall_status = 'excellent'
            elif status_counts['optimal'] > total * 0.4:
                record.overall_status = 'good'
            else:
                record.overall_status = 'average'

    @api.depends('analysis_type_id', 'analysis_date')
    def _compute_next_analysis_date(self):
        for record in self:
            if not record.analysis_type_id or not record.analysis_date:
                record.next_analysis_date = False
                continue
                
            frequency_map = {
                'weekly': 7,
                'monthly': 30,
                'quarterly': 90,
                'biannual': 180,
                'annual': 365,
                'biennial': 730,
            }
            
            frequency = record.analysis_type_id.recommended_frequency
            if frequency in frequency_map:
                days = frequency_map[frequency]
                record.next_analysis_date = record.analysis_date.date() + timedelta(days=days)
            else:
                record.next_analysis_date = False

    @api.onchange('farm_id')
    def _onchange_farm_id(self):
        self.parcel_id = False
        self.culture_id = False

    @api.onchange('parcel_id')
    def _onchange_parcel_id(self):
        self.culture_id = False

    @api.onchange('analysis_type_id')
    def _onchange_analysis_type_id(self):
        if self.analysis_type_id:
            # Créer les résultats basés sur les paramètres du type d'analyse
            self.result_ids = [(5, 0, 0)]  # Clear existing
            results = []
            for param in self.analysis_type_id.parameter_ids:
                results.append((0, 0, {
                    'parameter_id': param.id,
                }))
            self.result_ids = results

    def action_sample(self):
        """Marquer comme échantillonné"""
        self.state = 'sampled'

    def action_analyze(self):
        """Marquer comme analysé"""
        self.state = 'analyzed'
        self._check_alerts()

    def action_validate(self):
        """Valider l'analyse"""
        self.state = 'validated'

    def action_archive(self):
        """Archiver l'analyse"""
        self.state = 'archived'

    def action_view_results(self):
        """Action pour voir les résultats détaillés"""
        return {
            'name': f'Résultats - {self.display_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.analysis.result',
            'view_mode': 'tree,form',
            'domain': [('analysis_id', '=', self.id)],
            'context': {'default_analysis_id': self.id},
        }

    def action_view_alerts(self):
        """Action pour voir les alertes"""
        return {
            'name': f'Alertes - {self.display_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.analysis.alert',
            'view_mode': 'tree,form',
            'domain': [('soil_analysis_id', '=', self.id)],
            'context': {'default_soil_analysis_id': self.id},
        }

    def _check_alerts(self):
        """Vérifier et créer les alertes basées sur les résultats"""
        for result in self.result_ids:
            param = result.parameter_id
            if not param.alert_enabled:
                continue
                
            value = result.get_value()
            if value is None:
                continue
                
            alert_type = None
            message = ''
            
            if param.data_type in ['float', 'integer', 'percentage']:
                if param.critical_min and value < param.critical_min:
                    alert_type = 'critical'
                    message = f'{param.name} critique: {result.display_value} < {param.critical_min}'
                elif param.critical_max and value > param.critical_max:
                    alert_type = 'critical'
                    message = f'{param.name} critique: {result.display_value} > {param.critical_max}'
                elif param.alert_threshold_low and value < param.alert_threshold_low:
                    alert_type = 'warning'
                    message = f'{param.name} bas: {result.display_value}'
                elif param.alert_threshold_high and value > param.alert_threshold_high:
                    alert_type = 'warning'
                    message = f'{param.name} élevé: {result.display_value}'
            
            if alert_type:
                self.env['bsr.analysis.alert'].create({
                    'soil_analysis_id': self.id,
                    'parameter_id': param.id,
                    'alert_type': alert_type,
                    'message': message,
                    'value': result.display_value,
                    'threshold_exceeded': True,
                })

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'La référence de l\'analyse doit être unique!'),
    ]