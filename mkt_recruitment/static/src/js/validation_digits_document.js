odoo.define('mkt_recruitment.validation_digits_document', function( require ) {
    'use restrict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');
    publicWidget.registry.ValidationDigitsDocument = publicWidget.Widget.extend({
        selector: '.o_document_signature_t',
        events: {
            'click .o_valterm': '_onClickSignValidationDocument',
        },
        _onClickSignValidationDocument: function ( event ) {
            event.preventDefault();
            var self = this;
            const document_url = new URL(window.location.href)
            if ( document_url.pathname.includes('my/documents')) {
                rpc.query({
                    model: 'recruitment.document',
                    method: 'send_email_to_validate_document',
                    args: [[self._getDocumentId()]],
                }).then(function(result) {
                    console.log('Successfully! ', result);
                }).catch(function(error) {
                    console.error('Error ', error);
                });
            }
        },
        _getDocumentId: function() {
            const url = new URL(window.location.href);
            const documentId = url.pathname.split('/').pop();
            return parseInt(documentId);
        },
    });
});