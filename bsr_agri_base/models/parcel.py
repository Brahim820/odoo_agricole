# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Parcel(models.Model):
    _name = 'bsr.parcel'
    _description = 'Parcelle'
    _order = 'farm_id, name'

    name = fields.Char('Nom de la parcelle', required=True)
    code = fields.Char('Code de la parcelle')
    description = fields.Text('Description')
    
    # Relation avec la ferme
    farm_id = fields.Many2one('bsr.farm', string='Ferme', required=True, ondelete='cascade')
    
    # Informations techniques
    surface = fields.Float('Surface (hectares)', required=True, digits=(10, 2))
    soil_type = fields.Selection([
        ('argile', 'Argile'),
        ('sable', 'Sable'),
        ('limon', 'Limon'),
        ('argilo_sableux', 'Argilo-sableux'),
        ('argilo_limoneux', 'Argilo-limoneux'),
        ('sablo_limoneux', 'Sablo-limoneux'),
        ('autres', 'Autres'),
    ], string='Type de sol')
    
    slope = fields.Selection([
        ('plat', 'Plat (0-2%)'),
        ('leger', 'Pente légère (2-5%)'),
        ('moyen', 'Pente moyenne (5-10%)'),
        ('fort', 'Pente forte (>10%)'),
    ], string='Pente')
    
    irrigation = fields.Boolean('Irrigation disponible', default=False)
    
    # Localisation GPS
    latitude = fields.Float('Latitude', digits=(10, 6))
    longitude = fields.Float('Longitude', digits=(10, 6))
    
    # Relation avec culture (une parcelle = une culture)
    culture_id = fields.Many2one('bsr.culture', string='Culture actuelle')
    culture_ids = fields.One2many('bsr.culture', 'parcel_id', string='Historique des cultures')
    culture_count = fields.Integer('Nombre de cultures', compute='_compute_culture_count')
    
    # Relations avec les équipements
    equipment_ids = fields.One2many('maintenance.equipment', 'parcel_id', string='Équipements')
    equipment_count = fields.Integer('Nombre d\'équipements', compute='_compute_equipment_count')
    vehicle_ids = fields.Many2many('fleet.vehicle', string='Véhicules utilisés')
    vehicle_count = fields.Integer('Nombre de véhicules', compute='_compute_vehicle_count')
    irrigation_consumable_ids = fields.Many2many('bsr.irrigation.consumable', 'bsr_parcel_irrigation_rel', 'parcel_id', 'consumable_id', string='Consommables d\'irrigation')
    irrigation_consumable_count = fields.Integer('Nombre de consommables', compute='_compute_irrigation_consumable_count')
    
    # Statut
    active = fields.Boolean('Actif', default=True)
    state = fields.Selection([
        ('available', 'Disponible'),
        ('cultivated', 'Cultivée'),
        ('rest', 'En repos'),
        ('maintenance', 'En maintenance'),
    ], string='État', default='available')

    @api.depends('culture_ids')
    def _compute_culture_count(self):
        for parcel in self:
            parcel.culture_count = len(parcel.culture_ids)

    @api.depends('equipment_ids')
    def _compute_equipment_count(self):
        for parcel in self:
            parcel.equipment_count = len(parcel.equipment_ids)

    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for parcel in self:
            parcel.vehicle_count = len(parcel.vehicle_ids)

    @api.depends('irrigation_consumable_ids')
    def _compute_irrigation_consumable_count(self):
        for parcel in self:
            parcel.irrigation_consumable_count = len(parcel.irrigation_consumable_ids)

    @api.constrains('surface')
    def _check_surface(self):
        for parcel in self:
            if parcel.surface <= 0:
                raise ValidationError(_('La surface de la parcelle doit être positive.'))

    @api.onchange('culture_id')
    def _onchange_culture_id(self):
        if self.culture_id:
            self.state = 'cultivated'
        else:
            self.state = 'available'

    def action_view_culture(self):
        """Action pour voir la culture de la parcelle"""
        self.ensure_one()
        if not self.culture_id:
            return {
                'type': 'ir.actions.act_window',
                'name': f'Nouvelle Culture pour {self.name}',
                'res_model': 'bsr.culture',
                'view_mode': 'form',
                'target': 'current',
                'context': {
                    'default_parcel_id': self.id,
                    'default_farm_id': self.farm_id.id,
                },
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': f'Culture de {self.name}',
                'res_model': 'bsr.culture',
                'res_id': self.culture_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

    def action_view_culture_history(self):
        """Action pour voir l'historique des cultures de la parcelle"""
        self.ensure_one()
        return {
            'name': f'Historique des cultures - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.culture',
            'view_mode': 'tree,form',
            'domain': [('parcel_id', '=', self.id)],
            'context': {'default_parcel_id': self.id, 'default_farm_id': self.farm_id.id},
        }

    def _update_current_culture(self):
        """Met à jour la culture actuelle basée sur les cultures en cours"""
        for parcel in self:
            # Chercher la culture en cours (non terminée, non annulée)
            current_culture = parcel.culture_ids.filtered(
                lambda c: c.state not in ['finished', 'cancelled']
            )
            if current_culture:
                # S'il y a plusieurs cultures en cours, prendre la plus récente
                parcel.culture_id = current_culture.sorted('start_date', reverse=True)[0]
                parcel.state = 'cultivated'
            else:
                parcel.culture_id = False
                parcel.state = 'available'

    def action_view_vehicles(self):
        """Action pour voir les véhicules utilisés sur cette parcelle"""
        self.ensure_one()
        return {
            'name': f'Véhicules - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'fleet.vehicle',
            'view_mode': 'tree,form',
            'domain': [('parcel_ids', 'in', [self.id])],
            'context': {'default_parcel_ids': [(4, self.id)]},
        }

    def action_view_irrigation_consumables(self):
        """Action pour voir les consommables d'irrigation de cette parcelle"""
        self.ensure_one()
        return {
            'name': f'Consommables d\'irrigation - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bsr.irrigation.consumable',
            'view_mode': 'kanban,tree,form',
            'domain': [('parcel_ids', 'in', [self.id])],
            'context': {'default_parcel_ids': [(4, self.id)]},
        }