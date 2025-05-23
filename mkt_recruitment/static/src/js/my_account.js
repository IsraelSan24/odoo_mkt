document.addEventListener('DOMContentLoaded', function () {
    // Elementos
    const privateSystem = document.querySelector('#private_pension_system');
    const nationalSystem = document.querySelector('#national_pension_system');
    const comingFromOnp = document.querySelector('#coming_from_onp');
    const comingFromAfp = document.querySelector('#coming_from_afp');
    const afpFirstJob = document.querySelector('#afp_first_job');

    const containerFirstJob = document.querySelector('#firstjob_container');
    const containerComingFromOnp = document.querySelector('#comingfromonp_container');
    const containerComingFromAfp = document.querySelector('#comingfromafp_container');

    // Mostrar u ocultar contenedores asociados al sistema privado
    function handlePrivateSystemChange() {
        if (privateSystem.checked) {
            nationalSystem.checked = false;
            containerFirstJob.classList.remove('inactive');
            containerComingFromOnp.classList.remove('inactive');
            containerComingFromAfp.classList.remove('inactive');
        } else {
            clearPrivateOptions();
            hidePrivateContainers();
        }
    }

    function handleNationalSystemChange() {
        if (nationalSystem.checked) {
            privateSystem.checked = false;
            clearPrivateOptions();
            hidePrivateContainers();
        }
    }

    // Lógica para evitar selecciones conflictivas
    function handleFirstJobChange() {
        if (privateSystem.checked && afpFirstJob.checked) {
            comingFromOnp.checked = false;
            comingFromAfp.checked = false;
        }
    }

    function handleComingFromOnpChange() {
        if (privateSystem.checked && comingFromOnp.checked) {
            afpFirstJob.checked = false;
            comingFromAfp.checked = false;
        }
    }

    function handleComingFromAfpChange() {
        if (privateSystem.checked && comingFromAfp.checked) {
            afpFirstJob.checked = false;
            comingFromOnp.checked = false;
        }
    }

    // Helpers
    function clearPrivateOptions() {
        afpFirstJob.checked = false;
        comingFromOnp.checked = false;
        comingFromAfp.checked = false;
    }

    function hidePrivateContainers() {
        containerFirstJob.classList.add('inactive');
        containerComingFromOnp.classList.add('inactive');
        containerComingFromAfp.classList.add('inactive');
    }

    // Eventos
    privateSystem.addEventListener('change', handlePrivateSystemChange);
    nationalSystem.addEventListener('change', handleNationalSystemChange);
    afpFirstJob.addEventListener('change', handleFirstJobChange);
    comingFromOnp.addEventListener('change', handleComingFromOnpChange);
    comingFromAfp.addEventListener('change', handleComingFromAfpChange);
});