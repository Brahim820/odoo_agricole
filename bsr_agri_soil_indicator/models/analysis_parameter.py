# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AnalysisParameter(models.Model):
    """Paramètres d'analyse configurables"""
    _name = 'bsr.analysis.parameter'
    _description = 'Paramètres d\'analyse'
    _order = 'analysis_type_id, sequence, name'

    name = fields.Char('Nom du paramètre', required=True, translate=True)
    code = fields.Char('Code', required=True, size=20)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Séquence', default=10)
    active = fields.Boolean('Actif', default=True)
    
    # Type d'analyse associé
    analysis_type_id = fields.Many2one('bsr.analysis.type', 'Type d\'analyse', 
                                      required=True, ondelete='cascade')
    
    # Type de données
    data_type = fields.Selection([
        ('float', 'Numérique décimal'),
        ('integer', 'Numérique entier'),
        ('boolean', 'Booléen (Oui/Non)'),
        ('selection', 'Liste de choix'),
        ('text', 'Texte'),
        ('percentage', 'Pourcentage'),
    ], string='Type de données', required=True, default='float')
    
    # Unité de mesure
    uom_id = fields.Many2one('uom.uom', 'Unité de mesure')
    uom_name = fields.Char(related='uom_id.name', readonly=True)
    
    # Valeurs de référence
    min_value = fields.Float('Valeur minimale')
    max_value = fields.Float('Valeur maximale')
    optimal_min = fields.Float('Optimum minimum')
    optimal_max = fields.Float('Optimum maximum')
    critical_min = fields.Float('Critique minimum')
    critical_max = fields.Float('Critique maximum')
    
    # Pour les champs de type selection
    selection_options = fields.Text('Options de sélection',
                                   help='Une option par ligne: code|libellé')
    
    # Alertes
    alert_enabled = fields.Boolean('Activer les alertes', default=True)
    alert_threshold_low = fields.Float('Seuil d\'alerte bas')
    alert_threshold_high = fields.Float('Seuil d\'alerte élevé')
    
    # Métadonnées
    company_id = fields.Many2one('res.company', string='Société', 
                                default=lambda self: self.env.company)
    
    # Formule de calcul (optionnel)
    is_calculated = fields.Boolean('Paramètre calculé')
    calculation_formula = fields.Text('Formule de calcul',
                                     help='Formule Python pour calcul automatique')
    depends_on_parameter_ids = fields.Many2many('bsr.analysis.parameter',
                                               'analysis_param_dependency_rel',
                                               'parameter_id', 'depends_on_id',
                                               'Dépend des paramètres')

    @api.onchange('data_type')
    def _onchange_data_type(self):
        """Reset values when data type changes"""
        if self.data_type == 'boolean':
            self.min_value = 0
            self.max_value = 1
        elif self.data_type == 'percentage':
            self.min_value = 0
            self.max_value = 100

    @api.constrains('min_value', 'max_value')
    def _check_min_max_values(self):
        for record in self:
            if record.min_value and record.max_value:
                if record.min_value >= record.max_value:
                    raise models.ValidationError(
                        'La valeur minimale doit être inférieure à la valeur maximale.'
                    )

    @api.constrains('optimal_min', 'optimal_max')
    def _check_optimal_values(self):
        for record in self:
            if record.optimal_min and record.optimal_max:
                if record.optimal_min >= record.optimal_max:
                    raise models.ValidationError(
                        'L\'optimum minimum doit être inférieur à l\'optimum maximum.'
                    )

    def get_selection_options(self):
        """Parse selection options text into list of tuples"""
        if not self.selection_options:
            return []
        
        options = []
        for line in self.selection_options.strip().split('\n'):
            if '|' in line:
                code, label = line.split('|', 1)
                options.append((code.strip(), label.strip()))
            else:
                options.append((line.strip(), line.strip()))
        return options

    def format_value(self, value):
        """Format value according to parameter type and unit"""
        if not value:
            return ''
        
        if self.data_type == 'percentage':
            return f"{value}%"
        elif self.data_type == 'boolean':
            return 'Oui' if value else 'Non'
        elif self.uom_id:
            return f"{value} {self.uom_id.name}"
        else:
            return str(value)

    _sql_constraints = [
        ('code_type_unique', 'UNIQUE(code, analysis_type_id)', 
         'Le code du paramètre doit être unique par type d\'analyse!'),
    ]