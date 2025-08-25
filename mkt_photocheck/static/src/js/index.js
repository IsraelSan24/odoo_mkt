document.addEventListener("DOMContentLoaded", function () {
  let cropper = null;
  
  // Cache de elementos del DOM
  const brandSelect = document.getElementById('photocheck_brand_group_id');
  const citySelect = document.getElementById('city_id');
  const supervisorSelect = document.getElementById('photocheck_supervisor_id');
  
  // ============================================
  // INICIALIZACIÓN
  // ============================================
  function initializeSelectOptions() {
    // Inicializar estado de los selects
    if (citySelect) citySelect.disabled = true;
    if (supervisorSelect) supervisorSelect.disabled = true;
  }

  // ============================================
  // FILTROS EN CASCADA CON API: BRAND → CITY → SUPERVISOR
  // ============================================
  async function filterCitiesByBrand() {
    if (!brandSelect || !citySelect || !supervisorSelect) return;
    
    const selectedBrandId = brandSelect.value;
    console.log('Brand selected:', selectedBrandId);
    
    // Reset city y supervisor
    citySelect.selectedIndex = 0;
    supervisorSelect.selectedIndex = 0;
    supervisorSelect.disabled = true;
    
    // Limpiar opciones de city y supervisor
    clearSelectOptions(citySelect);
    clearSelectOptions(supervisorSelect);
    
    if (selectedBrandId && selectedBrandId !== '') {
      try {
        // Llamar a la API para obtener ciudades por marca
        const response = await fetch('/photocheck/get_cities_by_brand', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              brand_id: selectedBrandId
            }
          })
        });
        
        const data = await response.json();
        const cities = data.result || [];
        
        console.log('Available cities for brand:', cities);
        
        // Poblar select de ciudades
        cities.forEach(city => {
          const option = document.createElement('option');
          option.value = city.id;
          option.textContent = city.name;
          citySelect.appendChild(option);
        });
        
        citySelect.disabled = false;
        
      } catch (error) {
        console.error('Error fetching cities:', error);
        citySelect.disabled = true;
      }
    } else {
      citySelect.disabled = true;
    }
    
    updatePreviewData();
  }

  async function filterSupervisorsByBrandAndCity() {
    if (!brandSelect || !citySelect || !supervisorSelect) return;
    
    const selectedBrandId = brandSelect.value;
    const selectedCityId = citySelect.value;
    console.log('Filtering supervisors for brand:', selectedBrandId, 'and city:', selectedCityId);
    
    // Reset supervisor
    supervisorSelect.selectedIndex = 0;
    clearSelectOptions(supervisorSelect);
    
    if (selectedBrandId && selectedCityId && selectedBrandId !== '' && selectedCityId !== '') {
      try {
        // Llamar a la API para obtener supervisores por marca y ciudad
        const response = await fetch('/photocheck/get_supervisors_by_brand_and_city', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'call',
            params: {
              brand_id: selectedBrandId,
              city_id: selectedCityId
            }
          })
        });
        
        const data = await response.json();
        const supervisors = data.result || [];
        
        console.log('Available supervisors:', supervisors);
        
        // Poblar select de supervisores
        supervisors.forEach(supervisor => {
          const option = document.createElement('option');
          option.value = supervisor.id;
          option.textContent = supervisor.name;
          // Mantener los data attributes para compatibilidad
          option.setAttribute('data-brand_group_ids', JSON.stringify(supervisor.brand_group_ids));
          option.setAttribute('data-city_ids', JSON.stringify(supervisor.city_ids));
          supervisorSelect.appendChild(option);
        });
        
        supervisorSelect.disabled = false;
        
      } catch (error) {
        console.error('Error fetching supervisors:', error);
        supervisorSelect.disabled = true;
      }
    } else {
      supervisorSelect.disabled = true;
    }
    
    updatePreviewData();
  }

  function clearSelectOptions(selectElement) {
    const firstOption = selectElement.querySelector('option[value=""]');
    selectElement.innerHTML = '';
    if (firstOption) {
      selectElement.appendChild(firstOption.cloneNode(true));
    }
  }

  // ============================================
  // ACTUALIZACIÓN DE PREVIEW
  // ============================================
  function updatePreviewData() {
    const firstNameInput = document.getElementById('first_name');
    const lastNameInput = document.getElementById('last_name');
    const dniInput = document.getElementById('dni');
    const jobSelect = document.getElementById('job_id');
    
    const firstNamePreview = document.getElementById('first_names');
    const lastNamePreview = document.getElementById('last_names');
    const dniPreview = document.getElementById('dnis');
    const jobPreview = document.getElementById('jobs');
    const brandPreview = document.getElementById('brands');

    if (firstNameInput && firstNamePreview) {
      firstNamePreview.textContent = (firstNameInput.value || 'MARIA').toUpperCase();
    }

    if (lastNameInput && lastNamePreview) {
      lastNamePreview.textContent = (lastNameInput.value || 'CASTRO CASTRO').toUpperCase();
    }

    if (dniInput && dniPreview) {
      dniPreview.textContent = dniInput.value || '44775566';
    }

    if (jobSelect && jobPreview) {
      const selectedJob = jobSelect.options[jobSelect.selectedIndex];
      jobPreview.textContent = (selectedJob && selectedJob.value ? selectedJob.text : 'ANALYST').toUpperCase();
    }

    if (brandSelect && brandPreview) {
      const selectedBrand = brandSelect.options[brandSelect.selectedIndex];
      brandPreview.textContent = (selectedBrand && selectedBrand.value ? selectedBrand.text : 'MARKETING').toUpperCase();
    }
  }

  // ============================================
  // EVENT LISTENERS
  // ============================================
  function setupEventListeners() {
    // Filtros en cascada con API
    if (brandSelect) {
      brandSelect.addEventListener('change', filterCitiesByBrand);
    }
    
    if (citySelect) {
      citySelect.addEventListener('change', filterSupervisorsByBrandAndCity);
    }
    
    // Actualización de preview en tiempo real
    const previewInputs = ['first_name', 'last_name', 'dni', 'job_id'];
    previewInputs.forEach(inputId => {
      const element = document.getElementById(inputId);
      if (element) {
        element.addEventListener('input', updatePreviewData);
        element.addEventListener('change', updatePreviewData);
      }
    });
    
    if (brandSelect) {
      brandSelect.addEventListener('change', updatePreviewData);
    }
  }

  // ============================================
  // CROPPER FUNCTIONALITY (SIN CAMBIOS)
  // ============================================
  $("#photo").on("change", () => {
    let styleSheets = document.styleSheets;
    console.log(styleSheets);

    console.log('Here!');
    let styleSheet = styleSheets[1];
    console.log(styleSheet);

    if (styleSheet instanceof CSSStyleSheet) {
      let cssRules = styleSheet.cssRules || styleSheet.rules;
      console.log('First if');

      for (let j = 0; j < cssRules.length; j++) {
        console.log('First if');
        let cssRule = cssRules[j];

        if (cssRule instanceof CSSMediaRule) {
          console.log('Second if');
          let mediaCssRules = cssRule.cssRules || cssRule.rules;

          for (let k = 0; k < mediaCssRules.length; k++) {
            console.log('last for');
            let mediaCssRule = mediaCssRules[k];

            console.log('last if');
            mediaCssRule.style.transform = '';
            mediaCssRule.style.removeProperty('transform');
          }
        }
      }
    }

    let image = document.getElementById("img-cropper");
    let input = document.getElementById("photo");
    let archivos = input.files;
    let extensiones = input.value.substring(
      input.value.lastIndexOf("."),
      input.value.length
    );
    console.log("input value" + input.value);
    console.log("archivo" + archivos);

    if (!archivos || !archivos.length) {
      image.src = "";
      input.value = "";
    } else if (input.getAttribute("accept").split(",").indexOf(extensiones) < 0) {
      alert("Debes seleccionar una imagen");
      input.value = "";
    } else {
      let imageUrl = URL.createObjectURL(archivos[0]);
      image.src = imageUrl;
      console.log("imageUrl" + imageUrl);
      cropper = new Cropper(image, {
        aspectRatio: 1,
        preview: ".img-sample",
        zoomable: false,
        viewMode: 1,
        responsive: false,
        dragMode: "none",
        ready() {
          document.querySelector(".cropper-container").style.width = "100%";
          document.querySelector(".cropper-container").style.heigth = "100%";
        },
      });
      console.log("cropepr" + cropper);
      $(".modal").addClass("active");
      $(".modal-content").addClass("active");
      $(".modal").removeClass("remove");
      $(".modal-content").removeClass("remove");
    }
  });

  $("#close").on("click", () => {
    let image = document.getElementById("img-cropper");
    let input = document.getElementById("photo");
    image.src = "";
    input.value = "";
    if (cropper) {
      cropper.destroy();
      cropper = null;
    }
    $(".modal").addClass("remove");
    $(".modal-content").addClass("remove");
    $(".modal").removeClass("active");
    $(".modal-content").removeClass("active");
  });

  $("#cut").on("click", () => {
    let crop_image = document.getElementById("crop-image");
    let canva = cropper.getCroppedCanvas();
    let image = document.getElementById("img-cropper");
    let input = document.getElementById("photo");
    canva.toBlob(function (blob) {
      var url_cut = URL.createObjectURL(blob);
      crop_image.src = url_cut;

      // 🔥 NUEVO: actualizar preview del photocheck
      const photoPreviewEl = document.getElementById("photos");
      if (photoPreviewEl) {
        photoPreviewEl.src = url_cut;
      }

      // Mantener el archivo recortado en el input file
      let dataTransfer = new DataTransfer();
      let file = new File([blob], "filename.jpg", { type: "image/jpeg" });
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;
    });
    image.src = "";
    input.value = "";
    if (cropper) {
      cropper.destroy();
      cropper = null;
    }
    $(".modal").addClass("remove");
    $(".modal-content").addClass("remove");
    $(".modal").removeClass("active");
    $(".modal-content").removeClass("active");
  });

  // Cropper controls
  let rotate = document.querySelectorAll(".modal-footer .rotate button");
  let flip = document.querySelectorAll(".modal-footer .flip button");
  var flipX = -1;
  var flipY = -1;
  
  if (flip[0]) {
    flip[0].onclick = () => {
      if (cropper) {
        cropper.scale(flipX, 1);
        flipX = -flipX;
      }
    };
  }

  if (flip[1]) {
    flip[1].onclick = () => {
      if (cropper) {
        cropper.scale(1, flipY);
        flipY = -flipY;
      }
    };
  }

  if (rotate[0]) {
    rotate[0].onclick = () => {
      if (cropper) cropper.rotate(45);
    };
  }

  if (rotate[1]) {
    rotate[1].onclick = () => {
      if (cropper) cropper.rotate(-45);
    };
  }

  // ============================================
  // FORM SUBMISSION FUNCTIONALITY
  // ============================================
  var submitButton = document.getElementById('submit-button');
  var confirmButton = document.getElementById('confirm-button');
  var form = document.getElementById('photocheck_form');
  var confirmationModal = document.getElementById('confirmationModal');
  var closeButtons = document.querySelectorAll('.modal-close3');
  var loadingOverlay = document.getElementById('loadingOverlay');
  var photoInput = document.getElementById('photo');

  function showAlert(message) {
    const alertContainer = document.createElement("div");
    alertContainer.classList.add("alert");
    alertContainer.innerHTML = `
        <div class="alert-content">
            <span class="alert-message">${message}</span>
            <button class="alert-close">&times;</button>
        </div>
    `;

    document.body.appendChild(alertContainer);

    const closeBtn = alertContainer.querySelector(".alert-close");
    closeBtn.addEventListener("click", () => {
      alertContainer.classList.add("alert-out");
      setTimeout(() => {
        if (document.body.contains(alertContainer)) {
          document.body.removeChild(alertContainer);
        }
      }, 300);
    });

    setTimeout(() => {
      alertContainer.classList.add("alert-in");
    }, 100);
  }

  function validarImagenAdjuntada() {
    if (!photoInput || photoInput.files.length === 0) {
      showAlert('Por favor, suba una imagen.');
      return false;
    }
    return true;
  }

  if (submitButton) {
    submitButton.addEventListener('click', function(event) {
      event.preventDefault();
      if (form && form.checkValidity() && validarImagenAdjuntada()) {
        if (confirmationModal) {
          confirmationModal.style.display = 'flex';
        }
      } else {
        if (form) form.reportValidity();
      }
    });
  }

  if (confirmButton) {
    confirmButton.addEventListener('click', function() {
      confirmButton.disabled = true;
      if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
      }
      if (form) {
        form.submit();
      }
    });
  }

  if (closeButtons) {
    closeButtons.forEach(function(button) {
      button.addEventListener('click', function() {
        if (confirmationModal) {
          confirmationModal.style.display = 'none';
        }
        if (confirmButton) {
          confirmButton.disabled = false;
        }
      });
    });
  }

  // ============================================
  // INICIALIZACIÓN PRINCIPAL
  // ============================================
  initializeSelectOptions();
  setupEventListeners();
  updatePreviewData();
});