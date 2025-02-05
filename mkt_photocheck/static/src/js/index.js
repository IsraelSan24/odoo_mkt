document.addEventListener("DOMContentLoaded", function () {
  let cropper = null;

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

    // INFO
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
    cropper.destroy();
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
      let dataTransfer = new DataTransfer();
      let file = new File([blob], "filename.jpg", { type: "image/jpeg" });
      dataTransfer.items.add(file);
      input.files = dataTransfer.files;
    });
    image.src = "";
    input.value = "";
    cropper.destroy();
    $(".modal").addClass("remove");
    $(".modal-content").addClass("remove");
    $(".modal").removeClass("active");
    $(".modal-content").removeClass("active");
  });
  let rotate = document.querySelectorAll(".modal-footer .rotate button");
  let flip = document.querySelectorAll(".modal-footer .flip button");
  var flipX = -1;
  var flipY = -1;
  flip[0].onclick = () => {
    cropper.scale(flipX, 1);
    flipX = -flipX;
  };
  flip[1].onclick = () => {
    cropper.scale(1, flipY);
    flipY = -flipY;
  };
  rotate[0].onclick = () => cropper.rotate(45);
  rotate[1].onclick = () => cropper.rotate(-45);


  function validarImagenAdjuntada() {
    const input = document.getElementById("photo");
    if (!input.files || !input.files.length) {
      showAlert("Por favor, adjunte una imagen.");
      return false;
    }
    return true;
  }
});

document.addEventListener('DOMContentLoaded', function() {
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
              document.body.removeChild(alertContainer);
          }, 300);
      });

      setTimeout(() => {
          alertContainer.classList.add("alert-in");
      }, 100);
  }

  function validarImagenAdjuntada() {
      if (photoInput.files.length === 0) {
          showAlert('Por favor, suba una imagen.');
          return false;
      }
      return true;
  }

  submitButton.addEventListener('click', function(event) {
      event.preventDefault();
      if (form.checkValidity() && validarImagenAdjuntada()) {
          confirmationModal.style.display = 'flex';
      } else {
          form.reportValidity();
      }
  });

  confirmButton.addEventListener('click', function() {
      confirmButton.disabled = true;
      form.submit();
  });

    confirmButton.addEventListener('click', function() {
      loadingOverlay.style.display = 'flex';
  });
  closeButtons.forEach(function(button) {
      button.addEventListener('click', function() {
          confirmationModal.style.display = 'none';
          confirmButton.disabled = false;
      });
  });
});