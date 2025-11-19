# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class IrrigationSession(models.Model):
    _name = 'bsr.irrigation.session'
    _description = 'Session d\'irrigation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char('Nom de la session', required=True, tracking=True)
    code = fields.Char('Code session', tracking=True)
    
    # Relations principales
    zone_id = fields.Many2one('bsr.irrigation.zone', string='Zone d\'irrigation', required=True, tracking=True)
    system_id = fields.Many2one('bsr.irrigation.system', string='Système d\'irrigation', required=True, tracking=True)
    program_id = fields.Many2one('bsr.irrigation.program', string='Programme origine', tracking=True)
    farm_id = fields.Many2one('bsr.farm', string='Ferme', related='zone_id.farm_id', store=True, readonly=True)
    parcel_id = fields.Many2one('bsr.parcel', string='Parcelle', related='zone_id.parcel_id', store=True, readonly=True)
    
    # Type et mode de session
    session_type = fields.Selection([
        ('manual', 'Manuel'),
        ('automatic', 'Automatique'),
        ('emergency', 'Urgence'),
        ('test', 'Test'),
    ], string='Type de session', required=True, default='manual', tracking=True)
    
    # Planification
    planned_start_datetime = fields.Datetime('Début planifié', tracking=True)
    planned_end_datetime = fields.Datetime('Fin planifiée', compute='_compute_planned_end_datetime', store=True)
    duration_minutes_planned = fields.Integer('Durée planifiée (min)', default=60)
    
    # Exécution réelle
    start_datetime = fields.Datetime('Début réel', tracking=True)
    end_datetime = fields.Datetime('Fin réelle', tracking=True)
    duration_hours = fields.Float('Durée réelle (h)', compute='_compute_actual_duration', store=True)
    duration_minutes = fields.Integer('Durée réelle (min)', compute='_compute_actual_duration_minutes', store=True)
    
    # Paramètres d'irrigation
    water_volume_target = fields.Float('Volume d\'eau cible (L)', digits=(12, 2))
    water_consumed = fields.Float('Volume d\'eau consommé (L)', digits=(12, 2), tracking=True)
    water_flow_rate_actual = fields.Float('Débit réel (L/h)', digits=(10, 2))
    water_efficiency = fields.Float('Efficacité (%)', compute='_compute_water_efficiency', store=True)
    
    # Conditions environnementales
    temperature_start = fields.Float('Température début (°C)', digits=(5, 2))
    temperature_end = fields.Float('Température fin (°C)', digits=(5, 2))
    humidity_start = fields.Float('Humidité début (%)', digits=(5, 2))
    humidity_end = fields.Float('Humidité fin (%)', digits=(5, 2))
    wind_speed = fields.Float('Vitesse vent (km/h)', digits=(5, 2))
    precipitation_during = fields.Float('Précipitations (mm)', digits=(5, 2))
    
    # Conditions du sol
    soil_moisture_before = fields.Float('Humidité sol avant (%)', digits=(5, 2))
    soil_moisture_after = fields.Float('Humidité sol après (%)', digits=(5, 2))
    soil_temperature = fields.Float('Température sol (°C)', digits=(5, 2))
    
    # Équipement et maintenance
    equipment_status = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('average', 'Moyen'),
        ('poor', 'Défaillant'),
        ('broken', 'En panne'),
    ], string='État équipement', default='good')
    
    # Personnel et responsabilité
    operator_id = fields.Many2one('res.users', string='Opérateur', tracking=True)
    supervisor_id = fields.Many2one('res.users', string='Superviseur')
    
    # État et résultats
    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('in_progress', 'En cours'),
        ('paused', 'En pause'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
        ('failed', 'Échouée'),
    ], string='État', default='planned', required=True, tracking=True)
    
    result = fields.Selection([
        ('success', 'Réussie'),
        ('partial', 'Partielle'),
        ('failed', 'Échouée'),
    ], string='Résultat', tracking=True)
    
    # Problèmes et observations
    issues_encountered = fields.Text('Problèmes rencontrés')
    operator_notes = fields.Text('Notes opérateur')
    quality_rating = fields.Selection([
        ('1', 'Très mauvais'),
        ('2', 'Mauvais'),
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent'),
    ], string='Évaluation qualité')
    
    # Coûts
    water_cost = fields.Float('Coût eau (€)', digits=(10, 2), compute='_compute_costs', store=True)
    energy_cost = fields.Float('Coût énergie (€)', digits=(10, 2))
    labor_cost = fields.Float('Coût main d\'œuvre (€)', digits=(10, 2))
    total_cost = fields.Float('Coût total (€)', digits=(10, 2), compute='_compute_costs', store=True)
    
    # Alarmes et alertes
    alert_ids = fields.One2many('bsr.irrigation.alert', 'session_id', string='Alertes')
    alert_count = fields.Integer('Nombre d\'alertes', compute='_compute_alert_count', store=True)
    has_critical_alerts = fields.Boolean('Alertes critiques', compute='_compute_alert_count', store=True)
    
    # Métriques de performance
    target_achievement = fields.Float('Atteinte objectif (%)', compute='_compute_performance_metrics', store=True)
    time_variance = fields.Float('Variance temps (min)', compute='_compute_performance_metrics', store=True)
    
    active = fields.Boolean('Actif', default=True)
    
    @api.depends('planned_start_datetime', 'duration_minutes_planned')
    def _compute_planned_end_datetime(self):
        for session in self:
            if session.planned_start_datetime and session.duration_minutes_planned:
                session.planned_end_datetime = session.planned_start_datetime + timedelta(minutes=session.duration_minutes_planned)
            else:
                session.planned_end_datetime = False
    
    @api.depends('start_datetime', 'end_datetime')
    def _compute_actual_duration(self):
        for session in self:
            if session.start_datetime and session.end_datetime:
                delta = session.end_datetime - session.start_datetime
                session.duration_hours = delta.total_seconds() / 3600
            else:
                session.duration_hours = 0.0
    
    @api.depends('duration_hours')
    def _compute_actual_duration_minutes(self):
        for session in self:
            session.duration_minutes = int(session.duration_hours * 60)
    
    @api.depends('water_volume_target', 'water_consumed')
    def _compute_water_efficiency(self):
        for session in self:
            if session.water_volume_target and session.water_consumed:
                session.water_efficiency = min(100, (session.water_consumed / session.water_volume_target) * 100)
            else:
                session.water_efficiency = 0.0
    
    @api.depends('water_consumed', 'energy_cost', 'labor_cost')
    def _compute_costs(self):
        for session in self:
            # Prix de l'eau par défaut (à paramétrer)
            water_price_per_liter = 0.002  # 2€ par m3
            session.water_cost = session.water_consumed * water_price_per_liter
            session.total_cost = session.water_cost + session.energy_cost + session.labor_cost
    
    @api.depends('alert_ids')
    def _compute_alert_count(self):
        for session in self:
            session.alert_count = len(session.alert_ids)
            session.has_critical_alerts = any(alert.priority == 'critical' for alert in session.alert_ids)
    
    @api.depends('water_volume_target', 'water_consumed', 'duration_minutes_planned', 'duration_minutes')
    def _compute_performance_metrics(self):
        for session in self:
            # Atteinte de l'objectif de volume d'eau
            if session.water_volume_target and session.water_consumed:
                session.target_achievement = min(100, (session.water_consumed / session.water_volume_target) * 100)
            else:
                session.target_achievement = 0.0
            
            # Variance de temps
            if session.duration_minutes_planned and session.duration_minutes:
                session.time_variance = session.duration_minutes - session.duration_minutes_planned
            else:
                session.time_variance = 0.0
    
    # Contraintes et validations
    @api.constrains('start_datetime', 'end_datetime')
    def _check_datetime_sequence(self):
        for session in self:
            if session.start_datetime and session.end_datetime and session.end_datetime <= session.start_datetime:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))
    
    @api.constrains('planned_start_datetime')
    def _check_planned_datetime(self):
        for session in self:
            if session.planned_start_datetime and session.planned_start_datetime < datetime.now() - timedelta(hours=24):
                raise ValidationError(_('La date planifiée ne peut pas être antérieure à hier.'))
    
    @api.constrains('water_volume_target', 'water_consumed')
    def _check_water_volumes(self):
        for session in self:
            if session.water_volume_target and session.water_volume_target <= 0:
                raise ValidationError(_('Le volume d\'eau cible doit être positif.'))
            if session.water_consumed and session.water_consumed < 0:
                raise ValidationError(_('Le volume d\'eau consommé ne peut pas être négatif.'))
    
    # Méthodes de workflow
    def action_start(self):
        """Démarrer la session d'irrigation"""
        for session in self:
            if session.state not in ['planned']:
                raise ValidationError(_('Seules les sessions planifiées peuvent être démarrées.'))
            
            session.write({
                'state': 'in_progress',
                'start_datetime': datetime.now(),
                'operator_id': self.env.user.id,
            })
    
    def action_pause(self):
        """Mettre en pause la session"""
        for session in self:
            if session.state != 'in_progress':
                raise ValidationError(_('Seules les sessions en cours peuvent être mises en pause.'))
            session.state = 'paused'
    
    def action_resume(self):
        """Reprendre la session"""
        for session in self:
            if session.state != 'paused':
                raise ValidationError(_('Seules les sessions en pause peuvent être reprises.'))
            session.state = 'in_progress'
    
    def action_complete(self):
        """Terminer la session avec succès"""
        for session in self:
            if session.state not in ['in_progress', 'paused']:
                raise ValidationError(_('Seules les sessions en cours ou en pause peuvent être terminées.'))
            
            session.write({
                'state': 'completed',
                'end_datetime': datetime.now(),
                'result': 'success' if session.water_efficiency >= 80 else 'partial',
            })
    
    def action_cancel(self):
        """Annuler la session"""
        for session in self:
            if session.state in ['completed', 'failed']:
                raise ValidationError(_('Une session terminée ou échouée ne peut pas être annulée.'))
            
            session.write({
                'state': 'cancelled',
                'end_datetime': datetime.now() if session.state == 'in_progress' else session.end_datetime,
            })
    
    def action_mark_failed(self):
        """Marquer la session comme échouée"""
        for session in self:
            if session.state == 'completed':
                raise ValidationError(_('Une session terminée ne peut pas être marquée comme échouée.'))
            
            session.write({
                'state': 'failed',
                'result': 'failed',
                'end_datetime': datetime.now() if session.state == 'in_progress' else session.end_datetime,
            })
    
    # Méthodes métier
    def calculate_water_flow_rate(self):
        """Calculer le débit d'eau réel"""
        self.ensure_one()
        if self.duration_hours and self.water_consumed:
            self.water_flow_rate_actual = self.water_consumed / self.duration_hours
    
    def create_maintenance_alert(self, issue_description):
        """Créer une alerte de maintenance"""
        self.ensure_one()
        alert_vals = {
            'name': f'Maintenance - {self.system_id.name}',
            'alert_type': 'equipment',
            'priority': 'high',
            'description': issue_description,
            'system_id': self.system_id.id,
            'session_id': self.id,
            'state': 'active',
        }
        return self.env['bsr.irrigation.alert'].create(alert_vals)
    
    def action_create_maintenance_request(self):
        """Créer une demande de maintenance pour l'équipement"""
        self.ensure_one()
        if not self.system_id.equipment_id:
            raise ValidationError(_('Aucun équipement de maintenance associé au système.'))
        
        return {
            'name': _('Demande de maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'context': {
                'default_equipment_id': self.system_id.equipment_id.id,
                'default_name': f'Maintenance suite session - {self.name}',
                'default_description': f'Problèmes rencontrés: {self.issues_encountered}',
            },
            'target': 'new',
        }
    
    def action_view_alerts(self):
        """Voir les alertes de la session"""
        self.ensure_one()
        return {
            'name': f'Alertes - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.alert',
            'view_mode': 'tree,form',
            'domain': [('session_id', '=', self.id)],
            'context': {'default_session_id': self.id},
        }
    
    def get_session_report_data(self):
        """Récupérer les données pour le rapport de session"""
        self.ensure_one()
        return {
            'session': self,
            'zone': self.zone_id,
            'system': self.system_id,
            'program': self.program_id,
            'performance': {
                'target_achievement': self.target_achievement,
                'water_efficiency': self.water_efficiency,
                'time_variance': self.time_variance,
            },
            'costs': {
                'water': self.water_cost,
                'energy': self.energy_cost,
                'labor': self.labor_cost,
                'total': self.total_cost,
            },
            'alerts': self.alert_ids,
        }
    
    @api.model
    def create(self, vals):
        """Générer automatiquement un code si non fourni"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.irrigation.session') or 'SESS-NEW'
        return super().create(vals)

    def name_get(self):
        """Format d'affichage personnalisé"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.start_datetime:
                name += f" ({record.start_datetime.strftime('%d/%m/%Y %H:%M')})"
            result.append((record.id, name))
        return result