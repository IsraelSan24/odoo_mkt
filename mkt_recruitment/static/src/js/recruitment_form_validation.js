odoo.define('mkt_recruitment.recruitment_form_validation', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.RecruitmentFormValidation = publicWidget.Widget.extend({
        selector: 'form[data-model_name="hr.applicant"]',
        events: {
            'change select[name="identification_type_id"]': '_onIdentificationTypeChange',
            'input input[name="vat"]': '_onVatInput',
            'change input[name="vat"]': '_onVatInput',
            'click .s_website_form_send': '_onSubmitClick',
        },

        start: function () {
            this.$vatInput = this.$('input[name="vat"]');
            this.$typeSelect = this.$('select[name="identification_type_id"]');
            return this._super.apply(this, arguments);
        },

        _onIdentificationTypeChange: function () {
            this._validateVat();
        },

        _onVatInput: function () {
            this._validateVat();
        },

        _onSubmitClick: function (ev) {
            this._validateVat();
            if (!this.$vatInput[0].checkValidity()) {
                this.$vatInput[0].reportValidity();
            }
        },

        _validateVat: function () {
            var $selectedOption = this.$typeSelect.find('option:selected');
            var code = $selectedOption.data('code');
            var vat = this.$vatInput.val();

            // Reset validity first
            this.$vatInput[0].setCustomValidity("");
            
            if (!code || !vat) {
                return;
            }

            var isValid = true;
            var message = "";

            // Convert code to string just in case
            code = String(code);

            if (code === '1') { // DNI
                if (!/^\d{8}$/.test(vat)) {
                    isValid = false;
                    message = "El DNI debe tener exactamente 8 dígitos numéricos.";
                }
            } else if (code === '4') { // Carnet de Extranjería
                // CE: 9 to 12 alphanumeric characters
                if (!/^[a-zA-Z0-9]{9,12}$/.test(vat)) {
                    isValid = false;
                    message = "El Carnet de Extranjería debe tener entre 9 y 12 caracteres alfanuméricos.";
                }
            } else if (code === '7') { // Pasaporte
                // Pasaporte: 6 to 12 alphanumeric characters
                if (!/^[a-zA-Z0-9]{6,12}$/.test(vat)) {
                    isValid = false;
                    message = "El Pasaporte debe tener entre 6 y 12 caracteres alfanuméricos.";
                }
            } else if (code === 'F') { // PTP
                // PTP: 9 digits
                if (!/^\d{9}$/.test(vat)) {
                    isValid = false;
                    message = "El PTP debe tener 9 dígitos numéricos.";
                }
            }

            if (!isValid) {
                this.$vatInput[0].setCustomValidity(message);
                // Only report validity if the field is not empty (to avoid annoying popups while typing, 
                // though setCustomValidity prevents submission). 
                // If we want immediate feedback:
                // this.$vatInput[0].reportValidity(); 
            } else {
                this.$vatInput[0].setCustomValidity("");
            }
        }
    });
});
