# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class IrrigationAlert(models.Model):
    _name = 'bsr.irrigation.alert'
    _description = 'Alerte irrigation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority_score desc, create_date desc'

    name = fields.Char('Titre de l\'alerte', required=True, tracking=True)
    code = fields.Char('Code alerte', tracking=True)
    description = fields.Text('Description', tracking=True)
    
    # Type et catégorie d'alerte
    alert_type = fields.Selection([
        ('equipment', 'Équipement'),
        ('water', 'Eau'),
        ('weather', 'Météo'),
        ('soil', 'Sol'),
        ('maintenance', 'Maintenance'),
        ('schedule', 'Planning'),
        ('quality', 'Qualité'),
        ('system', 'Système'),
    ], string='Type d\'alerte', required=True, tracking=True)
    
    priority = fields.Selection([
        ('info', 'Information'),
        ('warning', 'Attention'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
        ('emergency', 'Urgence'),
    ], string='Priorité', required=True, default='warning', tracking=True)
    
    priority_score = fields.Integer('Score priorité', compute='_compute_priority_score', store=True)
    
    # Relations
    system_id = fields.Many2one('bsr.irrigation.system', string='Système d\'irrigation', tracking=True)
    zone_id = fields.Many2one('bsr.irrigation.zone', string='Zone d\'irrigation', tracking=True)
    session_id = fields.Many2one('bsr.irrigation.session', string='Session d\'irrigation', tracking=True)
    program_id = fields.Many2one('bsr.irrigation.program', string='Programme d\'irrigation', tracking=True)
    farm_id = fields.Many2one('bsr.farm', string='Ferme', compute='_compute_farm_id', store=True)
    
    # Conditions de déclenchement
    trigger_condition = fields.Text('Condition de déclenchement')
    trigger_value = fields.Float('Valeur déclenchement', digits=(12, 4))
    threshold_value = fields.Float('Seuil d\'alerte', digits=(12, 4))
    
    # Dates et temporalité
    detected_datetime = fields.Datetime('Date détection', default=lambda self: datetime.now(), tracking=True)
    acknowledged_datetime = fields.Datetime('Date accusé réception', tracking=True)
    resolved_datetime = fields.Datetime('Date résolution', tracking=True)
    
    # Durées calculées
    response_time = fields.Float('Temps de réponse (h)', compute='_compute_response_time', store=True)
    resolution_time = fields.Float('Temps de résolution (h)', compute='_compute_resolution_time', store=True)
    
    # Personnes responsables
    assigned_user_id = fields.Many2one('res.users', string='Assigné à', tracking=True)
    acknowledged_by = fields.Many2one('res.users', string='Accusé par', tracking=True)
    resolved_by = fields.Many2one('res.users', string='Résolu par', tracking=True)
    
    # État et suivi
    state = fields.Selection([
        ('active', 'Active'),
        ('acknowledged', 'Accusée'),
        ('in_progress', 'En cours'),
        ('resolved', 'Résolue'),
        ('dismissed', 'Ignorée'),
        ('escalated', 'Escaladée'),
    ], string='État', default='active', required=True, tracking=True)
    
    # Actions et résolution
    recommended_action = fields.Text('Action recommandée')
    action_taken = fields.Text('Action entreprise', tracking=True)
    resolution_notes = fields.Text('Notes de résolution', tracking=True)
    
    # Impact et conséquences
    impact_level = fields.Selection([
        ('low', 'Faible'),
        ('medium', 'Moyen'),
        ('high', 'Élevé'),
        ('critical', 'Critique'),
    ], string='Niveau d\'impact', default='medium')
    
    affected_area = fields.Float('Zone affectée (hectares)', digits=(10, 4))
    estimated_loss = fields.Float('Perte estimée (€)', digits=(10, 2))
    
    # Récurrence et historique
    is_recurring = fields.Boolean('Alerte récurrente')
    recurrence_count = fields.Integer('Nombre d\'occurrences', default=1)
    parent_alert_id = fields.Many2one('bsr.irrigation.alert', string='Alerte parente')
    child_alert_ids = fields.One2many('bsr.irrigation.alert', 'parent_alert_id', string='Alertes liées')
    
    # Notifications
    email_sent = fields.Boolean('Email envoyé', default=False)
    sms_sent = fields.Boolean('SMS envoyé', default=False)
    notification_count = fields.Integer('Notifications envoyées', default=0)
    
    # Métriques de performance
    auto_resolved = fields.Boolean('Résolution automatique', default=False)
    manual_intervention = fields.Boolean('Intervention manuelle', default=True)
    
    active = fields.Boolean('Actif', default=True)
    
    @api.depends('priority')
    def _compute_priority_score(self):
        priority_scores = {
            'info': 1,
            'warning': 2,
            'high': 3,
            'critical': 4,
            'emergency': 5,
        }
        for alert in self:
            alert.priority_score = priority_scores.get(alert.priority, 2)
    
    @api.depends('system_id', 'zone_id', 'session_id')
    def _compute_farm_id(self):
        for alert in self:
            farm_id = False
            if alert.system_id:
                farm_id = alert.system_id.farm_id.id
            elif alert.zone_id:
                farm_id = alert.zone_id.farm_id.id
            elif alert.session_id:
                farm_id = alert.session_id.farm_id.id
            alert.farm_id = farm_id
    
    @api.depends('detected_datetime', 'acknowledged_datetime')
    def _compute_response_time(self):
        for alert in self:
            if alert.detected_datetime and alert.acknowledged_datetime:
                delta = alert.acknowledged_datetime - alert.detected_datetime
                alert.response_time = delta.total_seconds() / 3600
            else:
                alert.response_time = 0.0
    
    @api.depends('detected_datetime', 'resolved_datetime')
    def _compute_resolution_time(self):
        for alert in self:
            if alert.detected_datetime and alert.resolved_datetime:
                delta = alert.resolved_datetime - alert.detected_datetime
                alert.resolution_time = delta.total_seconds() / 3600
            else:
                alert.resolution_time = 0.0
    
    # Contraintes et validations
    @api.constrains('detected_datetime', 'acknowledged_datetime', 'resolved_datetime')
    def _check_datetime_sequence(self):
        for alert in self:
            if alert.acknowledged_datetime and alert.detected_datetime and alert.acknowledged_datetime < alert.detected_datetime:
                raise ValidationError(_('La date d\'accusé de réception ne peut pas être antérieure à la date de détection.'))
            if alert.resolved_datetime and alert.detected_datetime and alert.resolved_datetime < alert.detected_datetime:
                raise ValidationError(_('La date de résolution ne peut pas être antérieure à la date de détection.'))
    
    @api.constrains('trigger_value', 'threshold_value')
    def _check_threshold_values(self):
        for alert in self:
            if alert.threshold_value and alert.trigger_value and alert.alert_type in ['water', 'soil']:
                # Logique de validation selon le type d'alerte
                pass
    
    # Méthodes de workflow
    def action_acknowledge(self):
        """Accuser réception de l'alerte"""
        for alert in self:
            if alert.state not in ['active']:
                raise ValidationError(_('Seules les alertes actives peuvent être accusées.'))
            
            alert.write({
                'state': 'acknowledged',
                'acknowledged_datetime': datetime.now(),
                'acknowledged_by': self.env.user.id,
            })
    
    def action_start_resolution(self):
        """Commencer la résolution"""
        for alert in self:
            if alert.state not in ['active', 'acknowledged']:
                raise ValidationError(_('Seules les alertes actives ou accusées peuvent être mises en cours de résolution.'))
            
            alert.write({
                'state': 'in_progress',
                'assigned_user_id': self.env.user.id,
            })
    
    def action_resolve(self):
        """Résoudre l'alerte"""
        for alert in self:
            if alert.state not in ['acknowledged', 'in_progress']:
                raise ValidationError(_('Seules les alertes accusées ou en cours peuvent être résolues.'))
            
            alert.write({
                'state': 'resolved',
                'resolved_datetime': datetime.now(),
                'resolved_by': self.env.user.id,
            })
    
    def action_dismiss(self):
        """Ignorer l'alerte"""
        for alert in self:
            if alert.state in ['resolved']:
                raise ValidationError(_('Une alerte résolue ne peut pas être ignorée.'))
            
            alert.write({
                'state': 'dismissed',
                'resolved_datetime': datetime.now(),
                'resolved_by': self.env.user.id,
            })
    
    def action_escalate(self):
        """Escalader l'alerte"""
        for alert in self:
            if alert.state in ['resolved', 'dismissed']:
                raise ValidationError(_('Une alerte résolue ou ignorée ne peut pas être escaladée.'))
            
            # Changer la priorité si pas déjà au maximum
            if alert.priority != 'emergency':
                priority_levels = ['info', 'warning', 'high', 'critical', 'emergency']
                current_index = priority_levels.index(alert.priority)
                new_priority = priority_levels[min(current_index + 1, len(priority_levels) - 1)]
                alert.priority = new_priority
            
            alert.state = 'escalated'
    
    def action_reactivate(self):
        """Réactiver une alerte ignorée"""
        for alert in self:
            if alert.state != 'dismissed':
                raise ValidationError(_('Seules les alertes ignorées peuvent être réactivées.'))
            
            alert.write({
                'state': 'active',
                'resolved_datetime': False,
                'resolved_by': False,
            })
    
    # Méthodes métier
    def send_notification(self, notification_type='email'):
        """Envoyer une notification pour l'alerte"""
        self.ensure_one()
        
        # Déterminer les destinataires
        recipients = []
        if self.assigned_user_id:
            recipients.append(self.assigned_user_id.partner_id)
        
        # Ajouter superviseurs selon la priorité
        if self.priority in ['critical', 'emergency']:
            supervisor_group = self.env.ref('bsr_agri_irrigation.group_irrigation_supervisor', raise_if_not_found=False)
            if supervisor_group:
                recipients.extend([user.partner_id for user in supervisor_group.users])
        
        if not recipients:
            return False
        
        # Créer le message
        subject = f"[{self.priority.upper()}] {self.name}"
        body = f"""
        Nouvelle alerte irrigation détectée:
        
        Type: {dict(self._fields['alert_type'].selection)[self.alert_type]}
        Priorité: {dict(self._fields['priority'].selection)[self.priority]}
        
        Description: {self.description or 'N/A'}
        
        Système: {self.system_id.name if self.system_id else 'N/A'}
        Zone: {self.zone_id.name if self.zone_id else 'N/A'}
        Ferme: {self.farm_id.name if self.farm_id else 'N/A'}
        
        Date de détection: {self.detected_datetime.strftime('%d/%m/%Y %H:%M')}
        
        Action recommandée: {self.recommended_action or 'Voir détails de l\'alerte'}
        """
        
        # Envoi via le système de mail d'Odoo
        for partner in recipients:
            self.message_post(
                partner_ids=[partner.id],
                subject=subject,
                body=body,
                message_type='email',
            )
        
        # Marquer comme envoyé
        self.write({
            'email_sent': True,
            'notification_count': self.notification_count + 1,
        })
        
        return True
    
    def check_recurrence(self):
        """Vérifier si l'alerte est récurrente"""
        self.ensure_one()
        
        # Rechercher des alertes similaires dans les dernières 24h
        domain = [
            ('alert_type', '=', self.alert_type),
            ('system_id', '=', self.system_id.id if self.system_id else False),
            ('zone_id', '=', self.zone_id.id if self.zone_id else False),
            ('detected_datetime', '>=', datetime.now() - timedelta(hours=24)),
            ('id', '!=', self.id),
        ]
        
        similar_alerts = self.search(domain)
        
        if similar_alerts:
            self.write({
                'is_recurring': True,
                'recurrence_count': len(similar_alerts) + 1,
                'parent_alert_id': similar_alerts[0].id,
            })
            
            # Mettre à jour l'alerte parente
            parent_alert = similar_alerts[0]
            if not parent_alert.parent_alert_id:
                parent_alert.write({
                    'is_recurring': True,
                    'recurrence_count': len(similar_alerts) + 1,
                })
    
    def get_resolution_suggestions(self):
        """Obtenir des suggestions de résolution basées sur l'historique"""
        self.ensure_one()
        
        # Rechercher des alertes similaires résolues
        domain = [
            ('alert_type', '=', self.alert_type),
            ('state', '=', 'resolved'),
            ('resolution_notes', '!=', False),
        ]
        
        if self.system_id:
            domain.append(('system_id', '=', self.system_id.id))
        elif self.zone_id:
            domain.append(('zone_id', '=', self.zone_id.id))
        
        resolved_alerts = self.search(domain, limit=5, order='resolved_datetime desc')
        
        suggestions = []
        for alert in resolved_alerts:
            if alert.resolution_notes:
                suggestions.append({
                    'alert': alert,
                    'resolution': alert.resolution_notes,
                    'resolution_time': alert.resolution_time,
                    'success': True,
                })
        
        return suggestions
    
    def action_create_maintenance_request(self):
        """Créer une demande de maintenance basée sur l'alerte"""
        self.ensure_one()
        
        if self.alert_type != 'equipment' or not self.system_id:
            raise ValidationError(_('Cette action n\'est disponible que pour les alertes d\'équipement avec un système défini.'))
        
        if not self.system_id.equipment_id:
            raise ValidationError(_('Aucun équipement de maintenance associé au système.'))
        
        return {
            'name': _('Demande de maintenance'),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'context': {
                'default_equipment_id': self.system_id.equipment_id.id,
                'default_name': f'Maintenance suite alerte - {self.name}',
                'default_description': f'Alerte: {self.description}\nAction recommandée: {self.recommended_action}',
                'default_priority': '3' if self.priority in ['critical', 'emergency'] else '2',
            },
            'target': 'new',
        }
    
    @api.model
    def create_automatic_alert(self, alert_data):
        """Créer automatiquement une alerte (utilisé par les systèmes de monitoring)"""
        alert_vals = {
            'name': alert_data.get('name', 'Alerte automatique'),
            'description': alert_data.get('description', ''),
            'alert_type': alert_data.get('alert_type', 'system'),
            'priority': alert_data.get('priority', 'warning'),
            'system_id': alert_data.get('system_id'),
            'zone_id': alert_data.get('zone_id'),
            'session_id': alert_data.get('session_id'),
            'trigger_condition': alert_data.get('trigger_condition'),
            'trigger_value': alert_data.get('trigger_value'),
            'threshold_value': alert_data.get('threshold_value'),
            'recommended_action': alert_data.get('recommended_action'),
        }
        
        alert = self.create(alert_vals)
        
        # Vérifier la récurrence
        alert.check_recurrence()
        
        # Envoyer notification si priorité élevée
        if alert.priority in ['high', 'critical', 'emergency']:
            alert.send_notification()
        
        return alert
    
    @api.model
    def create(self, vals):
        """Générer automatiquement un code si non fourni"""
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.irrigation.alert') or 'ALERT-NEW'
        return super().create(vals)

    def name_get(self):
        """Format d'affichage personnalisé"""
        result = []
        for record in self:
            name = record.name
            if record.code:
                name = f"[{record.code}] {name}"
            
            priority_label = dict(record._fields['priority'].selection)[record.priority]
            name += f" ({priority_label})"
            
            result.append((record.id, name))
        return result

    def action_view_session(self):
        """Ouvre la vue de la session d'irrigation liée"""
        if not self.session_id:
            return False
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Session d\'irrigation'),
            'res_model': 'bsr.irrigation.session',
            'res_id': self.session_id.id,
            'view_mode': 'form',
            'target': 'current',
        }