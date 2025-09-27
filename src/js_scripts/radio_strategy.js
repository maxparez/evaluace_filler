/**
 * Radio Strategy JavaScript
 * Selects radio button by finding label text match
 */

function executeRadioStrategy(selectedAnswer) {
    console.log('Radio choice selection:', selectedAnswer);
    var targetRadio = Array.from(document.querySelectorAll('input[type="radio"]')).find(radio => {
        var label = radio.parentElement || radio.nextElementSibling || radio.previousElementSibling;
        return label && label.textContent && label.textContent.includes(selectedAnswer);
    });

    if (targetRadio) {
        targetRadio.click();
        console.log('Radio clicked:', targetRadio.id);
        return {success: true, clicked: targetRadio.id};
    } else {
        console.log('Target radio not found');
        return {success: false, error: 'Radio not found'};
    }
}