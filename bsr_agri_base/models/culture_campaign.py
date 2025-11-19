# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class CultureCampaign(models.Model):
    _name = 'bsr.culture.campaign'
    _description = 'Campagne de Culture'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, season desc, culture_id'

    name = fields.Char('Nom de la campagne', compute='_compute_name', store=True)
    culture_id = fields.Many2one('bsr.culture', string='Culture principale', required=True, ondelete='cascade')
    
    # Informations temporelles
    year = fields.Integer('Année', required=True, default=lambda self: datetime.now().year)
    season = fields.Selection([
        ('spring', 'Printemps'),
        ('summer', 'Été'),
        ('autumn', 'Automne'), 
        ('winter', 'Hiver'),
    ], string='Saison')
    cycle_number = fields.Integer('Numéro du cycle', default=1, help="Numéro du cycle pour cette culture")
    
    # Dates du cycle
    start_date = fields.Date('Date de début', required=True)
    end_date = fields.Date('Date de fin')
    expected_end_date = fields.Date('Date de fin prévue')
    
    # États et phases
    state = fields.Selection([
        ('planned', 'Planifiée'),
        ('active', 'En cours'),
        ('completed', 'Terminée'),
        ('suspended', 'Suspendue'),
        ('cancelled', 'Annulée'),
    ], string='État', default='planned', tracking=True)
    
    # Données de production
    expected_yield = fields.Float('Rendement attendu', digits=(10, 2))
    actual_yield = fields.Float('Rendement réel', digits=(10, 2))
    yield_unit = fields.Selection([
        ('kg', 'Kilogrammes'),
        ('t', 'Tonnes'),
        ('l', 'Litres'),
        ('units', 'Unités'),
    ], string='Unité de rendement', default='kg')
    
    # Finances
    budget = fields.Float('Budget alloué', digits=(10, 2))
    actual_cost = fields.Float('Coût réel', digits=(10, 2))
    revenue = fields.Float('Revenus', digits=(10, 2))
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id)
    
    # Relations
    # Notes
    notes = fields.Text('Notes et observations')
    active = fields.Boolean('Actif', default=True)

    @api.depends('culture_id', 'year', 'season', 'cycle_number')
    def _compute_name(self):
        for campaign in self:
            if campaign.culture_id:
                parts = [campaign.culture_id.name, str(campaign.year)]
                if campaign.season:
                    seasons = dict(campaign._fields['season'].selection)
                    parts.append(seasons.get(campaign.season, ''))
                if campaign.cycle_number > 1:
                    parts.append(f'Cycle {campaign.cycle_number}')
                campaign.name = ' - '.join(parts)
            else:
                campaign.name = 'Nouvelle campagne'

    @api.constrains('start_date', 'end_date', 'expected_end_date')
    def _check_dates(self):
        for campaign in self:
            if campaign.end_date and campaign.start_date and campaign.end_date < campaign.start_date:
                raise ValidationError(_('La date de fin ne peut pas être antérieure à la date de début.'))
            if campaign.expected_end_date and campaign.start_date and campaign.expected_end_date < campaign.start_date:
                raise ValidationError(_('La date de fin prévue ne peut pas être antérieure à la date de début.'))

    @api.model
    def create_next_campaign(self, culture_id):
        """Créer automatiquement la campagne suivante pour une culture cyclique"""
        culture = self.env['bsr.culture'].browse(culture_id)
        if not culture.culture_type_id.is_cyclical:
            return False
            
        last_campaign = self.search([('culture_id', '=', culture_id)], order='year desc, cycle_number desc', limit=1)
        
        if last_campaign:
            # Calculer la date de début de la prochaine campagne
            last_start = fields.Date.from_string(str(last_campaign.start_date))
            months_to_add = culture.culture_type_id.cycle_duration_months or 12
            next_year = last_start.year + (months_to_add // 12)
            next_month = last_start.month + (months_to_add % 12)
            if next_month > 12:
                next_year += 1
                next_month -= 12
            next_start = last_start.replace(year=next_year, month=next_month)
            next_cycle = last_campaign.cycle_number + 1
        else:
            next_start = fields.Date.today()
            next_cycle = 1
            
        # Déterminer la saison
        month = next_start.month
        if 3 <= month <= 5:
            season = 'spring'
        elif 6 <= month <= 8:
            season = 'summer'
        elif 9 <= month <= 11:
            season = 'autumn'
        else:
            season = 'winter'
            
        # Calculer la date de fin prévue
        months_duration = culture.culture_type_id.cycle_duration_months or 12
        end_year = next_start.year + (months_duration // 12)
        end_month = next_start.month + (months_duration % 12)
        if end_month > 12:
            end_year += 1
            end_month -= 12
        expected_end = next_start.replace(year=end_year, month=end_month)
            
        new_campaign = self.create({
            'culture_id': culture_id,
            'year': next_start.year,
            'season': season,
            'cycle_number': next_cycle,
            'start_date': next_start,
            'expected_end_date': expected_end,
        })
        
        return new_campaign

    def action_start_campaign(self):
        """Démarrer la campagne"""
        self.ensure_one()
        if self.state != 'planned':
            raise ValidationError(_('Seules les campagnes planifiées peuvent être démarrées.'))
        self.state = 'active'

    def action_complete_campaign(self):
        """Terminer la campagne"""
        self.ensure_one()
        if self.state != 'active':
            raise ValidationError(_('Seules les campagnes actives peuvent être terminées.'))
        self.state = 'completed'
        self.end_date = fields.Date.today()
        
        # Créer automatiquement la campagne suivante si culture cyclique
        if self.culture_id.culture_type_id.is_cyclical:
            self.create_next_campaign(self.culture_id.id)

    def action_suspend_campaign(self):
        """Suspendre la campagne"""
        self.ensure_one()
        if self.state != 'active':
            raise ValidationError(_('Seules les campagnes actives peuvent être suspendues.'))
        self.state = 'suspended'

    def action_resume_campaign(self):
        """Reprendre la campagne"""
        self.ensure_one()
        if self.state != 'suspended':
            raise ValidationError(_('Seules les campagnes suspendues peuvent être reprises.'))
        self.state = 'active'

    def action_cancel_campaign(self):
        """Annuler la campagne"""
        self.ensure_one()
        if self.state in ['completed', 'cancelled']:
            raise ValidationError(_('Cette campagne ne peut pas être annulée.'))
        self.state = 'cancelled'