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
            event.preventDefault();

            const url = new URL(window.location.href);
            const path = url.pathname;

            if (path.includes('my/contracts')) {
                this._geoContract();
            } else if (path.includes('portal/compliance/signall')) {
                this._geoCompliance();
            } else {
                alert('Error de url, por favor contactarse con el area de sistemas de Marketing Alterno.');
            }
        },

        _geoContract: function() {
            const self = this;
            console.log("Ejecutando geolocalización de contrato...");
            this._getGeo(function(latitude, longitude, ip, user_agent) {
                rpc.query({
                    model: 'hr.contract',
                    method: 'geolocation',
                    args: [[self._getContractId()], latitude, longitude, ip, user_agent],
                }).then(result => console.log("Geo contract OK:", result))
                    .catch(error => console.log("Geo contract error:", error));
            });
        },

        _geoCompliance: function() {
            const self = this;
            console.log("Ejecutando geolocalición de compliance...");
            this._getGeo(function(latitude, longitude, ip, user_agent) {
                const rec_id = self._getDocumentId();
                const contract_id = self._getContractId();
                console.log("REC ID", rec_id);
                console.log("CON ID", contract_id);
                if (rec_id) {
                    rpc.query({
                        model: 'recruitment.document',
                        method: 'geolocation',
                        args: [[rec_id], latitude, longitude, ip, user_agent],
                    });
                }
                if (contract_id) {
                    rpc.query({
                        model: 'hr.contract',
                        method: 'geolocation',
                        args: [[contract_id], latitude, longitude, ip, user_agent],
                    });
                }
            });
        },

        _getGeo: function(callback) {
            if (!navigator.geolocation) {
                alert("Error de geolocalización. Contacte al Área de Sistemas");
                return;
            }
            navigator.geolocation.getCurrentPosition(function(position){
                fetch('https://api.ipify.org?format=json')
                    .then(response => response.json())
                    .then(data => callback(position.coords.latitude, position.coords.longitude, data.ip, navigator.userAgent))
            });
        },
            
        _getDocumentId: function() {
            const documentId = $('form#contractaccept').data('rec-document-id');
            if (documentId) {
                return parseInt(documentId);
            }
            const url = new URL(window.location.href);
            return parseInt(url.pathname.split('/').pop());
            },
        
        _getContractId: function() {
            const contractId = $('form#contractaccept').data('document-id');
            if (contractId) {
                return parseInt(contractId);
            }
            const url = new URL(window.location.href);
            return parseInt(url.pathname.split('/').pop());
            },

        });
    });