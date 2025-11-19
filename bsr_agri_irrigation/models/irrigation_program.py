# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class IrrigationProgram(models.Model):
    _name = 'bsr.irrigation.program'
    _description = 'Programme d\'irrigation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, name'

    name = fields.Char('Nom du programme', required=True, tracking=True)
    code = fields.Char('Code programme', tracking=True)
    description = fields.Text('Description')
    
    # Relations principales
    zone_id = fields.Many2one('bsr.irrigation.zone', string='Zone d\'irrigation', required=True, tracking=True)
    system_id = fields.Many2one('bsr.irrigation.system', string='Système d\'irrigation', related='zone_id.system_id', store=True, readonly=True)
    farm_id = fields.Many2one('bsr.farm', string='Ferme', related='zone_id.farm_id', store=True, readonly=True)
    
    # Type et priorité
    program_type = fields.Selection([
        ('manual', 'Manuel'),
        ('scheduled', 'Programmé'),
        ('conditional', 'Conditionnel'),
        ('emergency', 'Urgence'),
    ], string='Type de programme', required=True, default='scheduled', tracking=True)
    
    priority = fields.Selection([
        ('low', 'Faible'),
        ('normal', 'Normal'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ], string='Priorité', default='normal', tracking=True)
    
    # Période d'activité
    start_date = fields.Date('Date de début', required=True, tracking=True)
    end_date = fields.Date('Date de fin', tracking=True)
    active_season = fields.Selection([
        ('spring', 'Printemps'),
        ('summer', 'Été'),
        ('autumn', 'Automne'),
        ('winter', 'Hiver'),
        ('all_year', 'Toute l\'année'),
    ], string='Saison active', default='all_year')
    
    # Configuration temporelle
    frequency_type = fields.Selection([
        ('daily', 'Quotidien'),
        ('alternate', 'Tous les 2 jours'),
        ('weekly', 'Hebdomadaire'),
        ('custom', 'Personnalisé'),
    ], string='Fréquence', default='alternate', required=True)
    
    frequency_days = fields.Integer('Fréquence (jours)', default=2, help='Nombre de jours entre les irrigations')
    
    # Horaires
    preferred_start_time = fields.Float('Heure de début préférée', default=6.0, help='Heure en format 24h (ex: 6.5 = 6h30)')
    max_start_time = fields.Float('Heure limite de début', default=8.0)
    duration_minutes = fields.Integer('Durée (minutes)', required=True, default=60)
    
    # Jours de la semaine (pour fréquence hebdomadaire)
    monday = fields.Boolean('Lundi')
    tuesday = fields.Boolean('Mardi') 
    wednesday = fields.Boolean('Mercredi')
    thursday = fields.Boolean('Jeudi')
    friday = fields.Boolean('Vendredi')
    saturday = fields.Boolean('Samedi')
    sunday = fields.Boolean('Dimanche')
    
    # Paramètres d'irrigation
    water_volume_target = fields.Float('Volume d\'eau cible (L)', digits=(12, 2))
    water_flow_rate = fields.Float('Débit souhaité (L/h)', digits=(10, 2))
    
    # Conditions de déclenchement
    soil_moisture_threshold = fields.Float('Seuil humidité sol (%)', digits=(5, 2), default=30.0)
    temperature_min = fields.Float('Température minimum (°C)', digits=(5, 2))
    temperature_max = fields.Float('Température maximum (°C)', digits=(5, 2))
    wind_speed_max = fields.Float('Vitesse vent max (km/h)', digits=(5, 2), default=15.0)
    
    # Conditions d'arrêt
    stop_if_rain = fields.Boolean('Arrêter si pluie', default=True)
    rain_threshold_mm = fields.Float('Seuil pluie (mm)', digits=(5, 2), default=5.0)
    stop_if_wet_soil = fields.Boolean('Arrêter si sol humide', default=True)
    
    # Intégration analyses du sol
    use_soil_analysis = fields.Boolean('Utiliser analyses du sol', default=True)
    soil_analysis_ids = fields.Many2many('bsr.soil.analysis', string='Analyses du sol référence')
    
    # Relations avec sessions
    session_ids = fields.One2many('bsr.irrigation.session', 'program_id', string='Sessions d\'irrigation')
    session_count = fields.Integer('Nombre de sessions', compute='_compute_session_count')
    last_execution_date = fields.Datetime('Dernière exécution', compute='_compute_last_execution', store=True)
    next_execution_date = fields.Datetime('Prochaine exécution', compute='_compute_next_execution', store=True)
    
    # Statistiques
    total_water_consumed = fields.Float('Eau consommée totale (L)', compute='_compute_program_stats', store=True)
    success_rate = fields.Float('Taux de réussite (%)', compute='_compute_program_stats', store=True)
    average_duration = fields.Float('Durée moyenne (min)', compute='_compute_program_stats', store=True)
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='draft', required=True, tracking=True)
    
    active = fields.Boolean('Actif', default=True)
    notes = fields.Text('Notes')
    
    @api.depends('session_ids')
    def _compute_session_count(self):
        for program in self:
            program.session_count = len(program.session_ids)
    
    @api.depends('session_ids', 'session_ids.start_datetime')
    def _compute_last_execution(self):
        for program in self:
            last_session = program.session_ids.filtered(lambda s: s.start_datetime).sorted('start_datetime', reverse=True)
            program.last_execution_date = last_session[0].start_datetime if last_session else False
    
    @api.depends('last_execution_date', 'frequency_days', 'state')
    def _compute_next_execution(self):
        for program in self:
            if program.state == 'active' and program.last_execution_date and program.frequency_days:
                program.next_execution_date = program.last_execution_date + timedelta(days=program.frequency_days)
            elif program.state == 'active' and not program.last_execution_date:
                # Premier démarrage
                program.next_execution_date = datetime.now() + timedelta(days=1)
            else:
                program.next_execution_date = False
    
    @api.depends('session_ids', 'session_ids.state', 'session_ids.water_consumed', 'session_ids.duration_hours')
    def _compute_program_stats(self):
        for program in self:
            sessions = program.session_ids
            if sessions:
                completed_sessions = sessions.filtered(lambda s: s.state == 'completed')
                program.total_water_consumed = sum(completed_sessions.mapped('water_consumed'))
                program.success_rate = (len(completed_sessions) / len(sessions)) * 100 if sessions else 0
                program.average_duration = sum(sessions.mapped('duration_hours')) * 60 / len(sessions) if sessions else 0
            else:
                program.total_water_consumed = 0
                program.success_rate = 0
                program.average_duration = 0
    
    # Contraintes et validations
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for program in self:
            if program.end_date and program.start_date and program.end_date <= program.start_date:
                raise ValidationError(_('La date de fin doit être postérieure à la date de début.'))
    
    @api.constrains('preferred_start_time', 'max_start_time')
    def _check_times(self):
        for program in self:
            if not (0 <= program.preferred_start_time <= 24):
                raise ValidationError(_('L\'heure de début préférée doit être entre 0 et 24.'))
            if not (0 <= program.max_start_time <= 24):
                raise ValidationError(_('L\'heure limite de début doit être entre 0 et 24.'))
            if program.max_start_time <= program.preferred_start_time:
                raise ValidationError(_('L\'heure limite doit être postérieure à l\'heure préférée.'))
    
    @api.constrains('duration_minutes', 'frequency_days')
    def _check_duration_frequency(self):
        for program in self:
            if program.duration_minutes <= 0:
                raise ValidationError(_('La durée doit être positive.'))
            if program.frequency_days and program.frequency_days <= 0:
                raise ValidationError(_('La fréquence doit être positive.'))
    
    @api.constrains('soil_moisture_threshold')
    def _check_moisture_threshold(self):
        for program in self:
            if program.soil_moisture_threshold and not (0 <= program.soil_moisture_threshold <= 100):
                raise ValidationError(_('Le seuil d\'humidité doit être entre 0 et 100%.'))
    
    # Méthodes de workflow
    def action_activate(self):
        """Activer le programme"""
        for program in self:
            if program.state not in ['draft', 'suspended']:
                raise ValidationError(_('Seuls les programmes en brouillon ou suspendus peuvent être activés.'))
            program.state = 'active'
    
    def action_suspend(self):
        """Suspendre le programme"""
        for program in self:
            if program.state != 'active':
                raise ValidationError(_('Seuls les programmes actifs peuvent être suspendus.'))
            program.state = 'suspended'
    
    def action_complete(self):
        """Terminer le programme"""
        for program in self:
            if program.state not in ['active', 'suspended']:
                raise ValidationError(_('Seuls les programmes actifs ou suspendus peuvent être terminés.'))
            program.state = 'completed'
    
    def action_cancel(self):
        """Annuler le programme"""
        for program in self:
            if program.state == 'completed':
                raise ValidationError(_('Un programme terminé ne peut pas être annulé.'))
            program.state = 'cancelled'
    
    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        for program in self:
            program.state = 'draft'
    
    # Méthodes métier
    def check_execution_conditions(self, weather_data=None):
        """Vérifier si les conditions d'exécution sont remplies"""
        self.ensure_one()
        
        # Vérifications de base
        if self.state != 'active':
            return False, _('Programme non actif')
        
        # Vérification des dates
        today = fields.Date.today()
        if self.start_date and today < self.start_date:
            return False, _('Date de début non atteinte')
        if self.end_date and today > self.end_date:
            return False, _('Date de fin dépassée')
        
        # Vérification de la fréquence
        if self.last_execution_date and self.frequency_days:
            next_date = self.last_execution_date.date() + timedelta(days=self.frequency_days)
            if today < next_date:
                return False, _('Fréquence non respectée')
        
        # Vérification des jours de la semaine
        if self.frequency_type == 'weekly':
            weekday = datetime.now().weekday()  # 0=Monday
            weekday_fields = [self.monday, self.tuesday, self.wednesday, self.thursday, 
                            self.friday, self.saturday, self.sunday]
            if not weekday_fields[weekday]:
                return False, _('Jour de la semaine non autorisé')
        
        # Vérification des conditions météo (si données fournies)
        if weather_data:
            if self.stop_if_rain and weather_data.get('precipitation', 0) >= self.rain_threshold_mm:
                return False, _('Pluie détectée')
            
            if self.temperature_min and weather_data.get('temperature', 0) < self.temperature_min:
                return False, _('Température trop basse')
            
            if self.temperature_max and weather_data.get('temperature', 0) > self.temperature_max:
                return False, _('Température trop élevée')
            
            if self.wind_speed_max and weather_data.get('wind_speed', 0) > self.wind_speed_max:
                return False, _('Vent trop fort')
        
        # Vérification humidité du sol (depuis analyses)
        if self.use_soil_analysis and self.soil_analysis_ids:
            latest_analysis = self.soil_analysis_ids.sorted('analysis_date', reverse=True)[0]
            # Logique simplifiée - à adapter selon les champs d'analyse
            soil_moisture = 50.0  # Valeur par défaut - à récupérer depuis l'analyse
            if self.stop_if_wet_soil and soil_moisture > (self.soil_moisture_threshold + 20):
                return False, _('Sol trop humide')
        
        return True, _('Conditions remplies')
    
    def create_irrigation_session(self):
        """Créer une nouvelle session d'irrigation basée sur ce programme"""
        self.ensure_one()
        
        # Vérifier les conditions
        can_execute, message = self.check_execution_conditions()
        if not can_execute:
            raise ValidationError(_('Impossible de créer la session: %s') % message)
        
        # Calculer l'heure de début
        now = datetime.now()
        start_hour = int(self.preferred_start_time)
        start_minute = int((self.preferred_start_time - start_hour) * 60)
        start_time = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        
        # Si l'heure est passée, programmer pour demain
        if start_time <= now:
            start_time += timedelta(days=1)
        
        # Créer la session
        session_vals = {
            'name': f'{self.name} - {start_time.strftime("%d/%m/%Y %H:%M")}',
            'program_id': self.id,
            'zone_id': self.zone_id.id,
            'system_id': self.system_id.id,
            'planned_start_datetime': start_time,
            'duration_minutes_planned': self.duration_minutes,
            'water_volume_target': self.water_volume_target,
            'session_type': 'automatic',
            'state': 'planned',
        }
        
        session = self.env['bsr.irrigation.session'].create(session_vals)
        return session
    
    def action_create_session(self):
        """Action pour créer une session d'irrigation"""
        self.ensure_one()
        try:
            session = self.create_irrigation_session()
            return {
                'name': _('Session créée'),
                'type': 'ir.actions.act_window',
                'res_model': 'bsr.irrigation.session',
                'res_id': session.id,
                'view_mode': 'form',
                'target': 'current',
            }
        except ValidationError as e:
            raise ValidationError(e)
    
    def action_view_sessions(self):
        """Voir les sessions du programme"""
        self.ensure_one()
        return {
            'name': f'Sessions - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.session',
            'view_mode': 'tree,form',
            'domain': [('program_id', '=', self.id)],
            'context': {'default_program_id': self.id},
        }
    
    @api.model
    def create(self, vals):
        """Générer automatiquement un code si non fourni"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.irrigation.program') or 'PROG-NEW'
        return super().create(vals)

    def name_get(self):
        """Format d'affichage personnalisé"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            if record.zone_id:
                name += f" ({record.zone_id.name})"
            result.append((record.id, name))
        return result