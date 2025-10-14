/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NameAndSignature } from "web.name_and_signature";

patch(NameAndSignature.prototype, "signature_patch_hide_draw", {
    start: async function () {
        // Llamamos al método original
        await this._super.apply(this, arguments);

        // Esperamos a que el DOM esté listo
        this.$el.ready(() => {
            // Ocultamos los botones o secciones relacionadas al "draw"
            this.$('.o_web_sign_draw_button').hide();
            this.$('.o_web_sign_draw').hide();
            this.$('.o_web_sign_draw_clear').hide();

            // Forzamos que el modo auto se seleccione automáticamente
            this.$('.o_web_sign_auto_button').trigger('click');

            // Forzamos altura
            // this.$('.o_web_sign_auto').css({
            // height: '20px', 
            // overflow: 'hidden',
            // });

            // Cambiar estilo de fuente por defecto
            const desiredFontIndex = 2;  
            this._setFont(desiredFontIndex);

            // Forzamos refresh de vista
            this._updatePreviewButtons?.();
        });
    },
});
