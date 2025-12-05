/** mkt_recruitment/static/src/js/trecord_geolocation.js **/
odoo.define('mkt_recruitment.trecord_geolocation', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const session = require('web.session');
    var rpc = require('web.rpc');

    publicWidget.registry.MyGeolocalizationTRecord = publicWidget.Widget.extend({
        selector: '.o_trecord_validate_box',
        events: {
            'click #validate-btn-boxes': '_onClickGeo',
        },

        _onClickGeo: function (event) {
            event.preventDefault();
            var self = this;

            // Opcional: validar contexto URL si quieres restringirlo
            // const url = new URL(window.location.href);
            // if (!url.pathname.includes('/my/trecord')) {
            //     alert('Error de url, por favor contactarse con el área de sistemas.');
            //     return;
            // }

            if (!navigator.geolocation) {
                alert('Error de geolocalización, por favor contactarse con el área de sistemas.');
                return;
            }

            navigator.geolocation.getCurrentPosition(function (position) {
                const userAgent = navigator.userAgent;
                // (ctx no es estrictamente necesario, pero lo dejamos por simetría)
                const ctx = Object.assign({}, session.user_context, {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    user_agent: userAgent,
                });

                fetch('https://api.ipify.org?format=json')
                    .then(resp => resp.json())
                    .then(data => {
                        const ip = data && data.ip;
                        const trecordID = self._getTRecordId();

                        if (!trecordID) {
                            console.error('[TRecord Geo] No se encontró el ID del T-Record.');
                            alert('No se encontró el documento a geolocalizar.');
                            return;
                        }

                        rpc.query({
                            model: 't.record',
                            method: 'geolocation',
                            args: [[trecordID], position.coords.latitude, position.coords.longitude, ip, userAgent],
                        }).then(function (result) {
                            console.log('[TRecord Geo] Geolocalización guardada correctamente:', result);
                        }).catch(function (error) {
                            console.error('[TRecord Geo] Error ejecutando geolocalización:', error);
                            alert('Error de acceso, por favor contactarse con el área de sistemas.');
                        });
                    })
                    .catch(() => {
                        alert('No se pudo obtener la IP pública.');
                    });

            }, function (error) {
                // Manejo de errores estándar como en el original
                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        alert('Permiso de ubicación denegado. Actívelo e intente nuevamente.');
                        break;
                    case error.POSITION_UNAVAILABLE:
                        alert('La información de ubicación no está disponible.');
                        break;
                    case error.TIMEOUT:
                        alert('La solicitud para obtener la ubicación ha expirado.');
                        break;
                    default:
                        alert('Ocurrió un error desconocido al obtener la ubicación.');
                        break;
                }
            }, {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            });
        },

        _getTRecordId: function () {
            // 1) Preferir data-attributes del form (coincide con tu template)
            const fromForm = $('form#trecordvalidatedigits').data('document-id');
            if (fromForm) return parseInt(fromForm);

            // 2) Fallback: parsear desde la URL
            const url = new URL(window.location.href);
            const tail = parseInt(url.pathname.split('/').pop());
            return isNaN(tail) ? null : tail;
        },
    });
});
