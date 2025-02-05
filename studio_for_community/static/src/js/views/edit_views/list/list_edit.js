odoo.define('studio_for_community.ListViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('studio_for_community.BaseEdit');
    var ListEditContent = require('studio_for_community.ListEditContent');
    var ListEditProperty = require('studio_for_community.ListEditProperty');


    var ListViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.sortData = [["tr, ._wFields", "tr"], ["._wSortable", "tr"]];
            this.view.property = ListEditProperty;
            this.view.content = ListEditContent;
        },
    });

    return ListViewEdit;
});
