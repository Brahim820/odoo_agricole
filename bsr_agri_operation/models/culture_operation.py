# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class CultureOperation(models.Model):
    _name = 'bsr.culture.operation'
    _description = 'Opération de Culture'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'planned_date, priority desc, name'

    # Identification
    name = fields.Char('Nom de l\'opération', required=True, tracking=True)
    sequence = fields.Char('Séquence', default='/')
    priority = fields.Selection([
        ('0', 'Normale'),
        ('1', 'Importante'),
        ('2', 'Urgente'),
    ], string='Priorité', default='0')

    # Relations principales
    campaign_id = fields.Many2one(
        'bsr.culture.campaign', 
        string='Campagne',
        required=True,
        ondelete='cascade',
        tracking=True
    )
    culture_id = fields.Many2one(
        related='campaign_id.culture_id',
        string='Culture',
        store=True,
        readonly=True
    )
    farm_id = fields.Many2one(
        related='culture_id.farm_id',
        string='Ferme',
        store=True,
        readonly=True
    )
    parcel_id = fields.Many2one(
        related='culture_id.parcel_id',
        string='Parcelle',
        store=True,
        readonly=True
    )

    # Type et catégorisation
    operation_type = fields.Selection([
        ('soil_preparation', 'Préparation du sol'),
        ('planting', 'Plantation/Semis'),
        ('irrigation', 'Irrigation'),
        ('fertilization', 'Fertilisation'),
        ('pest_control', 'Traitement phytosanitaire'),
        ('pruning', 'Taille'),
        ('weeding', 'Désherbage'),
        ('harvest', 'Récolte'),
        ('post_harvest', 'Post-récolte'),
        ('maintenance', 'Maintenance'),
        ('monitoring', 'Surveillance'),
        ('other', 'Autre'),
    ], string='Type d\'opération', required=True, tracking=True)

    # Planification temporelle
    planned_date = fields.Datetime('Date et heure prévues', required=True, tracking=True)
    planned_duration = fields.Float('Durée prévue (heures)', digits=(8, 2))
    deadline = fields.Datetime('Date limite')
    
    # Réalisation
    actual_start = fields.Datetime('Début effectif', tracking=True)
    actual_end = fields.Datetime('Fin effective', tracking=True)
    actual_duration = fields.Float('Durée réelle (heures)', compute='_compute_actual_duration', store=True)
    
    # État et workflow
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifiée'),
        ('ready', 'Prête'),
        ('in_progress', 'En cours'),
        ('paused', 'En pause'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='draft', tracking=True)

    # Ressources humaines
    responsible_id = fields.Many2one('hr.employee', string='Responsable')
    employee_ids = fields.Many2many('hr.employee', string='Équipe')
    external_contractor = fields.Char('Prestataire externe')

    # Équipements et matériel
    equipment_ids = fields.Many2many('maintenance.equipment', string='Équipements')
    vehicle_ids = fields.Many2many('fleet.vehicle', string='Véhicules')
    tool_ids = fields.Many2many('product.product', string='Outils et matériel')

    # Produits et consommables
    product_line_ids = fields.One2many('bsr.operation.product.line', 'operation_id', string='Produits utilisés')
    
    # Localisation et surface
    work_area = fields.Float('Surface travaillée (ha)', digits=(10, 4))
    gps_coordinates = fields.Char('Coordonnées GPS')
    weather_conditions = fields.Text('Conditions météorologiques')

    # Coûts et finances
    estimated_cost = fields.Float('Coût estimé', digits='Product Price')
    actual_cost = fields.Float('Coût réel', compute='_compute_actual_cost', store=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # Qualité et résultats
    quality_rating = fields.Selection([
        ('1', 'Très mauvais'),
        ('2', 'Mauvais'), 
        ('3', 'Moyen'),
        ('4', 'Bon'),
        ('5', 'Excellent'),
    ], string='Évaluation qualité')
    
    yield_quantity = fields.Float('Quantité produite', digits=(10, 2))
    yield_unit = fields.Many2one('uom.uom', string='Unité de mesure')
    
    # Documentation
    description = fields.Html('Description')
    internal_notes = fields.Text('Notes internes')
    client_notes = fields.Text('Notes client')
    attachment_ids = fields.Many2many('ir.attachment', string='Pièces jointes')

    # Méta-données
    active = fields.Boolean('Actif', default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # Champs calculés et techniques
    delay_days = fields.Integer('Retard (jours)', compute='_compute_delays', store=True)
    is_delayed = fields.Boolean('En retard', compute='_compute_delays', store=True)
    completion_rate = fields.Float('Taux de completion (%)', compute='_compute_completion_rate')

    @api.depends('actual_start', 'actual_end')
    def _compute_actual_duration(self):
        for operation in self:
            if operation.actual_start and operation.actual_end:
                delta = operation.actual_end - operation.actual_start
                operation.actual_duration = delta.total_seconds() / 3600.0
            else:
                operation.actual_duration = 0.0

    @api.depends('product_line_ids.total_cost')
    def _compute_actual_cost(self):
        for operation in self:
            total_cost = 0.0
            
            # Coût des produits
            for line in operation.product_line_ids:
                total_cost += line.total_cost
                
            # TODO: Coût de la main d'œuvre (si configuré)
            # TODO: Coût des équipements (amortissement)
            
            operation.actual_cost = total_cost

    @api.depends('planned_date', 'deadline', 'state')
    def _compute_delays(self):
        today = fields.Datetime.now()
        for operation in self:
            if operation.deadline:
                if today > operation.deadline and operation.state not in ['completed', 'cancelled']:
                    delta = today - operation.deadline
                    operation.delay_days = delta.days
                    operation.is_delayed = True
                else:
                    operation.delay_days = 0
                    operation.is_delayed = False
            else:
                operation.delay_days = 0
                operation.is_delayed = False

    @api.depends('state', 'planned_date', 'actual_end')
    def _compute_completion_rate(self):
        for operation in self:
            if operation.state == 'completed':
                operation.completion_rate = 100.0
            elif operation.state == 'cancelled':
                operation.completion_rate = 0.0
            elif operation.state in ['in_progress', 'paused']:
                # Calcul basé sur le temps écoulé
                if operation.actual_start and operation.planned_duration > 0:
                    elapsed = fields.Datetime.now() - operation.actual_start
                    elapsed_hours = elapsed.total_seconds() / 3600.0
                    rate = min(100.0, (elapsed_hours / operation.planned_duration) * 100.0)
                    operation.completion_rate = rate
                else:
                    operation.completion_rate = 50.0  # Estimation par défaut
            else:
                operation.completion_rate = 0.0

    def action_plan(self):
        """Passer à l'état planifié"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Seules les opérations en brouillon peuvent être planifiées.'))
        self.state = 'planned'
        self.message_post(body=_('Opération planifiée'))

    def action_ready(self):
        """Marquer comme prête"""
        self.ensure_one()
        if self.state != 'planned':
            raise ValidationError(_('L\'opération doit être planifiée pour être marquée comme prête.'))
        self.state = 'ready'
        self.message_post(body=_('Opération prête à être exécutée'))

    def action_start(self):
        """Démarrer l'opération"""
        self.ensure_one()
        if self.state not in ['planned', 'ready']:
            raise ValidationError(_('L\'opération doit être planifiée ou prête pour être démarrée.'))
        self.state = 'in_progress'
        if not self.actual_start:
            self.actual_start = fields.Datetime.now()
        self.message_post(body=_('Opération démarrée'))

    def action_pause(self):
        """Mettre en pause l'opération"""
        self.ensure_one()
        if self.state != 'in_progress':
            raise ValidationError(_('Seules les opérations en cours peuvent être mises en pause.'))
        self.state = 'paused'
        self.message_post(body=_('Opération mise en pause'))

    def action_resume(self):
        """Reprendre l'opération"""
        self.ensure_one()
        if self.state != 'paused':
            raise ValidationError(_('Seules les opérations en pause peuvent être reprises.'))
        self.state = 'in_progress'
        self.message_post(body=_('Opération reprise'))

    def action_complete(self):
        """Terminer l'opération"""
        self.ensure_one()
        if self.state not in ['in_progress', 'paused']:
            raise ValidationError(_('L\'opération doit être en cours ou en pause pour être terminée.'))
        self.state = 'completed'
        if not self.actual_end:
            self.actual_end = fields.Datetime.now()
        self.message_post(body=_('Opération terminée'))

    def action_cancel(self):
        """Annuler l'opération"""
        self.ensure_one()
        if self.state in ['completed']:
            raise ValidationError(_('Une opération terminée ne peut pas être annulée.'))
        self.state = 'cancelled'
        self.message_post(body=_('Opération annulée'))

    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        self.ensure_one()
        if self.state not in ['cancelled']:
            raise ValidationError(_('Seules les opérations annulées peuvent être remises en brouillon.'))
        self.state = 'draft'
        self.actual_start = False
        self.actual_end = False
        self.message_post(body=_('Opération remise en brouillon'))

    def action_view_progress(self):
        """Action pour voir les détails de progression"""
        self.ensure_one()
        # Action vide pour les boutons statistiques
        return True

    def action_view_delay(self):
        """Action pour voir les détails du retard"""
        self.ensure_one()
        # Action vide pour les boutons statistiques
        return True

    @api.model
    def create(self, vals):
        if vals.get('sequence', '/') == '/':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('bsr.culture.operation') or '/'
        return super().create(vals)

    @api.constrains('planned_date', 'deadline')
    def _check_dates(self):
        for operation in self:
            if operation.deadline and operation.planned_date:
                if operation.deadline < operation.planned_date:
                    raise ValidationError(_('La date limite ne peut pas être antérieure à la date prévue.'))

    @api.constrains('actual_start', 'actual_end')
    def _check_actual_dates(self):
        for operation in self:
            if operation.actual_start and operation.actual_end:
                if operation.actual_end < operation.actual_start:
                    raise ValidationError(_('La date de fin ne peut pas être antérieure à la date de début.'))

    def name_get(self):
        result = []
        for operation in self:
            name = f"[{operation.sequence}] {operation.name}"
            if operation.campaign_id:
                name += f" - {operation.campaign_id.name}"
            result.append((operation.id, name))
        return result

    @api.model
    def _check_delayed_operations(self):
        """Méthode appelée par le cron pour identifier les opérations en retard"""
        delayed_operations = self.search([
            ('is_delayed', '=', True),
            ('state', 'not in', ['completed', 'cancelled'])
        ])
        
        # Créer des activités pour alerter les responsables
        for operation in delayed_operations:
            if operation.responsible_id and operation.responsible_id.user_id:
                operation.activity_schedule(
                    'mail.mail_activity_data_warning',
                    user_id=operation.responsible_id.user_id.id,
                    summary=f"Opération en retard: {operation.name}",
                    note=f"L'opération {operation.name} est en retard de {operation.delay_days} jours."
                )

    @api.model
    def _auto_start_ready_operations(self):
        """Méthode appelée par le cron pour démarrer automatiquement les opérations prêtes"""
        ready_operations = self.search([
            ('state', '=', 'ready'),
            ('planned_date', '<=', fields.Datetime.now())
        ])
        
        for operation in ready_operations:
            try:
                operation.action_start()
            except Exception as e:
                _logger.warning(f"Impossible de démarrer automatiquement l'opération {operation.id}: {e}")