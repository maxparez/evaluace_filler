/**
 * Matrix Random Strategy JavaScript
 * Randomly selects different ratings (A5/A6/A7) for each matrix row
 */

function executeMatrixRandomStrategy(ratingOptions) {
    console.log('Matrix random rating with options:', ratingOptions);
    var totalClicked = 0;
    var totalAlready = 0;
    var ratingCounts = {};

    // Initialize rating counts
    ratingOptions.forEach(function(rating) {
        ratingCounts[rating] = 0;
    });

    // Find all radio button groups (matrix rows)
    var processedRows = new Set();
    var allRadios = document.querySelectorAll('input[type="radio"]');

    allRadios.forEach(function(radio) {
        // Extract row identifier from radio name/id
        var rowId = radio.name || radio.id.split('-')[0];

        if (!processedRows.has(rowId)) {
            processedRows.add(rowId);

            // Randomly select rating for this row
            var randomRating = ratingOptions[Math.floor(Math.random() * ratingOptions.length)];

            // Find radio for this rating in this row
            var targetRadio = document.querySelector(
                'input[type="radio"][name="' + rowId + '"][value="' + randomRating + '"]'
            );

            if (!targetRadio && radio.id) {
                // Fallback: try to find by ID pattern
                var baseId = radio.id.split('-')[0];
                targetRadio = document.querySelector('#' + baseId + '-' + randomRating);
            }

            if (targetRadio) {
                if (!targetRadio.checked) {
                    targetRadio.click();
                    totalClicked++;
                    ratingCounts[randomRating]++;
                } else {
                    totalAlready++;
                }
            }
        }
    });

    return {
        total_clicked: totalClicked,
        total_already: totalAlready,
        rating_distribution: ratingCounts,
        total_processed: totalClicked + totalAlready
    };
}