# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FarmSoilIntegration(models.Model):
    """Étendre le modèle Farm pour intégrer les analyses"""
    _inherit = 'bsr.farm'

    # Analyses de sol
    soil_analysis_ids = fields.One2many('bsr.soil.analysis', 'farm_id', 'Analyses de sol')
    soil_analysis_count = fields.Integer('Nombre d\'analyses de sol', compute='_compute_soil_analysis_count')
    last_soil_analysis_date = fields.Date('Dernière analyse de sol', compute='_compute_last_soil_analysis_date')
    
    # Analyses de culture
    culture_analysis_ids = fields.One2many('bsr.culture.analysis', 'farm_id', 'Analyses de culture')
    culture_analysis_count = fields.Integer('Nombre d\'analyses de culture', compute='_compute_culture_analysis_count')
    last_culture_analysis_date = fields.Date('Dernière analyse de culture', compute='_compute_last_culture_analysis_date')
    
    # Alertes
    analysis_alert_ids = fields.One2many('bsr.analysis.alert', 'farm_id', 'Alertes d\'analyse')
    active_alert_count = fields.Integer('Alertes actives', compute='_compute_active_alert_count')
    critical_alert_count = fields.Integer('Alertes critiques', compute='_compute_critical_alert_count')

    @api.depends('soil_analysis_ids')
    def _compute_soil_analysis_count(self):
        for record in self:
            record.soil_analysis_count = len(record.soil_analysis_ids)

    @api.depends('culture_analysis_ids')
    def _compute_culture_analysis_count(self):
        for record in self:
            record.culture_analysis_count = len(record.culture_analysis_ids)

    @api.depends('soil_analysis_ids.analysis_date')
    def _compute_last_soil_analysis_date(self):
        for record in self:
            if record.soil_analysis_ids:
                record.last_soil_analysis_date = max(record.soil_analysis_ids.mapped('analysis_date')).date()
            else:
                record.last_soil_analysis_date = False

    @api.depends('culture_analysis_ids.analysis_date')
    def _compute_last_culture_analysis_date(self):
        for record in self:
            if record.culture_analysis_ids:
                record.last_culture_analysis_date = max(record.culture_analysis_ids.mapped('analysis_date')).date()
            else:
                record.last_culture_analysis_date = False

    @api.depends('analysis_alert_ids.state')
    def _compute_active_alert_count(self):
        for record in self:
            record.active_alert_count = len([a for a in record.analysis_alert_ids 
                                           if a.state in ['new', 'acknowledged', 'in_progress']])

    @api.depends('analysis_alert_ids.alert_type', 'analysis_alert_ids.state')
    def _compute_critical_alert_count(self):
        for record in self:
            record.critical_alert_count = len([a for a in record.analysis_alert_ids 
                                             if a.alert_type == 'critical' and a.state in ['new', 'acknowledged', 'in_progress']])

    def action_view_soil_analyses(self):
        """Action pour voir les analyses de sol de cette ferme"""
        return {
            'name': f'Analyses de sol - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.soil.analysis',
            'view_mode': 'tree,form,kanban',
            'domain': [('farm_id', '=', self.id)],
            'context': {'default_farm_id': self.id},
        }

    def action_view_culture_analyses(self):
        """Action pour voir les analyses de culture de cette ferme"""
        return {
            'name': f'Analyses de culture - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.culture.analysis',
            'view_mode': 'tree,form,kanban',
            'domain': [('farm_id', '=', self.id)],
            'context': {'default_farm_id': self.id},
        }

    def action_view_analysis_alerts(self):
        """Action pour voir les alertes d'analyse de cette ferme"""
        return {
            'name': f'Alertes d\'analyse - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.analysis.alert',
            'view_mode': 'tree,form,kanban',
            'domain': [('farm_id', '=', self.id)],
            'context': {'default_farm_id': self.id},
        }


class ParcelSoilIntegration(models.Model):
    """Étendre le modèle Parcel pour intégrer les analyses"""
    _inherit = 'bsr.parcel'

    # Analyses de sol
    soil_analysis_ids = fields.One2many('bsr.soil.analysis', 'parcel_id', 'Analyses de sol')
    soil_analysis_count = fields.Integer('Nombre d\'analyses de sol', compute='_compute_soil_analysis_count')
    last_soil_analysis_date = fields.Date('Dernière analyse de sol', compute='_compute_last_soil_analysis_date')
    
    # Analyses de culture
    culture_analysis_ids = fields.One2many('bsr.culture.analysis', 'parcel_id', 'Analyses de culture')
    culture_analysis_count = fields.Integer('Nombre d\'analyses de culture', compute='_compute_culture_analysis_count')
    
    # Statut du sol (basé sur dernière analyse)
    soil_health_status = fields.Selection([
        ('unknown', 'Inconnu'),
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('average', 'Moyen'),
        ('poor', 'Médiocre'),
        ('critical', 'Critique'),
    ], string='Statut santé du sol', compute='_compute_soil_health_status', store=True)
    
    # Indicateurs clés du sol
    soil_ph = fields.Float('pH du sol', compute='_compute_soil_indicators', store=True)
    soil_organic_matter = fields.Float('Matière organique (%)', compute='_compute_soil_indicators', store=True)
    soil_nitrogen = fields.Float('Azote (kg/ha)', compute='_compute_soil_indicators', store=True)
    soil_phosphorus = fields.Float('Phosphore (kg/ha)', compute='_compute_soil_indicators', store=True)
    soil_potassium = fields.Float('Potassium (kg/ha)', compute='_compute_soil_indicators', store=True)

    @api.depends('soil_analysis_ids')
    def _compute_soil_analysis_count(self):
        for record in self:
            record.soil_analysis_count = len(record.soil_analysis_ids)

    @api.depends('culture_analysis_ids')
    def _compute_culture_analysis_count(self):
        for record in self:
            record.culture_analysis_count = len(record.culture_analysis_ids)

    @api.depends('soil_analysis_ids.analysis_date')
    def _compute_last_soil_analysis_date(self):
        for record in self:
            if record.soil_analysis_ids:
                record.last_soil_analysis_date = max(record.soil_analysis_ids.mapped('analysis_date')).date()
            else:
                record.last_soil_analysis_date = False

    @api.depends('soil_analysis_ids.overall_status', 'soil_analysis_ids.analysis_date')
    def _compute_soil_health_status(self):
        for record in self:
            if not record.soil_analysis_ids:
                record.soil_health_status = 'unknown'
                continue
                
            # Prendre le statut de la dernière analyse validée
            latest_analysis = record.soil_analysis_ids.filtered(
                lambda x: x.state in ['analyzed', 'validated']
            ).sorted('analysis_date', reverse=True)[:1]
            
            if latest_analysis:
                record.soil_health_status = latest_analysis.overall_status
            else:
                record.soil_health_status = 'unknown'

    @api.depends('soil_analysis_ids.result_ids.parameter_id', 'soil_analysis_ids.result_ids.value_float',
                 'soil_analysis_ids.analysis_date', 'soil_analysis_ids.state')
    def _compute_soil_indicators(self):
        for record in self:
            # Valeurs par défaut
            record.soil_ph = 0.0
            record.soil_organic_matter = 0.0
            record.soil_nitrogen = 0.0
            record.soil_phosphorus = 0.0
            record.soil_potassium = 0.0
            
            # Prendre les valeurs de la dernière analyse validée
            latest_analysis = record.soil_analysis_ids.filtered(
                lambda x: x.state in ['analyzed', 'validated']
            ).sorted('analysis_date', reverse=True)[:1]
            
            if not latest_analysis:
                continue
                
            for result in latest_analysis.result_ids:
                param_code = result.parameter_id.code.lower()
                value = result.value_float or 0.0
                
                if 'ph' in param_code:
                    record.soil_ph = value
                elif 'organic' in param_code or 'matiere' in param_code:
                    record.soil_organic_matter = value
                elif 'nitrogen' in param_code or 'azote' in param_code:
                    record.soil_nitrogen = value
                elif 'phosph' in param_code:
                    record.soil_phosphorus = value
                elif 'potass' in param_code or 'kalium' in param_code:
                    record.soil_potassium = value

    def action_view_soil_analyses(self):
        """Action pour voir les analyses de sol de cette parcelle"""
        return {
            'name': f'Analyses de sol - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.soil.analysis',
            'view_mode': 'tree,form,kanban',
            'domain': [('parcel_id', '=', self.id)],
            'context': {'default_parcel_id': self.id, 'default_farm_id': self.farm_id.id},
        }

    def action_view_culture_analyses(self):
        """Action pour voir les analyses de culture de cette parcelle"""
        return {
            'name': f'Analyses de culture - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.culture.analysis',
            'view_mode': 'tree,form,kanban',
            'domain': [('parcel_id', '=', self.id)],
            'context': {'default_parcel_id': self.id, 'default_farm_id': self.farm_id.id},
        }


class CultureSoilIntegration(models.Model):
    """Étendre le modèle Culture pour intégrer les analyses"""
    _inherit = 'bsr.culture'

    # Analyses de culture
    culture_analysis_ids = fields.One2many('bsr.culture.analysis', 'culture_id', 'Analyses de culture')
    culture_analysis_count = fields.Integer('Nombre d\'analyses', compute='_compute_culture_analysis_count')
    last_culture_analysis_date = fields.Date('Dernière analyse', compute='_compute_last_culture_analysis_date')
    
    # Statut de santé
    health_status = fields.Selection([
        ('unknown', 'Inconnu'),
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('average', 'Moyen'),
        ('poor', 'Médiocre'),
        ('critical', 'Critique'),
    ], string='Statut de santé', compute='_compute_health_status', store=True)
    
    # Score de santé visuelle moyen
    avg_visual_health_score = fields.Float('Score santé visuelle moyen', 
                                          compute='_compute_avg_visual_health_score', store=True)

    @api.depends('culture_analysis_ids')
    def _compute_culture_analysis_count(self):
        for record in self:
            record.culture_analysis_count = len(record.culture_analysis_ids)

    @api.depends('culture_analysis_ids.analysis_date')
    def _compute_last_culture_analysis_date(self):
        for record in self:
            if record.culture_analysis_ids:
                record.last_culture_analysis_date = max(record.culture_analysis_ids.mapped('analysis_date')).date()
            else:
                record.last_culture_analysis_date = False

    @api.depends('culture_analysis_ids.overall_status', 'culture_analysis_ids.analysis_date')
    def _compute_health_status(self):
        for record in self:
            if not record.culture_analysis_ids:
                record.health_status = 'unknown'
                continue
                
            # Prendre le statut de la dernière analyse validée
            latest_analysis = record.culture_analysis_ids.filtered(
                lambda x: x.state in ['analyzed', 'validated']
            ).sorted('analysis_date', reverse=True)[:1]
            
            if latest_analysis:
                record.health_status = latest_analysis.overall_status
            else:
                record.health_status = 'unknown'

    @api.depends('culture_analysis_ids.visual_health_score', 'culture_analysis_ids.state')
    def _compute_avg_visual_health_score(self):
        for record in self:
            validated_analyses = record.culture_analysis_ids.filtered(
                lambda x: x.state in ['analyzed', 'validated'] and x.visual_health_score
            )
            
            if validated_analyses:
                scores = [int(a.visual_health_score) for a in validated_analyses]
                record.avg_visual_health_score = sum(scores) / len(scores)
            else:
                record.avg_visual_health_score = 0.0

    def action_view_culture_analyses(self):
        """Action pour voir les analyses de cette culture"""
        return {
            'name': f'Analyses - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.culture.analysis',
            'view_mode': 'tree,form,kanban',
            'domain': [('culture_id', '=', self.id)],
            'context': {
                'default_culture_id': self.id,
                'default_parcel_id': self.parcel_id.id,
                'default_farm_id': self.parcel_id.farm_id.id
            },
        }