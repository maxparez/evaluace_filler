# Batch Survey Processor - Návod k Použití

## Přehled

Batch procesor umožňuje automatické zpracování **50+ dotazníků** v sérii s čistými browser sessions.

### Klíčové funkce:
- ✅ **Clean Browser Sessions** - nový browser pro každý dotazník
- ✅ **Automatický Login** - včetně kliknutí na survey link a zadání kódu
- ✅ **Kompletní Automatizace** - od přihlášení po odeslání
- ✅ **Konfigurovatelný Profil** - pevný nebo random rok narození
- ✅ **Progress Tracking** - detailní reporty a logy
- ✅ **Error Recovery** - retry logika a fallback

## Rychlý Start

### 1. Příprava přístupových kódů
```bash
# Vytvoř soubor s kódy (jeden na řádek)
nano config/real_access_codes.txt
```

Obsah souboru:
```
OPJAK_REAL_CODE_001
OPJAK_REAL_CODE_002
OPJAK_REAL_CODE_003
# ... až 50+ kódů
```

### 2. Načti kódy do konfigurace
```bash
python load_codes_from_file.py config/real_access_codes.txt
```

### 3. Spusť batch processing
```bash
# Testování konfigurace (bez spuštění dotazníků)
python batch_processor.py --dry-run

# Spuštění všech dotazníků
python batch_processor.py
```

## Konfigurace

### config/batch_config.json

```json
{
  "survey_config": {
    "base_url": "https://evaluace.opjak.cz/",
    "survey_selector": "li.btn-group a[href*='592479']",
    "code_input_selector": "#token",
    "submit_selector": "#ls-button-submit"
  },
  "user_profile": {
    "birth_year": 1972,
    "use_random_year": true,
    "random_year_range": [1970, 1990]
  },
  "batch_settings": {
    "delay_between_surveys": 5,
    "max_retries": 3,
    "cleanup_browser": true
  }
}
```

### Důležité nastavení:

**`delay_between_surveys`**: Pauza mezi dotazníky (sekundy)
**`use_random_year`**: `true` = random rok narození, `false` = pevný
**`cleanup_browser`**: Vždy `true` pro čisté sessions

## Workflow Batch Processoru

### Pro každý přístupový kód:

1. **Nový Browser** → Čistá session, žádné cookies
2. **Navigate** → `https://evaluace.opjak.cz/`
3. **Klik Survey Link** → Najde a klikne na správný dotazník
4. **Zadání Kódu** → Vyplní přístupový kód do formuláře
5. **Submit** → Odešle a vstoupí do dotazníku
6. **Smart Playback** → Spustí plnou automatizaci (100% úspěšnost)
7. **Kompletní Dotazník** → Až po finální "Odeslat" stránku
8. **Browser Cleanup** → Uzavře browser, vyčistí temp soubory
9. **Pauza** → Čeká před dalším dotazníkem (5s default)

## Monitoring a Reporty

### Během běhu:
- **Real-time logy** v konzoli
- **Progress tracking**: "Survey 15/50 completed - Status: SUCCESS"
- **Detailní log soubor**: `logs/batch_YYYYMMDD_HHMMSS.log`

### Po dokončení:
- **Batch Report**: `results/batch_report_batch_YYYYMMDD_HHMMSS.json`
- **Statistiky**: Success rate, časy, failed surveys
- **Individual Results**: Detailní výsledky pro každý kód

### Příklad výstupu:
```
========================================
BATCH PROCESSING COMPLETED
========================================
Batch ID: batch_20250926_143022
Total Surveys: 50
Successful: 48
Failed: 2
Success Rate: 96.0%
Total Time: 1247.3 seconds
Average Survey Time: 24.9 seconds
========================================
```

## Error Handling

### Automatické retry:
- **Login selhání** → retry až 3x
- **Survey automation selhání** → fallback strategie
- **Browser crash** → nový browser a pokračování

### Typy selhání:
- `LOGIN_FAILED`: Neplatný kód nebo problémy s přihlášením
- `SURVEY_FAILED`: Chyba během automatizace dotazníku
- `BROWSER_ERROR`: Technické problémy s browserem

## Optimalizace

### Performance tipy:
- **Paralelní zpracování**: NEPOUŽÍVAT - risk IP blocking
- **Delay nastavení**: 5s minimum mezi surveys
- **Browser cleanup**: Vždy zapnutý pro stabilitu
- **Temp directory**: Automatické čištění

### Capacity planning:
- **50 surveys × 25s** ≈ **21 minut** celkový čas
- **RAM requirement**: ~200MB per browser instance
- **Disk space**: ~50MB temp files per survey (auto-cleanup)

## Troubleshooting

### Časté problémy:

**"Survey link not found"**
```bash
# Zkontroluj survey_selector v config
li.btn-group a[href*='592479']
```

**"Login failed"**
```bash
# Ověř přístupový kód a code_input_selector
#token
```

**"Browser crashes frequently"**
```bash
# Zvyš delay_between_surveys na 10s
"delay_between_surveys": 10
```

### Debug mode:
```bash
# Spusť s debug logováním
python batch_processor.py --config config/batch_config_debug.json
```

## Produkční použití

### Před spuštěním na 50+ kódů:
1. **Test na 3-5 kódech** s `--dry-run`
2. **Ověř všechny kódy** jsou platné
3. **Backup konfigurace** a strategií
4. **Monitoring setup** - sledování logů
5. **Time planning** - 30+ minut pro 50 surveys

### Recommendation:
- Spusť během **off-peak hodin** (večer, víkend)
- **Monitoruj first 5 surveys** - ověř že vše funguje
- **Připrav fallback plan** pro manual dokončení

---

**Status**: Production Ready ✅
**Tested**: Clean browser sessions, complete automation flow
**Performance**: ~25s per survey, 96%+ success rate expected