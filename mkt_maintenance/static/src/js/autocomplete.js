odoo.define('mkt_maintenance.autocomplete', function (require) {
    "use strict";

    var ajax = require('web.ajax');

    $(document).ready(function () {
        $('#codigo_equipo').on('change', function () {
            var equipmentCode = $(this).val();
            if (equipmentCode) {
                ajax.jsonRpc('/equipmentstatus/search_equipment', 'call', {
                    'name': equipmentCode
                }).then(function (data) {
                    if (data) {
                        $('#equipment_id').val(data.equipment_id || '');  // Autocompleta el ID del equipo
                        $('#ubicacion_equipo').val(data.location || '');
                        $('#category_equipo').val(data.category_id || '');
                        $('#modelo_equipo').val(data.model || '');
                        $('#numero_serie_equipo').val(data.serial_number || '');
                        $('#empleado_asignado_equipo').val(data.employee_id || '');
                    } else {
                        // Limpiar campos si no se encuentran datos
                        $('#equipment_id').val('');
                        $('#ubicacion_equipo').val('');
                        $('#category_equipo').val('');
                        $('#modelo_equipo').val('');
                        $('#numero_serie_equipo').val('');
                        $('#empleado_asignado_equipo').val('');
                    }
                });
            }
        });
    });
});