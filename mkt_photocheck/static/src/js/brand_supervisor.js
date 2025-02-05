odoo.define('mkt_photocheck.brand_supervisor', function(require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.brandSupervisor = publicWidget.Widget.extend({
        selector: '.o_brand_supervisor',
        events: {
            'change select[name="photocheck_brand_group_id"]': '_onBrandChange',
        },

        start: function () {
            var def = this._super.apply(this, arguments);

            this.$brand = this.$('select[name="photocheck_brand_group_id"]');
            this.$supervisor = this.$('select[name="photocheck_supervisor_id"]');
            this.$supervisorOptions = this.$supervisor.find('option:not(:first)');

            this._adaptSupervisorForm();

            return def;
        },

        _adaptSupervisorForm: function () {
            var brandID = this.$brand.val() || 0;
            
            this.$supervisorOptions.detach();
            var $displayedSupervisors = this.$supervisorOptions.filter(function() {
                var brandGroupIds = $(this).data('brand_group_ids');
                return brandGroupIds && brandGroupIds.includes(parseInt(brandID));
            });
            
            this.$supervisor.find('option:not(:first)').remove();
            $displayedSupervisors.appendTo(this.$supervisor);
            
            var nb = $displayedSupervisors.length;
            this.$supervisor.parent().toggle(nb >= 1);
            
            // Resetear la selección del supervisor
            this.$supervisor.val('');
        },

        _onBrandChange: function () {
            this._adaptSupervisorForm();
        },
    });
});