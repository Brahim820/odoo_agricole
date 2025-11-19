# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class ProductionCycle(models.Model):
    _name = 'bsr.production.cycle'
    _description = 'Cycle de Production'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, name'

    # === FIELDS === #
    name = fields.Char(
        string='Nom du Cycle',
        required=True,
        tracking=True,
        help="Nom du cycle de production"
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        copy=False,
        tracking=True,
        help="Code unique du cycle"
    )
    
    description = fields.Text(
        string='Description',
        help="Description du cycle de production"
    )
    
    # Relations principales
    campaign_id = fields.Many2one(
        'bsr.production.campaign',
        string='Campagne',
        required=True,
        ondelete='cascade',
        tracking=True,
        help="Campagne de production associée"
    )
    
    parcel_id = fields.Many2one(
        'bsr.parcel',
        string='Parcelle',
        required=True,
        tracking=True,
        help="Parcelle cultivée dans ce cycle"
    )
    
    culture_id = fields.Many2one(
        'bsr.culture',
        string='Culture',
        required=True,
        tracking=True,
        help="Culture produite dans ce cycle"
    )
    
    variety = fields.Char(
        string='Variété',
        tracking=True,
        help="Variété spécifique de la culture"
    )
    
    # Dates du cycle
    start_date = fields.Date(
        string='Date de Début',
        required=True,
        tracking=True,
        help="Date de début du cycle (généralement semis/plantation)"
    )
    
    planned_end_date = fields.Date(
        string='Fin Prévue',
        required=True,
        tracking=True,
        help="Date de fin prévue du cycle (récolte)"
    )
    
    actual_end_date = fields.Date(
        string='Fin Réelle',
        tracking=True,
        help="Date de fin réelle du cycle"
    )
    
    # Phase du cycle
    current_phase = fields.Selection([
        ('preparation', 'Préparation'),
        ('sowing', 'Semis/Plantation'),
        ('emergence', 'Levée'),
        ('growth', 'Croissance'),
        ('flowering', 'Floraison'),
        ('fruiting', 'Fructification'),
        ('maturation', 'Maturation'),
        ('harvest_ready', 'Prêt à Récolter'),
        ('harvest', 'Récolte'),
        ('post_harvest', 'Post-Récolte')
    ], string='Phase Actuelle', default='preparation', tracking=True)
    
    # État du cycle
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifié'),
        ('active', 'En Cours'),
        ('completed', 'Terminé'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulé')
    ], string='État', default='draft', required=True, tracking=True)
    
    # Surface et quantités
    cultivated_area = fields.Float(
        string='Surface Cultivée (ha)',
        required=True,
        help="Surface réellement cultivée"
    )
    
    planted_quantity = fields.Float(
        string='Quantité Plantée',
        help="Quantité de semences/plants utilisés"
    )
    
    planted_unit = fields.Char(
        string='Unité Plantée',
        default='kg',
        help="Unité de mesure pour la quantité plantée"
    )
    
    # Prévisions
    planned_harvest_qty = fields.Float(
        string='Récolte Prévue (kg)',
        help="Quantité de récolte prévue"
    )
    
    expected_yield = fields.Float(
        string='Rendement Attendu (kg/ha)',
        compute='_compute_expected_yield',
        store=True,
        help="Rendement attendu par hectare"
    )
    
    # Réalisé
    actual_harvest_qty = fields.Float(
        string='Récolte Réelle (kg)',
        help="Quantité réellement récoltée"
    )
    
    actual_yield = fields.Float(
        string='Rendement Réel (kg/ha)',
        compute='_compute_actual_yield',
        store=True,
        help="Rendement réel par hectare"
    )
    
    # Progression
    progress = fields.Float(
        string='Avancement (%)',
        compute='_compute_progress',
        store=True,
        help="Pourcentage d'avancement du cycle"
    )
    
    # Durée
    planned_duration = fields.Integer(
        string='Durée Prévue (jours)',
        compute='_compute_planned_duration',
        store=True
    )
    
    actual_duration = fields.Integer(
        string='Durée Réelle (jours)',
        compute='_compute_actual_duration',
        store=True
    )
    
    # Données héritées de la campagne
    farm_id = fields.Many2one(
        'bsr.farm',
        string='Ferme',
        related='campaign_id.farm_id',
        store=True,
        readonly=True
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        related='campaign_id.user_id',
        store=True,
        readonly=True
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        related='campaign_id.company_id',
        store=True,
        readonly=True
    )
    
    # Couleur pour kanban
    color = fields.Integer('Couleur', default=0)
    
    # Active
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    # === COMPUTED FIELDS === #
    @api.depends('planned_harvest_qty', 'cultivated_area')
    def _compute_expected_yield(self):
        for cycle in self:
            if cycle.cultivated_area > 0:
                cycle.expected_yield = cycle.planned_harvest_qty / cycle.cultivated_area
            else:
                cycle.expected_yield = 0.0
    
    @api.depends('actual_harvest_qty', 'cultivated_area')
    def _compute_actual_yield(self):
        for cycle in self:
            if cycle.cultivated_area > 0:
                cycle.actual_yield = cycle.actual_harvest_qty / cycle.cultivated_area
            else:
                cycle.actual_yield = 0.0
    
    @api.depends('current_phase', 'state')
    def _compute_progress(self):
        # Mapping des phases vers pourcentage
        phase_progress = {
            'preparation': 5,
            'sowing': 15,
            'emergence': 25,
            'growth': 45,
            'flowering': 65,
            'fruiting': 75,
            'maturation': 85,
            'harvest_ready': 90,
            'harvest': 95,
            'post_harvest': 100
        }
        
        for cycle in self:
            if cycle.state == 'completed':
                cycle.progress = 100
            elif cycle.state in ('failed', 'cancelled'):
                cycle.progress = 0
            else:
                cycle.progress = phase_progress.get(cycle.current_phase, 0)
    
    @api.depends('start_date', 'planned_end_date')
    def _compute_planned_duration(self):
        for cycle in self:
            if cycle.start_date and cycle.planned_end_date:
                delta = cycle.planned_end_date - cycle.start_date
                cycle.planned_duration = delta.days + 1
            else:
                cycle.planned_duration = 0
    
    @api.depends('start_date', 'actual_end_date')
    def _compute_actual_duration(self):
        for cycle in self:
            if cycle.start_date and cycle.actual_end_date:
                delta = cycle.actual_end_date - cycle.start_date
                cycle.actual_duration = delta.days + 1
            else:
                cycle.actual_duration = 0
    
    # === CONSTRAINTS === #
    @api.constrains('start_date', 'planned_end_date')
    def _check_planned_dates(self):
        for cycle in self:
            if cycle.start_date and cycle.planned_end_date:
                if cycle.planned_end_date < cycle.start_date:
                    raise ValidationError(_("La date de fin prévue doit être postérieure à la date de début."))
    
    @api.constrains('start_date', 'actual_end_date')
    def _check_actual_dates(self):
        for cycle in self:
            if cycle.start_date and cycle.actual_end_date:
                if cycle.actual_end_date < cycle.start_date:
                    raise ValidationError(_("La date de fin réelle doit être postérieure à la date de début."))
    
    @api.constrains('cultivated_area')
    def _check_cultivated_area(self):
        for cycle in self:
            if cycle.cultivated_area <= 0:
                raise ValidationError(_("La surface cultivée doit être positive."))
            
            # Vérifier que la surface ne dépasse pas celle de la parcelle
            if cycle.parcel_id and cycle.cultivated_area > cycle.parcel_id.area:
                raise ValidationError(_("La surface cultivée ne peut pas dépasser celle de la parcelle."))
    
    # === ONCHANGE === #
    @api.onchange('culture_id')
    def _onchange_culture_id(self):
        if self.culture_id:
            # Proposer un nom par défaut
            self.name = f"{self.culture_id.name} - {self.parcel_id.name if self.parcel_id else 'Parcelle'}"
    
    @api.onchange('parcel_id')
    def _onchange_parcel_id(self):
        if self.parcel_id:
            # Proposer la surface de la parcelle
            self.cultivated_area = self.parcel_id.area
            
            # Mettre à jour le nom si on a aussi la culture
            if self.culture_id:
                self.name = f"{self.culture_id.name} - {self.parcel_id.name}"
    
    @api.onchange('campaign_id')
    def _onchange_campaign_id(self):
        if self.campaign_id:
            # Limiter les parcelles à celles de la ferme
            return {
                'domain': {
                    'parcel_id': [('farm_id', '=', self.campaign_id.farm_id.id)]
                }
            }
    
    # === CRUD === #
    @api.model
    def create(self, vals):
        # Générer un code automatique si non fourni
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.production.cycle') or 'NEW'
        
        cycle = super().create(vals)
        
        # Log de création
        _logger.info(f"Nouveau cycle créé: {cycle.name} ({cycle.code})")
        
        return cycle
    
    # === ACTIONS === #
    def action_plan(self):
        """Planifier le cycle"""
        for cycle in self:
            if cycle.state != 'draft':
                raise UserError(_("Seuls les cycles en brouillon peuvent être planifiés."))
            
            cycle.write({'state': 'planned'})
            cycle.message_post(body=_("Cycle planifié"))
        
        return True
    
    def action_start(self):
        """Démarrer le cycle"""
        for cycle in self:
            if cycle.state != 'planned':
                raise UserError(_("Seuls les cycles planifiés peuvent être démarrés."))
            
            cycle.write({'state': 'active'})
            cycle.message_post(body=_("Cycle démarré"))
        
        return True
    
    def action_complete(self):
        """Terminer le cycle"""
        for cycle in self:
            if cycle.state != 'active':
                raise UserError(_("Seuls les cycles actifs peuvent être terminés."))
            
            cycle.write({
                'state': 'completed',
                'actual_end_date': fields.Date.context_today(self)
            })
            cycle.message_post(body=_("Cycle terminé"))
        
        return True
    
    def action_fail(self):
        """Marquer le cycle comme échec"""
        for cycle in self:
            if cycle.state not in ('active', 'planned'):
                raise UserError(_("Ce cycle ne peut pas être marqué en échec."))
            
            cycle.write({
                'state': 'failed',
                'actual_end_date': fields.Date.context_today(self)
            })
            cycle.message_post(body=_("Cycle marqué en échec"))
        
        return True
    
    def action_cancel(self):
        """Annuler le cycle"""
        for cycle in self:
            if cycle.state in ('completed', 'failed'):
                raise UserError(_("Ce cycle ne peut pas être annulé."))
            
            cycle.write({'state': 'cancelled'})
            cycle.message_post(body=_("Cycle annulé"))
        
        return True
    
    def action_advance_phase(self):
        """Avancer à la phase suivante"""
        phase_sequence = [
            'preparation', 'sowing', 'emergence', 'growth',
            'flowering', 'fruiting', 'maturation', 'harvest_ready',
            'harvest', 'post_harvest'
        ]
        
        for cycle in self:
            current_index = phase_sequence.index(cycle.current_phase)
            if current_index < len(phase_sequence) - 1:
                next_phase = phase_sequence[current_index + 1]
                cycle.write({'current_phase': next_phase})
                cycle.message_post(body=_("Phase avancée à: %s") % dict(cycle._fields['current_phase'].selection)[next_phase])
        
        return True
    
    # === HELPERS === #
    def name_get(self):
        result = []
        for cycle in self:
            name = f"[{cycle.code}] {cycle.name}"
            result.append((cycle.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Recherche par code ou nom
            cycles = self.search([
                '|',
                ('code', operator, name),
                ('name', operator, name)
            ] + args, limit=limit, access_uid=name_get_uid)
            return cycles.name_get()
        return super()._name_search(name, args, operator, limit, name_get_uid)