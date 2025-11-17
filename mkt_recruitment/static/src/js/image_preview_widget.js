odoo.define('mkt_recruitment.ImagePreviewWidget', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    // ... (CSS sin cambios) ...
    const styles = `
    .outer-container {
        height: 75vh;
        max-width: 100%;
        min-width: 800px;
        min-height: 500px;
        // overflow: auto;
        // border: 1px solid #ddd;
        // background: #f1f1f1;
        margin-top: 40px;
        cursor: grab;
    }
    .outer-container.is-grabbing {
        cursor: grabbing;
    }
    .zoom-wrapper {
        transform-origin: top left;
        transition: transform 0.2s ease-out;
        display: inline-block;
    }
    .rotation-wrapper {
        transform-origin: top left;
        transition: transform 0.2s ease-out;
        display: block;
    }
    .preview-image {
        display: block;
        max-width: none;
        user-select: none;
        pointer-events: none;
    }
    `;

    $('<style>').text(styles).appendTo(document.head);


    // ────────────────────────────────────────────
    // Widget principal
    // ────────────────────────────────────────────
    const ImagePreviewWidget = AbstractField.extend({

        className: 'o_field_image_preview',
        
        state: {
            scale: 1,
            rotation: 0,
            naturalWidth: 0,
            naturalHeight: 0,
        },
        
        isDragging: false,
        startX: 0,
        startY: 0,
        startScrollLeft: 0,
        startScrollTop: 0,

        _render: function () {
            // ... (Función _render sin cambios) ...
            this.$el.empty();
            const imageData = this.value;
            
            this.state = { scale: 1, rotation: 0, naturalWidth: 0, naturalHeight: 0 };
            this.isDragging = false; 

            if (!imageData) {
                this.$el.html('<p>No hay documento disponible</p>');
                return;
            }

            this.$el.html(`
                <div>
                    <div style="
                        position: fixed;
                        top: 80px; left: 50%; transform: translateX(-50%);
                        background: white; padding: 10px; border: 1px solid #ccc;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1); z-index: 9999;
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

            // --- Carga y Transformaciones ---
            const img = this.$('.preview-image')[0];
            const _onImageReady = (target) => {
                if (this.state.naturalWidth > 0) return;
                this.state.naturalWidth = target.naturalWidth;
                this.state.naturalHeight = target.naturalHeight;
                this._updateTransform(); 
            };
            if (img.complete) {
                _onImageReady(img);
            } else {
                this.$('.preview-image').on('load', (e) => {
                    _onImageReady(e.target);
                });
            }
            this._bindEvents();
        },

        /**
         * Aplica las transformaciones CSS basadas en el estado.
         */
        _updateTransform: function () {
            // ... (Función _updateTransform sin cambios) ...
            if (this.state.naturalWidth === 0) {
                return;
            }
            const { scale, rotation, naturalWidth, naturalHeight } = this.state;
            let tx = 0, ty = 0;
            const normRotation = (rotation % 360 + 360) % 360;
            let currentWidth = naturalWidth;
            let currentHeight = naturalHeight;
            
            if (normRotation === 90) { tx = naturalHeight; ty = 0; currentWidth = naturalHeight; currentHeight = naturalWidth; }
            else if (normRotation === 180) { tx = naturalWidth; ty = naturalHeight; }
            else if (normRotation === 270) { tx = 0; ty = naturalWidth; currentWidth = naturalHeight; currentHeight = naturalWidth; }
            
            this.$('.rotation-wrapper').css({
                width: currentWidth + 'px',
                height: currentHeight + 'px'
            });
            
            this.$('.zoom-wrapper').css('transform', `scale(${scale})`);
            this.$('.rotation-wrapper').css(
                'transform', 
                `translate(${tx}px, ${ty}px) rotate(${rotation}deg)`
            );
        },

        /**
         * Reinicia el scroll del visor a la esquina superior izquierda.
         */
        _resetScroll: function() {
            // ... (Función _resetScroll sin cambios) ...
            this.$('.outer-container').scrollTop(0).scrollLeft(0);
        },
        
        /**
         * Asigna los eventos a los botones
         */
        _bindEvents: function() {
            
            // --- Eventos de Botones ---
            this.$('.zoom-in').on('click', () => {
                this.state.scale += 0.2; this._updateTransform();
            });
            this.$('.zoom-out').on('click', () => {
                if (this.state.scale > 0.3) { this.state.scale -= 0.2; this._updateTransform(); }
            });
            this.$('.rotate-left').on('click', (e) => {
                e.preventDefault(); this.state.rotation -= 90; this._updateTransform(); this._resetScroll();
            });
            this.$('.rotate-right').on('click', (e) => {
                e.preventDefault(); this.state.rotation += 90; this._updateTransform(); this._resetScroll();
            });
            this.$('.reset').on('click', () => {
                this.state.scale = 1; this.state.rotation = 0; this._updateTransform(); this._resetScroll();
            });
            
            // --- Eventos de Paneo ---
            const $container = this.$('.outer-container');

            $container.on('mousedown', (e) => {
                if (e.button !== 0) return;
                e.preventDefault(); 
                this.isDragging = true;
                this.startX = e.clientX;
                this.startY = e.clientY;
                this.startScrollLeft = $container.scrollLeft();
                this.startScrollTop = $container.scrollTop();
                $container.addClass('is-grabbing');
            });

            this.$el.on('mouseup mouseleave', () => {
                if (!this.isDragging) return;
                this.isDragging = false;
                $container.removeClass('is-grabbing');
            });

            $container.on('mousemove', (e) => {
                if (!this.isDragging) return;
                e.preventDefault(); 
                const deltaX = e.clientX - this.startX;
                const deltaY = e.clientY - this.startY;
                $container.scrollLeft(this.startScrollLeft - deltaX);
                $container.scrollTop(this.startScrollTop - deltaY);
            });
            
            // --- NUEVO: Evento de Zoom con Rueda del Ratón ---
            
            $container.on('wheel', (e) => {
                // Solo activamos el zoom si la tecla Ctrl está presionada
                if (!e.ctrlKey) {
                    // Si Ctrl no está presionado, permite el scroll vertical
                    // normal del contenedor.
                    return;
                }

                // Si Ctrl SÍ está presionado, prevenimos el zoom del navegador
                e.preventDefault();

                // Usamos un incremento más pequeño para la rueda, da mejor sensación
                const zoomIncrement = 0.1;

                // e.originalEvent.deltaY < 0 es rueda "hacia arriba" (Zoom In)
                if (e.originalEvent.deltaY < 0) {
                    this.state.scale += zoomIncrement;
                    this._updateTransform();
                } else {
                // e.originalEvent.deltaY > 0 es rueda "hacia abajo" (Zoom Out)
                    if (this.state.scale > (zoomIncrement + 0.1)) {
                        this.state.scale -= zoomIncrement;
                        this._updateTransform();
                    }
                }
            });
        }
    });

    fieldRegistry.add('image_preview', ImagePreviewWidget);
    return ImagePreviewWidget;
});