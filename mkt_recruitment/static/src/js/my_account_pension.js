odoo.define('mkt_recruitment.my_account', function (require) {
    'use strict';

    const publicWidget = require('web.public.widget');

    publicWidget.registry.PensionUIController = publicWidget.Widget.extend({
        selector: '#pension_system',

        events: {
            'change #private_pension_system': '_onPrivatePensionToggle',
            'change #afp_first_job': '_onAFPSelection',
            'change #coming_from_onp': '_onAFPSync',
            'change #coming_from_afp': '_onAFPSync',
            'change #national_pension_system': '_onNationalToggle',
        },

        start: function () {
            this._toggleAFPOptions();
            return this._super.apply(this, arguments);
        },

        // -----------------------------
        // PRIVATE PENSION LOGIC
        // -----------------------------
        _onPrivatePensionToggle: function () {
            const privateSys = this.$('#private_pension_system');
            const nationalSys = this.$('#national_pension_system');

            // If private system is selected → unselect national
            if (privateSys.is(':checked')) {
                nationalSys.prop('checked', false);
            }

            this._toggleAFPOptions();
        },

        // Show / hide AFP options
        _toggleAFPOptions: function () {
            const isPrivate = this.$('#private_pension_system').is(':checked');
            const afpContainer = this.$('#afp_options');

            if (isPrivate) {
                afpContainer.removeClass('d-none').hide().fadeIn(150);
            } else {
                afpContainer.fadeOut(150, () => {
                    afpContainer.addClass('d-none');
                    this.$('#afp_first_job, #coming_from_onp, #coming_from_afp').prop('checked', false);
                });
            }
        },

        // -----------------------------
        // NATIONAL SYSTEM LOGIC
        // -----------------------------
        _onNationalToggle: function () {
            const nationalSys = this.$('#national_pension_system');
            const privateSys = this.$('#private_pension_system');

            if (nationalSys.is(':checked')) {
                // Unselect private system + unselect all AFP
                privateSys.prop('checked', false);

                this.$('#afp_first_job, #coming_from_onp, #coming_from_afp').prop('checked', false);

                // Hide AFP container
                this.$('#afp_options').fadeOut(150, () => {
                    this.$('#afp_options').addClass('d-none');
                });
            } else {
                // If national is deselected, private can be managed normally
                this._toggleAFPOptions();
            }
        },

        // -----------------------------
        // AFP MUTUAL EXCLUSION
        // -----------------------------
        _onAFPSelection: function () {
            if (this.$('#afp_first_job').is(':checked')) {
                this.$('#coming_from_onp, #coming_from_afp').prop('checked', false);
            }
        },

        _onAFPSync: function () {
            if (
                this.$('#coming_from_onp').is(':checked') ||
                this.$('#coming_from_afp').is(':checked')
            ) {
                this.$('#afp_first_job').prop('checked', false);
            }
        },
    });

    return publicWidget.registry.PensionUIController;
});
