odoo.define('mkt_recruitment.document_validate_box', function( require ) {
    'use restrict';

    var publicWidget = require('web.public.widget');
    var rpc = require('web.rpc');

    publicWidget.registry.DocumentValidationBox = publicWidget.Widget.extend({
        selector: '.o_document_validate_box',
        events: {
            'input .digit-input': '_onInputValidateDocumentCode',
            // 'click #validate-btn-boxes': '_onClickValidateDocumentCode',
            'click #validate-document-btn-boxes': '_onClickValidateDocumentCode',
        },
        _onInputValidateDocumentCode: function ( event ) {
            var self = this;
            var current = event.target;
            if ( current.value.length >= 1) {
                var nextField = self.$(current).next('.digit-input');
                if ( nextField.length ) {
                    nextField.focus();
                }
                current.value = current.value.slice(0,1)
            }
            const p_number1 = $('#input1').val();
            const p_number2 = $('#input2').val();
            const p_number3 = $('#input3').val();
            const p_number4 = $('#input4').val();
            const enteredCode = p_number1 + p_number2 + p_number3 + p_number4;
            console.log('Código ' + enteredCode)
            if ( enteredCode.length === 4 ) {
                rpc.query({
                    model: 'recruitment.document',
                    method: 'action_validation_password',
                    args: [[self._getDocumentId()], enteredCode],
                }).then(function(result){
                    if ( result ) {
                        // $('#validate-btn-boxes').css('display','block');
                        $('#validate-document-btn-boxes').css('display','block');
                        // $('#validation-error-boxes').css('display','none');
                        $('#validation-document-error-boxes').css('display','none');
                    } else {
                        // $('#validate-btn-boxes').css('display','none');
                        $('#validate-document-btn-boxes').css('display','none');
                        // $('#validation-error-boxes').css('display','block');
                        $('#validation-document-error-boxes').css('display','block');
                    }
                }).catch(function(error) { 
                    console.log('Error ', error);
                });
            }
        },
        _onClickValidateDocumentCode: function(event) {
            event && event.preventDefault();
            var self = this;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    self.exitoUbicacion.bind(self),
                    self.errorUbicacion.bind(self), {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0,
                });
            } else {
                alert('Geolocation is not supported by your browser.');
            }
        },

        exitoUbicacion: function(position) { 
            console.log('Success location geolocation');
            // $('#validate-btn-boxes').attr('data-target', '#signdocument');
            $('#validate-document-btn-boxes').attr('data-target', '#signdocument');
            // $('#validate-btn-boxes').off('click').on('click', function () {
            $('#validate-document-btn-boxes').off('click').on('click', function () {
                $('#signdocument').modal('show');
            })
        },
        errorUbicacion: function(error) { 
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    // console.log('errorUbicacion permission denied document', $('#validate-btn-boxes'))
                    console.log('errorUbicacion permission denied document', $('#validate-document-btn-boxes'))
                    this.requestAccessLocation();
                    break;
                case error.POSITION_UNAVAILABLE:
                    alert('La información de ubicación no está disponible.');
                case error.TIMEOUT:
                    alert('La solicitud para obtener la ubicación del usuario ha expirado.');
                    break;
                case error.UNKNOWN_ERROR:
                    alert('Un error desconocido ha sucedido');
                    break;
            }
            // $('#validate-btn-boxes').removeAttr('data-target');
            $('#validate-document-btn-boxes').removeAttr('data-target');
        },

        requestAccessLocation: function() {
            if (confirm('Es necesario permitir el acceso a tu ubicación para continuar. ¿Deseas intentar de nuevo?')) {
                this._onClickValidateDocumentCode();
                // this.exitoUbicacion();
            } else {
                // $('#validate-btn-boxes').removeAttr('data-target');
                $('#validate-document-btn-boxes').removeAttr('data-target');
                // console.log('requestAccessLocation else ', $('#validate-btn-boxes'));
                console.log('requestAccessLocation else ', $('#validate-document-btn-boxes'));
            }
        },

        _getDocumentId: function() {
            const url = new URL(window.location.href);
            const documentId = url.pathname.split('/').pop();
            return parseInt(documentId);
        }
    })

})