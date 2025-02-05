document.addEventListener('DOMContentLoaded', function() {
    console.log('Primera linaaa');
    var currentDate = new Date();
    var day = currentDate.getDate();
    var month = currentDate.getMonth() + 1; // Los meses en JavaScript son indexados desde 0
    var year = currentDate.getFullYear();
    var formattedDate = day + '/' + month + '/' + year;
    var main = document.querySelector('#today');
    var newSpan = document.createElement('span');
    newSpan.innerHTML = formattedDate;
    main.append(newSpan);
})