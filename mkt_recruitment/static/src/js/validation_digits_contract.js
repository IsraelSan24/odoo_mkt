odoo.define('mkt_recruitment.validation_digits_contract', function( require ) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.ValidationDigitsContract = publicWidget.Widget.extend({
        selector: '.o_contract_signature_t',
        events: {
            'click .o_valterm': '_onOpenSignOptions',
        },

        start: function () {
            var self = this;
            
            // Delegación de eventos DESPUÉS de que el DOM esté listo
            // Usamos el namespace para poder removerlos después
            $(document).on('click.contract_validation', '#send-via-sms', function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                self._onSendViaSms();
            });
            $(document).on('click.contract_validation', '#send-via-email', function (ev) {
                ev.preventDefault();
                ev.stopPropagation();
                console.log('Email button clicked');
                self._onSendViaEmail();
            });

            return this._super.apply(this, arguments);
        },

        destroy: function() {
            // Limpiar event listeners al destruir el widget
            $(document).off('click.contract_validation');
            this._super.apply(this, arguments);
        },


        _onOpenSignOptions: function (ev) {
            if (ev) {
                ev.preventDefault();
                ev.stopPropagation();
            }
            
            // Resetear estado del modal
            $('#send-method-error').hide();
            $('#send-method-spinner').hide();
            // Abrir modal
            $('#contractSignOptionsModal').modal('show');
        },

        _updateVerificationMessage: function(method) {
            // Guardar el método en un campo oculto
            $('#verification_method').val(method);

            if (method === 'email') {
                $('#verification-text').text('Te enviamos un código de validación a tu correo:');
                $('#email-info').show();
                $('#sms-info').hide();
            } else if (method === 'sms') {
                $('#verification-text').text('Te enviamos un código de validación a tu celular:');
                $('#email-info').hide();
                $('#sms-info').show();
            }
        },

        // Handler para "Send via Email"
        _onSendViaEmail: function (ev) {
            var self = this;
            var contract_id = this._getContractId();

            if (!contract_id) {
                $('#send-method-error').text(_t('Contract ID not found')).show();
                return;
            }

            // Mostrar spinner, ocultar error
            $('#send-method-error').hide();
            $('#send-method-spinner').show();

            // Deshabilitar botones mientras se procesa
            $('#send-via-email, #send-via-sms').prop('disabled', true);

            rpc.query({
                model: 'hr.contract',
                method: 'send_email_to_validate_contract',
                args: [[contract_id]],
            }).then(function(result) {
            
                $('#send-method-spinner').hide();
                $('#send-via-email, #send-via-sms').prop('disabled', false);
                
                if (result === true || (result && result.success)) {
                    // Cerrar modal de opciones
                    $('#contractSignOptionsModal').modal('hide');
                    
                    self._updateVerificationMessage('email');
                    // Esperar a que se cierre completamente antes de abrir el siguiente
                    $('#contractSignOptionsModal').on('hidden.bs.modal', function() {
                        $('#contractvalidatedigits input[type=number]').val('');
                        $('#contractvalidatebox').modal('show');

                        $('#contractvalidatebox').on('shown.bs.modal', function() {
                            $('#input1').focus();
                        });
                    });
                } else {
                    var errorMsg = (result && result.message) || _t('Failed to send email');
                    $('#send-method-error').text(errorMsg).show();
                }
            }).catch(function(err) {
                $('#send-method-spinner').hide();
                $('#send-via-email, #send-via-sms').prop('disabled', false);
                $('#send-method-error').text(_t('Error sending email. Please try again.')).show();
            });
        },

        // Handler para "Send via SMS"
        _onSendViaSms: function (ev) {
            var self = this;
            var contract_id = this._getContractId();
            
            if (!contract_id) {
                $('#send-method-error').text(_t('Contract ID not found')).show();
                return;
            }

            $('#send-method-error').hide();
            $('#send-method-spinner').show();
            $('#send-via-email, #send-via-sms').prop('disabled', true);

            rpc.query({
                model: 'hr.contract',
                method: 'send_sms_to_validate_contract', // Método diferente para SMS
                args: [[contract_id]],
            }).then(function(result) {
                
                $('#send-method-spinner').hide();
                $('#send-via-email, #send-via-sms').prop('disabled', false);
                
                if (result === true || (result && result.success)) {
                    $('#contractSignOptionsModal').modal('hide');
                    
                    self._updateVerificationMessage('sms');

                    $('#contractSignOptionsModal').on('hidden.bs.modal', function() {
                        $('#contractvalidatedigits input[type=number]').val('');
                        $('#contractvalidatebox').modal('show');
                        
                        $('#contractvalidatebox').on('shown.bs.modal', function() {
                            $('#input1').focus();
                        });
                    });
                } else {
                    var errorMsg = (result && result.message) || _t('Failed to send SMS');
                    $('#send-method-error').text(errorMsg).show();
                }
            }).catch(function(err) {
                $('#send-method-spinner').hide();
                $('#send-via-email, #send-via-sms').prop('disabled', false);
                $('#send-method-error').text(_t('Error sending SMS. Please try again.')).show();
            });
        },
        
        _getContractId: function() {
            const contractId = this.$el.data('document-id');
            if (contractId) {
                return parseInt(contractId);
            }
            const url = new URL(window.location.href);
            return parseInt(url.pathname.split('/').pop());
            },
    });

    return publicWidget.registry.ValidationDigitsContract;
});
