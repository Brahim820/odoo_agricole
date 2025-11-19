# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class IrrigationZone(models.Model):
    _name = 'bsr.irrigation.zone'
    _description = 'Zone d\'irrigation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char('Nom de la zone', required=True, tracking=True)
    code = fields.Char('Code zone', tracking=True)
    sequence = fields.Integer('Séquence', default=10)
    description = fields.Text('Description')
    
    # Relations principales
    parcel_id = fields.Many2one('bsr.parcel', string='Parcelle', required=True, tracking=True)
    farm_id = fields.Many2one('bsr.farm', string='Ferme', related='parcel_id.farm_id', store=True, readonly=True)
    system_id = fields.Many2one('bsr.irrigation.system', string='Système d\'irrigation', required=True, tracking=True)
    
    # Caractéristiques géographiques
    surface_area = fields.Float('Surface (hectares)', digits=(10, 4), required=True)
    latitude = fields.Float('Latitude', digits=(10, 7))
    longitude = fields.Float('Longitude', digits=(10, 7))
    elevation = fields.Float('Altitude (m)', digits=(8, 2))
    
    # Coordonnées GPS polygone (optionnel pour zones complexes)
    gps_coordinates = fields.Text('Coordonnées GPS (polygone)', help='Format: lat1,lng1;lat2,lng2;...')
    
    # Caractéristiques du sol et culture
    soil_type = fields.Selection([
        ('clay', 'Argile'),
        ('loam', 'Limon'),
        ('sand', 'Sable'),
        ('silt', 'Limon fin'),
        ('clay_loam', 'Argilo-limoneux'),
        ('sandy_loam', 'Limono-sableux'),
        ('silty_clay', 'Argilo-limoneux'),
        ('mixed', 'Mixte'),
    ], string='Type de sol', tracking=True)
    
    slope_percentage = fields.Float('Pente (%)', digits=(5, 2))
    drainage_capacity = fields.Selection([
        ('poor', 'Faible'),
        ('moderate', 'Modéré'),
        ('good', 'Bon'),
        ('excellent', 'Excellent'),
    ], string='Capacité de drainage', default='moderate')
    
    # Culture et besoins hydriques
    culture_id = fields.Many2one('bsr.culture', string='Culture actuelle')
    culture_type_id = fields.Many2one('bsr.culture.type', string='Type de culture', related='culture_id.culture_type_id', store=True, readonly=True)
    water_requirement_daily = fields.Float('Besoin hydrique journalier (L/m²)', digits=(8, 4), default=2.0)
    
    # Configuration irrigation
    irrigation_frequency_days = fields.Integer('Fréquence irrigation (jours)', default=2)
    irrigation_duration_minutes = fields.Integer('Durée irrigation (minutes)', default=60)
    water_flow_rate = fields.Float('Débit d\'eau (L/h)', digits=(10, 2))
    
    # Relations avec programmes et sessions
    program_ids = fields.One2many('bsr.irrigation.program', 'zone_id', string='Programmes d\'irrigation')
    session_ids = fields.One2many('bsr.irrigation.session', 'zone_id', string='Sessions d\'irrigation')
    
    # Statistiques et compteurs
    program_count = fields.Integer('Nombre de programmes', compute='_compute_program_count')
    session_count = fields.Integer('Nombre de sessions', compute='_compute_session_count')
    last_irrigation_date = fields.Datetime('Dernière irrigation', compute='_compute_last_irrigation_date', store=True)
    total_water_consumed = fields.Float('Eau consommée totale (L)', compute='_compute_irrigation_stats', store=True)
    
    # État et contrôle
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Active'),
        ('suspended', 'Suspendue'),
        ('archived', 'Archivée'),
    ], string='État', default='draft', required=True, tracking=True)
    
    active = fields.Boolean('Actif', default=True)
    notes = fields.Text('Notes')
    
    @api.depends('program_ids')
    def _compute_program_count(self):
        for zone in self:
            zone.program_count = len(zone.program_ids)
    
    @api.depends('session_ids')
    def _compute_session_count(self):
        for zone in self:
            zone.session_count = len(zone.session_ids)
    
    @api.depends('session_ids', 'session_ids.start_datetime')
    def _compute_last_irrigation_date(self):
        for zone in self:
            last_session = zone.session_ids.filtered(lambda s: s.start_datetime).sorted('start_datetime', reverse=True)
            zone.last_irrigation_date = last_session[0].start_datetime if last_session else False
    
    @api.depends('session_ids', 'session_ids.water_consumed')
    def _compute_irrigation_stats(self):
        for zone in self:
            completed_sessions = zone.session_ids.filtered(lambda s: s.state == 'completed')
            zone.total_water_consumed = sum(completed_sessions.mapped('water_consumed'))
    
    # Contraintes et validations
    @api.constrains('surface_area')
    def _check_surface_area(self):
        for zone in self:
            if zone.surface_area <= 0:
                raise ValidationError(_('La surface de la zone doit être positive.'))
            if zone.parcel_id and zone.surface_area > zone.parcel_id.surface:
                raise ValidationError(_('La surface de la zone ne peut pas dépasser la surface de la parcelle (%s ha).') % zone.parcel_id.surface)
    
    @api.constrains('latitude', 'longitude')
    def _check_coordinates(self):
        for zone in self:
            if zone.latitude and not (-90 <= zone.latitude <= 90):
                raise ValidationError(_('La latitude doit être comprise entre -90 et 90 degrés.'))
            if zone.longitude and not (-180 <= zone.longitude <= 180):
                raise ValidationError(_('La longitude doit être comprise entre -180 et 180 degrés.'))
    
    @api.constrains('water_requirement_daily', 'water_flow_rate')
    def _check_water_specs(self):
        for zone in self:
            if zone.water_requirement_daily and zone.water_requirement_daily <= 0:
                raise ValidationError(_('Le besoin hydrique journalier doit être positif.'))
            if zone.water_flow_rate and zone.water_flow_rate <= 0:
                raise ValidationError(_('Le débit d\'eau doit être positif.'))
    
    @api.constrains('slope_percentage')
    def _check_slope(self):
        for zone in self:
            if zone.slope_percentage and not (0 <= zone.slope_percentage <= 100):
                raise ValidationError(_('La pente doit être comprise entre 0 et 100%.'))
    
    # Méthodes de workflow
    def action_activate(self):
        """Activer la zone d'irrigation"""
        for zone in self:
            if zone.state not in ['draft', 'suspended']:
                raise ValidationError(_('Seules les zones en brouillon ou suspendues peuvent être activées.'))
            zone.state = 'active'
    
    def action_suspend(self):
        """Suspendre la zone d'irrigation"""
        for zone in self:
            if zone.state != 'active':
                raise ValidationError(_('Seules les zones actives peuvent être suspendues.'))
            zone.state = 'suspended'
    
    def action_archive(self):
        """Archiver la zone"""
        for zone in self:
            zone.state = 'archived'
            zone.active = False
    
    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        for zone in self:
            zone.state = 'draft'
    
    # Méthodes métier
    def calculate_daily_water_needs(self):
        """Calculer les besoins en eau journaliers pour la zone"""
        self.ensure_one()
        if not self.surface_area or not self.water_requirement_daily:
            return 0
        # Surface en hectares * besoin en L/m² * 10000 m²/ha
        return self.surface_area * self.water_requirement_daily * 10000
    
    def calculate_optimal_irrigation_duration(self, target_water_volume=None):
        """Calculer la durée d'irrigation optimale"""
        self.ensure_one()
        if not self.water_flow_rate:
            return 0
        
        if not target_water_volume:
            target_water_volume = self.calculate_daily_water_needs()
        
        if target_water_volume and self.water_flow_rate:
            # Durée en heures = Volume en L / Débit en L/h
            return target_water_volume / self.water_flow_rate
        return 0
    
    def get_soil_analysis_data(self):
        """Récupérer les données d'analyse du sol pour cette zone"""
        self.ensure_one()
        if not self.parcel_id:
            return False
        
        # Rechercher les analyses de sol récentes pour cette parcelle
        soil_analyses = self.env['bsr.soil.analysis'].search([
            ('parcel_id', '=', self.parcel_id.id),
            ('state', '=', 'validated'),
        ], order='analysis_date desc', limit=5)
        
        return soil_analyses
    
    def action_create_irrigation_program(self):
        """Créer un nouveau programme d'irrigation pour cette zone"""
        self.ensure_one()
        return {
            'name': _('Nouveau programme d\'irrigation'),
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.program',
            'view_mode': 'form',
            'context': {
                'default_zone_id': self.id,
                'default_name': f'Programme - {self.name}',
            },
            'target': 'new',
        }
    
    def action_start_irrigation_session(self):
        """Démarrer une nouvelle session d'irrigation"""
        self.ensure_one()
        return {
            'name': _('Nouvelle session d\'irrigation'),
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.session',
            'view_mode': 'form',
            'context': {
                'default_zone_id': self.id,
                'default_system_id': self.system_id.id,
                'default_name': f'Session - {self.name}',
            },
            'target': 'new',
        }
    
    def action_view_programs(self):
        """Voir les programmes d'irrigation"""
        self.ensure_one()
        return {
            'name': f'Programmes - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.program',
            'view_mode': 'tree,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id},
        }
    
    def action_view_sessions(self):
        """Voir les sessions d'irrigation"""
        self.ensure_one()
        return {
            'name': f'Sessions - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.session',
            'view_mode': 'tree,form',
            'domain': [('zone_id', '=', self.id)],
            'context': {'default_zone_id': self.id},
        }
    
    @api.model
    def create(self, vals):
        """Générer automatiquement un code si non fourni"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.irrigation.zone') or 'ZONE-NEW'
        return super().create(vals)

    def name_get(self):
        """Format d'affichage personnalisé"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.surface_area:
                name += f" ({record.surface_area:.2f} ha)"
            result.append((record.id, name))
        return result