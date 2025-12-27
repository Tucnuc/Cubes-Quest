# CUBE'S QUEST
Jednoduchá mřížková dungeon crawler hra, kde hráč chodí z místnosti do místnosti, sbírá mince aby koupil vylepšení a schopnosti, vyhýbá se nepřátelům a snaží se přežít co nejdéle.

## Ovládání
Hráč se pohybuje za pomocí šipkových kláves. Pokud má koupenou Demolisher schopnost, tak ji může aktivovat klávesou E. Může ji ale aktivovat i kliknutím myši. Kdyby se hráč zasekl - dveře jsou zablokované zdí a hráč nemá Demolisher schopnost, může použít Restart tlačítko v levém dolním rohu.

## Obchod
Po každém ukončením hry, ať už poražením od nepřítele nebo resetováním za pomocí tlačítka, se hráč přesune do obchodu. Za každých 10 mincí, se mu přičte 1 zlato. Zlato se ukládá, též koupené vylepšení.<br>
Nabídka obchodu:
+ **Demolisher** - Stojí 5 zlata. Hráč může prorážet zdi. Každé proražení stojí 3 mince.
+ **Extra Hearts** - Stojí 5 zlata. Přidá hráčovi 3 extra srdíčka. Můžou se léčit za pomocí léčící fontány.
+ **Super Hearts** - Stojí 10 zlata. Přidá hráčovi 2 zlatá srdíčka. Každé z nich se léčí automaticky po 15 sekundách. Lze je vyléčit i na léčíčí fontáně.

## Místnosti
Ve hře se nachází 5 typů místností, na které může hráč narazit. Do místností se přechází za pomocí dveří, jinak obarvené políčka ve venkovních zdech. Čím déle hráč hru hraje, čím více místností prošel, tak tím častěji se mu budou dávat těžší místnosti. Dokud nedošel do bodu kdy bude mít na výběr už jenom Boss Rooms. Kromě speciálních jako Treasure nebo Healing.<br>
Typy místností:
+ **Normal Rooms** - Dveře mají světle modrou barvu. Nenachází se zde žádní nepřátelé, ale neobsahuje moc mincí a může se stát že tu i žádné nebudou.
+ **Danger Rooms** - Dveře mají oranžovou barvu. Obsahuje nepřátele. Mince už jsou ale garantované a lze jich najít víc než v normálních místnostech.
+ **Boss Rooms** - Dveře mají červenou barvu. Pokud je v místnosti dost místa, může se spawnout i boss. Obsahuje také normální nepřátele. Obsahuje více mincí a také super mince (1 super mince = 3 normální mince).
+ **Treasure Rooms** - Dveře mají žlutou barvu. Má 5% šanci na objevení v průběhu celé hry. Neobsahuje nepřátele. Obsahuje největší možný počet jak super tak i normálních mincí.
+ **Healing Rooms** - Dveře mají zelenou barvu. Má 5% šanci na objevení v průběhu celé hry. Neobsahuje nepřátele. Nachází se zdé léčicí fontána. Když na ni hráč stoupne, vyléčí se mu všechny ztracené životy.

## Nepřátelé
Hra obsahuje 3 nepřátele. Jakmile hráč vstoupí do místnosti s nepřáteli, snaží se dostat k němu. Dávají 1 dmg, až na bosse, který dává 2.
+ **Čtverec** - Nejvíce běžný nepřítel. Má červenou barvu.
+ **Trojuhelník** - Má 30% šanci že se spawne místo čtverce. Je zelený. Je rychlejší.
+ **Kruh** - Boss. Je 2x2, fialový s bílým ohraničením. Je pomalejší než čtverec, ale nic ho nezastaví. Jde rovnou k hráčovi a ničí všechny zdi v cestě.

<br><br>
Tato hra byla vytvořena jako školní projekt do programování. Hra je napsaná v Pythonu s využitím knihoven Tkinter a Pygame. Grafická část je čistě vytvořena za pomocí Tkinteru. Pygame slouží pro určité logické prvky a přehrávání hudby a zvukových efektů.