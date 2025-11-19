# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class ProductionCampaign(models.Model):
    _name = 'bsr.production.campaign'
    _description = 'Campagne de Production Agricole'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc, name'

    # === FIELDS === #
    name = fields.Char(
        string='Nom de Campagne',
        required=True,
        tracking=True,
        help="Nom de la campagne de production (ex: Campagne Hiver 2024-2025)"
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        copy=False,
        tracking=True,
        help="Code unique de la campagne"
    )
    
    description = fields.Text(
        string='Description',
        help="Description détaillée de la campagne"
    )
    
    # Dates
    start_date = fields.Date(
        string='Date de Début',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help="Date de début de la campagne"
    )
    
    end_date = fields.Date(
        string='Date de Fin',
        required=True,
        tracking=True,
        help="Date de fin prévue de la campagne"
    )
    
    # Relations
    farm_id = fields.Many2one(
        'bsr.farm',
        string='Ferme',
        required=True,
        tracking=True,
        help="Ferme concernée par cette campagne"
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        required=True,
        default=lambda self: self.env.company,
        help="Société propriétaire de la campagne"
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Responsable',
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        help="Responsable de la campagne"
    )
    
    # État
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('planned', 'Planifiée'),
        ('active', 'En Cours'),
        ('completed', 'Terminée'),
        ('cancelled', 'Annulée')
    ], string='État', default='draft', required=True, tracking=True)
    
    # Cycles de production
    cycle_ids = fields.One2many(
        'bsr.production.cycle',
        'campaign_id',
        string='Cycles de Production'
    )
    
    cycle_count = fields.Integer(
        string='Nombre de Cycles',
        compute='_compute_cycle_count',
        store=True
    )
    
    # Métriques
    total_area = fields.Float(
        string='Surface Totale (ha)',
        compute='_compute_metrics',
        store=True,
        help="Surface totale des cycles de la campagne"
    )
    
    total_planned_harvest = fields.Float(
        string='Récolte Prévue (kg)',
        compute='_compute_metrics',
        store=True,
        help="Quantité totale de récolte prévue"
    )
    
    progress = fields.Float(
        string='Avancement (%)',
        compute='_compute_progress',
        store=True,
        help="Pourcentage d'avancement de la campagne"
    )
    
    # Couleur pour kanban
    color = fields.Integer('Couleur', default=0)
    
    # Champs calculés pour durée
    duration_days = fields.Integer(
        string='Durée (jours)',
        compute='_compute_duration',
        store=True
    )
    
    # Active
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    # === COMPUTED FIELDS === #
    @api.depends('cycle_ids')
    def _compute_cycle_count(self):
        for campaign in self:
            campaign.cycle_count = len(campaign.cycle_ids)
    
    @api.depends('cycle_ids.parcel_id', 'cycle_ids.planned_harvest_qty')
    def _compute_metrics(self):
        for campaign in self:
            total_area = 0.0
            total_harvest = 0.0
            
            for cycle in campaign.cycle_ids:
                if cycle.parcel_id:
                    total_area += cycle.parcel_id.area
                total_harvest += cycle.planned_harvest_qty or 0.0
            
            campaign.total_area = total_area
            campaign.total_planned_harvest = total_harvest
    
    @api.depends('cycle_ids.progress')
    def _compute_progress(self):
        for campaign in self:
            if campaign.cycle_ids:
                avg_progress = sum(campaign.cycle_ids.mapped('progress')) / len(campaign.cycle_ids)
                campaign.progress = avg_progress
            else:
                campaign.progress = 0.0
    
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for campaign in self:
            if campaign.start_date and campaign.end_date:
                delta = campaign.end_date - campaign.start_date
                campaign.duration_days = delta.days + 1
            else:
                campaign.duration_days = 0
    
    # === CONSTRAINTS === #
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for campaign in self:
            if campaign.start_date and campaign.end_date:
                if campaign.end_date < campaign.start_date:
                    raise ValidationError(_("La date de fin doit être postérieure à la date de début."))
    
    @api.constrains('code')
    def _check_code_unique(self):
        for campaign in self:
            if campaign.code:
                existing = self.search([
                    ('code', '=', campaign.code),
                    ('id', '!=', campaign.id)
                ])
                if existing:
                    raise ValidationError(_("Le code de campagne doit être unique."))
    
    # === ONCHANGE === #
    @api.onchange('farm_id')
    def _onchange_farm_id(self):
        if self.farm_id:
            # Proposer un nom par défaut
            current_year = fields.Date.context_today(self).year
            self.name = f"Campagne {self.farm_id.name} {current_year}"
    
    # === CRUD === #
    @api.model
    def create(self, vals):
        # Générer un code automatique si non fourni
        if not vals.get('code'):
            vals['code'] = self.env['ir.sequence'].next_by_code('bsr.production.campaign') or 'NEW'
        
        campaign = super().create(vals)
        
        # Log de création
        _logger.info(f"Nouvelle campagne créée: {campaign.name} ({campaign.code})")
        
        return campaign
    
    # === ACTIONS === #
    def action_plan(self):
        """Planifier la campagne"""
        for campaign in self:
            if campaign.state != 'draft':
                raise UserError(_("Seules les campagnes en brouillon peuvent être planifiées."))
            
            # Validation avant planification
            if not campaign.cycle_ids:
                raise UserError(_("Impossible de planifier une campagne sans cycles de production."))
            
            campaign.write({'state': 'planned'})
            campaign.message_post(body=_("Campagne planifiée"))
        
        return True
    
    def action_start(self):
        """Démarrer la campagne"""
        for campaign in self:
            if campaign.state != 'planned':
                raise UserError(_("Seules les campagnes planifiées peuvent être démarrées."))
            
            campaign.write({'state': 'active'})
            campaign.message_post(body=_("Campagne démarrée"))
        
        return True
    
    def action_complete(self):
        """Terminer la campagne"""
        for campaign in self:
            if campaign.state != 'active':
                raise UserError(_("Seules les campagnes actives peuvent être terminées."))
            
            # Vérifier que tous les cycles sont terminés
            unfinished_cycles = campaign.cycle_ids.filtered(lambda c: c.state not in ('completed', 'cancelled'))
            if unfinished_cycles:
                raise UserError(_("Tous les cycles doivent être terminés avant de pouvoir terminer la campagne."))
            
            campaign.write({'state': 'completed'})
            campaign.message_post(body=_("Campagne terminée"))
        
        return True
    
    def action_cancel(self):
        """Annuler la campagne"""
        for campaign in self:
            if campaign.state in ('completed', 'cancelled'):
                raise UserError(_("Cette campagne ne peut pas être annulée."))
            
            campaign.write({'state': 'cancelled'})
            campaign.message_post(body=_("Campagne annulée"))
        
        return True
    
    def action_reset_to_draft(self):
        """Remettre en brouillon"""
        for campaign in self:
            campaign.write({'state': 'draft'})
            campaign.message_post(body=_("Campagne remise en brouillon"))
        
        return True
    
    def action_view_cycles(self):
        """Action pour voir les cycles de la campagne"""
        self.ensure_one()
        return {
            'name': f'Cycles de {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.production.cycle',
            'view_mode': 'tree,form,kanban',
            'domain': [('campaign_id', '=', self.id)],
            'context': {'default_campaign_id': self.id},
        }
    
    # === HELPERS === #
    def name_get(self):
        result = []
        for campaign in self:
            name = f"[{campaign.code}] {campaign.name}"
            result.append((campaign.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if name:
            # Recherche par code ou nom
            campaigns = self.search([
                '|',
                ('code', operator, name),
                ('name', operator, name)
            ] + args, limit=limit, access_uid=name_get_uid)
            return campaigns.name_get()
        return super()._name_search(name, args, operator, limit, name_get_uid)