Automatizace Vyplňování Webových Dotazníků: Od Základu po Pokročilý Systém
Tento dokument shrnuje postup a vývoj myšlenek při tvorbě automatizačního nástroje pro vyplňování evaluačních dotazníků OP JAK. Cílem bylo eliminovat repetitivní manuální práci při vyplňování dotazníků pro 50 různých škol.
1. Počáteční Analýza a Problém
Problém: Nutnost vyplnit velké množství (50+) podobných webových dotazníků.
Technické překážky: Dotazník je dynamický. Každý krok (přechod na další stránku) je řešen přes POST HTTP request a formulář je chráněn CSRF tokenem. To znemožňuje použití jednoduchých nástrojů jako BeautifulSoup s requests, které by vyžadovaly složitou správu session a tokenů.
Prvotní řešení: Volba padla na Selenium, nástroj pro automatizaci prohlížeče, který se s těmito překážkami vypořádá přirozeně, protože simuluje reálného uživatele.
2. Fáze I: Základní Automatizace pomocí Selenium
První verze skriptu se zaměřila na přímou simulaci uživatele.
Princip:
Selenium otevře prohlížeč s danou URL.
V cyklu prochází stránkami dotazníku.
Na každé stránce najde všechny relevantní input prvky (např. radio buttony pro "Souhlasím") pomocí jejich atributů (např. value="A6").
Na každý nalezený prvek simuluje kliknutí.
Najde tlačítko "Další" (podle ID nebo name) a klikne na něj.
Cyklus se opakuje, dokud tlačítko "Další" existuje.
Klíčový Python kód:
code
Python
from selenium.webdriver.common.by import By

# ... inicializace driveru ...

# Najdi všechny "Souhlasím" radio buttony
souhlas_buttons = driver.find_elements(By.XPATH, "//input[@type='radio' and @value='A6']")
for button in souhlas_buttons:
    button.click()

# Klikni na další
driver.find_element(By.ID, 'ls-button-submit').click()
3. Fáze II: Zrychlení pomocí Injektáže JavaScriptu
Pro zrychlení a zjednodušení akcí na jedné stránce jsme přešli k přímému provádění JavaScriptu v kontextu stránky.
Princip: Místo aby Selenium hledalo desítky prvků jednotlivě, vloží do stránky jeden JavaScriptový příkaz, který provede všechny akce najednou a mnohem rychleji.
Klíčový JavaScript kód (pro vložení do konzole):
code
JavaScript
// Vybere všechny odpovědi "Souhlasím" a klikne na "Další"
document.querySelectorAll("input[type='radio'][value='A6']").forEach(b => b.click());
document.getElementById('ls-button-submit').click();
Propojení se Selenium: Python skript byl upraven tak, aby tento JavaScriptový blok spouštěl na každé stránce.
code
Python
# JavaScript kód jako string v Pythonu
javascript_command = """
document.querySelectorAll("input[type='radio'][value='A6']").forEach(b => b.click());
document.getElementById('ls-button-submit').click();
"""
# Spuštění přes Selenium
driver.execute_script(javascript_command)
4. Fáze III: Zvýšení Robustnosti pro Různé Typy Otázek
Zjistili jsme, že dotazníky obsahují různé typy stránek (maticové otázky, Ano/Ne, výběr z možností). Skript musel být upraven, aby se nezastavil na neznámé stránce.
Princip: JavaScriptový blok byl rozšířen o podmínkovou logiku. Postupně zkouší různé typy akcí a provede tu první, která je na dané stránce možná.
Příklad rozšířeného JavaScriptu:
code
JavaScript
let answeredSomething = false;

// Zkus maticovou otázku
const matrixButtons = document.querySelectorAll("input[type='radio'][value='A6']");
if (matrixButtons.length > 0) {
    matrixButtons.forEach(b => b.click());
    answeredSomething = true;
}

// Pokud ne, zkus Ano/Ne
if (!answeredSomething) {
    // ... kód pro kliknutí na "Ne" ...
}

// ... atd.
5. Fáze IV: Interaktivní Režim (Poloautomatizace)
Aby byl skript absolutně spolehlivý, implementovali jsme mechanismus, který v případě neznámé situace předá řízení zpět uživateli.
Princip:
JavaScript už nekliká na "Další". Jeho úkolem je pouze vyplnit stránku a vrátit výsledek (true/false) do Pythonu.
Python je hlavní mozek. Spustí JS a zkontroluje výsledek.
Pokud je výsledek true, Python sám klikne na "Další" a pokračuje.
Pokud je výsledek false, Python vypíše zprávu "Nevím, co dělat, prosím zasáhni" a pozastaví se pomocí input(). Uživatel ručně vyplní stránku a stiskem Enteru opět spustí automatizaci.
6. Finální Architektura: Data-Driven Systém (Oddělení Logiky a Dat)
Toto je nejpokročilejší a nejudržitelnější řešení, které kombinuje všechny předchozí nápady. Logika skriptu je oddělena od "znalostí" o konkrétních dotaznících.
A. Znalostní Databáze (scenarios.json)
Vytvořili jsme externí JSON soubor, který slouží jako databáze známých stránek a akcí, které se na nich mají provést.
Struktura: Slovník, kde klíčem je unikátní text otázky a hodnotou je typ akce.
Příklad scenarios.json:
code
JSON
{
    "Uveďte, prosím, do jaké míry souhlasíte s následujícími výroky...": {
        "action_type": "A6_MATRIX"
    },
    "Setkali jste se s nějakými problémy/komplikacemi v průběhu realizace projektu?": {
        "action_type": "CLICK_NE"
    },
    "Kolik rodičů se v průměru zapojilo...": {
        "action_type": "SELECT_1_10_RODICU"
    }
}
B. Chytrý Vykonavatel (player.py)
Finální Python skript, který funguje jako "přehrávač" scénářů z databáze.
Pracovní cyklus:
Načtení: Na začátku si načte celý scenarios.json do paměti.
Identifikace: Na každé stránce dotazníku najde element s textem otázky (.ls-label-question).
Vyhledání: Získaný text použije jako klíč pro vyhledání v načtené databázi.
Provedení akce:
Pokud je klíč nalezen: Skript provede příslušnou akci definovanou v JSON (např. spustí JS pro A6_MATRIX nebo najde a klikne na tlačítko "Ne"). Poté sám klikne na "Další".
Pokud klíč není nalezen: Skript se přepne do interaktivního režimu a požádá uživatele o manuální zásah.
Opakování: Cyklus se opakuje, dokud nedojde na konec dotazníku.
Hlavní výhody finálního řešení:
Škálovatelnost: Když se objeví nový typ otázky, není třeba měnit Python kód. Stačí přidat nový záznam do scenarios.json.
Udržovatelnost: Kód je čistý a má jedinou zodpovědnost – provádět akce. Všechny "znalosti" jsou na jednom místě v datovém souboru.
Robustnost: Kombinace automatizace a možnosti manuálního zásahu zaručuje, že skript dokončí svou práci za jakýchkoliv okolností.