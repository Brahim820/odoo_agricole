# TODO - Module BSR Agri RH

## 📋 Objectif du Module
Gestion des équipes agricoles et leur affectation aux opérations de culture.

## 🎯 Fonctionnalités Principales

### 1. **Gestion des Équipes Agricoles**
- [ ] Création d'équipes spécialisées (semis, récolte, traitement, etc.)
- [ ] Affectation d'employés aux équipes
- [ ] Gestion des compétences et spécialisations
- [ ] Planning des équipes par période
- [ ] Chef d'équipe et hiérarchie

### 2. **Gestion des Compétences**
- [ ] Catalogue des compétences agricoles
- [ ] Niveau de compétence par employé
- [ ] Formations et certifications
- [ ] Évaluation des performances

### 3. **Affectation aux Opérations**
- [ ] Recommandation automatique d'équipes selon l'opération
- [ ] Disponibilité des équipes
- [ ] Conflits de planning
- [ ] Historique des affectations

### 4. **Suivi des Performances**
- [ ] Temps de travail par équipe
- [ ] Productivité par opération
- [ ] Coûts RH par activité
- [ ] Indicateurs de performance

## 🗂️ Structure des Modèles

### **bsr.agri.team** (Équipe Agricole)
```python
- name : Nom de l'équipe
- team_type : Type d'équipe (semis, récolte, traitement...)
- leader_id : Chef d'équipe (hr.employee)
- member_ids : Membres de l'équipe (hr.employee)
- specialization_ids : Spécialisations
- active_period : Période d'activité
- farm_ids : Fermes assignées
- state : État (active, inactive, seasonal)
```

### **bsr.agri.skill** (Compétence Agricole)
```python
- name : Nom de la compétence
- category_id : Catégorie de compétence
- description : Description
- required_for_operations : Opérations nécessitant cette compétence
```

### **bsr.employee.skill** (Compétence d'Employé)
```python
- employee_id : Employé
- skill_id : Compétence
- level : Niveau (1-5)
- certification_date : Date de certification
- expiry_date : Date d'expiration
- certified_by : Certifié par
```

### **bsr.team.assignment** (Affectation d'Équipe)
```python
- team_id : Équipe
- operation_id : Opération
- start_date : Date de début
- end_date : Date de fin
- hours_planned : Heures planifiées
- hours_actual : Heures réelles
- state : État (planned, in_progress, completed)
```

## 🔧 Fonctionnalités Techniques

### **Algorithmes de Recommandation**
- [ ] Matching équipe-opération basé sur compétences
- [ ] Optimisation des affectations
- [ ] Gestion des priorités

### **Intégrations**
- [ ] Module HR (employés)
- [ ] Module bsr_agri_operation (opérations)
- [ ] Module bsr_agri_base (fermes, parcelles)

### **Vues Spécialisées**
- [ ] Planning Gantt des équipes
- [ ] Tableau de bord RH agricole
- [ ] Vue calendrier des affectations
- [ ] Matrice compétences-employés

## 📊 Tableaux de Bord

### **Dashboard Responsable RH**
- Disponibilité des équipes
- Compétences manquantes
- Planning des formations
- Performance des équipes

### **Dashboard Chef d'Équipe**
- Opérations assignées
- Membres de l'équipe
- Progression des tâches
- Heures travaillées

### **Dashboard Employé**
- Mes affectations
- Mes compétences
- Formations disponibles
- Historique de travail

## 🔐 Sécurité et Droits

### **Groupes d'Utilisateurs**
- **RH Manager** : Gestion complète des équipes et compétences
- **Team Leader** : Gestion de son équipe et affectations
- **Employee** : Vue de ses propres affectations
- **Operation Planner** : Affectation des équipes aux opérations

## 📈 Rapports et Analyses

### **Rapports RH**
- [ ] Rapport de productivité par équipe
- [ ] Analyse des compétences
- [ ] Coûts RH par opération
- [ ] Temps de travail détaillé

### **Analyses Prédictives**
- [ ] Prévision des besoins en personnel
- [ ] Identification des goulots d'étranglement
- [ ] Optimisation des équipes

## 🚀 Phases de Développement

### **Phase 1 - Core (Semaines 1-2)**
- [ ] Modèles de base (Team, Skill, Assignment)
- [ ] Vues principales (Form, Tree, Kanban)
- [ ] Sécurité de base
- [ ] Intégration avec HR

## 🔗 Dépendances

### **Modules Odoo Standard**
- `hr` : Gestion des employés
- `hr_skills` : Compétences employés (si disponible)
- `resource` : Gestion des ressources

### **Modules BSR**
- `bsr_agri_base` : Fermes, parcelles, cultures
- `bsr_agri_operation` : Opérations de culture

---

**Note** : Ce module s'intègre parfaitement avec `bsr_agri_operation` pour fournir une solution complète de gestion agricole incluant la planification RH.

*Créé le 18 novembre 2025*  
*Version : 1.0.0*