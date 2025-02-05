odoo.define('studio_for_community.CalendarViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('studio_for_community.BaseEdit');
    var CalendarViewContent = require('studio_for_community.CalendarViewContent');
    var CalendarViewProperty = require('studio_for_community.CalendarViewProperty');


    var FormViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.view.property = CalendarViewProperty;
            this.view.content = CalendarViewContent;
        },

    });

    return FormViewEdit;
});
