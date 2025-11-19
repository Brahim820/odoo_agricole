# -*- coding: utf-8 -*-

from odoo import models, fields, api


class IrrigationConsumable(models.Model):
    _name = 'bsr.irrigation.consumable'
    _description = 'Consommable d\'Irrigation'
    _order = 'name'

    name = fields.Char('Nom du consommable', required=True)
    code = fields.Char('Code')
    product_id = fields.Many2one('product.product', string='Produit associé')
    
    # Informations techniques
    type = fields.Selection([
        ('tuyau', 'Tuyau'),
        ('raccord', 'Raccord'),
        ('goutte_goutte', 'Goutteur'),
        ('asperseur', 'Asperseur'),
        ('vanne', 'Vanne'),
        ('filtre', 'Filtre'),
        ('pompe', 'Pompe'),
        ('reservoir', 'Réservoir'),
        ('autres', 'Autres'),
    ], string='Type de consommable', required=True)
    
    # Spécifications techniques
    diameter = fields.Float('Diamètre (mm)', digits=(8, 2))
    length = fields.Float('Longueur (m)', digits=(8, 2))
    pressure_rating = fields.Float('Pression maximale (bar)', digits=(8, 2))
    flow_rate = fields.Float('Débit (L/h)', digits=(8, 2))
    
    # Gestion des stocks
    stock_qty = fields.Float('Stock disponible', compute='_compute_stock_info', readonly=True)
    stock_uom = fields.Many2one('uom.uom', string='Unité', compute='_compute_stock_info', readonly=True)
    
    # Coût et fournisseur
    standard_price = fields.Float('Prix de revient', compute='_compute_price_info', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Devise', compute='_compute_price_info', readonly=True)
    
    # Informations complémentaires
    description = fields.Text('Description')
    active = fields.Boolean('Actif', default=True)
    
    # Relations avec les fermes/parcelles
    farm_ids = fields.Many2many('bsr.farm', string='Fermes utilisatrices')
    parcel_ids = fields.Many2many('bsr.parcel', string='Parcelles utilisatrices')

    @api.depends('product_id')
    def _compute_stock_info(self):
        for record in self:
            if record.product_id:
                record.stock_qty = record.product_id.qty_available
                record.stock_uom = record.product_id.uom_id
            else:
                record.stock_qty = 0.0
                record.stock_uom = False

    @api.depends('product_id')
    def _compute_price_info(self):
        for record in self:
            if record.product_id:
                record.standard_price = record.product_id.standard_price
                record.currency_id = record.product_id.currency_id or self.env.company.currency_id
            else:
                record.standard_price = 0.0
                record.currency_id = self.env.company.currency_id

    @api.model
    def create(self, vals):
        # Créer automatiquement le produit si nécessaire
        if not vals.get('product_id') and vals.get('name'):
            # Obtenir la catégorie de produit pour les consommables d'irrigation
            try:
                default_categ = self.env.ref('bsr_agri_base.product_category_irrigation')
            except ValueError:
                # Si la catégorie n'existe pas, utiliser la première catégorie disponible ou en créer une
                default_categ = self.env['product.category'].search([('parent_id', '=', False)], limit=1)
                if not default_categ:
                    default_categ = self.env['product.category'].create({
                        'name': 'Consommables d\'Irrigation',
                    })
                
            product_vals = {
                'name': vals['name'],
                'type': 'product',
                'categ_id': default_categ.id,
                'default_code': vals.get('code'),
                'description': vals.get('description'),
                'is_storable': True,
            }
            product = self.env['product.product'].create(product_vals)
            vals['product_id'] = product.id
        return super().create(vals)