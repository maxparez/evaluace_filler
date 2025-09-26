#!/bin/bash
# Run Interactive Survey Mapper

echo "🎯 SPOUŠTÍM INTERACTIVE SURVEY MAPPER"
echo "========================================"

# Activate virtual environment
source venv/bin/activate

# Check if browser is running
echo "🔍 Kontroluji browser na portu 9222..."
if curl -s http://localhost:9222/json >/dev/null 2>&1; then
    echo "✅ Browser běží na portu 9222"
else
    echo "❌ Browser neběží! Spusť browser s:"
    echo "   google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome_evaluace"
    exit 1
fi

echo ""
echo "🚀 Spouštím interaktivní mapper..."
echo "📋 INSTRUKCE:"
echo "   1. Naviguj v browseru na začátek dotazníku"
echo "   2. Pak stiskni ENTER v tomto terminálu"
echo "   3. Pro každou stránku zvol strategii (1-6)"
echo "   4. Script automaticky naviguje a ukládá"
echo ""

# Run the interactive mapper
python interactive_survey_mapper.py