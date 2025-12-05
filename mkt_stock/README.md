# Stock Modifications

## Propósito

Este módulo extiende la funcionalidad del módulo de inventario (`stock`) estándar de Odoo para adaptar el flujo de operaciones a necesidades específicas de Marketing Alterno. Sus principales objetivos son:

1.  Permitir el registro de números de guía y responsables de almacén en las operaciones de inventario.
2.  Mejorar la visualización del stock disponible por ubicación permitida para el usuario.
3.  Restringir la selección de productos en movimientos de inventario a aquellos disponibles en la ubicación de origen.

## Uso

- **Operaciones (Pickings)**: En los formularios y listas de transferencias, se pueden registrar y visualizar los campos "Guide Number" (Número de Guía) y "Warehouse Keeper" (Responsable de Almacén).
- **Productos**: En la vista Kanban de productos, se muestra la cantidad disponible (`location_quantity`) calculada específicamente para las ubicaciones permitidas al usuario actual, en lugar de la cantidad a mano global.
- **Movimientos**: Al crear movimientos internos o de salida, la selección de productos se filtra automáticamente para mostrar solo aquellos con stock en la ubicación de origen seleccionada.

## Modelos

### Modelos Heredados

- `product.template`:
  - Se añade el campo computado `location_quantity` que suma el stock disponible en las ubicaciones asignadas al usuario actual (`user.stock_location_ids`).
- `stock.move`:
  - Se añade lógica (`_onchange_product_ubication`) para filtrar los productos seleccionables basándose en el stock disponible en la ubicación de origen (`location_id`) de la transferencia.
- `stock.move.line`:
  - Se añade el campo relacionado `picking_guide_number` para mostrar el número de guía de la transferencia en las líneas de movimiento.
- `stock.picking`:
  - Se añaden los campos `guide_number` (Char) y `warehouse_keeper` (Many2one `res.partner`) para trazabilidad adicional.

## Vistas Modificadas

- **Product Kanban**: Se oculta el campo `qty_available` estándar y se muestra `location_quantity` (`view_mkt_product_template_kanban_stock`).
- **Stock Move Line Tree**: Se añaden columnas para el partner de la transferencia y el número de guía (`tree_product_stock_move_line_view`).
- **Stock Picking Form/Tree**:
  - Se añaden los campos `guide_number` y `warehouse_keeper`.
  - Se oculta el campo `origin` en la vista de formulario (`view_mkt_stock_picking_form`, `view_mkt_stock_picking_tree`).

## Integraciones y Dependencias

- **Dependencias**: `base`, `stock`.
- **Integración**: Interactúa directamente con los modelos core de inventario y productos.

## Reglas de Acceso

- No define reglas de acceso propias (`ir.model.access.csv` o `security.xml`), por lo que hereda y respeta los permisos estándar del módulo `stock`.
