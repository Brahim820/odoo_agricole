# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


class CultureAnalysis(models.Model):
    """Analyses des cultures"""
    _name = 'bsr.culture.analysis'
    _description = 'Analyse de Culture'
    _order = 'analysis_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    # Informations générales
    name = fields.Char('Référence', required=True, copy=False, readonly=True,
                      default=lambda self: self.env['ir.sequence'].next_by_code('bsr.culture.analysis'))
    display_name = fields.Char('Nom', compute='_compute_display_name', store=True)
    
    # Localisation et culture
    farm_id = fields.Many2one('bsr.farm', 'Ferme', required=True, tracking=True)
    parcel_id = fields.Many2one('bsr.parcel', 'Parcelle', required=True, tracking=True,
                               domain="[('farm_id', '=', farm_id)]")
    culture_id = fields.Many2one('bsr.culture', 'Culture', required=True, tracking=True,
                                domain="[('parcel_id', '=', parcel_id)]")
    
    # Détails de la culture
    growth_stage = fields.Selection([
        ('germination', 'Germination'),
        ('emergence', 'Émergence'),
        ('vegetative', 'Croissance végétative'),
        ('flowering', 'Floraison'),
        ('fruit_development', 'Formation des fruits'),
        ('maturity', 'Maturité'),
        ('harvest', 'Récolte'),
        ('post_harvest', 'Post-récolte'),
    ], string='Stade de croissance', tracking=True)
    
    plant_height = fields.Float('Hauteur des plants (cm)')
    plant_density = fields.Float('Densité (plants/m²)')
    
    # Échantillonnage
    sampling_date = fields.Datetime('Date d\'échantillonnage', required=True, tracking=True,
                                   default=fields.Datetime.now)
    sampling_method = fields.Selection([
        ('random', 'Échantillonnage aléatoire'),
        ('systematic', 'Échantillonnage systématique'),
        ('representative', 'Échantillon représentatif'),
        ('targeted', 'Échantillonnage ciblé'),
        ('transect', 'Transect'),
    ], string='Méthode d\'échantillonnage', default='representative')
    
    sample_size = fields.Integer('Taille de l\'échantillon', default=1)
    sample_weight = fields.Float('Poids échantillon (kg)')
    sample_type = fields.Selection([
        ('leaves', 'Feuilles'),
        ('stem', 'Tige'),
        ('root', 'Racines'),
        ('fruit', 'Fruits'),
        ('grain', 'Grains'),
        ('whole_plant', 'Plant entier'),
    ], string='Type d\'échantillon')
    
    # Coordonnées GPS (optionnel)
    sampling_latitude = fields.Float('Latitude échantillonnage', digits=(16, 6))
    sampling_longitude = fields.Float('Longitude échantillonnage', digits=(16, 6))
    
    # Analyse
    analysis_type_id = fields.Many2one('bsr.analysis.type', 'Type d\'analyse', required=True,
                                      domain=[('category', 'in', ['culture', 'harvest', 'nutritional'])], 
                                      tracking=True)
    analysis_date = fields.Datetime('Date d\'analyse', required=True, tracking=True)
    laboratory_id = fields.Many2one('res.partner', 'Laboratoire',
                                   domain=[('is_company', '=', True)], tracking=True)
    laboratory_reference = fields.Char('Référence laboratoire')
    
    # Conditions environnementales
    temperature = fields.Float('Température (°C)')
    humidity = fields.Float('Humidité (%)')
    weather_conditions = fields.Selection([
        ('sunny', 'Ensoleillé'),
        ('cloudy', 'Nuageux'),
        ('rainy', 'Pluvieux'),
        ('windy', 'Venteux'),
        ('storm', 'Orageux'),
    ], string='Conditions météorologiques')
    
    # Résultats
    result_ids = fields.One2many('bsr.analysis.result', 'culture_analysis_id', 'Résultats')
    result_count = fields.Integer('Nombre de résultats', compute='_compute_result_count', store=True)
    
    # Évaluation visuelle
    visual_health_score = fields.Selection([
        ('1', 'Très mauvais (1)'),
        ('2', 'Mauvais (2)'),
        ('3', 'Médiocre (3)'),
        ('4', 'Moyen (4)'),
        ('5', 'Bon (5)'),
        ('6', 'Très bon (6)'),
        ('7', 'Excellent (7)'),
    ], string='Score santé visuelle')
    
    diseases_observed = fields.Text('Maladies observées')
    pests_observed = fields.Text('Ravageurs observés')
    stress_symptoms = fields.Text('Symptômes de stress')
    
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
    
    # Recommandations et actions
    recommendations = fields.Text('Recommandations')
    actions_taken = fields.Text('Actions réalisées')
    next_analysis_date = fields.Date('Prochaine analyse recommandée',
                                    compute='_compute_next_analysis_date', store=True)
    
    # Documents
    report_file = fields.Binary('Rapport d\'analyse')
    report_filename = fields.Char('Nom du fichier rapport')
    photos = fields.Text('Photos (URLs)')
    
    # Métadonnées
    technician_id = fields.Many2one('res.users', 'Technicien', default=lambda self: self.env.user)
    responsible_id = fields.Many2one('res.users', 'Responsable')
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)
    
    # Alertes générées
    alert_ids = fields.One2many('bsr.analysis.alert', 'culture_analysis_id', 'Alertes')
    alert_count = fields.Integer('Nombre d\'alertes', compute='_compute_alert_count', store=True)
    
    # Liens avec autres analyses
    related_soil_analysis_ids = fields.Many2many('bsr.soil.analysis', 
                                                 'culture_soil_analysis_rel',
                                                 'culture_analysis_id', 'soil_analysis_id',
                                                 string='Analyses de sol liées')

    @api.depends('name', 'culture_id', 'analysis_date')
    def _compute_display_name(self):
        for record in self:
            culture_name = record.culture_id.name if record.culture_id else ''
            date_str = record.analysis_date.strftime('%d/%m/%Y') if record.analysis_date else ''
            record.display_name = f"{record.name} - {culture_name} ({date_str})"

    @api.depends('result_ids')
    def _compute_result_count(self):
        for record in self:
            record.result_count = len(record.result_ids)

    @api.depends('alert_ids')
    def _compute_alert_count(self):
        for record in self:
            record.alert_count = len(record.alert_ids)

    @api.depends('result_ids.status', 'visual_health_score')
    def _compute_overall_status(self):
        for record in self:
            if not record.result_ids and not record.visual_health_score:
                record.overall_status = 'average'
                continue
                
            # Score basé sur les résultats d'analyse
            analysis_score = 0
            if record.result_ids:
                status_weights = {
                    'critical': 1,
                    'warning': 3,
                    'normal': 5,
                    'optimal': 7
                }
                
                total_weight = 0
                weighted_sum = 0
                for result in record.result_ids:
                    weight = status_weights.get(result.status, 5)
                    weighted_sum += weight
                    total_weight += 1
                
                analysis_score = weighted_sum / total_weight if total_weight > 0 else 5
            
            # Score basé sur l'évaluation visuelle
            visual_score = int(record.visual_health_score) if record.visual_health_score else 5
            
            # Score combiné
            if record.result_ids and record.visual_health_score:
                combined_score = (analysis_score + visual_score) / 2
            elif record.result_ids:
                combined_score = analysis_score
            else:
                combined_score = visual_score
            
            # Déterminer le statut
            if combined_score >= 6.5:
                record.overall_status = 'excellent'
            elif combined_score >= 5.5:
                record.overall_status = 'good'
            elif combined_score >= 4:
                record.overall_status = 'average'
            elif combined_score >= 2.5:
                record.overall_status = 'poor'
            else:
                record.overall_status = 'critical'

    @api.depends('analysis_type_id', 'analysis_date', 'growth_stage')
    def _compute_next_analysis_date(self):
        for record in self:
            if not record.analysis_type_id or not record.analysis_date:
                record.next_analysis_date = False
                continue
                
            # Adapter la fréquence selon le stade de croissance
            frequency_map = {
                'weekly': 7,
                'monthly': 30,
                'quarterly': 90,
                'biannual': 180,
                'annual': 365,
            }
            
            # Fréquence plus élevée pendant les stades critiques
            if record.growth_stage in ['flowering', 'fruit_development']:
                days = 14  # Bi-hebdomadaire pendant floraison/fructification
            else:
                frequency = record.analysis_type_id.recommended_frequency
                days = frequency_map.get(frequency, 30)
            
            record.next_analysis_date = record.analysis_date.date() + timedelta(days=days)

    @api.onchange('farm_id')
    def _onchange_farm_id(self):
        self.parcel_id = False
        self.culture_id = False

    @api.onchange('parcel_id')
    def _onchange_parcel_id(self):
        self.culture_id = False
        
        # Proposer des analyses de sol récentes de la même parcelle
        if self.parcel_id:
            soil_analyses = self.env['bsr.soil.analysis'].search([
                ('parcel_id', '=', self.parcel_id.id),
                ('state', 'in', ['analyzed', 'validated'])
            ], limit=5, order='analysis_date desc')
            self.related_soil_analysis_ids = [(6, 0, soil_analyses.ids)]

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
            'domain': [('culture_analysis_id', '=', self.id)],
            'context': {'default_culture_analysis_id': self.id},
        }

    def action_view_alerts(self):
        """Action pour voir les alertes"""
        return {
            'name': f'Alertes - {self.display_name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.analysis.alert',
            'view_mode': 'tree,form',
            'domain': [('culture_analysis_id', '=', self.id)],
            'context': {'default_culture_analysis_id': self.id},
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
                    'culture_analysis_id': self.id,
                    'parameter_id': param.id,
                    'alert_type': alert_type,
                    'message': message,
                    'value': result.display_value,
                    'threshold_exceeded': True,
                })

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'La référence de l\'analyse doit être unique!'),
    ]