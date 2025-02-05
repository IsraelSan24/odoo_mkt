document.addEventListener('DOMContentLoaded', function() {
    var emergencyContactInput = document.querySelector('input[name="emergency_contact"]');
    var emergencyPhoneInput = document.querySelector('input[name="emergency_phone"]');
    var zipcodeInput = document.querySelector('input[name="zipcode"]');
    var streetInput = document.querySelector('input[name="street"]');
    var referenceLocationInput = document.querySelector('input[name="reference_location"]');
    
    emergencyContactInput.addEventListener('input', function() {
        var hasLetter = /[a-zA-Z]/.test(this.value);
        this.value = this.value.replace(/[0-9]/g, '');


        if (!hasLetter) {
            this.value = this.value.replace(/\s/g, '');
        }
    });

    emergencyPhoneInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');

        if (this.value.length > 9) {
            this.value = this.value.slice(0, 9);
        }
    });

    zipcodeInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');

        if (this.value.length > 9) {
            this.value = this.value.slice(0, 9);
        }
    });

    streetInput.addEventListener('input', function() {
        var hasLetter = /[a-zA-Z]/.test(this.value);

        if (!hasLetter) {
            this.value = this.value.replace(/\s/g, '');
            this.value = this.value.replace(/[0-9]/g, '');
            console.log('accede')
        }
    });

    referenceLocationInput.addEventListener('input', function() {
        var hasLetter = /[a-zA-Z]/.test(this.value);

        if (!hasLetter) {
            this.value = this.value.replace(/\s/g, '');
            this.value = this.value.replace(/[0-9]/g, '');
        }
    });
});

function validateForm(event) {
    event.preventDefault();   
    $('#confirmationModal').modal('show');
  }