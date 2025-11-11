odoo.define('mkt_recruitment.contract_and_rec_documents_geolocation', function( require ) {
    'use strict';

    var publicWidget = require('web.public.widget');
    const session = require('web.session');
    var rpc = require('web.rpc');
    var latitude;
    var longitude;

    publicWidget.registry.MyGeolocalizationCompliance = publicWidget.Widget.extend({
        selector: '.o_contract_validate_box',
        events: {
            'click #validate-btn-boxes': '_onClickGeo',
        },
        _onClickGeo: function ( event ) {
            event.preventDefault();
            var self = this;
            const contract_url = new URL(window.location.href)
            console.log("URL CONTRACT:", contract_url)
            if ( contract_url.pathname.includes('portal/compliance/signall') ) {
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
                        ;
                        fetch('https://api.ipify.org?format=json')
                            .then(response => response.json())
                            .then(data =>{
                                const ip = data.ip;
                                console.log('Ip ' + ip);
                                
                                // 1. For recruitment document
                                const recruitment_documentID = self._getDocumentId();
                                console.log("RC IDL: ", recruitment_documentID)
                                if (recruitment_documentID) {
                                    rpc.query({
                                        model: 'recruitment.document',
                                        method: 'geolocation',
                                        args: [[recruitment_documentID], position.coords.latitude, position.coords.longitude, ip, userAgent],
                                    }).then(function(result) {
                                        console.log('CONTRACT: Successfully executed geolocation function:', result);
                                    }).catch(function(error) {
                                        console.error('CONTRACT: Error executing geolocation function:', error);
                                        alert('CONTRACT: Error de acceso, por favor contactarse con el area de sistemas de Marketing Alterno.');
                                    });
                                }

                                // 2. For contract
                                const contractID = self._getContractId()
                                console.log("Contract: ", contractID)
                                if (contractID) {
                                    rpc.query({
                                        model: 'hr.contract',
                                        method: 'geolocation',
                                        args: [[contractID], position.coords.latitude, position.coords.longitude, ip, userAgent],
                                    }).then(function(result) {
                                        console.log('RECRUITMENT DOCUMENT: Successfully executed geolocation function:', result);
                                    }).catch(function(error) {
                                        console.error('RECRUITMENT DOCUMENT: Error executing geolocation function:', error);
                                        alert('RECRUITMENT DOCUMENT: Error de acceso, por favor contactarse con el area de sistemas de Marketing Alterno.');
                                    });
                                }
                            })
                    });
                }
                else {
                    alert('Error de geolocalización, por favor contactarse con el area de sistemas de Marketing Alterno.');
                }
            }
            else {
                alert('Error de url, por favor contactarse con el area de sistemas de Marketing Alterno.');
            }
        },
        _getDocumentId: function() {
            const documentId = $('form#contractaccept').data('rec-document-id');
            if (documentId) {
                return parseInt(documentId);
            }},
        _getContractId: function() {
            const contractId = $('form#contractaccept').data('document-id');
            if (contractId) {
                return parseInt(contractId);
            }},
    });

});