odoo.define('studio_for_community.GraphViewProperty', function (require) {
"use strict";

    var core = require('web.core');
    var Base = require('studio_for_community.BaseEdit');


    var GraphViewProperty = Base.PropertyBase.extend({
        start: function () {
            this._super();
            const {view} = this.property;
            view.graph = {};
            view.graph.graph = [];
        },
        renderTab: function () {},
    });

    return GraphViewProperty;
});
