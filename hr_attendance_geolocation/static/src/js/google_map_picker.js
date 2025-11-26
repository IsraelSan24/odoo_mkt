odoo.define('hr_attendance_geolocation.google_map_picker', function (require) {
    "use strict";
    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    function loadGoogleMapsScript(apiKey) {
        return new Promise((resolve, reject) => {
            if (window.google && window.google.maps) {
                return resolve();
            }
            if (document.getElementById('google-maps-script')) {
                const check = () => {
                    if (window.google && window.google.maps) resolve();
                    else setTimeout(check, 300);
                };
                check();
                return;
            }
            const script = document.createElement('script');
            script.id = 'google-maps-script';
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,geometry`;
            script.async = true;
            script.defer = true;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    const GoogleMapPicker = AbstractField.extend({
        template: 'hr_attendance_geolocation.GoogleMapPicker',
        supportedFieldTypes: ['float'],

        /**
         * @override
         */
        start: function () {
            this._super.apply(this, arguments);
            const API_KEY = 'AIzaSyB8ccMU2g5AjT0at_sD-F-QTmkHwRvOc0c';

            return loadGoogleMapsScript(API_KEY).then(() => {
                const mapDiv = this.el;

                if (!mapDiv || !mapDiv.classList.contains('o_google_map_picker')) {
                    this.$el.html('<div class="alert alert-danger">El contenedor del mapa no es válido.</div>');
                    console.error("El contenedor del mapa no es válido. Se esperaba un div con la clase 'o_google_map_picker'.", this.el);
                    return;
                }

                const lat = parseFloat(this.recordData.latitude) || -12.0464;
                const lng = parseFloat(this.recordData.longitude) || -77.0428;
                const proximityRadius = parseFloat(this.recordData.proximity_radius) || 1; // Radio en km

                this.map = new google.maps.Map(mapDiv, {
                    center: { lat, lng },
                    zoom: 15,
                });

                // Crear el marcador
                this.marker = new google.maps.Marker({
                    position: { lat, lng },
                    map: this.map,
                    draggable: true,
                });

                // Crear el círculo de cobertura
                this.circle = new google.maps.Circle({
                    strokeColor: '#4285F4',
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#4285F4',
                    fillOpacity: 0.2,
                    map: this.map,
                    center: { lat, lng },
                    radius: proximityRadius * 1000, // Convertir km a metros
                });

                // Evento cuando se arrastra el marcador
                google.maps.event.addListener(this.marker, 'dragend', (event) => {
                    const lat = event.latLng.lat();
                    const lng = event.latLng.lng();
                    
                    // Actualizar la posición del círculo
                    this.circle.setCenter(event.latLng);
                    
                    // Actualizar los campos
                    this.trigger_up('field_changed', {
                        dataPointID: this.dataPointID,
                        changes: { 
                            latitude: lat,
                            longitude: lng 
                        },
                    });
                });

                // Evento cuando se hace clic en el mapa
                this.map.addListener('click', (event) => {
                    const lat = event.latLng.lat();
                    const lng = event.latLng.lng();
                    
                    // Actualizar posición del marcador
                    this.marker.setPosition(event.latLng);
                    
                    // Actualizar posición del círculo
                    this.circle.setCenter(event.latLng);
                    
                    // Actualizar los campos
                    this.trigger_up('field_changed', {
                        dataPointID: this.dataPointID,
                        changes: { 
                            latitude: lat,
                            longitude: lng 
                        },
                    });
                });

            }).catch((err) => {
                this.$el.html('<div class="alert alert-danger">La API de Google Maps no se pudo cargar.</div>');
                console.error(err);
            });
        },

        /**
         * @override
         * Actualizar el círculo cuando cambie el radio de proximidad
         */
        _render: function () {
            this._super.apply(this, arguments);
            
            if (this.circle && this.recordData.proximity_radius) {
                const proximityRadius = parseFloat(this.recordData.proximity_radius);
                this.circle.setRadius(proximityRadius * 1000); // Convertir km a metros
            }
            
            if (this.marker && this.recordData.latitude && this.recordData.longitude) {
                const lat = parseFloat(this.recordData.latitude);
                const lng = parseFloat(this.recordData.longitude);
                const newPosition = { lat, lng };
                
                this.marker.setPosition(newPosition);
                if (this.circle) {
                    this.circle.setCenter(newPosition);
                }
                this.map.setCenter(newPosition);
            }
        },
    });

    fieldRegistry.add('google_map_picker', GoogleMapPicker);
    return GoogleMapPicker;
});