document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('addComponentRow').addEventListener('click', function() {
        var tbody = document.getElementById('componentTableBody');
        var newRow = document.createElement('tr');

        newRow.innerHTML = `
            <td>
                <select name="component_name[]" class="form-control">
                    <option value="">Selecciona Componente...</option>
                    <option value="screen">Pantalla</option>
                    <option value="keyboard">Teclado</option>
                    <option value="battery">Batería</option>
                    <option value="charger">Cargador</option>
                    <option value="wifi">Wi-Fi</option>
                    <option value="casing">Carcasa</option>
                    <option value="touchpad">Touchpad</option>
                    <option value="ports">Puertos</option>
                </select>
            </td>
            <td>
                <select name="condition[]" class="form-control">
                    <option value="good">Bueno</option>
                    <option value="bad">Malo</option>
                </select>
            <td>
                <input type="text" name="observation[]" class="form-control" placeholder="Observación"/>
            </td>
        `;

        tbody.appendChild(newRow);
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