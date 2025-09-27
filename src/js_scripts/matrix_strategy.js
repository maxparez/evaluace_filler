/**
 * Matrix Strategy JavaScript
 * Fills matrix questions with specific rating level (A1-A7)
 */

function executeMatrixStrategy(ratingLevel) {
    console.log('Matrix filling with rating', ratingLevel);
    var radios = document.querySelectorAll('input[type="radio"][id*="answer"][id$="-' + ratingLevel + '"]');
    console.log('Found', radios.length, 'radio buttons');

    var clicked = 0;
    var alreadySelected = 0;

    radios.forEach(function(radio) {
        if (radio.checked) {
            alreadySelected++;
        } else {
            try {
                radio.click();
                clicked++;
            } catch(e) {
                console.error('Click failed:', e);
            }
        }
    });

    var totalSelected = clicked + alreadySelected;
    console.log('Matrix result: clicked', clicked, ', already selected', alreadySelected, ', total selected', totalSelected);

    return {
        total: radios.length,
        clicked: clicked,
        alreadySelected: alreadySelected,
        totalSelected: totalSelected
    };
}