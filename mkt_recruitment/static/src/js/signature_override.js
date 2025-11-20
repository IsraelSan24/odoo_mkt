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
            // const desiredFontIndex = 2;  
            // this._setFont(desiredFontIndex);

            // Forzamos refresh de vista
            this._updatePreviewButtons?.();

            // FIX: Force white background and black ink for dark mode compatibility
            const $sigContainer = this.$('.o_web_sign_name_and_signature');
            const $canvas = this.$('canvas.jSignature');

            if ($sigContainer.length) {
                $sigContainer.css({
                    'background-color': '#FFFFFF',
                    'color': '#000000',
                    'border': '1px solid #CCCCCC'
                });
            }

            if ($canvas.length) {
                // Force canvas background to white
                $canvas.css('background-color', '#FFFFFF');

                // Try to set jSignature settings if accessible
                // Note: jSignature usually takes options at init, changing after might require internal API
                // But we can at least ensure the container is white so transparent canvas looks white.

                // If we need to force the ink color, we might need to access the jSignature instance
                // specific to how Odoo initializes it. 
                // Usually Odoo's NameAndSignature uses jSignature.

                // Ensure the "draw" area specifically is white
                this.$('.o_web_sign_signature').css('background-color', '#FFFFFF');
            }
        });
    },
});
