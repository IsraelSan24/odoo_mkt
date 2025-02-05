odoo.define('mkt_recruitment.validation_digits_contract', function( require ) {
    'use restrict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    publicWidget.registry.ValidationDigitsContract = publicWidget.Widget.extend({
        selector: '.o_contract_signature_t',
        events: {
            'click .o_valterm': '_onClickSignValidation',
        },
        _onClickSignValidation: function ( event ) {
            event.preventDefault();
            var self = this;
            const contract_url = new URL(window.location.href)
            if ( contract_url.pathname.includes('my/contracts') ) {
                rpc.query({
                    model: 'hr.contract',
                    method: 'send_email_to_validate_contract',
                    args: [[self._getContractId()]],
                }).then(function(result) {
                    console.log('Successfully! ', result);
                }).catch(function(error) {
                    console.error('Error ', error);
                });
            }
        },
        _getContractId: function() {
            const url = new URL(window.location.href);
            const contractId = url.pathname.split('/').pop();
            return parseInt(contractId);
        },
    });

});
