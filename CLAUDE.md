# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **Odoo 15** custom modules repository for Marketing Alterno. The repository contains custom Odoo modules that extend and customize various business processes including HR recruitment, payroll, inventory management, document management, and more. Each directory represents an independent Odoo module that can be installed separately.

## Development Environment

**Python Paths**: The project references an external Odoo 15 installation:
- Main Odoo installation: `C:/Users/marketing/Documents/Github/Desarrollo/odoo15-local`
- Additional modules path: `C:/Users/marketing/Documents/Github/Desarrollo`

These paths are configured in `.vscode/settings.json` for Python analysis.

## Module Structure

All modules follow the standard Odoo module structure:
```
module_name/
├── __init__.py           # Module entry point
├── __manifest__.py       # Module metadata and dependencies
├── controllers/          # Web controllers (routes, APIs, portal)
├── models/              # Business logic and data models
├── views/               # XML views (forms, lists, kanban, etc.)
├── security/            # Access rights and record rules
│   ├── ir.model.access.csv
│   ├── ir_rule.xml
│   └── res_groups.xml
├── data/                # Demo and default data
├── wizard/              # Transient models for wizards
├── report/              # Report templates and logic
├── static/              # CSS, JS, images
│   ├── src/js/
│   └── src/scss/
└── i18n/                # Translations
```

## Key Modules

**mkt_recruitment**: Core HR recruitment module with extensive features including:
- Applicant management with document workflow
- Contract generation and management
- Portal access for applicants and employees
- Integration with external APIs (DNI validation, RUC consultation)
- Geolocation tracking
- Massive employee terminations
- Employee reinstatement processes

**mkt_payroll**: Payroll management extending mkt_recruitment
- Paycheck generation and portal access
- Depends on `mkt_recruitment` module

**mkt_documental_managment**: Document management system with:
- Budget tracking and settlements
- API integrations (DNI, RUC, CPE, exchange rates)
- Multiple consultation services
- Expense control reporting

**mkt_stock** series: Stock/inventory customizations
- `mkt_stock`: Basic stock modifications
- `mkt_stock_hp`, `mkt_stock_sistemas`, `mkt_stock_restriction`: Specialized stock workflows
- `mkt_stock_picking_report`: Custom picking reports

**mkt_supervision**: Employee supervision and attendance tracking

**hr_zk_attendance**: ZKTeco biometric device integration for attendance

**mkt_maintenance**: Equipment maintenance management with component tracking

## Git Workflow

**Branches**:
- `main`: Production branch (merge target for PRs)
- `dev2`: Current development branch (HEAD)
- `demo`: Demo environment branch
- Feature branches follow pattern: `feature/*` or `fix/*`

**Commit Message Convention**:
The repository uses prefix-based commit messages. Examples from history:
- `[UPDATE]` - Updates or enhancements to existing features
- `[FIX]` - Bug fixes
- `[FEATURE]` - New features
- Use descriptive messages in English or Spanish

## Model Inheritance Patterns

Models extensively use Odoo's inheritance patterns:
- `_inherit` is used to extend standard Odoo models (e.g., `hr.applicant`, `hr.employee`, `stock.picking`)
- Most modules extend core Odoo functionality rather than creating standalone models
- Custom fields are added to standard models throughout

## Security Architecture

Security is implemented through:
1. **Module categories**: Defined in `security/ir_module_category.xml`
2. **User groups**: Defined in `security/res_groups.xml`
3. **Access rights**: Defined in `security/ir.model.access.csv`
4. **Record rules**: Defined in `security/ir_rule.xml` for row-level security

Access control is validated in model logic (see `hr_applicant.py:39` for group permission checks).

## Portal Integration

Multiple modules provide portal access:
- Controllers in `controllers/portal.py` handle portal routes
- Portal templates in `views/*_portal_templates.xml`
- Typically extend `/my/*` routes for employee/applicant self-service

## API Integrations

External API integrations are common:
- **DNI validation**: `models/api_dni.py`, `models/api_dni_plus.py`
- **RUC consultation**: `models/api_ruc.py`, `models/scraper_ruc.py`
- **CPE validation**: `models/api_cpe.py`
- **Exchange rates**: `models/api_change_type.py`
- **Third-party service**: `models/apiperu.py`

## Frontend Assets

JavaScript and CSS assets are declared in `__manifest__.py` under `assets`:
- `web.assets_frontend`: For portal/website functionality
- `web.assets_backend`: For backend interface enhancements

Common patterns:
- Geolocation tracking JS
- Form validation
- Custom notifications and effects

## Translation Support

The codebase uses Odoo's translation system:
- Import translation function: `from odoo import _`
- Wrap user-facing strings: `_("Translatable text")`
- Translations stored in `i18n/*.po` files

Recent commits indicate translation improvements are ongoing.

## Testing

Limited test coverage exists. Test files found in:
- `hr_attendance_geolocation/tests/`
- `stock_no_negative/tests/`
- `report_xlsx/tests/`
- `web_responsive/tests/`

Tests follow Odoo's testing framework using `odoo.tests` module.

## Data Migration

The `migrator` module handles data migrations with:
- `models/migrator.py`: Migration logic
- `models/self_migrator.py`: Self-service migration utilities

## Development Notes

1. **Module Dependencies**: Check `__manifest__.py` `depends` list before modifying - many modules have interdependencies (e.g., `mkt_payroll` depends on `mkt_recruitment`)

2. **Localization**: Heavy use of Peruvian localization (`l10n_pe`, `l10n_latam_base`)

3. **Wizards**: Transient models for multi-step processes are in `wizard/` directories

4. **Computed Fields**: Extensive use of `@api.depends` decorated compute methods

5. **Stage-based Workflows**: Recruitment uses stage-based progression with sequence validation (see `hr_applicant.py:48` - sequential stage changes only)

6. **Logging**: Uses Python's logging: `_logger = logging.getLogger(__name__)`

## File References

When making changes, note that:
- VSCode Python analysis is configured for the external Odoo installation
- Import paths assume Odoo addons structure: `from odoo import models, fields, api`
- Relative imports within modules: `from odoo.addons.module_name.models.file import function`