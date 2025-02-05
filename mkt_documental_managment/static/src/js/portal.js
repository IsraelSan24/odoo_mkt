

  document.addEventListener('DOMContentLoaded', function () {
    var petitionerInput = document.getElementById('user_id');
    var vatInput = document.getElementById('user_vat');
    var jobInput = document.getElementById('job_id');
    var locationInput = document.getElementById('location');
    var stateInput = document.getElementById('state_id');
    var cityInput = document.getElementById('city_id');
    var districtInput = document.getElementById('district_id');
    var conceptInput = document.getElementById('concept');
    var activityInput = document.getElementById('activity');
    var amountInput = document.getElementById('amount');
    
    var displayPetitioner = document.getElementById('displayPetitioner');
    var displayVat = document.getElementById('displayVat');
    var displayJob = document.getElementById('displayJob');
    var displayLocation = document.getElementById('displayLocation');
    var displayState = document.getElementById('displayState');
    var displayCity = document.getElementById('displayCity');
    var displayDistrict = document.getElementById('displayDistrict');
    var displayConcept = document.getElementById('displayConcept');
    var displayActivity = document.getElementById('displayActivity');
    var displayAmount = document.getElementById('displayAmount');

    function updateInputDisplay(inputElement, displayElement) {
        displayElement.textContent = inputElement.value || '-';
    }
    function updateSelectDisplay(selectElement, displayElement) {
        var selectedIndex = selectElement.selectedIndex;
        var selectedText = selectElement.options[selectedIndex].text || selectElement.options[0].text;
        displayElement.textContent = selectedText;
    }

    petitionerInput.addEventListener('input', function() {
        updateSelectDisplay(petitionerInput,displayPetitioner);
    });
    vatInput.addEventListener('input', function() {
        updateInputDisplay(vatInput, displayVat);
    });
    jobInput.addEventListener('input', function() {
        updateSelectDisplay(jobInput,displayJob);
    });
    locationInput.addEventListener('input', function() {
        displayLocation.textContent = locationInput.value || '-';
    });
    stateInput.addEventListener('change', function() {
        var selectedState = stateInput.options[stateInput.selectedIndex].text;
        displayState.textContent = selectedState || '-';
    });
    cityInput.addEventListener('change', function() {
        var selectedCity = cityInput.options[cityInput.selectedIndex].text;
        displayCity.textContent = selectedCity || '-';
    });
    districtInput.addEventListener('change', function() {
        var selectedDistrict = districtInput.options[districtInput.selectedIndex].text;
        displayDistrict.textContent = selectedDistrict || '-';
    });
    conceptInput.addEventListener('input', function() {
        displayConcept.textContent = conceptInput.value || '-';
    });
    activityInput.addEventListener('input', function() {
        displayActivity.textContent = activityInput.value || '-';
    });
    amountInput.addEventListener('input', function() {
        displayAmount.textContent = amountInput.value || '-';
    });
    
    updateSelectDisplay(petitionerInput, displayPetitioner);
    updateSelectDisplay(jobInput, displayJob);

    updateInputDisplay(vatInput, displayVat);
});

document.addEventListener('DOMContentLoaded', function () {
    var dateInput = document.getElementById('date');
    var displayDate = document.getElementById('displayDate');

    dateInput.addEventListener('input', function() {
        if (dateInput.value) {
            var date = new Date(dateInput.value + 'T00:00:00'); 

            var options = { year: 'numeric', month: 'long', day: 'numeric' };
            var formattedDate = date.toLocaleDateString('es-ES', options);

            var day = ("0" + date.getDate()).slice(-2);
            var month = formattedDate.split(' de ')[1].charAt(0).toUpperCase() + formattedDate.split(' de ')[1].slice(1);
            var year = date.getFullYear();

            displayDate.textContent = `Lima, ${day} de ${month} del ${year}`;
        } else {
            displayDate.textContent = 'Lima, __________';
        }
    });
});


document.addEventListener('DOMContentLoaded', function () {
    var form = document.getElementById('affidavitForm');
    var submitButton = form.querySelector('button[type="submit"]');
    var loadingOverlay = document.getElementById('loadingOverlay');

    form.addEventListener('submit', function(event) {
        loadingOverlay.style.display = 'flex';
        submitButton.disabled = true;

        event.preventDefault();
        var formData = new FormData(form);

        fetch(form.action, {
            method: form.method,
            body: formData,
        })         
        .then(response => response.text())
        .then(html => {
            document.body.innerHTML = html;
            loadingOverlay.style.display = 'none';
            submitButton.disabled = false;

            $('#downloadModal').modal('show');
        })
    });
});