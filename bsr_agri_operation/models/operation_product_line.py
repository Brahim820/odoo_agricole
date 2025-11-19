# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class OperationProductLine(models.Model):
    _name = 'bsr.operation.product.line'
    _description = 'Ligne de produit d\'opération'
    _order = 'operation_id, sequence, id'

    # Relations
    operation_id = fields.Many2one(
        'bsr.culture.operation', 
        string='Opération',
        required=True, 
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Produit', 
        required=True,
        domain=[('type', 'in', ['product', 'consu'])]
    )
    
    # Ordre et identification
    sequence = fields.Integer('Séquence', default=10)
    name = fields.Char('Description', related='product_id.name', readonly=True)

    # Quantités et unités
    quantity = fields.Float(
        'Quantité utilisée', 
        required=True, 
        digits='Product Unit of Measure',
        default=1.0
    )
    uom_id = fields.Many2one(
        'uom.uom', 
        string='Unité de mesure', 
        required=True,
        related='product_id.uom_id',
        readonly=True
    )
    
    # Application et méthodes
    application_rate = fields.Float(
        'Taux d\'application', 
        digits=(10, 4),
        help="Quantité par hectare"
    )
    application_method = fields.Selection([
        ('spray', 'Pulvérisation'),
        ('granules', 'Granulés'),
        ('injection', 'Injection'),
        ('manual', 'Application manuelle'),
        ('irrigation', 'Fertigation'),
        ('broadcast', 'Épandage'),
        ('seed_treatment', 'Traitement de semence'),
        ('foliar', 'Application foliaire'),
    ], string='Mode d\'application')

    # Coûts
    unit_cost = fields.Float(
        'Coût unitaire', 
        digits='Product Price',
        help="Coût du produit par unité"
    )
    total_cost = fields.Float(
        'Coût total', 
        compute='_compute_total_cost', 
        store=True,
        digits='Product Price'
    )

    # Informations techniques
    concentration = fields.Float('Concentration (%)', digits=(5, 2))
    dilution_rate = fields.Float('Taux de dilution', digits=(10, 2))
    
    # Traçabilité et lot
    lot_id = fields.Many2one('stock.production.lot', string='Lot/Numéro de série')
    expiry_date = fields.Date('Date d\'expiration')
    
    # Conditions d'application
    temperature_min = fields.Float('Température min. (°C)')
    temperature_max = fields.Float('Température max. (°C)')
    humidity_max = fields.Float('Humidité max. (%)')
    wind_speed_max = fields.Float('Vitesse vent max. (km/h)')
    
    # Documentation
    notes = fields.Text('Notes d\'application')
    safety_instructions = fields.Text('Consignes de sécurité')
    
    # Méta-données
    active = fields.Boolean('Actif', default=True)
    
    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.unit_cost

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Mise à jour des valeurs par défaut lors du changement de produit"""
        if self.product_id:
            # Récupération du coût standard
            self.unit_cost = self.product_id.standard_price
            
            # Récupération des informations techniques si configurées
            # TODO: Ajouter des champs techniques au produit si nécessaire
            
    @api.onchange('application_rate')
    def _onchange_application_rate(self):
        """Calcul automatique de la quantité basé sur le taux d'application"""
        if self.application_rate and self.operation_id.work_area:
            self.quantity = self.application_rate * self.operation_id.work_area

    @api.constrains('quantity')
    def _check_quantity(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('La quantité doit être positive.'))

    @api.constrains('unit_cost')
    def _check_unit_cost(self):
        for line in self:
            if line.unit_cost < 0:
                raise ValidationError(_('Le coût unitaire ne peut pas être négatif.'))

    @api.constrains('concentration')
    def _check_concentration(self):
        for line in self:
            if line.concentration and (line.concentration < 0 or line.concentration > 100):
                raise ValidationError(_('La concentration doit être comprise entre 0 et 100%.'))

    @api.constrains('temperature_min', 'temperature_max')
    def _check_temperature(self):
        for line in self:
            if line.temperature_min and line.temperature_max:
                if line.temperature_min > line.temperature_max:
                    raise ValidationError(_('La température minimale ne peut pas être supérieure à la température maximale.'))

    def name_get(self):
        result = []
        for line in self:
            name = f"{line.product_id.name}"
            if line.quantity:
                name += f" - {line.quantity} {line.uom_id.name}"
            if line.application_method:
                method_dict = dict(line._fields['application_method'].selection)
                name += f" ({method_dict.get(line.application_method, '')})"
            result.append((line.id, name))
        return result