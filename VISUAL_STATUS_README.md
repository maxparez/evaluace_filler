# Visual Status Indicators for Survey Automation

## 🎯 Overview

Systém vizuálních status indikátorů poskytuje real-time feedback během automatického vyplňování dotazníků. Barevný pruh v horní části stránky informuje uživatele o současném stavu automatizace.

## 🎨 Visual Status Types

### ✅ **Running (Běžící automatizace)**
- **Barva**: Zelená (`#4CAF50`)
- **Text**: "🤖 Probíhá automatické vyplňování..."
- **Kdy**: Během normálního vyplňování stránek
- **Akce**: Žádná akce potřebná

### ⚡ **Processing (Zpracování stránky)**
- **Barva**: Modrá (`#2196F3`)
- **Text**: "⚡ Zpracovávám stránku..."
- **Kdy**: Během analýzy a vyplňování konkrétní stránky
- **Akce**: Čekejte na dokončení

### ⏳ **Waiting (Čekání)**
- **Barva**: Oranžová (`#FF9800`)
- **Text**: "⏳ Čekám na načtení stránky..."
- **Kdy**: Během přechodu mezi stránkami
- **Akce**: Čekejte na načtení

### ⚠️ **Manual Required (Manuální zásah)**
- **Barva**: Červená (`#F44336`)
- **Text**: "⚠️ Požadován manuální zásah - zkontrolujte stránku"
- **Kdy**: Když automatizace nerozpozná typ stránky
- **Akce**: **VYPLŇTE RUČNĚ a pokračujte tlačítkem "Další"**

### ❌ **Error (Chyba)**
- **Barva**: Červená (`#F44336`)
- **Text**: "❌ Chyba při automatickém vyplňování"
- **Kdy**: Při systémové chybě nebo přerušení
- **Akce**: Zkontrolujte konzoli a případně restartujte

### 🎉 **Completed (Dokončeno)**
- **Barva**: Zelená (`#4CAF50`)
- **Text**: "🎉 Automatické vyplňování dokončeno úspěšně!"
- **Kdy**: Po úspěšném dokončení celého dotazníku
- **Akce**: Žádná - automaticky zmizí za 5 sekund

## 🔧 Technická implementace

### JavaScript komponenta (`status_indicator.js`)
```javascript
// Inicializace systému
window.AutomationStatusIndicator.init();

// Nastavení statusu
window.AutomationStatusIndicator.setStatus('running');

// Status s progress
window.AutomationStatusIndicator.setStatusWithProgress('running', 3, 10, 'Zpracovávám');
```

### Python API (`StatusIndicatorManager`)
```python
from src.utils.status_indicator_manager import StatusIndicatorManager

# Inicializace
status_manager = StatusIndicatorManager(driver)

# Základní stavy
status_manager.set_status('running')
status_manager.set_manual_required('Neznámý typ stránky', 'Vyplňte ručně')

# Convenience metody
status_manager.start_automation(page_number=1, total_pages=10)
status_manager.processing_page(3, 'Zpracovávám otázky')
status_manager.automation_completed()
```

## 🎪 Features a animace

### **Smooth animace**
- Slide down při zobrazení
- Slide up při skrytí
- Plynulé přechody mezi stavy (0.3s ease-in-out)

### **Progress indikátory**
```
🤖 Probíhá automatické vyplňování... (Stránka 3/10 - Zpracovávám otázky)
```

### **Interaktivní prvky**
- **Close tlačítko (✕)**: Zobrazí se při hover u manual intervention
- **Auto-hide**: Completed status automaticky zmizí za 5 sekund
- **Z-index 999999**: Vždy na vrchu stránky

### **Responsive design**
- Fixní pozice v horní části obrazovky
- Adaptivní šířka podle obsahu
- Professional shadows a border

## 🚀 Použití v praxi

### **Automatický workflow**
1. **Spuštění**: Zelený pruh "Probíhá automatické vyplňování"
2. **Každá stránka**: Modrý pruh "Zpracovávám stránku X"
3. **Přechod**: Oranžový pruh "Čekám na načtení"
4. **Dokončení**: Zelený pruh "Dokončeno" (5s auto-hide)

### **Manuální zásah**
1. **Detekce problému**: Červený pruh "Manuální zásah"
2. **Uživatel vyplní**: Stránku vyplní ručně
3. **Pokračování**: Klikne "Další" pro pokračování automatizace
4. **Návrat**: Systém pokračuje automaticky

### **Error handling**
1. **Detekce chyby**: Červený pruh s popisem chyby
2. **Logování**: Detaily v konzoli/logach
3. **Recovery**: Možnost manuálního pokračování

## 🧪 Testování

### **Ruční testování**
```bash
# Spuštění test suite
python test_status_indicators.py

# Test všech stavů s vizuální verifikací
# Test integrace se SmartPlaybackSystem
# Test progress indikátorů
```

### **Testovací scenarios**
1. **Všechny stavy**: Postupné testování všech status typů
2. **Progress updates**: Test s různými čísly stránek
3. **Manual intervention**: Test červených alertů
4. **Animations**: Test hide/show funkcionalit
5. **Integration**: Test s reálnou automatizací

## 📋 Konfigurace

### **Environment variables**
Žádné speciální proměnné - používá standardní Config

### **Customization možnosti**
```javascript
// Vlastní text
AutomationStatusIndicator.setStatus('running', 'Vlastní zpráva');

// Vlastní progress
AutomationStatusIndicator.setStatusWithProgress('processing', 5, 20, 'Custom akce');
```

## 🔍 Troubleshooting

### **Status bar se nezobrazuje**
- Zkontrolujte, že `status_indicator.js` je načten
- Ověřte console na JavaScript errory
- Zkontrolujte, že `StatusIndicatorManager` je inicializován

### **Animace nefungují**
- Ověřte CSS support v prohlížeči
- Zkontrolujte, že stránka nemá conflicting styles
- CSS animations vyžadují moderní prohlížeč

### **Status se neaktualizuje**
- Ověřte connection mezi Python a browser
- Zkontrolujte Selenium WebDriver komunikaci
- Logování v `StatusIndicatorManager` pro debugging

## 🎯 Best Practices

### **Pro vývojáře**
1. **Vždy inicializovat** status manager při připojení k browseru
2. **Update status** při každé významné akci
3. **Používat convenience metody** místo raw set_status
4. **Testovat manual intervention** scenarios

### **Pro uživatele**
1. **Sledovat barevné indikátory** pro pochopení stavu
2. **Při červeném pruhu** vždy vyplnit ručně a pokračovat
3. **Nerestartovat** při oranžové/modré (čekání je normální)
4. **Zelený = OK** - automatizace funguje správně

## 🎉 Výhody systému

### **User Experience**
- **Okamžitý feedback** o stavu automatizace
- **Jasné instrukce** při potřebě manuálního zásahu
- **Professional vzhled** s smooth animacemi
- **Non-intrusive** - nezasahuje do obsahu stránky

### **Development Benefits**
- **Easy debugging** - vizuální confirmation stavů
- **Modulární design** - lze snadno rozšířit
- **Testovatelné** - comprehensive test suite
- **Maintainable** - čistá separace JS/Python kódu

---

**🎉 Visual Status Indicators poskytují profesionální user experience během automatického vyplňování dotazníků!**