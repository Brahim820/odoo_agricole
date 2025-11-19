# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime


class Culture(models.Model):
    _name = 'bsr.culture'
    _description = 'Culture'
    _order = 'start_date desc, name'

    name = fields.Char('Nom de la culture', required=True)
    code = fields.Char('Code de la culture')
    
    # Type de culture
    culture_type_id = fields.Many2one('bsr.culture.type', string='Type de culture', required=True)
    variety = fields.Char('Variété')
    
    # Dates
    start_date = fields.Date('Date de début', required=True, default=fields.Date.context_today)
    expected_end_date = fields.Date('Date de fin prévue')
    actual_end_date = fields.Date('Date de fin réelle')
    
    # Relations
    parcel_id = fields.Many2one('bsr.parcel', string='Parcelle', required=True)
    farm_id = fields.Many2one(related='parcel_id.farm_id', string='Ferme', store=True, readonly=True)
    
    # Gestion des campagnes (cycles)
    campaign_ids = fields.One2many('bsr.culture.campaign', 'culture_id', string='Campagnes')
    campaign_count = fields.Integer('Nombre de campagnes', compute='_compute_campaign_count')
    current_campaign_id = fields.Many2one('bsr.culture.campaign', string='Campagne actuelle', 
                                          compute='_compute_current_campaign', store=True)
    is_cyclical = fields.Boolean(related='culture_type_id.is_cyclical', string='Culture cyclique', readonly=True)
    
    # Informations techniques
    planted_quantity = fields.Float('Quantité plantée', digits=(10, 2))
    planted_unit = fields.Selection([
        ('kg', 'Kilogrammes'),
        ('t', 'Tonnes'),
        ('plants', 'Plants'),
        ('graines', 'Graines'),
        ('m2', 'Mètres carrés'),
        ('ha', 'Hectares'),
    ], string='Unité', default='kg')
    
    expected_yield = fields.Float('Rendement attendu', digits=(10, 2))
    actual_yield = fields.Float('Rendement réel', digits=(10, 2))
    yield_unit = fields.Selection([
        ('kg_ha', 'kg/hectare'),
        ('t_ha', 'tonnes/hectare'),
        ('plants_m2', 'plants/m²'),
    ], string='Unité de rendement', default='kg_ha')
    
    # Coûts et revenus
    production_cost = fields.Float('Coût de production', digits=(10, 2))
    expected_revenue = fields.Float('Revenus attendus', digits=(10, 2))
    actual_revenue = fields.Float('Revenus réels', digits=(10, 2))
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    
    # Statut
    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('planted', 'Plantée'),
        ('growing', 'En croissance'),
        ('ready', 'Prête à récolter'),
        ('harvested', 'Récoltée'),
        ('finished', 'Terminée'),
        ('cancelled', 'Annulée'),
    ], string='État', default='planned')
    
    active = fields.Boolean('Actif', default=True)
    
    # Notes
    notes = fields.Text('Notes')
    
    # Champs calculés
    duration_days = fields.Integer('Durée (jours)', compute='_compute_duration', store=True)
    profitability = fields.Float('Rentabilité (%)', compute='_compute_profitability', store=True, digits=(5, 2))

    @api.depends('campaign_ids')
    def _compute_campaign_count(self):
        for culture in self:
            culture.campaign_count = len(culture.campaign_ids)

    @api.depends('campaign_ids', 'campaign_ids.state')
    def _compute_current_campaign(self):
        for culture in self:
            current_campaign = culture.campaign_ids.filtered(lambda c: c.state == 'active')
            culture.current_campaign_id = current_campaign[0] if current_campaign else False

    @api.depends('start_date', 'actual_end_date', 'expected_end_date')
    def _compute_duration(self):
        for culture in self:
            end_date = culture.actual_end_date or culture.expected_end_date
            if culture.start_date and end_date:
                culture.duration_days = (end_date - culture.start_date).days
            else:
                culture.duration_days = 0

    @api.depends('actual_revenue', 'production_cost')
    def _compute_profitability(self):
        for culture in self:
            if culture.production_cost > 0:
                culture.profitability = ((culture.actual_revenue - culture.production_cost) / culture.production_cost) * 100
            else:
                culture.profitability = 0.0

    @api.constrains('start_date', 'expected_end_date', 'actual_end_date')
    def _check_dates(self):
        for culture in self:
            if culture.expected_end_date and culture.start_date and culture.expected_end_date < culture.start_date:
                raise ValidationError(_('La date de fin prévue ne peut pas être antérieure à la date de début.'))
            if culture.actual_end_date and culture.start_date and culture.actual_end_date < culture.start_date:
                raise ValidationError(_('La date de fin réelle ne peut pas être antérieure à la date de début.'))

    @api.model
    def create(self, vals):
        culture = super().create(vals)
        # Mettre à jour la culture actuelle de la parcelle
        if culture.parcel_id:
            culture.parcel_id._update_current_culture()
        
        # Créer automatiquement la première campagne si la culture est cyclique
        if culture.culture_type_id.is_cyclical:
            self.env['bsr.culture.campaign'].create({
                'culture_id': culture.id,
                'year': culture.start_date.year,
                'start_date': culture.start_date,
                'expected_end_date': culture.expected_end_date,
                'cycle_number': 1,
                'state': 'planned',
            })
        
        return culture

    def write(self, vals):
        result = super().write(vals)
        # Mettre à jour la culture actuelle de la parcelle
        for culture in self:
            if culture.parcel_id:
                culture.parcel_id._update_current_culture()
        return result

    def action_start_planting(self):
        """Action pour commencer la plantation"""
        self.state = 'planted'

    def action_mark_growing(self):
        """Action pour marquer comme en croissance"""
        self.state = 'growing'

    def action_mark_ready(self):
        """Action pour marquer comme prête à récolter"""
        self.state = 'ready'

    def action_harvest(self):
        """Action pour marquer comme récoltée"""
        self.state = 'harvested'
        if not self.actual_end_date:
            self.actual_end_date = fields.Date.context_today(self)

    def action_finish(self):
        """Action pour terminer la culture"""
        self.state = 'finished'
        if not self.actual_end_date:
            self.actual_end_date = fields.Date.context_today(self)

    def action_cancel(self):
        """Action pour annuler la culture"""
        self.state = 'cancelled'
        
    def action_view_campaigns(self):
        """Action pour afficher les campagnes de cette culture"""
        self.ensure_one()
        return {
            'name': _('Campagnes - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.culture.campaign',
            'view_mode': 'tree,form,kanban',
            'domain': [('culture_id', '=', self.id)],
            'context': {
                'default_culture_id': self.id,
                'default_year': datetime.now().year,
            },
        }
        
    def action_create_next_campaign(self):
        """Créer la campagne suivante pour une culture cyclique"""
        self.ensure_one()
        if not self.is_cyclical:
            return False
        campaign_obj = self.env['bsr.culture.campaign']
        next_campaign = campaign_obj.create_next_campaign(self.id)
        if next_campaign:
            return {
                'name': _('Nouvelle campagne'),
                'type': 'ir.actions.act_window',
                'res_model': 'bsr.culture.campaign',
                'view_mode': 'form',
                'res_id': next_campaign.id,
                'target': 'new',
            }