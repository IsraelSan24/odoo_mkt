odoo.define('mkt_login_cleanup.login', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.MKTLoginCleanup = publicWidget.Widget.extend({
        selector: '.oe_login_form',
        events: {
            'submit': '_onSubmit',
        },

        _onSubmit: function (ev) {
            var loginInput = this.$el.find('input[name="login"]');
            var passwordInput = this.$el.find('input[name="password"]');

            if (loginInput.length) {
                var loginValue = loginInput.val();
                loginInput.val(loginValue.trim().toLowerCase());
            }

            if (passwordInput.length) {
                var passwordValue = passwordInput.val();
                passwordInput.val(passwordValue.trim());
            }
        },
    });

    return publicWidget.registry.MKTLoginCleanup;
});