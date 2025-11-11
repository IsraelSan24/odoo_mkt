document.addEventListener('DOMContentLoaded', function() {

    const annexes = document.querySelectorAll('input[id^="annex_"]');
    const signatureButton = document.querySelector('#signaturebutton');
    const complianceStep2Button = document.querySelector('#compliance_step2_button');
    const complianceProcess = document.querySelector('#compliance_process');
    const complianceProcessValue = complianceProcess?.value === 'True';
    
    function displaySignButton() {
        const allChecked = Array.from(annexes).every(cb => cb.checked);

        if (complianceProcessValue) {
            complianceStep2Button.disabled = !allChecked;
            complianceStep2Button.classList.toggle('inactive', !allChecked);
        } else {
            signatureButton.disabled = !allChecked;
            signatureButton.classList.toggle('inactive', !allChecked);
        }
    }
    annexes.forEach(cb => cb.addEventListener('change', displaySignButton))
    displaySignButton();
});
