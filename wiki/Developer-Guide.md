# 👨‍💻 Guide du Développeur

Bienvenue dans le guide de contribution à l'écosystème BSR Agriculture !

## 🛠️ Environnement de Développement

### Prérequis Développeur

```bash
# Outils requis
- Python 3.8+ avec virtualenv
- PostgreSQL 12+
- Git 2.20+
- VS Code (recommandé) avec extensions Odoo
- Node.js 14+ (pour outils de build)
```

### Configuration Environnement

```bash
# 1. Clone du repository
git clone https://github.com/Brahim820/odoo_agricole.git
cd odoo_agricole

# 2. Environnement virtuel Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# 3. Installation dépendances développement
pip install -r requirements-dev.txt

# 4. Configuration pre-commit hooks
pre-commit install
```

## 📝 Standards de Code

### Structure des Fichiers

```
bsr_agri_[module]/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   └── [model_name].py
├── views/
│   ├── [model_name]_views.xml
│   └── menus.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── data/
│   └── [data_files].xml
├── reports/
│   └── [report_files].xml
├── static/
│   ├── description/
│   └── src/
└── tests/
    └── test_[model_name].py
```

### Conventions de Nommage

```python
# Modèles
class ProductionCampaign(models.Model):
    _name = 'bsr.production.campaign'
    _description = 'Campaign de Production Agricole'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

# Champs
name = fields.Char(
    string='Nom de la Campagne',
    required=True,
    tracking=True,
    help="Nom unique de la campagne de production"
)

# Méthodes
def action_start_campaign(self):
    """Démarre la campagne de production"""
    pass

@api.depends('field1', 'field2')
def _compute_total(self):
    """Calcule le total"""
    pass
```

### Standards Python

```python
# Imports order
import base64
import logging
from datetime import datetime, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    # Ordre des attributs de classe
    _name = 'bsr.my.model'
    _description = 'Description du modèle'
    _inherit = ['mail.thread']
    _order = 'name'
    _rec_name = 'name'
    
    # Champs par ordre logique
    # 1. Champs basiques
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    
    # 2. Champs relationnels
    partner_id = fields.Many2one('res.partner')
    line_ids = fields.One2many('bsr.my.line', 'parent_id')
    
    # 3. Champs calculés
    total = fields.Float(compute='_compute_total', store=True)
    
    # Contraintes
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Le nom doit être unique')
    ]
    
    # Méthodes par ordre
    # 1. Méthodes CRUD
    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)
    
    # 2. Méthodes compute
    @api.depends('line_ids.amount')
    def _compute_total(self):
        for record in self:
            record.total = sum(record.line_ids.mapped('amount'))
    
    # 3. Contraintes
    @api.constrains('name')
    def _check_name(self):
        if not self.name:
            raise ValidationError(_("Le nom est requis"))
    
    # 4. Actions métier
    def action_confirm(self):
        self.state = 'confirmed'
```

## 🧪 Tests et Qualité

### Tests Unitaires

```python
# tests/test_production_campaign.py
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

class TestProductionCampaign(TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.Campaign = self.env['bsr.production.campaign']
        self.farm = self.env.ref('bsr_agri_base.demo_farm_1')
    
    def test_create_campaign(self):
        """Test création campagne basique"""
        campaign = self.Campaign.create({
            'name': 'Test Campaign',
            'farm_id': self.farm.id,
            'start_date': '2025-01-01',
        })
        self.assertEqual(campaign.state, 'draft')
        self.assertTrue(campaign.code)
    
    def test_campaign_validation(self):
        """Test validation des contraintes"""
        with self.assertRaises(ValidationError):
            self.Campaign.create({
                'name': '',  # Nom requis
                'farm_id': self.farm.id,
            })
    
    def test_campaign_workflow(self):
        """Test workflow complet"""
        campaign = self.Campaign.create({
            'name': 'Test Workflow',
            'farm_id': self.farm.id,
            'start_date': '2025-01-01',
        })
        
        # Test transition d'état
        campaign.action_start()
        self.assertEqual(campaign.state, 'in_progress')
        
        # Test cycle creation
        campaign.action_create_cycles()
        self.assertTrue(campaign.cycle_ids)
```

### Lancement des Tests

```bash
# Tests unitaires module spécifique
python odoo-bin -d test_db -i bsr_agri_production --test-enable --stop-after-init

# Tests avec coverage
python -m pytest tests/ --cov=. --cov-report=html

# Tests d'intégration
python odoo-bin -d test_db --test-enable --test-tags=post_install
```

### Linting et Formatage

```bash
# Configuration .pylintrc
pip install pylint-odoo
pylint --load-plugins=pylint_odoo [module_name]/

# Black formatter
black --line-length=88 [module_name]/

# Flake8
flake8 [module_name]/

# Pre-commit hooks automatiques
pre-commit run --all-files
```

## 🔄 Workflow de Contribution

### 1. Branching Strategy

```bash
# Feature branches
git checkout -b feature/irrigation-sensors
git checkout -b bugfix/production-calculation
git checkout -b refactor/security-model

# Commit messages conventionnels
git commit -m "feat: Add IoT sensor integration for irrigation"
git commit -m "fix: Correct production cycle calculation"
git commit -m "refactor: Improve security domain rules"
```

### 2. Pull Request Process

```markdown
## 🎯 Description
Brief description of changes...

## 🧪 Tests
- [ ] Tests unitaires ajoutés/modifiés
- [ ] Tests manuels effectués
- [ ] Pas de régression

## 📋 Checklist
- [ ] Code conforme aux standards BSR
- [ ] Documentation mise à jour
- [ ] Pas de données sensibles dans le code
- [ ] Migration script si nécessaire

## 🔗 Issues liées
Closes #123
```

### 3. Code Review

**Points de contrôle** :
- ✅ Respect des conventions de nommage
- ✅ Tests unitaires présents et pertinents
- ✅ Sécurité : pas de failles SQL injection
- ✅ Performance : pas de requêtes N+1
- ✅ Documentation : docstrings présentes
- ✅ Traduction : strings externalisées

## 🚀 Déploiement

### Environnements

```yaml
# .github/workflows/ci.yml
name: BSR Agriculture CI/CD

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          python odoo-bin --test-enable --stop-after-init
```

### Migrations

```python
# migrations/15.0.1.1.0/pre-migrate.py
import logging

_logger = logging.getLogger(__name__)

def migrate(cr, version):
    """Migration script v1.1.0"""
    _logger.info("Starting migration to v1.1.0")
    
    # Ajout nouvelle colonne
    cr.execute("""
        ALTER TABLE bsr_production_campaign 
        ADD COLUMN IF NOT EXISTS new_field VARCHAR(255)
    """)
    
    # Mise à jour données existantes
    cr.execute("""
        UPDATE bsr_production_campaign 
        SET new_field = 'default_value' 
        WHERE new_field IS NULL
    """)
    
    _logger.info("Migration to v1.1.0 completed")
```

### Release Process

```bash
# 1. Version bump
# Modifier __manifest__.py : 'version': '1.1.0'

# 2. Changelog
echo "## v1.1.0 (2025-11-20)
- feat: Ajout capteurs IoT irrigation
- fix: Correction calculs production
- docs: Amélioration documentation API" >> CHANGELOG.md

# 3. Tag release
git tag -a v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0

# 4. GitHub Release automatique via Actions
```

## 📚 Documentation Code

### Docstrings

```python
def create_production_cycle(self, parcel_id, culture_type):
    """Crée un nouveau cycle de production.
    
    Cette méthode initialise un cycle de production complet
    avec toutes les phases prédéfinies pour le type de culture.
    
    Args:
        parcel_id (int): ID de la parcelle
        culture_type (str): Type de culture à planter
    
    Returns:
        bsr.production.cycle: Le cycle créé
        
    Raises:
        ValidationError: Si la parcelle n'est pas disponible
        UserError: Si le type de culture n'existe pas
        
    Example:
        >>> campaign = self.env['bsr.production.campaign']
        >>> cycle = campaign.create_production_cycle(1, 'wheat')
        >>> print(cycle.phase_ids.mapped('name'))
        ['Planification', 'Préparation Sol', ...]
    """
    pass
```

### Documentation API

```python
# Utilisation d'OpenAPI/Swagger pour REST API
"""
@api_route('/api/v1/campaigns', methods=['GET', 'POST'])
def campaigns_api(self, **kwargs):
    '''
    GET /api/v1/campaigns - Liste des campagnes
    
    Query Parameters:
    - farm_id (int): Filtrer par ferme
    - state (str): Filtrer par état
    - limit (int): Nombre max de résultats
    
    Response:
    {
        "campaigns": [
            {
                "id": 1,
                "name": "Campagne Blé 2025",
                "state": "in_progress",
                "farm_name": "Ferme du Nord"
            }
        ],
        "count": 1
    }
    '''
"""
```

## 🔧 Outils de Développement

### VS Code Configuration

```json
// .vscode/settings.json
{
    "python.defaultInterpreter": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.pylintPath": "pylint",
    "python.formatting.provider": "black",
    "xml.validation.enabled": true,
    "odoo.addons.paths": ["./"],
    "odoo.pythonPath": "./venv/bin/python"
}
```

### Extensions Recommandées

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "jigar-patel.odooSnippets",
        "ms-vscode.vscode-xml",
        "odoo.odoo-development",
        "bradlc.vscode-tailwindcss"
    ]
}
```

## 🐛 Debugging

### Configuration Debugger

```json
// .vscode/launch.json
{
    "configurations": [
        {
            "name": "Odoo Debug",
            "type": "python",
            "request": "launch",
            "program": "odoo-bin",
            "args": [
                "--config=odoo.conf",
                "--dev=xml,reload,qweb",
                "--log-level=debug"
            ],
            "console": "integratedTerminal"
        }
    ]
}
```

### Techniques de Debug

```python
# 1. Logging structuré
import logging
_logger = logging.getLogger(__name__)

def my_method(self):
    _logger.info("Début traitement campagne %s", self.name)
    _logger.debug("Paramètres: %s", self._context)
    
    try:
        # Logique métier
        result = self._complex_computation()
        _logger.info("Résultat: %s", result)
    except Exception as e:
        _logger.error("Erreur dans campagne %s: %s", self.name, e)
        raise

# 2. Breakpoints conditionnels
import pdb
if self.env.user.login == 'developer@bsr.com':
    pdb.set_trace()  # S'arrête seulement pour ce user

# 3. Performance profiling
import cProfile
import pstats

def profile_method(self):
    pr = cProfile.Profile()
    pr.enable()
    
    # Code à profiler
    self._heavy_computation()
    
    pr.disable()
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative').print_stats(10)
```

---

🎯 **Ce guide vous donne toutes les clés pour contribuer efficacement à BSR Agriculture !**

👉 **Questions ?** → [Issues GitHub](https://github.com/Brahim820/odoo_agricole/issues) ou support@bsr-agriculture.com