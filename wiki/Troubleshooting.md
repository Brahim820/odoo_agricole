# 🐛 Dépannage BSR Agriculture

Guide de résolution des problèmes les plus courants de l'écosystème BSR Agriculture.

## 🚨 Problèmes d'Installation

### ❌ Module ne s'installe pas

**Symptôme** :
```
Error: Module 'bsr_agri_production' cannot be loaded
```

**Solutions** :

1. **Vérifier les dépendances** :
```bash
# Vérifier que bsr_agri_base est installé AVANT
python odoo-bin -d database --check-dependencies bsr_agri_production
```

2. **Ordre d'installation correct** :
```python
# Installer dans cet ordre EXACT :
1. bsr_agri_base
2. bsr_agri_soil_indicator  
3. bsr_agri_irrigation
4. bsr_agri_pepinaire
5. bsr_agri_operation
6. bsr_agri_rh
7. bsr_agri_production  # En dernier
```

3. **Nettoyer le cache** :
```bash
# Supprimer les fichiers .pyc
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +

# Redémarrer Odoo
sudo systemctl restart odoo
```

### ❌ Erreur de domaine de sécurité

**Symptôme** :
```
AccessError: You cannot access this record
```

**Diagnostic** :
```sql
-- Vérifier les règles de sécurité
SELECT name, model_id, domain_force 
FROM ir_rule 
WHERE model_id IN (
    SELECT id FROM ir_model 
    WHERE model LIKE 'bsr.%'
);
```

**Solutions** :
```python
# 1. Vérifier appartenance utilisateur aux groupes
user = self.env.user
groups = user.groups_id.mapped('name')
print("Groupes utilisateur:", groups)

# 2. Vérifier ownership des fermes
farm = self.env['bsr.farm'].search([('id', '=', farm_id)])
print("Users ferme:", farm.partner_id.user_ids.mapped('login'))

# 3. Temporairement désactiver règles pour debug
self = self.sudo()  # ATTENTION: Seulement pour debug
```

## 🔧 Problèmes de Configuration

### ❌ Séquences qui ne fonctionnent pas

**Symptôme** :
```
Sequence 'CAMP-%(year)s-###' not working
```

**Solutions** :

1. **Vérifier la séquence** :
```python
# Dans Paramètres > Séquences
seq = self.env['ir.sequence'].search([
    ('code', '=', 'bsr.production.campaign')
])
print(f"Séquence trouvée: {seq.name}, Active: {seq.active}")
```

2. **Recréer si nécessaire** :
```xml
<!-- data/production_sequence.xml -->
<record id="seq_production_campaign" model="ir.sequence">
    <field name="name">Campagnes de Production</field>
    <field name="code">bsr.production.campaign</field>
    <field name="prefix">CAMP-%(year)s-</field>
    <field name="suffix"></field>
    <field name="padding">3</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
</record>
```

### ❌ Menus manquants

**Symptôme** : Menus BSR Agriculture n'apparaissent pas

**Solutions** :

1. **Vérifier les permissions** :
```python
# L'utilisateur a-t-il le groupe requis ?
user = self.env.user
has_agri_access = user.has_group('bsr_agri_base.group_agriculture_user')
print(f"Accès Agriculture: {has_agri_access}")
```

2. **Forcer mise à jour des menus** :
```python
# En mode développeur
# Paramètres > Actions > Mettre à jour liste des modules
# Cocher "bsr_agri_*" et cliquer "Mettre à jour"
```

3. **Vérifier héritage des menus** :
```xml
<!-- Les menus enfants doivent référencer le parent correct -->
<menuitem id="menu_production_root" 
          parent="bsr_agri_base.menu_agriculture_root"/>
```

## 📊 Problèmes de Performance

### ❌ Lenteur lors du chargement des campagnes

**Diagnostic** :
```python
# Activer le mode debug SQL
# Dans odoo.conf :
# log_level = debug
# log_db = True

# Vérifier les requêtes N+1
import time
start = time.time()
campaigns = self.env['bsr.production.campaign'].search([])
print(f"Temps de recherche: {time.time() - start:.2f}s")

# Compter les cycles pour chaque campagne
for campaign in campaigns:
    print(f"{campaign.name}: {len(campaign.cycle_ids)} cycles")
print(f"Temps total: {time.time() - start:.2f}s")
```

**Solutions** :

1. **Ajouter des index** :
```sql
-- Index pour améliorer les performances
CREATE INDEX IF NOT EXISTS idx_production_cycle_campaign 
ON bsr_production_cycle(campaign_id);

CREATE INDEX IF NOT EXISTS idx_production_cycle_state 
ON bsr_production_cycle(state);

CREATE INDEX IF NOT EXISTS idx_production_cycle_parcel_date 
ON bsr_production_cycle(parcel_id, start_date);
```

2. **Optimiser les vues listes** :
```xml
<!-- Limiter les champs affichés -->
<field name="cycle_ids" invisible="1"/>
<!-- Utiliser des champs calculés avec store=True -->
<field name="cycle_count"/>
```

3. **Pagination automatique** :
```python
# Dans les modèles
class ProductionCampaign(models.Model):
    _order = 'create_date desc'
    _limit_default = 50  # Limiter par défaut
```

## 🔄 Problèmes de Workflow

### ❌ Transition d'état bloquée

**Symptôme** :
```
Campaign cannot move to 'in_progress' state
```

**Diagnostic** :
```python
# Debug des contraintes
campaign = self.env['bsr.production.campaign'].browse(campaign_id)
print(f"État actuel: {campaign.state}")
print(f"Ferme: {campaign.farm_id.name}")
print(f"Parcelles: {len(campaign.parcel_ids)}")
print(f"Cycles: {len(campaign.cycle_ids)}")

# Tester manuellement
try:
    campaign.action_start()
    print("✅ Transition réussie")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

**Solutions** :

1. **Vérifier les contraintes métier** :
```python
@api.constrains('state', 'start_date')
def _check_start_conditions(self):
    for campaign in self:
        if campaign.state == 'in_progress':
            if not campaign.parcel_ids:
                raise ValidationError("Aucune parcelle assignée")
            if not campaign.start_date:
                raise ValidationError("Date de début requise")
```

2. **Ajouter logging détaillé** :
```python
def action_start(self):
    _logger.info(f"Démarrage campagne {self.name}")
    
    if not self.parcel_ids:
        _logger.error("Pas de parcelles pour %s", self.name)
        raise UserError("Veuillez assigner au moins une parcelle")
    
    self.state = 'in_progress'
    _logger.info(f"Campagne {self.name} démarrée avec succès")
```

## 🗄️ Problèmes de Base de Données

### ❌ Erreur de clé étrangère

**Symptôme** :
```
foreign key constraint "bsr_production_cycle_parcel_id_fkey" failed
```

**Solutions** :

1. **Vérifier la cohérence des données** :
```sql
-- Rechercher les références orphelines
SELECT pc.id, pc.name, pc.parcel_id 
FROM bsr_production_cycle pc 
LEFT JOIN bsr_parcel p ON pc.parcel_id = p.id 
WHERE p.id IS NULL AND pc.parcel_id IS NOT NULL;
```

2. **Nettoyer les données corrompues** :
```sql
-- ATTENTION: Sauvegarder avant !
-- Supprimer les références orphelines
DELETE FROM bsr_production_cycle 
WHERE parcel_id NOT IN (SELECT id FROM bsr_parcel);

-- Ou mettre à NULL
UPDATE bsr_production_cycle 
SET parcel_id = NULL 
WHERE parcel_id NOT IN (SELECT id FROM bsr_parcel);
```

### ❌ Problème de migration

**Symptôme** : Erreur lors de mise à jour de module

**Solutions** :

1. **Vérifier les scripts de migration** :
```python
# migrations/15.0.1.1.0/pre-migrate.py
def migrate(cr, version):
    # Toujours vérifier l'existence avant modification
    cr.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='bsr_production_campaign' 
        AND column_name='old_field'
    """)
    
    if cr.fetchone():
        cr.execute("ALTER TABLE bsr_production_campaign DROP COLUMN old_field")
```

2. **Migration manuelle si nécessaire** :
```bash
# Sauvegarder la base
pg_dump -U odoo -d production_db > backup_$(date +%Y%m%d).sql

# Mode maintenance
python odoo-bin -d production_db -u bsr_agri_production --stop-after-init

# Vérifier les logs
tail -f /var/log/odoo/odoo-server.log
```

## 🔐 Problèmes de Sécurité

### ❌ Utilisateur ne voit pas ses données

**Diagnostic** :
```python
# Vérifier les règles de domaine
user = self.env.user
print(f"Utilisateur: {user.name} ({user.login})")
print(f"Groupes: {user.groups_id.mapped('name')}")

# Tester l'accès aux fermes
farms = self.env['bsr.farm'].search([])
print(f"Fermes visibles: {len(farms)}")
for farm in farms:
    print(f"- {farm.name} (Users: {farm.partner_id.user_ids.mapped('login')})")
```

**Solutions** :

1. **Corriger les règles de domaine** :
```xml
<record id="production_campaign_rule" model="ir.rule">
    <field name="domain_force">
        ['|', 
         ('farm_id.partner_id.user_ids', 'in', [user.id]),
         ('create_uid', '=', user.id)]
    </field>
</record>
```

2. **Assigner l'utilisateur à la ferme** :
```python
# Via interface ou code
farm = self.env['bsr.farm'].browse(farm_id)
user = self.env['res.users'].browse(user_id)
farm.partner_id.user_ids = [(4, user.id)]
```

## 📱 Problèmes d'Interface

### ❌ Champs ne s'affichent pas

**Solutions** :

1. **Vérifier les attributs invisible** :
```xml
<!-- Éviter les conditions complexes -->
<field name="my_field" attrs="{'invisible': [('state', '!=', 'draft')]}"/>

<!-- Préférer les groupes -->
<field name="advanced_field" groups="bsr_agri_base.group_agriculture_manager"/>
```

2. **Debug mode pour inspecter** :
```python
# Activer mode développeur
# URL: ?debug=1
# Puis inspecter les champs via "Afficher les métadonnées"
```

## 🔍 Outils de Diagnostic

### Script de Diagnostic Complet

```python
# diagnostic.py - À lancer en shell Odoo
def diagnose_bsr_system():
    """Diagnostic complet système BSR"""
    
    print("=== DIAGNOSTIC BSR AGRICULTURE ===\n")
    
    # 1. Modules installés
    modules = env['ir.module.module'].search([
        ('name', 'ilike', 'bsr_agri'),
        ('state', '=', 'installed')
    ])
    print(f"✅ Modules BSR installés: {len(modules)}")
    for mod in modules:
        print(f"   - {mod.name} v{mod.installed_version}")
    
    # 2. Fermes et utilisateurs
    farms = env['bsr.farm'].search([])
    print(f"\n🏡 Fermes: {len(farms)}")
    for farm in farms:
        users = farm.partner_id.user_ids
        print(f"   - {farm.name}: {len(users)} utilisateurs")
    
    # 3. Campagnes actives
    campaigns = env['bsr.production.campaign'].search([
        ('state', 'in', ['draft', 'in_progress'])
    ])
    print(f"\n🌾 Campagnes actives: {len(campaigns)}")
    
    # 4. Performance tables
    env.cr.execute("""
        SELECT schemaname, tablename, n_live_tup, n_dead_tup
        FROM pg_stat_user_tables 
        WHERE tablename LIKE 'bsr_%' 
        ORDER BY n_live_tup DESC LIMIT 10
    """)
    print(f"\n📊 Top tables BSR:")
    for row in env.cr.fetchall():
        print(f"   - {row[1]}: {row[2]} lignes")
    
    # 5. Erreurs récentes
    env.cr.execute("""
        SELECT COUNT(*) FROM ir_logging 
        WHERE create_date >= NOW() - INTERVAL '24 hours'
        AND level = 'ERROR'
        AND name LIKE '%bsr%'
    """)
    error_count = env.cr.fetchone()[0]
    print(f"\n🚨 Erreurs BSR (24h): {error_count}")
    
    print("\n=== FIN DIAGNOSTIC ===")

# Lancer le diagnostic
diagnose_bsr_system()
```

## 📞 Support Escalation

### Niveaux de Support

**Niveau 1 - Documentation** :
1. Consulter cette page de dépannage
2. Vérifier le [Guide Utilisateur](User-Guide)
3. Rechercher dans [Issues GitHub](https://github.com/Brahim820/odoo_agricole/issues)

**Niveau 2 - Community Support** :
1. Créer une [GitHub Issue](https://github.com/Brahim820/odoo_agricole/issues/new)
2. Joindre logs et captures d'écran
3. Fournir contexte complet

**Niveau 3 - Support Direct** :
1. Email : support@bsr-agriculture.com, brahim820@gmail.com
2. Inclure : version Odoo, modules BSR, logs d'erreur
3. Environnement : production/test, OS, PostgreSQL version

### Template de Bug Report

```markdown
**🐛 Description du problème**
Description claire et concise...

**🔄 Étapes pour reproduire**
1. Aller dans...
2. Cliquer sur...
3. Observer l'erreur...

**✅ Comportement attendu**
Ce qui devrait se passer...

**🖼️ Captures d'écran**
Si applicable...

**🔧 Environnement**
- OS: [Linux/Windows/Mac]
- Odoo: [15.0.x]
- Modules BSR: [versions]
- PostgreSQL: [version]

**📋 Logs d'erreur**
```
Coller les logs ici...
```

**⚡ Impact**
- [ ] Bloque complètement
- [ ] Ralentit le travail  
- [ ] Problème mineur
```

---

🎯 **90% des problèmes trouvent leur solution dans ce guide !**

❓ **Problème non résolu ?** → [Créer une issue](https://github.com/Brahim820/odoo_agricole/issues/new)