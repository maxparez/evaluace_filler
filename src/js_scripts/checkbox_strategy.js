/**
 * Checkbox Strategy JavaScript
 * Selects specific checkboxes by their indices
 */

function executeCheckboxStrategy(selectedIndices) {
    console.log('Checkbox selection:', selectedIndices);
    var checkboxes = document.querySelectorAll('input[type="checkbox"]');
    var clickedCount = 0;

    console.log('Found', checkboxes.length, 'checkboxes');

    // Parse selected indices (can be array or comma-separated string)
    var targetIndices = Array.isArray(selectedIndices)
        ? selectedIndices
        : selectedIndices.split(',').map(function(i) { return parseInt(i.trim()); });

    console.log('Target indices:', targetIndices);

    // Click target checkboxes
    targetIndices.forEach(function(index) {
        var checkbox = checkboxes[index - 1]; // 1-based to 0-based indexing
        if (checkbox) {
            if (!checkbox.checked) {
                checkbox.click();
                clickedCount++;
                console.log('Clicked checkbox', index, ':', checkbox.id || checkbox.name);
            } else {
                console.log('Checkbox', index, 'already checked');
            }
        } else {
            console.log('Checkbox', index, 'not found');
        }
    });

    // Final count of target checkboxes that are selected
    var finalSelected = 0;
    targetIndices.forEach(function(index) {
        var checkbox = checkboxes[index - 1];
        if (checkbox && checkbox.checked) {
            finalSelected++;
        }
    });

    console.log('Clicked', clickedCount, 'checkboxes, now', finalSelected, 'target checkboxes selected');

    return {
        total: checkboxes.length,
        clicked: clickedCount,
        targetSelected: finalSelected,
        requiredCount: targetIndices.length
    };
}