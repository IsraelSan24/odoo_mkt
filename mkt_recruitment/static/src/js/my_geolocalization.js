odoo.define('mkt_recruitment.my_geolocalization', function( require ) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const session = require('web.session');
    var rpc = require('web.rpc');
    var latitude;
    var longitude;

    publicWidget.registry.MyGeolocalization = publicWidget.Widget.extend({
        selector: '.o_contract_validate_box',
        events: {
            'click #validate-btn-boxes': '_onClickGeo',
        },
        _onClickGeo: function ( event ) {
            console.log('------------------------------------------------se ejecuto------------------------------------------------');
            event.preventDefault();
            var self = this;
            const contract_url = new URL(window.location.href)
            if ( contract_url.pathname.includes('my/contracts')) {
                console.log('In contract');
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
                            .then(data =>{
                                const ip = data.ip;
                                console.log('Ip ' + ip);
                                rpc.query({
                                    model: 'hr.contract',
                                    method: 'geolocation',
                                    args: [[self._getContractId()], position.coords.latitude, position.coords.longitude, ip, userAgent],
                                }).then(function(result) {
                                    console.log('Successfully executed geolocation function:', result);
                                }).catch(function(error) {
                                    console.error('Error executing geolocation function:', error);
                                    alert('Error de acceso, por favor contactarse con el area de sistemas de Marketing Alterno.');
                                });
                            })
                    });
                }
                else {
                    alert('Error de geolocalisación, por favor contactarse con el area de sistemas de Marketing Alterno.');
                }
            }
            else {
                alert('Error de url, por favor contactarse con el area de sistemas de Marketing Alterno.');
            }
        },
        _getContractId: function() {
            const url = new URL(window.location.href);
            const contractId = url.pathname.split('/').pop();
            return parseInt(contractId);
        },
    });

});