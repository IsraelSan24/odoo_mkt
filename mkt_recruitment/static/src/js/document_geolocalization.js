odoo.define('mkt_recruitment.my_document_geolocalization', function( require ) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const session = require('web.session');
    var rpc = require('web.rpc');
    var latitude;
    var longitude;

    publicWidget.registry.MyDocumentGeolocalization = publicWidget.Widget.extend({
        selector: '.o_portal_signature_form',
        events: {
            'click .o_portal_sign_submit': '_onClickGeolocation',
        },
        _onClickGeolocation: function ( event ) {
            event.preventDefault();
            var self = this;
            const document_url = new URL(window.location.href)
            if ( document_url.pathname.includes('my/documents')) {
                console.log('In document');
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(function(position) {
                        const userAgent = navigator.userAgent;
                        const ctx = Object.assign({}, session.user_context, {
                            latitude: position.coords.latitude,
                            longitude: position.coords.longitude,
                            user_agent: userAgent,
                        });
                        latitude = position.coords.latitude;
                        longitude = position.coords.longitude;
                        fetch('https://api.ipify.org?format=json')
                            .then(response => response.json())
                            .then(data => {
                                const ip = data.ip;
                                console.log('Ip ' + ip);
                                rpc.query({
                                    model: 'recruitment.document',
                                    method: 'geolocation',
                                    args: [[self._getDocumentId()], position.coords.latitude,position.coords.longitude, ip, userAgent],
                                }).then(function(result) {
                                    console.log('Successfully executed geolocation function', result);
                                }).catch(function(error) {
                                    console.error('Error executing geolocation function', error);
                                });
                            })
                    });
                }
            }
        },
        _getDocumentId: function() {
            const url = new URL(window.location.href);
            const documentId = url.pathname.split('/').pop();
            return parseInt(documentId);
        },
    });

});