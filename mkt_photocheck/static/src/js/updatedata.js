document.addEventListener("DOMContentLoaded", function () {
  var jobsNames;
  var brandsNames;
  var fotoInput = document.getElementById("crop-image");
  var nombreInput = document.getElementById("first_name");
  var apellidoInput = document.getElementById("last_name");
  var jobsInput = document.getElementById("job_id");
  var brandsInput = document.getElementById("photocheck_brand_group_id");
  var dniInput = document.getElementById("dni");
  fotoInput.addEventListener("input", actualizarDatos);
  nombreInput.addEventListener("input", actualizarDatos);
  apellidoInput.addEventListener("input", actualizarDatos);
  jobsInput.addEventListener("change", function () {
    var selectedOption = this.options[this.selectedIndex];
    jobsNames = selectedOption.textContent.trim();
    actualizarDatos();
  });
  brandsInput.addEventListener("change", function () {
    var selectedOptions = this.options[this.selectedIndex];
    brandsNames = selectedOptions.textContent.trim();
    actualizarDatos();
  });
  dniInput.addEventListener("input", actualizarDatos);
  function actualizarDatos() {
    var nombre = nombreInput.value;
    var apellido = apellidoInput.value;
    var jobs = jobsNames;
    var dnis = dniInput.value;
    var brands = brandsNames;
    var fotoPreview = document.getElementById("crop-image");
    var cropImageSrc = fotoPreview.getAttribute("src");
    var foto = document.getElementById("photos");
    foto.src = cropImageSrc;
    document.getElementById("first_names").textContent = nombre;
    document.getElementById("last_names").textContent = apellido;
    document.getElementById("jobs").textContent = jobs;
    document.getElementById("dnis").textContent = dnis;
    document.getElementById("brands").textContent = brands;
  }
  console.log(actualizarDatos);
});