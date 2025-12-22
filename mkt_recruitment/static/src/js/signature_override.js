/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NameAndSignature } from "web.name_and_signature";

patch(NameAndSignature.prototype, "signature_patch_force_black_white", {
    start: async function () {
        await this._super.apply(this, arguments);

        this.$el.ready(() => {
            // 1. Configuración de botones: Ocultar Draw, Forzar Auto
            this.$('.o_web_sign_draw_button').hide();
            this.$('.o_web_sign_draw').hide();
            this.$('.o_web_sign_draw_clear').hide();
            this.$('.o_web_sign_auto_button').trigger('click');
            this._updatePreviewButtons?.();

            // ============================================
            // 2. INYECTAR CSS GLOBAL CON !important
            // ============================================
            const injectGlobalStyles = () => {
                const existingStyle = document.getElementById('signature_force_styles');
                if (existingStyle) {
                    existingStyle.remove();
                }

                const style = document.createElement('style');
                style.id = 'signature_force_styles';
                style.textContent = `
                    /* FORZAR TODO EL COMPONENTE A MODO CLARO */
                    .o_web_sign_name_and_signature,
                    .o_web_sign_name_and_signature *,
                    .modal-content:has(.o_web_sign_name_and_signature),
                    .card:has(.o_web_sign_name_and_signature) {
                        color-scheme: light !important;
                    }

                    /* CONTENEDOR PRINCIPAL */
                    .o_web_sign_name_and_signature {
                        background-color: #FFFFFF !important;
                        color: #000000 !important;
                    }

                    /* ÁREA DE FIRMA - FONDO BLANCO */
                    .o_web_sign_signature {
                        background-color: #FFFFFF !important;
                        border: 1px solid #CCCCCC !important;
                        color: #000000 !important;
                    }

                    /* INPUTS */
                    .o_web_sign_name_and_signature input,
                    .o_web_sign_name_and_signature input[type="text"] {
                        background-color: #FFFFFF !important;
                        color: #000000 !important;
                        border: 1px solid #CCCCCC !important;
                        -webkit-text-fill-color: #000000 !important;
                    }

                    /* CANVAS - FONDO TRANSPARENTE, FIRMA NEGRA */
                    .o_web_sign_signature canvas {
                        background-color: transparent !important;
                        mix-blend-mode: multiply !important;
                    }

                    /* SVG - FONDO TRANSPARENTE, FIRMA NEGRA */
                    .o_web_sign_signature svg {
                        background-color: transparent !important;
                    }

                    .o_web_sign_signature svg * {
                        fill: #000000 !important;
                        stroke: #000000 !important;
                    }

                    /* IMG - FONDO TRANSPARENTE, FIRMA NEGRA */
                    .o_web_sign_signature img {
                        background-color: transparent !important;
                        mix-blend-mode: multiply !important;
                    }

                    /* MODAL/CARD CONTENEDOR */
                    .modal-content:has(.o_web_sign_name_and_signature),
                    .card:has(.o_web_sign_name_and_signature) {
                        background-color: #FFFFFF !important;
                        color: #000000 !important;
                    }

                    /* LABELS Y TEXTO */
                    .o_web_sign_name_and_signature label,
                    .o_web_sign_name_and_signature .form-label {
                        color: #000000 !important;
                    }
                `;
                document.head.appendChild(style);
            };

            // ============================================
            // 3. FORZAR ESTILOS INLINE + CANVAS PROCESSING
            // ============================================
            const forceInlineStyles = () => {
                const container = this.el.querySelector('.o_web_sign_name_and_signature');
                const inputs = this.el.querySelectorAll('input');
                const area = this.el.querySelector('.o_web_sign_signature');
                const canvas = this.el.querySelector('.o_web_sign_signature canvas');
                const svg = this.el.querySelector('.o_web_sign_signature svg');
                const img = this.el.querySelector('.o_web_sign_signature img');
                const card = this.el.closest('.card, .modal-content, .modal');

                // Forzar color-scheme en elementos principales
                [this.el, container, area, card].forEach(el => {
                    if (el) {
                        el.style.setProperty('color-scheme', 'light', 'important');
                        el.style.setProperty('background-color', '#FFFFFF', 'important');
                        el.style.setProperty('color', '#000000', 'important');
                    }
                });

                // Área de firma: fondo blanco sólido
                if (area) {
                    area.style.setProperty('background-color', '#FFFFFF', 'important');
                }

                // Inputs
                inputs.forEach(input => {
                    input.style.setProperty('background-color', '#FFFFFF', 'important');
                    input.style.setProperty('color', '#000000', 'important');
                    input.style.setProperty('border', '1px solid #CCCCCC', 'important');
                    input.style.setProperty('-webkit-text-fill-color', '#000000', 'important');
                });

                // Canvas: transparente con mix-blend-mode multiply
                if (canvas) {
                    canvas.style.setProperty('background-color', 'transparent', 'important');
                    canvas.style.setProperty('mix-blend-mode', 'multiply', 'important');
                    
                    // Procesar el canvas para invertir colores si es necesario
                    processCanvas(canvas);
                }

                // SVG: firma negra
                if (svg) {
                    svg.style.setProperty('background-color', 'transparent', 'important');
                    svg.querySelectorAll('*').forEach(el => {
                        el.style.setProperty('fill', '#000000', 'important');
                        el.style.setProperty('stroke', '#000000', 'important');
                    });
                }

                // IMG: transparente con mix-blend-mode
                if (img) {
                    img.style.setProperty('background-color', 'transparent', 'important');
                    img.style.setProperty('mix-blend-mode', 'multiply', 'important');
                }
            };

            // ============================================
            // 4. PROCESAR CANVAS PARA INVERTIR COLORES BLANCOS
            // ============================================
            const processCanvas = (canvas) => {
                if (!canvas || canvas.width === 0 || canvas.height === 0) return;

                try {
                    const ctx = canvas.getContext('2d');
                    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                    const data = imageData.data;

                    // Recorrer cada pixel
                    for (let i = 0; i < data.length; i += 4) {
                        const r = data[i];
                        const g = data[i + 1];
                        const b = data[i + 2];
                        const a = data[i + 3];

                        // Si el pixel es blanco o casi blanco (firma en modo oscuro)
                        if (r > 200 && g > 200 && b > 200 && a > 0) {
                            // Convertir a negro
                            data[i] = 0;
                            data[i + 1] = 0;
                            data[i + 2] = 0;
                            // Mantener alpha
                        }
                        // Si el pixel es transparente o de fondo
                        else if (a === 0 || (r < 10 && g < 10 && b < 10)) {
                            // Hacerlo completamente transparente
                            data[i + 3] = 0;
                        }
                    }

                    // Aplicar los cambios
                    ctx.putImageData(imageData, 0, 0);
                } catch (e) {
                    console.warn('No se pudo procesar el canvas:', e);
                }
            };

            // ============================================
            // 5. OBSERVER PARA DETECTAR CAMBIOS EN EL DOM
            // ============================================
            const setupObserver = () => {
                const targetNode = this.el.querySelector('.o_web_sign_signature');
                if (!targetNode) return;

                const observer = new MutationObserver(() => {
                    forceInlineStyles();
                });

                observer.observe(targetNode, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    attributeFilter: ['style', 'class']
                });

                this._signatureObserver = observer;
            };

            // ============================================
            // 6. APLICAR TODO
            // ============================================
            const applyAll = () => {
                injectGlobalStyles();
                forceInlineStyles();
            };

            // Ejecutar inmediatamente
            applyAll();
            setupObserver();

            // Re-aplicar en intervalos
            const intervals = [50, 100, 200, 500, 1000, 2000];
            intervals.forEach(delay => setTimeout(applyAll, delay));

            // Re-aplicar cuando cambie el modo auto/draw
            this.$('.o_web_sign_auto_button, .o_web_sign_draw_button').on('click', () => {
                setTimeout(applyAll, 50);
                setTimeout(applyAll, 200);
            });

            // Re-aplicar cuando se escriba en inputs
            this.$('input').on('input change keyup', () => {
                setTimeout(applyAll, 100);
                setTimeout(applyAll, 300);
            });
        });
    },

    destroy: function () {
        if (this._signatureObserver) {
            this._signatureObserver.disconnect();
        }
        const existingStyle = document.getElementById('signature_force_styles');
        if (existingStyle) {
            existingStyle.remove();
        }
        return this._super.apply(this, arguments);
    }
});