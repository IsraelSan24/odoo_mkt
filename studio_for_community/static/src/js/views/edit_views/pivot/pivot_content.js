/** @odoo-module alias=studio_for_community.PivotViewContent**/

import {PivotView} from "@web/views/pivot/pivot_view";
import Base from 'studio_for_community.BaseEdit';
import {ViewContainer} from 'studio_for_community.ViewContainer';
import {View} from "@web/views/view";

const {mount} = owl;


var PivotEditContent = Base.ContentBase.extend({
    template: 'PivotViewEdit.Content',
    init: function (parent, params) {
        this._super(parent, params);
        this.parent = parent;
    },
    start: function () {
        const {action} = this.props;
        this.action = action;
    },
    bindAction: function () {
    },
    renderView: async function () {
        let self = this;
        const {context, res_model} = this.action, {rootViewType} = this.props;
        const props = {
            resModel: res_model,
            type: rootViewType,
            context: context,
            display: {
                controlPanel: false,
            }
        }
        // const info = {
        //     Component: View,
        //     componentProps: props
        // }
        // const env = odoo.rootStudio.env;
        // await mount(ViewContainer, {
        //     env,
        //     props: {info: info},
        //     target: self.$el[0],
        //     position: "first-child"
        // });

        // const info = {
        //     Component: View,
        //     componentProps: props
        // }
        const env = odoo.rootStudio.env;
        await mount(View, {
            env,
            props: props,
            target: self.$el[0],
            position: "first-child"
        });
    },
});

export default PivotEditContent;

// });
