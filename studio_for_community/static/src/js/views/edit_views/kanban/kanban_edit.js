odoo.define('studio_for_community.KanbanViewEdit', function (require) {
"use strict";

    // var core = require('web.core');
    var Base = require('studio_for_community.BaseEdit');
    var KanbanViewContent = require('studio_for_community.KanbanViewContent');
    var KanbanViewProperty = require('studio_for_community.KanbanViewProperty');


    var KanbanViewEdit = Base.EditBase.extend({
        start: function () {
            this._super();
            this.sortData = [[".oe_kanban_card", ".oe_kanban_card"]];
            this.view.property = KanbanViewProperty;
            this.view.content = KanbanViewContent;
        },
        _prepareParamProperty: function () {
            let res = this._super();
            res.onChangeTemplate = this.onChangeTemplate.bind(this);
            res.onChangeFieldSelect = this.onChangeFieldSelect.bind(this);
            return res;
        },
        _prepareParamContent: function () {
            let res = this._super();
            res.onAddTag = this.onAddTag.bind(this);
            return res;
        },
        onChangeFieldSelect: function (fieldName, addId) {
            this.ref.content.onChangeFieldSelect(fieldName, addId)
        },
        onChangeTemplate: function (template) {
            this.ref.content.changeTemplate(template);
        },
        onAddTag: function (tagType, addId) {
            this.ref.property.onClickAddTag(tagType, addId);
        },
    });

    return KanbanViewEdit;
});
