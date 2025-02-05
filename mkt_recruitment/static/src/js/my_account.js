document.addEventListener('DOMContentLoaded', function() {

    const privateSystem = document.querySelector('#private_pension_system');
    const nationalSystem = document.querySelector('#national_pension_system');
    const comingFromOnp = document.querySelector('#coming_from_onp');
    const afpFirstJob = document.querySelector('#afp_first_job');
    const containerFirstJob = document.querySelector('#firstjob_container');
    const containerComingFromOnp = document.querySelector('#comingfromonp_container');

    function onchangeNationalSystem() {
        if ( privateSystem.checked ) {
            nationalSystem.checked = false;
            containerFirstJob.classList.remove('inactive');
            containerComingFromOnp.classList.remove('inactive');
            console.log('Second Private if');
        }
        else {
            afpFirstJob.checked = false;
            comingFromOnp.checked = false;
            containerFirstJob.classList.add('inactive');
            containerComingFromOnp.classList.add('inactive');
            console.log('Second Private else');
        }
    }

    function onchangePrivateSystem() {
        if ( nationalSystem.checked ) {
            privateSystem.checked = false;
            afpFirstJob.checked = false;
            comingFromOnp.checked = false;
            containerFirstJob.classList.add('inactive');
            containerComingFromOnp.classList.add('inactive');
            console.log('Second National if');
        }
    }

    function onchangeComingFromOnp() {
        if ( privateSystem.checked && afpFirstJob.checked ) {
            comingFromOnp.checked = false;
        }
    }

    function onchangeFirstJob() {
        if ( privateSystem.checked && comingFromOnp.checked) {
            afpFirstJob.checked = false;
        }
    }

    privateSystem.addEventListener('change', onchangeNationalSystem);
    nationalSystem.addEventListener('change', onchangePrivateSystem);
    afpFirstJob.addEventListener('change', onchangeComingFromOnp);
    privateSystem.addEventListener('change', onchangeComingFromOnp);
    comingFromOnp.addEventListener('change', onchangeFirstJob);
    privateSystem.addEventListener('change', onchangeFirstJob);
});
