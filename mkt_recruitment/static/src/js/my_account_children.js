odoo.define('mkt_recruitment.children_logic', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.ChildrenLogic = publicWidget.Widget.extend({
        selector: '#children', // Asegúrate de que esto envuelva tu tabla
        events: {
            'change input[name="children"]': '_onChildrenChange',
            'keyup input[name="children"]': '_onChildrenChange',
            'change .custom-file-input': '_onFileChanged', // <--- ESTO SOLUCIONA TU PROBLEMA
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // Ejecutar la lógica al cargar la página para mostrar las filas correctas
                self._updateChildrenRows();
            });
        },

        /**
         * Detecta cuando cambia el número de hijos
         */
        _onChildrenChange: function (ev) {
            this._updateChildrenRows();
        },

        /**
         * Detecta cuando subes un archivo y actualiza el texto del Label
         * ESTA ES LA PARTE QUE FALTABA O FALLABA ANTES
         */
        _onFileChanged: function (ev) {
            var $input = $(ev.currentTarget);
            var fileName = $input.val().split('\\').pop(); // Obtiene solo el nombre del archivo
            
            // Si el usuario cancela la selección, fileName puede estar vacío
            if (fileName) {
                $input.next('.custom-file-label').addClass("selected").html(fileName);
            } else {
                $input.next('.custom-file-label').removeClass("selected").html('Select file');
            }
        },

        /**
         * Muestra u oculta filas según el número
         */
        _updateChildrenRows: function () {
            // Buscar primero el input (para modo editable)
            var $inputChildren = this.$('input[name="children"]');
            
            // Buscar el span (para modo de solo lectura/validado)
            var $spanChildren = this.$('#span-children');
            
            var count = 0;

            if ($inputChildren.length > 0) {
                // Caso 1: Modo Editable (usamos el input y escuchamos cambios)
                count = parseInt($inputChildren.val()) || 0;
            } else if ($spanChildren.length > 0) {
                // Caso 2: Modo de Solo Lectura (usamos el valor del span)
                // Asegúrate de usar .text() o .html() para obtener el valor del span
                count = parseInt($spanChildren.text()) || 0;
            }

            // Límites de seguridad
            if (count > 6) count = 6;
            if (count < 0) count = 0;
            
            // --- El resto de tu lógica de bucle se mantiene igual ---
            for (var i = 1; i <= 6; i++) {
                // Necesitamos manejar las filas con y sin "-validated"
                var $rowEditable = this.$('#child-' + i);
                var $rowValidated = this.$('#child-' + i + '-validated'); // Nueva fila validada
                
                if (i <= count) {
                    // MOSTRAR AMBAS FILAS si existen, la que corresponda según t-if/t-else
                    $rowEditable.show(); 
                    $rowValidated.show();
                } else {
                    // OCULTAR Y LIMPIAR
                    if ($rowEditable.is(':visible')) {
                        this._clearRowInputs($rowEditable);
                    }
                    $rowEditable.hide();
                    
                    // OCULTAR la fila validada, no necesitamos limpiarla, solo ocultarla.
                    $rowValidated.hide();
                }
            }
        },

    // ... (rest of the functions: _onChildrenChange, _onFileChanged, _clearRowInputs) ...
// ...

        /**
         * Limpia los inputs de la fila oculta para no enviar basura
         */
        _clearRowInputs: function ($row) {
            // 1. Limpiar textos, fechas y números
            $row.find('input[type="text"], input[type="number"], input[type="date"]').val('');

            // 2. Limpiar inputs de archivo
            var $fileInputs = $row.find('input[type="file"]');
            $fileInputs.val(''); 

            // 3. Resetear visualmente el label del archivo a "Select file"
            $fileInputs.next('.custom-file-label').removeClass("selected").html('Select file');
        }
    });
});