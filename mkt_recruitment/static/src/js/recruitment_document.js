document.addEventListener('DOMContentLoaded', function() {

    console.log('Hola')
    const annexOne =  document.querySelector('#annex_1');
    const annexTwo =  document.querySelector('#annex_2');
    const annexThree =  document.querySelector('#annex_3');
    const annexFour =  document.querySelector('#annex_4');
    const annexFive =  document.querySelector('#annex_5');
    const annexSix =  document.querySelector('#annex_6');
    const annexSeven =  document.querySelector('#annex_7');
    const signatureButton = document.querySelector('#signaturebutton');
    
    function displaySignButton() {
        if (annexOne.checked && annexTwo.checked && annexThree.checked && annexFour.checked && annexFive.checked && annexSix.checked && annexSeven.checked) {
            signatureButton.classList.remove('inactive')
        } else {
            signatureButton.classList.add('inactive')
        }
    }
    annexOne.addEventListener('change', displaySignButton);
    annexTwo.addEventListener('change', displaySignButton);
    annexThree.addEventListener('change', displaySignButton);
    annexFour.addEventListener('change', displaySignButton); 
    annexFive.addEventListener('change', displaySignButton); 
    annexSix.addEventListener('change', displaySignButton); 
    annexSeven.addEventListener('change', displaySignButton); 
});
