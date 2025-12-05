# HP Stock View

## Propósito

Este módulo proporciona vistas y reportes personalizados para la gestión de inventario de HP, enfocándose específicamente en las ubicaciones 'MKT/HP TRADE Magdalena' y 'MKT/HP TRADE Chorrillos'. Permite visualizar el stock actual, movimientos de entrada y salida, y generar reportes en Excel con imágenes de productos.

## Uso

El módulo agrega un menú principal "HP Stock" con las siguientes opciones:

1.  **Report View**: Vista de lista personalizada (`report.stock.hp`) que muestra el stock consolidado por producto, lote, categoría y ubicación, con columnas para cantidades de entrada, salida y stock actual. Permite visualizar la imagen del producto.
2.  **In**: Muestra los movimientos de inventario (`stock.move`) con destino a las ubicaciones de HP.
3.  **Out**: Muestra los movimientos de inventario (`stock.move`) con origen en las ubicaciones de HP.
4.  **Report > HP Stock Report**: Asistente para generar un reporte en Excel del stock actual.
5.  **Portal**: Enlace directo al portal web de Marketing Alterno.

## Modelos

### Nuevos Modelos

- `report.stock.hp`: Modelo basado en una vista SQL (`stock_quant`) que consolida la información de stock, movimientos y ubicación para facilitar el reporte.
- `stock.hp.report`: Modelo transitorio (Wizard) para la generación del reporte en Excel. Hereda de `report.formats`.

### Modelos Heredados

- `stock.move`: Se añade el campo `date_done` relacionado con `picking_id.date_done` para facilitar la visualización de la fecha de realización en las vistas de lista.

## Vistas Modificadas y Nuevas

- **Report Stock HP**: Vista de árbol (`view_report_stock_hp_tree`) y búsqueda para el modelo `report.stock.hp`.
- **HP Moves**: Vista de árbol (`view_hp_stock_move_tree`) para `stock.move` simplificada para el contexto de HP.
- **HP Inventory Stock**: Vista de árbol (`view_hp_stock_quant_tree`) para `stock.quant`.

## Reportes

- **Excel**: El módulo permite generar un reporte en formato Excel ("Stock HP") a través del asistente `stock.hp.report`. El reporte incluye columnas para Producto, Serie, Categoría, Tipo, Ubicación, Entradas, Salidas y Stock.

## Integraciones y Dependencias

- **Dependencias**: `stock`, `product`, `mkt_report_formats`, `mkt_gallery`.
- **Integración**: Utiliza `mkt_gallery` para visualizar imágenes de productos y `mkt_report_formats` para la estructura base de reportes.

## Reglas de Acceso

- Se definen reglas de acceso en `security/security.xml` que otorgan permisos completos (lectura, escritura, creación, eliminación) sobre los modelos `stock.hp.report` y `report.stock.hp` a todos los usuarios (sin restricción de grupo específica en la definición).
