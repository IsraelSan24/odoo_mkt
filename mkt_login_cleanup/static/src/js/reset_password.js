odoo.define('mkt_login_cleanup.reset_password', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    // Widget para limpiar el formulario de reset password
    publicWidget.registry.MKTResetPasswordCleanup = publicWidget.Widget.extend({
        selector: '.oe_reset_password_form',
        events: {
            'submit': '_onSubmit',
            'input input[name="login"]': '_onEmailInput',
        },

        /**
         * Limpiar y validar email al enviar formulario
         */
        _onSubmit: function (ev) {
            console.log('MKT Reset Password: Formulario enviado');
            
            var loginInput = this.$el.find('input[name="login"]');
            
            if (loginInput.length) {
                var loginValue = loginInput.val();
                console.log('Email original:', loginValue);
                
                // Eliminar espacios y convertir a minúsculas
                var cleanedValue = loginValue.trim().toLowerCase();
                loginInput.val(cleanedValue);
                
                console.log('Email limpio:', cleanedValue);
                
                // Validar formato de email básico
                if (cleanedValue && !this._isValidEmail(cleanedValue)) {
                    ev.preventDefault();
                    this._showError('Por favor, ingresa un correo electrónico válido');
                    return false;
                }
            }
        },

        /**
         * Limpiar espacios en tiempo real mientras escribe
         */
        _onEmailInput: function (ev) {
            var input = $(ev.currentTarget);
            var value = input.val();
            
            // Si hay espacios al inicio o final, eliminarlos
            var trimmed = value.trim();
            if (value !== trimmed && value.length > 0 && (value.startsWith(' ') || value.endsWith(' '))) {
                var cursorPos = input[0].selectionStart;
                input.val(trimmed);
                input[0].setSelectionRange(cursorPos - 1, cursorPos - 1);
            }
        },

        /**
         * Validar formato de email
         */
        _isValidEmail: function (email) {
            var emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            return emailRegex.test(email);
        },

        /**
         * Mostrar mensaje de error personalizado
         */
        _showError: function (message) {
            // Remover alertas anteriores
            this.$el.find('.mkt-alert-custom').remove();
            
            // Crear nueva alerta
            var alert = $('<div>', {
                class: 'alert alert-danger mkt-alert-custom',
                role: 'alert',
                html: '<i class="fa fa-exclamation-circle"></i> ' + message
            });
            
            // Insertar antes del primer campo del formulario
            this.$el.find('.field-login').before(alert);
            
            // Auto-ocultar después de 5 segundos
            setTimeout(function() {
                alert.fadeOut(400, function() {
                    $(this).remove();
                });
            }, 5000);
        },
    });

    return publicWidget.registry.MKTResetPasswordCleanup;
});