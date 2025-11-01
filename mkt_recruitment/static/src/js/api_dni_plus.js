// static/src/js/dni_validator.js
odoo.define('mkt_recruitment.dni_validator', function(require) {
    'use strict';
    
    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.DNIValidator = publicWidget.Widget.extend({
        selector: '.o_dni_validation_form',
        events: {
            'click .btn_validate_dni': '_onValidateDNI',
            'blur input[name="dni"]': '_onValidateDNIAuto',
        },

        /**
         * Valida DNI automáticamente cuando el campo pierde el foco
         */
        _onValidateDNIAuto: function(ev) {
            var $input = $(ev.currentTarget);
            var dni = $input.val().trim();
            
            // Solo validar si tiene 8 dígitos (DNI peruano)
            if (dni.length === 8 && /^\d+$/.test(dni)) {
                this._validateDNI(dni);
            }
        },

        /**
         * Valida DNI cuando se hace clic en el botón
         */
        _onValidateDNI: function(ev) {
            ev.preventDefault();
            var dni = this.$('input[name="dni"]').val().trim();
            
            if (!dni) {
                // this._showError(_t('Por favor ingrese un DNI'));
                return;
            }
            
            if (dni.length !== 8 || !/^\d+$/.test(dni)) {
                // this._showError(_t('El DNI debe tener 8 dígitos'));
                return;
            }
            
            this._validateDNI(dni);
        },

        /**
         * Llama al backend para validar el DNI
         */
        _validateDNI: function(dni) {
            var self = this;
            
            // Mostrar spinner
            this._showLoading();
            this._showFormReadonly();
            
            // Llamar al endpoint del backend
            return rpc.query({
                route: '/api/dni/validate',
                params: {
                    dni: dni
                }
            }).then(function(result) {
                self._hideLoading();
                self._hideFormReadonly();
                
                if (result.success) {
                    self._fillFormWithDNIData(result.data);
                    // self._showSuccess(_t('DNI validado correctamente'));
                } 
                // else {
                //     self._showError(result.message || _t('Error al validar el DNI'));
                // }
            }).catch(function(error) {
                self._hideLoading();
                self._hideFormReadonly();
                console.error('Error validating DNI:', error);
                // self._showError(_t('Error de conexión. Por favor intente nuevamente.'));
            });
        },

        /**
         * Rellena el formulario con los datos del DNI
         */

        /**
         * Rellena el formulario con los datos del DNI
         * Incluye campos de texto y selects de ubicación
         */
        _fillFormWithDNIData: function(data) {
            var self = this;
            
            // 1. DATOS PERSONALES
            // Nombre completo
            if (data.nombres && data.apellido_paterno && data.apellido_materno) {
                const nombre_completo = `${data.apellido_paterno} ${data.apellido_materno}, ${data.nombres}`;
                this.$('input[name="name"]').val(nombre_completo).trigger('change');
            }
            
            // Fecha de nacimiento
            if (data.fecha_nacimiento) {
                // Convierte "30/05/2001" → "2001-05-30"
                const parts = data.fecha_nacimiento.split('/');
                if (parts.length === 3) {
                    const formattedDate = `${parts[2]}-${parts[1]}-${parts[0]}`;
                    this.$('input[name="birthday"]').val(formattedDate).trigger('change');
                }
            }

            // Sexo
            if (data.sexo) {
                var sexo
                if (data.sexo === "M") {
                    sexo = "male";
                }
                if (data.sexo === "F") {
                    sexo = "female";
                }
                this.$('select[name="gender"]').val(sexo).trigger('change');
                
            }
                        
            // Dirección
            if (data.direccion) {
                this.$('input[name="street"]').val(data.direccion).trigger('change');
            }
                        
            // Departamento (State)
            if (data.departamento) {
                var departmentName = this._normalizeDepartmentName(data.departamento);
                this._setDepartment(departmentName);
            }
            
            // Provincia (City)
            if (data.provincia) {
                var provinceName = this._normalizeProvinceName(data.provincia);
                setTimeout(function() {
                    self._setProvince(provinceName);
                }, 300); // Esperar a que se carguen las provincias
            }
            
            // Distrito (District)
            if (data.distrito) {
                var districtName = this._normalizeDistrictName(data.distrito);
                setTimeout(function() {
                    self._setDistrict(districtName);
                }, 600); // Esperar a que se carguen los distritos
            }
            
        },

        /**
         * Establece el departamento en el select
         */
        _setDepartment: function(departmentName) {
            if (!departmentName) return;
            
            var $stateSelect = this.$('#state_id');
            var normalizedSearch = departmentName.toUpperCase().trim();
            
            // Buscar la opción que coincida
            var $option = $stateSelect.find('option').filter(function() {
                var text = $(this).text().trim().toUpperCase();
                return text === normalizedSearch || text.includes(normalizedSearch);
            });
            
            if ($option.length > 0) {
                $stateSelect.val($option.val()).trigger('change');
                console.log('Department set to:', $option.text());
                
                // Trigger del evento change para cargar provincias
                // this._onStateChange();
            } else {
                console.warn('Department not found:', departmentName);
            }
        },

        /**
         * Establece la provincia en el select
         */
        _setProvince: function(provinceName) {
            if (!provinceName) return;
            
            var $citySelect = this.$('#city_id');
            var normalizedSearch = provinceName.toUpperCase().trim();
            
            // Buscar la opción que coincida
            var $option = $citySelect.find('option').filter(function() {
                var text = $(this).text().trim().toUpperCase();
                return text === normalizedSearch || text.includes(normalizedSearch);
            });
            
            if ($option.length > 0) {
                $citySelect.val($option.val()).trigger('change');
                console.log('Province set to:', $option.text());
                
                // Trigger del evento change para cargar distritos
                // this._onCityChange();
            } else {
                console.warn('Province not found:', provinceName);
            }
        },

        /**
         * Establece el distrito en el select
         */
        _setDistrict: function(districtName) {
            if (!districtName) return;
            
            var $districtSelect = this.$('#district_id');
            var normalizedSearch = districtName.toUpperCase().trim();
            
            // Buscar la opción que coincida
            var $option = $districtSelect.find('option').filter(function() {
                var text = $(this).text().trim().toUpperCase();
                return text === normalizedSearch || text.includes(normalizedSearch);
            });
            
            if ($option.length > 0) {
                $districtSelect.val($option.val()).trigger('change');
                console.log('District set to:', $option.text());
            } else {
                console.warn('District not found:', districtName);
            }
        },

        /**
         * Normaliza nombres de departamentos (mapeo de variaciones)
         */
        _normalizeDepartmentName: function(name) {
            if (!name) return '';
            
            var mappings = {
                'LIMA': 'LIMA',
                'CALLAO': 'CALLAO',
                'CUSCO': 'CUSCO',
                'CUZCO': 'CUSCO',
                'AREQUIPA': 'AREQUIPA',
                'LA LIBERTAD': 'LA LIBERTAD',
                'PIURA': 'PIURA',
                'LAMBAYEQUE': 'LAMBAYEQUE',
                'JUNIN': 'JUNÍN',
                'JUNÍN': 'JUNÍN',
                'ICA': 'ICA',
                'ANCASH': 'ANCASH',
                'HUANUCO': 'HUÁNUCO',
                'HUÁNUCO': 'HUÁNUCO',
                'SAN MARTIN': 'SAN MARTÍN',
                'SAN MARTÍN': 'SAN MARTÍN',
                'LORETO': 'LORETO',
                'UCAYALI': 'UCAYALI',
                'CAJAMARCA': 'CAJAMARCA',
                'PUNO': 'PUNO',
                'AYACUCHO': 'AYACUCHO',
                'HUANCAVELICA': 'HUANCAVELICA',
                'APURIMAC': 'APURÍMAC',
                'APURÍMAC': 'APURÍMAC',
                'AMAZONAS': 'AMAZONAS',
                'TACNA': 'TACNA',
                'TUMBES': 'TUMBES',
                'MOQUEGUA': 'MOQUEGUA',
                'PASCO': 'PASCO',
                'MADRE DE DIOS': 'MADRE DE DIOS',
            };
            
            var normalized = name.toUpperCase().trim();
            return mappings[normalized] || normalized;
        },

        /**
         * Normaliza nombres de provincias
         */
        _normalizeProvinceName: function(name) {
            if (!name) return '';
            
            var normalized = name.toUpperCase().trim();
            
            // Casos especiales comunes
            var mappings = {
                'LIMA': 'LIMA',
                'CALLAO': 'CALLAO',
                'CUSCO': 'CUSCO',
                'CUZCO': 'CUSCO',
                'HUANCAYO': 'HUANCAYO',
                'TRUJILLO': 'TRUJILLO',
                'CHICLAYO': 'CHICLAYO',
                'PIURA': 'PIURA',
                'IQUITOS': 'MAYNAS', // Iquitos pertenece a provincia Maynas
                'AREQUIPA': 'AREQUIPA',
            };
            
            return mappings[normalized] || normalized;
        },

        /**
         * Normaliza nombres de distritos
         */
        _normalizeDistrictName: function(name) {
            if (!name) return '';
            return name.toUpperCase().trim();
        },

        /**
         * Muestra un mensaje de error
         */
        _showError: function(message) {
            this.$('.dni_validation_message').remove();
            this.$('.o_dni_validation_field').prepend(
                $('<div class="alert alert-danger dni_validation_message" role="alert">')
                    .text(message)
            );
        },

        /**
         * Muestra un mensaje de éxito
         */
        _showSuccess: function(message) {
            this.$('.dni_validation_message').remove();
            this.$('.o_dni_validation_field').prepend(
                $('<div class="alert alert-success dni_validation_message" role="alert">')
                    .text(message)
            );
            
            // Ocultar mensaje después de 3 segundos
            setTimeout(function() {
                $('.dni_validation_message').fadeOut();
            }, 3000);
        },

        /**
         * Muestra spinner de carga
         */
        _showLoading: function() {
            this.$('.btn_validate_dni').prop('disabled', true);
            this.$('.btn_validate_dni').html('<i class="fa fa-spinner fa-spin"></i>');
        },

        /**
         * Oculta spinner de carga
         */
        _hideLoading: function() {
            this.$('.btn_validate_dni').prop('disabled', false);
            this.$('.btn_validate_dni').html('<i class="fa fa-check"></i>');
        },

        _showFormReadonly: function() {
            // Desactiva inputs, selects y botones dentro del formulario de DNI
            self.$('.o_dni_validation_form')
                .find('input, select, button, textarea')
                .attr('disabled', true)
                .addClass('readonly-disabled');
        },

        _hideFormReadonly: function() {
            // Reactiva los mismos elementos
            self.$('.o_dni_validation_form')
                .find('input, select, button, textarea')
                .removeAttr('disabled')
                .removeClass('readonly-disabled');
        },

        _onStateChange: function() {
            var self = this;
            var stateId = this.$('#state_id').val();
            
            if (!stateId) return;
            
            // Filtrar cities por state
            this.$('#city_id option').each(function() {
                var $option = $(this);
                var optionStateId = $option.data('state_id');
                
                if (!optionStateId || optionStateId == stateId) {
                    $option.show();
                } else {
                    $option.hide();
                }
            });
            
            // Reset dependientes
            this.$('#city_id').val('');
            this.$('#district_id').val('').find('option:not(:first)').hide();
        },

        _onCityChange: function() {
            var self = this;
            var cityId = this.$('#city_id').val();
            
            if (!cityId) return;
            
            // Filtrar districts por city
            this.$('#district_id option').each(function() {
                var $option = $(this);
                var optionCityId = $option.data('city_id');
                
                if (!optionCityId || optionCityId == cityId) {
                    $option.show();
                } else {
                    $option.hide();
                }
            });
            
            // Reset
            this.$('#district_id').val('');
        },


    });

    return publicWidget.registry.DNIValidator;
});