odoo.define('mkt_documental_managment.affidavit', function( require ) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.Affidavit = publicWidget.Widget.extend({
        selector: '.o_affidavit',
        events: {
            "change select[name='state_id']": '_onDepartmentChange',
            "change select[name='city_id']": '_onProvinceChange',
        },
        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);

            this.$province = this.$("select[name='city_id']");
            this.$district = this.$("select[name='district_id']");
            this.$provinceOptions = this.$province.filter(':enabled').find('option:not(:first)');
            this.$districtOptions = this.$district.filter(':enabled').find('option:not(:first)');

            this._adaptProvinceForm();
            this._adaptDistrictForm();

            return def;
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         */
        
        _adaptProvinceForm: function () {
            var $department = this.$("select[name='state_id']");
            var departmentID = ($department.val() || 0);
            this.$provinceOptions.detach();
            var $displayedProvince = this.$provinceOptions.filter('[data-state_id=' + departmentID + ']');
            var nb = $displayedProvince.appendTo(this.$province).show().length;
            this.$province.parent().toggle(nb >= 1);
        },

        _adaptDistrictForm: function () {
            var $province = this.$("select[name='city_id']");
            var provinceID = ($province.val() || 0);
            this.$districtOptions.detach();
            var $displayedDistrict = this.$districtOptions.filter('[data-city_id=' + provinceID + ']');
            var nb = $displayedDistrict.appendTo(this.$district).show().length;
            this.$district.parent().toggle(nb >= 1);
        },


        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         */

        _onDepartmentChange: function () {
            this._adaptProvinceForm();
        },

        _onProvinceChange: function () {
            this._adaptDistrictForm();
        },
    })
});