odoo.define('mkt_recruitment.ImagePreviewWidget', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    // ────────────────────────────────────────────
    // Inyectar CSS del widget
    // ────────────────────────────────────────────
    const styles = `
    /* --- Estilos Comunes --- */
    .o_field_image_preview {
        width: 100%;
    }

    /* --- Estilos para Modo IMAGEN (Tu visor personalizado) --- */
    .image-viewer-container {
        height: 75vh;
        max-width: 100%;
        min-width: 800px;
        min-height: 500px;
        // overflow: auto;
        // border: 1px solid #ddd;
        // background: #f1f1f1;
        margin-top: 40px;
        cursor: grab;
        position: relative;
    }
    .image-viewer-container.is-grabbing {
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
        pointer-events: none; /* Para permitir el paneo sin arrastrar la img fantasma */
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
    }

    /* --- Estilos para Modo PDF (Visor nativo) --- */
    .pdf-viewer-container {
        height: 80vh; /* Un poco más alto para el PDF */
        width: 100%;
        border: 1px solid #ccc;
    }
    .pdf-viewer-iframe {
        width: 100%;
        height: 100%;
        border: none;
        display: block;
    }
    `;

    $('<style>').text(styles).appendTo(document.head);


    // ────────────────────────────────────────────
    // Widget principal
    // ────────────────────────────────────────────
    const ImagePreviewWidget = AbstractField.extend({

        className: 'o_field_image_preview',
        
        // Estado solo necesario para el modo Imagen
        state: {
            scale: 1,
            rotation: 0,
            naturalWidth: 0,
            naturalHeight: 0,
        },
        
        // Variables para el Paneo (solo imagen)
        isDragging: false,
        startX: 0,
        startY: 0,
        startScrollLeft: 0,
        startScrollTop: 0,

        _render: function () {
            this.$el.empty();
            const data = this.value;
            
            // Reiniciar estado
            this.state = { scale: 1, rotation: 0, naturalWidth: 0, naturalHeight: 0 };
            this.isDragging = false;

            if (!data) {
                this.$el.html('<p class="text-muted">No hay documento disponible</p>');
                return;
            }

            // 1. Detectar si es PDF
            const isPdf = data.startsWith('JVBERi');

            if (isPdf) {
                // ============================================================
                // MODO PDF: Visor Nativo
                // ============================================================
                // Sin botones custom, sin eventos custom. Solo el iframe.
                const src = 'data:application/pdf;base64,' + data;
                
                this.$el.html(`
                    <div class="pdf-viewer-container">
                        <iframe class="pdf-viewer-iframe" src="${src}" type="application/pdf">
                            <p>Tu navegador no soporta visualización de PDF.</p>
                        </iframe>
                    </div>
                `);
                
                // AQUÍ TERMINA EL RENDER PARA PDF. NO HACEMOS NADA MÁS.
                return;
            }

            // ============================================================
            // MODO IMAGEN: Visor Personalizado
            // ============================================================
            const src = 'data:image/png;base64,' + data;

            // Renderizamos botones y estructura compleja
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
                    
                    <div class="image-viewer-container">
                        <div class="zoom-wrapper">
                            <div class="rotation-wrapper">
                                <img class="preview-image" src="${src}">
                            </div>
                        </div>
                    </div>
                </div>
            `);

            // --- Lógica de Carga de Imagen ---
            const img = this.$('.preview-image')[0];
            
            const _onImageReady = (target) => {
                if (this.state.naturalWidth > 0) return;
                this.state.naturalWidth = target.naturalWidth;
                this.state.naturalHeight = target.naturalHeight;
                this._updateTransform(); // Aplicar estado inicial
            };

            if (img.complete) {
                _onImageReady(img);
            } else {
                this.$('.preview-image').on('load', (e) => {
                    _onImageReady(e.target);
                });
            }
            
            // Adjuntar eventos SOLO para la imagen
            this._bindImageEvents();
        },

        // ────────────────────────────────────────────
        // Funciones Exclusivas para MODO IMAGEN
        // ────────────────────────────────────────────

        _updateTransform: function () {
            if (this.state.naturalWidth === 0) return;

            const { scale, rotation, naturalWidth, naturalHeight } = this.state;
            let tx = 0, ty = 0;
            const normRotation = (rotation % 360 + 360) % 360;
            
            let currentWidth = naturalWidth;
            let currentHeight = naturalHeight;
            
            // Calcular compensaciones de rotación y tamaño del contenedor
            if (normRotation === 90) { 
                tx = naturalHeight; ty = 0; 
                currentWidth = naturalHeight; currentHeight = naturalWidth; 
            }
            else if (normRotation === 180) { 
                tx = naturalWidth; ty = naturalHeight; 
            }
            else if (normRotation === 270) { 
                tx = 0; ty = naturalWidth; 
                currentWidth = naturalHeight; currentHeight = naturalWidth; 
            }
            
            // Forzar tamaño del wrapper para que el scroll funcione bien
            this.$('.rotation-wrapper').css({
                width: currentWidth + 'px',
                height: currentHeight + 'px'
            });
            
            this.$('.zoom-wrapper').css('transform', `scale(${scale})`);
            
            // Orden: Translate primero, luego Rotate
            this.$('.rotation-wrapper').css(
                'transform', 
                `translate(${tx}px, ${ty}px) rotate(${rotation}deg)`
            );
        },

        _resetScroll: function() {
            this.$('.image-viewer-container').scrollTop(0).scrollLeft(0);
        },
        
        _bindImageEvents: function() {
            // 1. Botones
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
            
            // 2. Paneo (Drag & Drop)
            const $container = this.$('.image-viewer-container');

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
            
            // 3. Zoom con Ctrl + Rueda
            $container.on('wheel', (e) => {
                if (!e.ctrlKey) return; // Si no es Ctrl, dejar scroll normal
                e.preventDefault();

                const zoomIncrement = 0.1;
                if (e.originalEvent.deltaY < 0) {
                    this.state.scale += zoomIncrement;
                } else {
                    if (this.state.scale > (zoomIncrement + 0.1)) {
                        this.state.scale -= zoomIncrement;
                    }
                }
                this._updateTransform();
            });
        }
    });

    fieldRegistry.add('image_preview', ImagePreviewWidget);
    return ImagePreviewWidget;
});