odoo.define('studio_for_community.GraphViewEdit', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('studio_for_community.BaseEdit');
    var GraphViewContent = require('studio_for_community.GraphViewContent');
    var GraphViewProperty = require('studio_for_community.GraphViewProperty');


    var GraphViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.view.property = GraphViewProperty;
            this.view.content = GraphViewContent;
        },

    });

    return GraphViewEdit;
});
