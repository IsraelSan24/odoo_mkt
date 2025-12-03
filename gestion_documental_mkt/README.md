# Gestión Documental MKT

## Propósito

Este módulo tiene como objetivo facilitar la generación, gestión y envío de documentos internos en formato PDF a través de formularios web accesibles desde el portal. Permite a los usuarios generar reportes estandarizados para Requerimientos de Pago, Liquidaciones, Gastos de Movilidad y Entrega de Equipos, automatizando el foliado y el envío por correo electrónico.

## Uso

El módulo habilita cuatro formularios web accesibles para usuarios autenticados:

1.  **Requerimientos**: Solicitud de pagos a proveedores o servicios.
2.  **Liquidaciones**: Rendición de cuentas y liquidación de gastos.
3.  **Gastos**: Planilla de gastos por movilidad.
4.  **Equipos**: Acta de entrega de equipos móviles.

Al completar y enviar cualquiera de estos formularios, el sistema genera automáticamente un PDF con la información, lo almacena y lo envía al correo electrónico especificado.

## Modelos

El módulo crea los siguientes modelos para gestionar correlativos y logs de envíos:

- `report.requerimiento`: Gestiona la numeración correlativa de los requerimientos.
- `report.liquidacion`: Gestiona la numeración correlativa de las liquidaciones.
- `report.gastos`: Gestiona la numeración correlativa de las planillas de gastos.
- `report.equipos`: Gestiona la numeración correlativa de las actas de entrega de equipos.
- `report.email`: Registra el historial de correos enviados, incluyendo destinatarios y números de documento generados.

## Vistas y Plantillas Web

Se han creado las siguientes plantillas QWeb para el portal (`website`):

- `requerimientos` (Ruta: `/requerimiento`)
- `liquidacion` (Ruta: `/liquidacion`)
- `gastos` (Ruta: `/gastos`)
- `equipos` (Ruta: `/equipos`)
- `correo_enviado`: Página de confirmación de envío exitoso.

## Flujos Automáticos

El flujo principal para cada tipo de documento es el siguiente:

1.  **Ingreso de Datos**: El usuario completa el formulario en el portal web.
2.  **Generación de Correlativo**: El sistema calcula el siguiente número de documento basado en los registros existentes en los modelos `report.*`.
3.  **Generación de PDF**: Se renderiza un reporte QWeb en formato PDF con los datos ingresados.
4.  **Almacenamiento**: El PDF generado se guarda como un adjunto (`ir.attachment`) en el sistema.
5.  **Envío de Correo**: Se crea un registro en `report.email` y se envía un correo electrónico al destinatario ingresado (y copia al usuario) utilizando una plantilla de correo específica, con el PDF adjunto.

## Reportes PDF

El módulo incluye las siguientes definiciones de reportes QWeb:

- `report-requerimiento.xml`: Formato de Requerimiento.
- `report-liquidacion.xml`: Formato de Liquidación.
- `report-gastos.xml`: Formato de Planilla de Gastos.
- `report-equipos.xml`: Formato de Acta de Entrega de Equipos.

## Integraciones y Dependencias

- **Dependencias**: `base`, `website`, `mail`, `web`.
- **Integración**: Utiliza el motor de reportes de Odoo y el sistema de plantillas de correo (`mail.template`) para el envío de notificaciones.

## Reglas de Acceso

- **Acceso a Formularios**: Requiere autenticación de usuario (`auth='user'`).
- **Envío de Datos**: Los endpoints de guardado (`/guardar/*`) están configurados como `auth='public'` para asegurar el procesamiento, pero el acceso inicial es restringido.

## Estado de Funcionamiento

No se usa.
