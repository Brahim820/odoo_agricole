# -*- coding: utf-8 -*-

from odoo import models, fields


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    farm_id = fields.Many2one('bsr.farm', string='Ferme', ondelete='set null')
    parcel_id = fields.Many2one('bsr.parcel', string='Parcelle', ondelete='set null')


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    farm_id = fields.Many2one('bsr.farm', string='Ferme', ondelete='set null')
    parcel_ids = fields.Many2many('bsr.parcel', string='Parcelles d\'utilisation')