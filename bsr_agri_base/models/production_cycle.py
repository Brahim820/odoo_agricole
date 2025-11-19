# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


class ProductionCycle(models.Model):
    _name = 'bsr.production.cycle'
    _description = 'Cycle de Production'
    _order = 'harvest_date desc, culture_id'

    name = fields.Char('Nom du cycle', compute='_compute_name', store=True)
    
    # Relations
    culture_id = fields.Many2one('bsr.culture', string='Culture', required=True, ondelete='cascade')
    parcel_id = fields.Many2one(related='culture_id.parcel_id', string='Parcelle', store=True, readonly=True)
    farm_id = fields.Many2one(related='culture_id.farm_id', string='Ferme', store=True, readonly=True)
    
    # Informations du cycle
    cycle_year = fields.Integer('Année du cycle', required=True, default=lambda self: date.today().year)
    cycle_number = fields.Integer('Numéro du cycle dans l\'année', default=1)
    
    # Dates spécifiques au cycle
    planting_date = fields.Date('Date de plantation/taille')
    flowering_date = fields.Date('Date de floraison')
    fruit_set_date = fields.Date('Date de nouaison')
    harvest_date = fields.Date('Date de récolte prévue')
    actual_harvest_date = fields.Date('Date de récolte réelle')
    
    # Production
    expected_yield = fields.Float('Rendement attendu', digits=(10, 2))
    actual_yield = fields.Float('Rendement réel', digits=(10, 2))
    yield_unit = fields.Selection([
        ('kg', 'Kilogrammes'),
        ('t', 'Tonnes'),
        ('kg_ha', 'kg/hectare'),
        ('t_ha', 'tonnes/hectare'),
        ('kg_arbre', 'kg/arbre'),
        ('unites', 'Unités'),
    ], string='Unité de rendement', default='kg')
    
    # Qualité
    quality_grade = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Bon'),
        ('average', 'Moyen'),
        ('poor', 'Médiocre'),
    ], string='Qualité')
    
    # Finances du cycle
    cycle_cost = fields.Float('Coût du cycle', digits=(10, 2))
    cycle_revenue = fields.Float('Revenus du cycle', digits=(10, 2))
    cycle_profit = fields.Float('Bénéfice du cycle', compute='_compute_cycle_profit', store=True, digits=(10, 2))
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    
    # État du cycle
    state = fields.Selection([
        ('planned', 'Planifié'),
        ('in_progress', 'En cours'),
        ('harvested', 'Récolté'),
        ('sold', 'Vendu'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
    ], string='État', default='planned', required=True, tracking=True)
    
    # Conditions météo et observations
    weather_conditions = fields.Text('Conditions météorologiques')
    observations = fields.Text('Observations du cycle')
    
    # Traitements appliqués
    treatment_ids = fields.One2many('bsr.cycle.treatment', 'cycle_id', string='Traitements appliqués')
    
    # Statut
    active = fields.Boolean('Actif', default=True)

    @api.depends('culture_id', 'cycle_year', 'cycle_number')
    def _compute_name(self):
        for cycle in self:
            if cycle.culture_id:
                cycle.name = f"{cycle.culture_id.name} - {cycle.cycle_year} (Cycle {cycle.cycle_number})"
            else:
                cycle.name = f"Cycle {cycle.cycle_year}"

    @api.depends('cycle_revenue', 'cycle_cost')
    def _compute_cycle_profit(self):
        for cycle in self:
            cycle.cycle_profit = cycle.cycle_revenue - cycle.cycle_cost

    @api.constrains('harvest_date', 'actual_harvest_date', 'planting_date')
    def _check_dates(self):
        for cycle in self:
            if cycle.planting_date and cycle.harvest_date and cycle.harvest_date < cycle.planting_date:
                raise ValidationError(_('La date de récolte ne peut pas être antérieure à la date de plantation.'))
            if cycle.actual_harvest_date and cycle.planting_date and cycle.actual_harvest_date < cycle.planting_date:
                raise ValidationError(_('La date de récolte réelle ne peut pas être antérieure à la date de plantation.'))

    @api.constrains('cycle_year', 'culture_id', 'cycle_number')
    def _check_unique_cycle(self):
        for cycle in self:
            existing = self.search([
                ('culture_id', '=', cycle.culture_id.id),
                ('cycle_year', '=', cycle.cycle_year),
                ('cycle_number', '=', cycle.cycle_number),
                ('id', '!=', cycle.id)
            ])
            if existing:
                raise ValidationError(_('Un cycle avec ce numéro existe déjà pour cette culture et cette année.'))

    def action_start_cycle(self):
        """Démarrer le cycle de production"""
        self.state = 'in_progress'

    def action_harvest(self):
        """Marquer comme récolté"""
        self.state = 'harvested'
        if not self.actual_harvest_date:
            self.actual_harvest_date = fields.Date.context_today(self)

    def action_mark_sold(self):
        """Marquer comme vendu"""
        if self.state != 'harvested':
            raise ValidationError(_('Seuls les cycles récoltés peuvent être marqués comme vendus.'))
        self.state = 'sold'

    def action_complete(self):
        """Terminer le cycle"""
        self.state = 'completed'

    def action_cancel(self):
        """Annuler le cycle"""
        self.state = 'cancelled'

    @api.model
    def create_annual_cycles(self, culture_id, year, number_of_cycles=1):
        """Créer les cycles annuels pour une culture arboricole"""
        culture = self.env['bsr.culture'].browse(culture_id)
        if culture.culture_type_id.category != 'arboriculture':
            raise ValidationError(_('Cette fonction est réservée aux cultures arboricoles.'))
        
        cycles = []
        for i in range(1, number_of_cycles + 1):
            cycle_vals = {
                'culture_id': culture_id,
                'cycle_year': year,
                'cycle_number': i,
                'harvest_date': date(year, 6 + (i-1) * 3, 15),  # Exemple: juin, septembre, décembre
            }
            cycles.append(self.create(cycle_vals))
        return cycles


class CycleTreatment(models.Model):
    _name = 'bsr.cycle.treatment'
    _description = 'Traitement du Cycle'
    _order = 'application_date desc'

    cycle_id = fields.Many2one('bsr.production.cycle', string='Cycle de production', required=True, ondelete='cascade')
    
    name = fields.Char('Nom du traitement', required=True)
    treatment_type = fields.Selection([
        ('fertilizer', 'Fertilisation'),
        ('pesticide', 'Pesticide'),
        ('fungicide', 'Fongicide'),
        ('herbicide', 'Herbicide'),
        ('pruning', 'Taille'),
        ('irrigation', 'Irrigation'),
        ('other', 'Autre'),
    ], string='Type de traitement', required=True)
    
    application_date = fields.Date('Date d\'application', required=True)
    product_used = fields.Char('Produit utilisé')
    quantity = fields.Float('Quantité', digits=(10, 2))
    unit = fields.Char('Unité')
    cost = fields.Float('Coût du traitement', digits=(10, 2))
    
    notes = fields.Text('Notes sur le traitement')
    responsible_user_id = fields.Many2one('res.users', string='Responsable du traitement')
    
    active = fields.Boolean('Actif', default=True)