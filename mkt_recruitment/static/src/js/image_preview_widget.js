odoo.define('mkt_recruitment.ImagePreviewWidget', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    // ────────────────────────────────────────────
    // Inyectar CSS del widget
    // ────────────────────────────────────────────
    const styles = `
    .outer-container {
        padding-top: 20px;
        max-height: none;
        min-height: 300px;
        max-width: 1000px;
        min-width: 600px;
        overflow: auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .rotation-wrapper {
        display: inline-block;
        transform-origin: center center; /* rotación desde el centro */
        transition: transform 0.3s ease;
    }

    .zoom-wrapper {
        display: inline-block;
        transform-origin: top left; /* zoom hacia top-left */
        transition: transform 0.3s ease;
    }

    .preview-image {
        display: block;
        max-width: none; /* importante: evitar que el zoom se limite */
    }
    `;

    $('<style>').text(styles).appendTo(document.head);


    // ────────────────────────────────────────────
    // Widget principal
    // ────────────────────────────────────────────
    const ImagePreviewWidget = AbstractField.extend({

        className: 'o_field_image_preview',

        _render: function () {
            this.$el.empty();
            const imageData = this.value;

            if (!imageData) {
                this.$el.html('<p>No hay documento disponible</p>');
                return;
            }

            this.$el.html(`
                <div style="text-align: center;">
                <div style="
                    position: fixed;
                    top: 19px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: white;
                    padding: 10px;
                    border: 1px solid #ccc;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    z-index: 9999;
                ">
                    <button class="btn btn-sm btn-primary zoom-in">Zoom +</button>
                    <button class="btn btn-sm btn-primary zoom-out">Zoom -</button>
                    <button class="btn btn-sm btn-secondary rotate-left">↺ Rotar Izq</button>
                    <button class="btn btn-sm btn-secondary rotate-right">↻ Rotar Der</button>
                    <button class="btn btn-sm btn-warning reset">Reset</button>
                </div>
                
                    <div class="outer-container">
                        <div class="zoom-wrapper">
                            <div class="rotation-wrapper">
                                <img class="preview-image" src="data:image/png;base64,${imageData}">
                            </div>
                        </div>
                    </div>
                </div>
            `);


            // ────────────────────────────────────────────
            // Transformaciones separadas
            // ────────────────────────────────────────────
            let scale = 1;
            let rotation = 0;

            const updateTransform = () => {
                this.$('.zoom-wrapper')
                    .css('transform', `scale(${scale})`);
                
                this.$('.rotation-wrapper')
                    .css('transform', `rotate(${rotation}deg)`);
                
            };

            const adjustContainerSize = () => {
                const img = this.$('.preview-image')[0];

                if (!img.naturalWidth) return;

                let w = img.naturalWidth * scale;
                let h = img.naturalHeight * scale;

                // Calcular la diagonal necesaria para acomodar la imagen rotada
                // Cuando se rota desde el centro, necesita espacio diagonal
                let diagonal = Math.sqrt(w * w + h * h);

                // Aplicar tamaño al wrapper exterior con espacio suficiente
                this.$('.outer-container').css({
                    'min-width':  (diagonal + 100) + 'px',
                    'min-height': (diagonal + 100) + 'px',
                });
            };

            const adjustContainerSizeOriginal = () => {
                const img = this.$('.preview-image')[0];

                if (!img.naturalWidth) return;

                let w = img.naturalWidth;
                let h = img.naturalHeight;

                // Aplicar tamaño al wrapper exterior en estado original
                this.$('.outer-container').css({
                    'min-width':  (w + 100) + 'px',
                    'min-height': (h ) + 'px',
                });
            };



            // ────────────────────────────────────────────
            // Eventos
            // ────────────────────────────────────────────
            this.$('.zoom-in').on('click', () => {
                scale += 0.2;
                updateTransform();
                // adjustContainerSize();
            });

            this.$('.zoom-out').on('click', () => {
                if (scale > 0.4) {
                    scale -= 0.2;
                    updateTransform();
                    // adjustContainerSize();
                }
            });

            this.$('.rotate-left').on('click', (e) => {
                e.preventDefault();
                rotation -= 90;
                updateTransform();
                adjustContainerSize();
            });

            this.$('.rotate-right').on('click', (e) => {
                e.preventDefault();
                rotation += 90;
                updateTransform();
                adjustContainerSize();
            });

            this.$('.reset').on('click', () => {
                // Aplicar tamaño al wrapper exterior
                scale = 1;
                rotation = 0;
                updateTransform();
                adjustContainerSizeOriginal();
            });
        },
    });

    fieldRegistry.add('image_preview', ImagePreviewWidget);
    return ImagePreviewWidget;
});
