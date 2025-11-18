odoo.define('hr_attendance_geolocation.google_map_viewer', function (require) {
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

    const GoogleMapViewer = AbstractField.extend({
        // NO usar template, crear el contenedor manualmente
        className: 'o_field_google_map_viewer',
        supportedFieldTypes: ['text', 'char'],

        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            console.log('GoogleMapViewer initialized');
        },

        /**
         * @override
         */
        start: function () {
            console.log('GoogleMapViewer start called');
            console.log('Field value:', this.value);
            
            const self = this;
            
            // Crear el contenedor del mapa manualmente
            this.$el.empty();
            this.$mapContainer = $('<div>')
                .addClass('o_google_map_viewer_container')
                .css({
                    'width': '100%',
                    'height': '400px',
                    'position': 'relative',
                    'border': '1px solid #ddd',
                    'border-radius': '4px'
                });
            this.$el.append(this.$mapContainer);
            
            return this._super.apply(this, arguments).then(function() {
                const API_KEY = 'AIzaSyB8ccMU2g5AjT0at_sD-F-QTmkHwRvOc0c';

                return loadGoogleMapsScript(API_KEY).then(function() {
                    console.log('Google Maps loaded successfully');
                    self._renderMap();
                }).catch(function(err) {
                    console.error('Error loading Google Maps:', err);
                    self.$el.html('<div class="alert alert-warning">No se pudo cargar el mapa de ubicación.</div>');
                });
            });
        },

        _renderMap: function () {
            console.log('_renderMap called');
            
            const mapDiv = this.$mapContainer[0];
            
            if (!mapDiv) {
                console.error("El contenedor del mapa no se encontró.");
                this.$el.html('<div class="alert alert-danger">El contenedor del mapa no se encontró.</div>');
                return;
            }

            console.log('Map container found:', mapDiv);

            // Parsear los datos JSON del campo
            let locationData;
            try {
                const fieldValue = this.value || '{}';
                console.log('Parsing field value:', fieldValue);
                locationData = JSON.parse(fieldValue);
                console.log('Location data parsed:', locationData);
            } catch (e) {
                console.error('Error parsing location data:', e);
                this.$el.html('<div class="alert alert-danger">Error al cargar datos de ubicación.</div>');
                return;
            }

            // Validar que existan coordenadas de check-in
            if (!locationData.has_check_in || !locationData.check_in_lat || !locationData.check_in_lng) {
                console.warn('No check-in coordinates found');
                this.$el.html('<div class="alert alert-info">No hay coordenadas de ubicación registradas.</div>');
                return;
            }

            const checkInLat = parseFloat(locationData.check_in_lat);
            const checkInLng = parseFloat(locationData.check_in_lng);
            const checkOutLat = parseFloat(locationData.check_out_lat);
            const checkOutLng = parseFloat(locationData.check_out_lng);
            const hasCheckOut = locationData.has_check_out;
            const workLocation = locationData.work_location;

            console.log('Check-in coordinates:', checkInLat, checkInLng);
            console.log('Check-out coordinates:', checkOutLat, checkOutLng, 'Has check-out:', hasCheckOut);
            console.log('Work location:', workLocation);

            // Inicializar el mapa centrado en el check-in
            this.map = new google.maps.Map(mapDiv, {
                center: { lat: checkInLat, lng: checkInLng },
                zoom: 16,
                disableDefaultUI: false,
                zoomControl: true,
                mapTypeControl: false,
                streetViewControl: false,
                fullscreenControl: true,
            });

            console.log('Map created successfully');

            // Crear marcador para el check-in (verde)
            const checkInMarker = new google.maps.Marker({
                position: { lat: checkInLat, lng: checkInLng },
                map: this.map,
                title: 'Check-in',
                icon: {
                    url: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
                },
                label: {
                    text: 'IN',
                    color: 'white',
                    fontWeight: 'bold'
                }
            });

            console.log('Check-in marker created');

            // Crear marcador para el check-out (rojo) si existe
            if (hasCheckOut && checkOutLat && checkOutLng && !isNaN(checkOutLat) && !isNaN(checkOutLng)) {
                const checkOutMarker = new google.maps.Marker({
                    position: { lat: checkOutLat, lng: checkOutLng },
                    map: this.map,
                    title: 'Check-out',
                    icon: {
                        url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
                    },
                    label: {
                        text: 'OUT',
                        color: 'white',
                        fontWeight: 'bold'
                    }
                });

                console.log('Check-out marker created');

                // Ajustar los límites del mapa para mostrar ambos marcadores
                const bounds = new google.maps.LatLngBounds();
                bounds.extend({ lat: checkInLat, lng: checkInLng });
                bounds.extend({ lat: checkOutLat, lng: checkOutLng });
                
                if (workLocation && workLocation.lat && workLocation.lng) {
                    bounds.extend({ lat: workLocation.lat, lng: workLocation.lng });
                }
                
                this.map.fitBounds(bounds);
            }

            // Si hay ubicación de trabajo asignada, mostrarla
            if (workLocation && workLocation.lat && workLocation.lng) {
                const workLat = parseFloat(workLocation.lat);
                const workLng = parseFloat(workLocation.lng);
                const proximityRadius = parseFloat(workLocation.radius) || 1;

                console.log('Creating work location marker at:', workLat, workLng);

                // Marcador de la ubicación de trabajo (azul)
                const workMarker = new google.maps.Marker({
                    position: { lat: workLat, lng: workLng },
                    map: this.map,
                    title: `Ubicación de trabajo: ${workLocation.name || 'Sin nombre'}`,
                    icon: {
                        url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
                    },
                    label: {
                        text: 'W',
                        color: 'white',
                        fontWeight: 'bold'
                    }
                });

                // Círculo de proximidad
                const proximityCircle = new google.maps.Circle({
                    strokeColor: '#4285F4',
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: '#4285F4',
                    fillOpacity: 0.15,
                    map: this.map,
                    center: { lat: workLat, lng: workLng },
                    radius: proximityRadius * 1000, // Convertir km a metros
                });

                console.log('Work location marker and circle created');

                // Ajustar el zoom para mostrar todo
                if (!hasCheckOut) {
                    const bounds = new google.maps.LatLngBounds();
                    bounds.extend({ lat: checkInLat, lng: checkInLng });
                    bounds.union(proximityCircle.getBounds());
                    this.map.fitBounds(bounds);
                }
            }

            // Agregar leyenda
            this._addLegend(hasCheckOut, workLocation);
            console.log('Map rendering complete');
        },

        _addLegend: function (hasCheckOut, workLocation) {
            const legend = document.createElement('div');
            legend.style.cssText = `
                background: white;
                padding: 10px;
                margin: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.3);
                font-family: Arial, sans-serif;
                font-size: 12px;
            `;

            let legendHTML = '<div style="font-weight: bold; margin-bottom: 5px;">Leyenda:</div>';
            legendHTML += '<div><span style="color: green;">●</span> Check-in</div>';
            
            if (hasCheckOut) {
                legendHTML += '<div><span style="color: red;">●</span> Check-out</div>';
            }
            
            if (workLocation) {
                legendHTML += '<div><span style="color: blue;">●</span> Ubicación de trabajo</div>';
                legendHTML += '<div><span style="color: #4285F4;">○</span> Radio de proximidad</div>';
            }

            legend.innerHTML = legendHTML;
            this.map.controls[google.maps.ControlPosition.LEFT_TOP].push(legend);
        },
    });

    fieldRegistry.add('google_map_viewer', GoogleMapViewer);
    
    console.log('GoogleMapViewer widget registered');
    
    return GoogleMapViewer;
});
// odoo.define('hr_attendance_geolocation.google_map_viewer', function (require) {
//     "use strict";
//     const AbstractField = require('web.AbstractField');
//     const fieldRegistry = require('web.field_registry');

//     function loadGoogleMapsScript(apiKey) {
//         return new Promise((resolve, reject) => {
//             if (window.google && window.google.maps) {
//                 return resolve();
//             }
//             if (document.getElementById('google-maps-script')) {
//                 const check = () => {
//                     if (window.google && window.google.maps) resolve();
//                     else setTimeout(check, 300);
//                 };
//                 check();
//                 return;
//             }
//             const script = document.createElement('script');
//             script.id = 'google-maps-script';
//             script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,geometry`;
//             script.async = true;
//             script.defer = true;
//             script.onload = resolve;
//             script.onerror = reject;
//             document.head.appendChild(script);
//         });
//     }

//     const GoogleMapViewer = AbstractField.extend({
//         template: 'hr_attendance_geolocation.GoogleMapViewer',
//         supportedFieldTypes: ['text', 'char'],

//         /**
//          * @override
//          */
//         init: function () {
//             this._super.apply(this, arguments);
//             console.log('GoogleMapViewer initialized');
//         },

//         /**
//          * @override
//          */
//         start: function () {
//             console.log('GoogleMapViewer start called');
//             console.log('Field value:', this.value);
            
//             const self = this;
//             return this._super.apply(this, arguments).then(function() {
//                 const API_KEY = 'AIzaSyB8ccMU2g5AjT0at_sD-F-QTmkHwRvOc0c';

//                 return loadGoogleMapsScript(API_KEY).then(function() {
//                     console.log('Google Maps loaded successfully');
//                     self._renderMap();
//                 }).catch(function(err) {
//                     console.error('Error loading Google Maps:', err);
//                     self.$el.html('<div class="alert alert-warning">No se pudo cargar el mapa de ubicación.</div>');
//                 });
//             });
//         },

//         _renderMap: function () {
//             console.log('_renderMap called');
            
//             const mapDiv = this.$el.find('.o_google_map_viewer_container')[0];
            
//             if (!mapDiv) {
//                 console.error("El contenedor del mapa no se encontró.");
//                 return;
//             }

//             console.log('Map container found:', mapDiv);

//             // Parsear los datos JSON del campo
//             let locationData;
//             try {
//                 const fieldValue = this.value || '{}';
//                 console.log('Parsing field value:', fieldValue);
//                 locationData = JSON.parse(fieldValue);
//                 console.log('Location data parsed:', locationData);
//             } catch (e) {
//                 console.error('Error parsing location data:', e);
//                 this.$el.html('<div class="alert alert-danger">Error al cargar datos de ubicación.</div>');
//                 return;
//             }

//             // Validar que existan coordenadas de check-in
//             if (!locationData.has_check_in || !locationData.check_in_lat || !locationData.check_in_lng) {
//                 console.warn('No check-in coordinates found');
//                 this.$el.html('<div class="alert alert-info">No hay coordenadas de ubicación registradas.</div>');
//                 return;
//             }

//             const checkInLat = parseFloat(locationData.check_in_lat);
//             const checkInLng = parseFloat(locationData.check_in_lng);
//             const checkOutLat = parseFloat(locationData.check_out_lat);
//             const checkOutLng = parseFloat(locationData.check_out_lng);
//             const hasCheckOut = locationData.has_check_out;
//             const workLocation = locationData.work_location;

//             console.log('Check-in coordinates:', checkInLat, checkInLng);
//             console.log('Check-out coordinates:', checkOutLat, checkOutLng, 'Has check-out:', hasCheckOut);
//             console.log('Work location:', workLocation);

//             // Inicializar el mapa centrado en el check-in
//             this.map = new google.maps.Map(mapDiv, {
//                 center: { lat: checkInLat, lng: checkInLng },
//                 zoom: 16,
//                 disableDefaultUI: false,
//                 zoomControl: true,
//                 mapTypeControl: false,
//                 streetViewControl: false,
//                 fullscreenControl: true,
//             });

//             console.log('Map created successfully');

//             // Crear marcador para el check-in (verde)
//             const checkInMarker = new google.maps.Marker({
//                 position: { lat: checkInLat, lng: checkInLng },
//                 map: this.map,
//                 title: 'Check-in',
//                 icon: {
//                     url: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
//                 },
//                 label: {
//                     text: 'IN',
//                     color: 'white',
//                     fontWeight: 'bold'
//                 }
//             });

//             console.log('Check-in marker created');

//             // Crear marcador para el check-out (rojo) si existe
//             if (hasCheckOut && checkOutLat && checkOutLng && !isNaN(checkOutLat) && !isNaN(checkOutLng)) {
//                 const checkOutMarker = new google.maps.Marker({
//                     position: { lat: checkOutLat, lng: checkOutLng },
//                     map: this.map,
//                     title: 'Check-out',
//                     icon: {
//                         url: 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
//                     },
//                     label: {
//                         text: 'OUT',
//                         color: 'white',
//                         fontWeight: 'bold'
//                     }
//                 });

//                 console.log('Check-out marker created');

//                 // Ajustar los límites del mapa para mostrar ambos marcadores
//                 const bounds = new google.maps.LatLngBounds();
//                 bounds.extend({ lat: checkInLat, lng: checkInLng });
//                 bounds.extend({ lat: checkOutLat, lng: checkOutLng });
                
//                 if (workLocation && workLocation.lat && workLocation.lng) {
//                     bounds.extend({ lat: workLocation.lat, lng: workLocation.lng });
//                 }
                
//                 this.map.fitBounds(bounds);
//             }

//             // Si hay ubicación de trabajo asignada, mostrarla
//             if (workLocation && workLocation.lat && workLocation.lng) {
//                 const workLat = parseFloat(workLocation.lat);
//                 const workLng = parseFloat(workLocation.lng);
//                 const proximityRadius = parseFloat(workLocation.radius) || 1;

//                 console.log('Creating work location marker at:', workLat, workLng);

//                 // Marcador de la ubicación de trabajo (azul)
//                 const workMarker = new google.maps.Marker({
//                     position: { lat: workLat, lng: workLng },
//                     map: this.map,
//                     title: `Ubicación de trabajo: ${workLocation.name || 'Sin nombre'}`,
//                     icon: {
//                         url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
//                     },
//                     label: {
//                         text: 'W',
//                         color: 'white',
//                         fontWeight: 'bold'
//                     }
//                 });

//                 // Círculo de proximidad
//                 const proximityCircle = new google.maps.Circle({
//                     strokeColor: '#4285F4',
//                     strokeOpacity: 0.8,
//                     strokeWeight: 2,
//                     fillColor: '#4285F4',
//                     fillOpacity: 0.15,
//                     map: this.map,
//                     center: { lat: workLat, lng: workLng },
//                     radius: proximityRadius * 1000, // Convertir km a metros
//                 });

//                 console.log('Work location marker and circle created');

//                 // Ajustar el zoom para mostrar todo
//                 if (!hasCheckOut) {
//                     const bounds = new google.maps.LatLngBounds();
//                     bounds.extend({ lat: checkInLat, lng: checkInLng });
//                     bounds.union(proximityCircle.getBounds());
//                     this.map.fitBounds(bounds);
//                 }
//             }

//             // Agregar leyenda
//             this._addLegend(hasCheckOut, workLocation);
//             console.log('Map rendering complete');
//         },

//         _addLegend: function (hasCheckOut, workLocation) {
//             const legend = document.createElement('div');
//             legend.style.cssText = `
//                 background: white;
//                 padding: 10px;
//                 margin: 10px;
//                 border-radius: 5px;
//                 box-shadow: 0 2px 6px rgba(0,0,0,0.3);
//                 font-family: Arial, sans-serif;
//                 font-size: 12px;
//             `;

//             let legendHTML = '<div style="font-weight: bold; margin-bottom: 5px;">Leyenda:</div>';
//             legendHTML += '<div><span style="color: green;">●</span> Check-in</div>';
            
//             if (hasCheckOut) {
//                 legendHTML += '<div><span style="color: red;">●</span> Check-out</div>';
//             }
            
//             if (workLocation) {
//                 legendHTML += '<div><span style="color: blue;">●</span> Ubicación de trabajo</div>';
//                 legendHTML += '<div><span style="color: #4285F4;">○</span> Radio de proximidad</div>';
//             }

//             legend.innerHTML = legendHTML;
//             this.map.controls[google.maps.ControlPosition.LEFT_TOP].push(legend);
//         },
//     });

//     fieldRegistry.add('google_map_viewer', GoogleMapViewer);
    
//     console.log('GoogleMapViewer widget registered');
    
//     return GoogleMapViewer;
// });