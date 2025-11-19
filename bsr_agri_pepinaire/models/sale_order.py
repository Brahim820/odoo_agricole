# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_pepiniere_order = fields.Boolean(string='Commande pépinière', default=False)
    lot_plant_ids = fields.Many2many('pepiniere.lot.plant', string='Lots concernés', 
                                      compute='_compute_lot_plant_ids', store=True)

    @api.depends('order_line.lot_plant_id')
    def _compute_lot_plant_ids(self):
        for order in self:
            order.lot_plant_ids = order.order_line.mapped('lot_plant_id')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    lot_plant_id = fields.Many2one('pepiniere.lot.plant', string='Lot de plants',
                                    domain="[('state', 'in', ['pret', 'vendu']), ('quantite_disponible', '>', 0)]")
    espece_id = fields.Many2one(related='lot_plant_id.espece_id', string='Espèce', readonly=True, store=True)
    variete_id = fields.Many2one(related='lot_plant_id.variete_id', string='Variété', readonly=True, store=True)
    quantite_disponible = fields.Integer(related='lot_plant_id.quantite_disponible', 
                                          string='Quantité disponible', readonly=True)

    @api.onchange('lot_plant_id')
    def _onchange_lot_plant_id(self):
        if self.lot_plant_id:
            # Créer un produit si nécessaire ou utiliser un produit existant
            self.price_unit = self.lot_plant_id.prix_vente_unitaire
            self.name = f"{self.lot_plant_id.name} - {self.lot_plant_id.variete_id.name}"
            # Marquer la commande comme commande pépinière
            if self.order_id:
                self.order_id.is_pepiniere_order = True

    @api.constrains('product_uom_qty', 'lot_plant_id')
    def _check_quantite_disponible(self):
        for line in self:
            if line.lot_plant_id and line.product_uom_qty > line.lot_plant_id.quantite_disponible:
                raise ValidationError(
                    _('La quantité demandée (%.0f) dépasse la quantité disponible (%.0f) pour le lot %s.') 
                    % (line.product_uom_qty, line.lot_plant_id.quantite_disponible, line.lot_plant_id.name)
                )

    def _prepare_invoice_line(self, **optional_values):
        """Ajouter les informations du lot dans la ligne de facture"""
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        if self.lot_plant_id:
            res['name'] = f"{self.lot_plant_id.name} - {self.lot_plant_id.variete_id.name}"
        return res
