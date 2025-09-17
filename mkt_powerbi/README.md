# Power BI Embed Module for Odoo

## Overview

This module allows embedding Power BI reports inside Odoo
using an iframe field with HTML rendering.

## Features

- Embed dynamic Power BI iframe URLs.
- Only users with access can view the iframe.
- Simple configuration via the PowerBI report view form.
- Compatible with Odoo 15.

## Usage

1. Go to the PowerBI Reports module.
1. Click on create new.
2. Paste the Power BI iframe URL in the URL field.
3. Go to customers page and assign users to allow them see the Power BI report.
4. The embedded report will be rendered automatically.

## Security

- Only users with access rights to the model can see the record report with the iframe. It can be controlled from the form view of each PowerBI Report.
- The report source (Power BI) must enforce its own access restrictions.

## Access Rights (Simplified)

| Group                         | Read | Create | Write | Delete |
|-------------------------------|------|--------|-------|--------|
| admin         | ✅    | ✅      | ✅     | ✅      |
| user         | ✅    | ✅      | ✅     | ✅      |
| customer        | ✅    | ❌      | ❌     | ❌      |

- `admin`: (1,1,1,1).
- `user`: (1,1,1,1) with rule.
- `customer`: (1,0,0,0) with rule. 

The iframe source is publicly visible in HTML inspector.

## Technical details

- Adds a computed `Html` field: `powerbi_embed`.
- Uses `widget="html"` in the form view.
- Styles applied through `assets.xml` to center iframe.


## Installation

- Copy the module into your Odoo `addons/` folder
- Install it from Apps (activate Developer Mode if needed)

## Dependencies

- `base` (standard)

## Author

Alexander Burgos - Marketing Alterno
