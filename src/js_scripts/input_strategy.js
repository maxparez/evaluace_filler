/**
 * Input Strategy JavaScript
 * Fills input fields (text/number) with specified value
 */

function executeInputStrategy(inputValue) {
    console.log('Input field filling:', inputValue);
    var inputs = document.querySelectorAll('input[type="text"], input[type="number"]');
    var filled = 0;

    console.log('Found', inputs.length, 'input fields');

    inputs.forEach(function(input, index) {
        console.log('Input', index, ':', input.id, 'current value:', input.value);

        // Always fill, even if has existing value
        input.focus();
        input.value = '';  // Clear first
        input.value = inputValue;

        // Trigger proper events for validation
        input.dispatchEvent(new Event('focus', {bubbles: true}));
        input.dispatchEvent(new Event('input', {bubbles: true}));
        input.dispatchEvent(new Event('change', {bubbles: true}));
        input.dispatchEvent(new Event('blur', {bubbles: true}));

        filled++;
        console.log('Filled input', index, 'with:', input.value);
    });

    console.log('Total filled:', filled, 'input fields');
    return {
        total: inputs.length,
        filled: filled,
        success: filled > 0
    };
}