/**
 * Barrier-Free Inclusion Strategy
 * Handles inclusion questions with barrier-free exceptions
 * - A1 (Rozhodně nesouhlasím) for barrier-free questions
 * - A6 (Souhlasím) for regular inclusion questions
 */

function executeBarrierFreeInclusion(barrierKeywords) {
    console.log('🔍 EXECUTING IMPROVED BARRIER-FREE STRATEGY');
    var barrierCount = 0;
    var regularCount = 0;
    var totalProcessed = 0;

    // Find all A1 and A6 radio buttons
    var allA1 = document.querySelectorAll('input[type="radio"][id*="-A1"]');
    var allA6 = document.querySelectorAll('input[type="radio"][id*="-A6"]');
    console.log('🔘 Total A1 radios:', allA1.length, 'A6 radios:', allA6.length);

    // Look through table rows for barrier-free keywords
    var tableRows = document.querySelectorAll('tr');

    tableRows.forEach(function(row, index) {
        var rowText = row.textContent.toLowerCase();
        var hasBarrierKeyword = barrierKeywords.some(function(keyword) {
            return rowText.includes(keyword.toLowerCase());
        });

        if (hasBarrierKeyword) {
            console.log('🎯 BARRIER-FREE FOUND in row:', index + 1, rowText.substring(0, 50) + '...');

            // Look for A1 in this row and nearby elements
            var a1InRow = row.querySelector('input[type="radio"][id*="-A1"]');
            var a1InNext = row.nextElementSibling ? row.nextElementSibling.querySelector('input[type="radio"][id*="-A1"]') : null;
            var a1InParent = row.parentElement.querySelector('input[type="radio"][id*="-A1"]');

            // Try to click any A1 we find
            var targetA1 = a1InRow || a1InNext || a1InParent;
            if (targetA1 && !targetA1.checked) {
                console.log('✅ CLICKING A1:', targetA1.id);
                targetA1.click();
                barrierCount++;
                totalProcessed++;
            }
        }
    });

    // Handle regular (non-barrier) questions with A6
    allA6.forEach(function(a6Radio) {
        if (!a6Radio.checked) {
            // Check if this A6 belongs to a barrier-free question
            var rowElement = a6Radio.closest('tr');
            var isBarrierFree = false;

            if (rowElement) {
                var rowText = rowElement.textContent.toLowerCase();
                isBarrierFree = barrierKeywords.some(function(keyword) {
                    return rowText.includes(keyword.toLowerCase());
                });
            }

            // Only click A6 if it's NOT a barrier-free question
            if (!isBarrierFree) {
                a6Radio.click();
                regularCount++;
                totalProcessed++;
            }
        }
    });

    console.log('📊 RESULT: A1=' + barrierCount + ', A6=' + regularCount + ', Total=' + totalProcessed);

    return {
        barrier_free_a1: barrierCount,
        regular_a6: regularCount,
        total_processed: totalProcessed
    };
}