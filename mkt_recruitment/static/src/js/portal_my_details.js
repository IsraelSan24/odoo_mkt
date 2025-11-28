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

    // zipcodeInput.addEventListener('input', function() {
    //     this.value = this.value.replace(/\D/g, '');

    //     if (this.value.length > 9) {
    //         this.value = this.value.slice(0, 9);
    //     }
    // });

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
    // 1. Prevenir el envío automático
    event.preventDefault();

    let isValid = true;
    let firstErrorField = null;

    // --- A. VALIDACIÓN ESTÁNDAR (Campos required) ---
    const requiredInputs = $('input[required="required"], select[required="required"], textarea[required="required"]');

    requiredInputs.each(function() {
        const $input = $(this);
        // Limpiar error previo
        $input.removeClass('is-invalid');

        if (!$input.val() || $input.val().trim() === '') {
            isValid = false;
            $input.addClass('is-invalid');
            if (firstErrorField === null) firstErrorField = $input;
        }
    });

    // --- B. VALIDACIÓN LÓGICA DE PENSIONES ---
    
    // Obtener referencias a los checkboxes
    const $afp = $('#private_pension_system');
    const $onp = $('#national_pension_system');
    
    // Sub-opciones de AFP
    const $afpFirstJob = $('#afp_first_job');
    const $afpFromOnp = $('#coming_from_onp');

    // 1. Limpiar estados previos de pensiones
    $afp.removeClass('is-invalid');
    $onp.removeClass('is-invalid');
    $afpFirstJob.removeClass('is-invalid');
    $afpFromOnp.removeClass('is-invalid');

    // 2. Validar que al menos uno (AFP o ONP) esté marcado
    // Nota: Solo validamos si los campos existen en el DOM (modo edición)
    if ($afp.length && $onp.length) {
        const isAfpChecked = $afp.is(':checked');
        const isOnpChecked = $onp.is(':checked');

        if (!isAfpChecked && !isOnpChecked) {
            isValid = false;
            // Marcamos ambos en rojo para indicar que falta seleccionar uno
            $afp.addClass('is-invalid');
            $onp.addClass('is-invalid');
            
            if (firstErrorField === null) firstErrorField = $afp;
        }

        // 3. Validar sub-opciones SI se seleccionó AFP
        if (isAfpChecked) {
            const isFirstJob = $afpFirstJob.is(':checked');
            const isFromOnp = $afpFromOnp.is(':checked');

            if (!isFirstJob && !isFromOnp) {
                isValid = false;
                // Marcamos las sub-opciones en rojo
                $afpFirstJob.addClass('is-invalid');
                $afpFromOnp.addClass('is-invalid');

                if (firstErrorField === null) firstErrorField = $afpFirstJob;
            }
        }
    }

    // --- C. DECISIÓN FINAL ---
    if (!isValid) {
        // Mostrar modal de advertencia
        $('#errorModal').modal('show');

        // Scroll al primer error
        if (firstErrorField) {
            $('html, body').animate({
                scrollTop: firstErrorField.offset().top - 150
            }, 500);
            firstErrorField.focus();
        }

    } else {
        // Todo correcto: Mostrar modal de confirmación
        $('#confirmationModal').modal('show');
    }
}

// Opcional: Quitar el rojo automáticamente cuando el usuario empiece a escribir/seleccionar
// document.addEventListener('input change', '[required="required"]', function() {
//     if (this.value) {
//         this.classList.remove('is-invalid');
//     }
// });
