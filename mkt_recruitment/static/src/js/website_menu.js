(function() {
  'use strict';
  window.addEventListener('load', function() {
    var forms = document.getElementsByClassName('needs-validation');
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add('was-validated');
      }, false);
    });
  }, false);
})();

document.addEventListener('DOMContentLoaded', function() {
  var familyMembersField = document.getElementById('familyMembers');
  var familyMembersFields = document.getElementById('familyMembersFields');

  familyMembersField.addEventListener('input', function() {
    var numFamilyMembers = parseInt(this.value);
    familyMembersFields.innerHTML = '';

    for (var i = 0; i < numFamilyMembers; i++) {
      var familyMemberField = document.createElement('div');
      familyMemberField.classList.add('form-row', 'mb-3');
      familyMemberField.innerHTML = `
        
          <div class="col-md-12">
              <h3 class="font-weight-bold text-info">Familiar${i + 1}</h3>
          </div>
          
          <div class="form-group col">
              <label for="familiar_dni${i + 1}">DNI</label>
              <input type="text" name="familiar_dni${i + 1}" id="familiar_dni${i + 1}" class="form-control" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese su DNI.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_full_name${i + 1}">Name</label>
              <input type="text" name="familiar_full_name${i + 1}" id="familiar_full_name${i + 1}" class="form-control" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese su nombre.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_birthday${i + 1}">F. Nac</label>
              <input type="date" name="familiar_birthday${i + 1}" class="form-control" id="familiar_birthday${i + 1}" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese su fecha de nacimiento.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_relationship${i + 1}">Parentesco</label>
              <select class="form-control" name="familiar_relationship${i + 1}" id="familiar_relationship${i + 1}" required="True">
                  <option value="">Seleccione una opción</option>
                  <option value="Esposo/a">Esposo(a)</option>
                  <option value="Conviviente">Conviviente</option>
                  <option value="Hijo">Hijo</option>
                  <option value="Hija">Hija</option>
              </select>
              <div class="invalid-feedback">
                Por favor, seleccione un parentesco.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_gender${i + 1}">Género</label>
              <select class="form-control" name="familiar_gender${i + 1}" id="familiar_gender${i + 1}" required="True">
                  <option value="">Seleccione una opción</option>
                  <option value="male">Masculino</option>
                  <option value="female">Femenino</option>
              </select>
              <div class="invalid-feedback">
                Por favor, seleccione un género.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_address${i + 1}">Dirección</label>
              <input type="text" name="familiar_address${i + 1}" class="form-control" id="familiar_address${i + 1}" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese una dirección.
              </div>
          </div>
          <div class="form-group col">
              <label for="is_beneficiary${i + 1}">Beneficiario</label>
              <input type="checkbox" name="is_beneficiary${i + 1}" class="form-control" id="is_beneficiary${i + 1}" checked/>
          </div>
          
        
      `;
      familyMembersFields.appendChild(familyMemberField);
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  var otrosMembersField = document.getElementById('otrosMembers');
  var otrosMembersFields = document.getElementById('otrosMembersFields');

  otrosMembersField.addEventListener('input', function() {
    var numFamilyMembers = parseInt(this.value);
    otrosMembersFields.innerHTML = '';

    for (var j = 0; j < numFamilyMembers; j++) {
      var otrosMembersField = document.createElement('div');
      otrosMembersField.classList.add('form-row', 'mb-3');
      otrosMembersField.innerHTML = `
        
          <div class="col-md-12">
              <h3 class="font-weight-bold text-info">Familiar${j + 7}</h3>
          </div>
          
          <div class="form-group col">
              <label for="familiar_dni${j + 7}">DNI</label>
              <input type="text" name="familiar_dni${j + 7}" id="familiar_dni${j + 7}" class="form-control" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese su DNI.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_full_name${j + 7}" >Nombre</label>
              <input type="text" name="familiar_full_name${j + 7}" id="familiar_full_name${j + 7}" class="form-control" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese su nombre.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_birthday${j + 7}">F. Nac</label>
              <input type="date" name="familiar_birthday${j + 7}" class="form-control" id="familiar_birthday${j + 7}" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese su fecha de nacimiento.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_relationship${j + 7}">Parentesco</label>
              <select class="form-control" name="familiar_relationship${j + 7}" id="familiar_relationship${j + 7}" required="True">
                  <option value="">Seleccione una opción</option>
                  <option value="Madre">Madre</option>
                  <option value="Padre">Padre</option>
                  <option value="Hermano">Hermano</option>
                  <option value="Hermana">Hermana</option>
              </select>
              <div class="invalid-feedback">
                Por favor, seleccione un parentesco.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_gender${j + 7}">Género</label>
              <select class="form-control" name="familiar_gender${j + 7}" id="familiar_gender${j + 7}" required="True">
                  <option value="">Seleccione una opción</option>
                  <option value="male">Masculino</option>
                  <option value="female">Femenino</option>
              </select>
              <div class="invalid-feedback">
                Por favor, seleccione un género.
              </div>
          </div>
          <div class="form-group col">
              <label for="familiar_address${j + 7}">Dirección</label>
              <input type="text" name="familiar_address${j + 7}" class="form-control" id="familiar_address${j + 7}" required="True"/>
              <div class="invalid-feedback">
                Por favor, ingrese una dirección.
              </div>
          </div>
          <div class="form-group col">
              <label for="is_beneficiary${j + 7}">Beneficiario</label>
              <input type="checkbox" name="is_beneficiary${j + 7}" class="form-control" id="is_beneficiary${j + 7}" checked/>
          </div>
          
        
      `;
      otrosMembersFields.appendChild(otrosMembersField);
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
var privatePensionCheckbox = document.getElementById('private_pension_system');
var pensionOptionsContainer = document.getElementById('pension_options');
var afpFirstJob = document.getElementById('afp_first_job');
var comingFromOnp = document.getElementById('coming_from_onp');
var radioOptions = document.querySelectorAll('.radio-option');

privatePensionCheckbox.addEventListener('change', function() {
  console.log('ingresamos')
if (this.checked) {
  pensionOptionsContainer.style.display = 'block';
} else {
  pensionOptionsContainer.style.display = 'none';
  radioOptions.forEach(radio => radio.checked = false);
  afpFirstJob.checked = false;
  comingFromOnp.checked = false;
}
});

radioOptions.forEach(radio => {
radio.addEventListener('change', function() {
  radioOptions.forEach(otherRadio => {
    if (otherRadio !== this) {
      otherRadio.checked = false;
    }
  });
});
});

});

function validateInputfamily() {
  var input = document.getElementById('familyMembers');
  var value = parseInt(input.value);
  if (value < 0 || value > 6) {
      alert('Only numbers 1, 2, 3, 4, 5 and 6 are allowed.');
      input.value = '';
  }
}

function validateInput() {
  var input = document.getElementById('otrosMembers');
  var value = parseInt(input.value);
  if (value < 0 || value > 4) {
      alert('Sólo se permiten los números 1, 2, 3 y 4.');
      input.value = '';
  }
}


function toggleCheckbox(checkbox) {
  var afpFirstJob = document.getElementById('afp_first_job');
  var comingFromOnp = document.getElementById('coming_from_onp');
  var otherCheckbox = document.getElementById(checkbox.id === 'private_pension_system' ? 'national_pension_system' : 'private_pension_system');
  if (checkbox.checked) {
      otherCheckbox.checked = false;
      if (checkbox.id === 'private_pension_system') {
          document.getElementById('pension_options').style.display = 'block';
      } else {
          document.getElementById('pension_options').style.display = 'none';
          afpFirstJob.checked = false;
          comingFromOnp.checked = false;
      }
  } else {
      document.getElementById('pension_options').style.display = 'none';
      afpFirstJob.checked = false;
      comingFromOnp.checked = false;
  }
}

async function apiperu_dni(dni) {
  const url = "https://apiperu.dev/api/dni";
  const token =
    "4b56a00274d444b40cc38d47e69c72d6f5a362dddbee20470b9f1dd8d6a65479";
  const headers = {
    Accept: "application/json",
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
  try {
    const params = { dni: String(dni) };
    const params_json = JSON.stringify(params);
    const response = await fetch(url, {
      method: "POST",
      headers: headers,
      body: params_json,
    });
    if (response.ok) {
      const data = await response.json();
      const access_data = data.data;
      return [
        access_data.nombre_completo,
      ];
    } else {
      console.error(`Error ${response.status}`);
      console.error(await response.text());
    }
  } catch (error) {
    console.error(`Error ${error}`);
  }
}

async function consultarDNI() {
  const dni = document.getElementById("dni").value;
  if (dni) {
    try {
      const [nombre_completo] = await apiperu_dni(dni);
      document.getElementById("name").value = nombre_completo;
      console.log(document.getElementById("name").value);
      console.log(name);
      console.log(nombre_completo);
    } catch (error) {
      console.error("Error al consultar el DNI:", error);
    }
  } else {
    console.error("Ingrese un número de DNI");
  }
}


function validateForm(event) {
  event.preventDefault();
  const form = document.getElementById('employeeForm');
  const fields = form.querySelectorAll('input, select, textarea');
  let allFieldsValid = true;
  let requiredFieldsValid = true;

  fields.forEach(field => {
      if (!field.checkValidity()) {
          allFieldsValid = false;
          if (field.hasAttribute('required')) {
              requiredFieldsValid = false;
          }
          field.classList.add('is-invalid');
      } else {
          field.classList.remove('is-invalid');
      }
  });

  if (requiredFieldsValid) {
   
      populateModal();
      $('#confirmationModal').modal('show');
  }
  return allFieldsValid;
}


document.addEventListener('DOMContentLoaded', function() {
  var privatePensionSystemField = document.getElementById('private_pension_system');
  if (privatePensionSystemField) {
    privatePensionSystemField.addEventListener('change', function() {
      const pensionOptions = document.getElementById('pension_options');
      
      if (privatePensionSystemField.type === 'checkbox') {
        pensionOptions.style.display = this.checked ? 'block' : 'none';
      } else {
        pensionOptions.style.display = this.value === 'yes' ? 'block' : 'none';
      }
      
      if (!this.checked && this.type === 'checkbox') {
        document.getElementById('afp_first_job').checked = false;
        document.getElementById('coming_from_onp').checked = false;
      }
    });
  }
});


function populateModal() {
  document.getElementById('modal-dni').innerText = document.getElementById('dni').value;
  document.getElementById('modal-name').innerText = document.getElementById('name').value;
  document.getElementById('modal-children').innerText = document.getElementById('children').value;
  document.getElementById('modal-gender').innerText = getSelectedOptionTextById('gender');
  document.getElementById('modal-birthday').innerText = document.getElementById('birthday').value;
  document.getElementById('modal-marital').innerText = getSelectedOptionTextById('marital');
  document.getElementById('modal-email').innerText = document.getElementById('email').value;
  document.getElementById('modal-phone').innerText = document.getElementById('phone').value;
  document.getElementById('modal-emergency_contact').innerText = document.getElementById('emergency_contact').value;
  document.getElementById('modal-emergency_phone').innerText = document.getElementById('emergency_phone').value;
  document.getElementById('modal-nationality').innerText = getSelectedOptionTextById('nationality_id');
  document.getElementById('modal-identification').innerText = getSelectedOptionTextById('identification_type_id');
  document.getElementById('modal-country').innerText = getSelectedOptionTextById('country_id');
  document.getElementById('modal-province').innerText = getSelectedOptionTextById('state_id');
  document.getElementById('modal-city').innerText = getSelectedOptionTextById('city_id');
  document.getElementById('modal-district').innerText = getSelectedOptionTextById('district_id');
  document.getElementById('modal-zip').innerText = document.getElementById('zip').value;
  document.getElementById('modal-street').innerText = document.getElementById('street').value;
  document.getElementById('modal-reference_location').innerText = document.getElementById('reference_location').value;
  document.getElementById('modal-education_level').innerText = getSelectedOptionTextBySelector('select[name="education_level"]');
  document.getElementById('modal-education_start_date').innerText = document.getElementById('education_start_date').value;
  document.getElementById('modal-education_end_date').innerText = document.getElementById('education_end_date').value;
  document.getElementById('modal-institution').innerText = document.getElementById('institution').value;
  document.getElementById('modal-profession').innerText = document.getElementById('profession').value;
  document.getElementById('modal-familyMembers').innerText = document.getElementById('familyMembers').value;
  document.getElementById('modal-otrosMembers').innerText = document.getElementById('otrosMembers').value;
  document.getElementById('modal-private_pension_system').innerText = document.getElementById('private_pension_system').checked ? 'Si' : 'No';
  document.getElementById('modal-national_pension_system').innerText = document.getElementById('national_pension_system').checked ? 'Si' : 'No';

  const privatePensionSystem = document.getElementById('private_pension_system').checked;
  const modalPrivatePensionSystem = document.getElementById('modal-private_pension_system');
  const modalPensionOption = document.getElementById('modal-pension-option');
  const modalPensOpti = document.getElementById('pens_opti');

  if (modalPrivatePensionSystem) {
      modalPrivatePensionSystem.innerText = privatePensionSystem ? 'Si' : 'No';
  }

  if (privatePensionSystem) {
      modalPensOpti.style.display = 'block';
  } else {
      modalPensOpti.style.display = 'none';
  }

  let pensionOptionText = 'No seleccionado';
  if (privatePensionSystem) {
      if (document.getElementById('afp_first_job').checked) {
          pensionOptionText = '(AFP) Primer empleo';
      } else if (document.getElementById('coming_from_onp').checked) {
          pensionOptionText = 'Procedente de la ONP';
      }
  }

  if (modalPensionOption) {
      modalPensionOption.innerText = pensionOptionText;
  }

  const familyMembersCount = parseInt(document.getElementById('familyMembers').value, 10);
  const familyMembersModal = document.getElementById('familyMembersModal');
  familyMembersModal.innerHTML = '';
  if (familyMembersCount > 0) {
      let tableHTML = `
          <table class="table table-striped">
              <thead>
                  <tr>
                      <th>DNI</th>
                      <th>Nombre</th>
                      <th>F. Nac</th>
                      <th>Parentesco</th>
                      <th>Género</th>
                      <th>Dirección</th>
                  </tr>
              </thead>
              <tbody>`;
      for (let i = 1; i <= familyMembersCount; i++) {
          tableHTML += `
              <tr>
                  <td>${document.getElementById(`familiar_dni${i}`).value}</td>
                  <td>${document.getElementById(`familiar_full_name${i}`).value}</td>
                  <td>${document.getElementById(`familiar_birthday${i}`).value}</td>
                  <td>${getSelectedOptionTextById(`familiar_relationship${i}`)}</td>
                  <td>${getSelectedOptionTextById(`familiar_gender${i}`)}</td>
                  <td>${document.getElementById(`familiar_address${i}`).value}</td>
              </tr>`;
      }
      tableHTML += `
              </tbody>
          </table>`;
      familyMembersModal.innerHTML = tableHTML;
  }

  const otrosMembersCount = parseInt(document.getElementById('otrosMembers').value, 10);
  const otrosMembersModal = document.getElementById('otrosMembersModal');
  otrosMembersModal.innerHTML = '';
  if (otrosMembersCount > 0) {
      let tableHTML = `
          <table class="table table-striped">
              <thead>
                  <tr>
                      <th>DNI</th>
                      <th>Nombre</th>
                      <th>F. Nac</th>
                      <th>Parentesco</th>
                      <th>Género</th>
                      <th>Dirección</th>
                  </tr>
              </thead>
              <tbody>`;
      const inicioOtros = 7;  // Asegura que otros beneficiarios empiecen en 7
      for (let j = inicioOtros; j < inicioOtros + otrosMembersCount; j++) {
          tableHTML += `
              <tr>
                  <td>${document.getElementById(`familiar_dni${j}`).value}</td>
                  <td>${document.getElementById(`familiar_full_name${j}`).value}</td>
                  <td>${document.getElementById(`familiar_birthday${j}`).value}</td>
                  <td>${getSelectedOptionTextById(`familiar_relationship${j}`)}</td>
                  <td>${getSelectedOptionTextById(`familiar_gender${j}`)}</td>
                  <td>${document.getElementById(`familiar_address${j}`).value}</td>
              </tr>`;
      }
      tableHTML += `
              </tbody>
          </table>`;
      otrosMembersModal.innerHTML = tableHTML;
  }
}

function getSelectedOptionTextBySelector(selector) {
  var selectElement = document.querySelector(selector);
  if (selectElement && selectElement.selectedIndex !== -1) {
      var selectedOption = selectElement.options[selectElement.selectedIndex];
      return selectedOption ? selectedOption.text : '';
  }
  return '';
}

function getSelectedOptionTextById(id) {
  const selectElement = document.getElementById(id);
  if (selectElement && selectElement.selectedIndex >= 0) {
      return selectElement.options[selectElement.selectedIndex].text;
  }
  return '';
}

document.addEventListener('DOMContentLoaded', function() {
  var employeeForm = document.getElementById('employeeForm');
  if (employeeForm) {
    employeeForm.addEventListener('submit', validateForm);
  } else {
    console.error('El formulario con ID "employeeForm" no se encontró en el DOM.');
  }
});


function submitForm() {
  const cancelButton = document.getElementById('cancelButton');
  const confirmButton = document.getElementById('confirmButton');
  
  cancelButton.disabled = true;
  confirmButton.disabled = true;
  confirmButton.innerText = "Processing...";

  document.getElementById('employeeForm').submit();
}

function volverAlFormulario() {
  window.location.href = '/applicantpartner';
}

document.addEventListener('DOMContentLoaded', function() {
  var identificationTypeSelect = document.getElementById('identification_type_id');
  var dniInput = document.getElementById('dni');

  identificationTypeSelect.addEventListener('change', function() {
      var selectedOption = identificationTypeSelect.options[identificationTypeSelect.selectedIndex].text;

      if (selectedOption === 'DNI') {
          dniInput.maxLength = 8;
          dniInput.pattern = '\\d{8}';
          dniInput.title = 'El DNI debe tener exactamente 8 dígitos.';
      } else {
          dniInput.maxLength = 9;
          dniInput.pattern = '\\d{1,9}';
          dniInput.title = 'La identificación debe tener un máximo de 9 dígitos.';
      }

      if (dniInput.value.length > dniInput.maxLength) {
          dniInput.value = '';
      }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.custom-file-input').forEach(function(input) {
      input.addEventListener('change', function() {
          let fileName = this.files[0].name;
          let label = this.nextElementSibling;
          label.classList.add("selected");
          label.innerText = fileName;
      });
  });
});

document.addEventListener('DOMContentLoaded', function () {
  var fileInputs = document.querySelectorAll('.custom-file-input');

  fileInputs.forEach(function(fileInput) {
      var fileLabel = fileInput.nextElementSibling;

      fileInput.addEventListener('change', function () {
          if (fileInput.files.length > 0) {
              fileLabel.classList.remove('icon-upload');
              fileLabel.classList.add('icon-check');
          } else {
              fileLabel.classList.remove('icon-check');
              fileLabel.classList.add('icon-upload');
          }
      });

      // Establecer la clase inicial
      fileLabel.classList.add('icon-upload');
  });
});

document.addEventListener('DOMContentLoaded', function () {
  var searchInput = document.getElementById('jobSearchInput');
  var jobsContainer = document.getElementById('jobs_grid');
  var jobs = jobsContainer.querySelectorAll('.card');

  searchInput.addEventListener('keyup', function () {
      var query = searchInput.value.toLowerCase();

      jobs.forEach(function (job) {
          var jobName = job.querySelector('h3').innerText.toLowerCase();
          var referenceName = job.querySelector('.text-muted') ? job.querySelector('.text-muted').innerText.toLowerCase() : '';

          if (jobName.includes(query) || referenceName.includes(query)) {
              job.style.display = '';
          } else {
              job.style.display = 'none';
          }
      });
  });
});