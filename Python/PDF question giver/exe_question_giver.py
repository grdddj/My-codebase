import random
import sys

QUESTIONS = {
    "a": [
        (
            "1. zajištění účelného využívání rádiových kmitočtů a správu rádiového spektra vykonává",
            "Český telekomunikační úřad",
        ),
        (
            "2. radiokomunikační službou je komunikační činnost, která spočívá v přenosu, vysílání nebo příjmu signálů prostřednictvím",
            "rádiových vln",
        ),
        (
            "3. plán přidělení kmitočtových pásem (národní kmitočtovou tabulku) stanoví",
            "Ministerstvo průmyslu a obchodu vyhláškou",
        ),
        (
            "4. individuální oprávnění k vyžívání rádiových kmitočtů uděluje",
            "Český telekomunikační úřad",
        ),
        (
            "5. držitel individuálního oprávnění k využívání rádiových kmitočtů je povinen platit za využívání rádiových kmitočtů",
            "poplatek dle nařízení vlády o poplatcích",
        ),
        (
            "6. rádiovým spektrem se rozumí elektromagnetické vlny v rozmezí",
            "9 kHz - 3000 GHz",
        ),
        (
            "7. státní kontrolu elektronických komunikací vykonává",
            "Český telekomunikační úřad",
        ),
        (
            "8.  fyzická osoba vykonávající obsluhu vysílacího rádiového zařízení bez platného průkazu odborné způsobilosti se dopustila",
            "přestupku",
        ),
        (
            "9.  za obsluhu vysílacího rádiového zařízení bez platného průkazu odborné způsobilosti může Úřad uložit fyzické osobě pokutu až do výše",
            "100 000 Kč",
        ),
        (
            "10.  v mezinárodní volací značce České republiky tvoří první dvě písmena (prefix) vždy dvojice písmen",
            "OK nebo OL",
        ),
        (
            "11. mezinárodní volací značka lodní stanice u lodí zapsaných v námořním rejstříku ČR je",
            "OL a další dvě písmena (případně OL a čtyři číslice u jachet)",
        ),
        ("12. volací značka OL1234 v radiotelefonním provozu je", "volací značka lodi"),
        ("13.  SPE je volací značka", "pobřežní stanice"),
        ("14. falešné volací značky a falešné signály", "se nesmí používat"),
        ("15. pohyblivá stanice námořní pohyblivé služby je", "lodní stanice"),
        (
            "16. pohyblivá služba mezi pobřežními stanicemi a lodními stanicemi nebo mezi lodními stanicemi se nazývá",
            "námořní pohyblivá služba",
        ),
        (
            "17. pořadí zpráv podle důležitosti je následující:",
            "tísňová zpráva (DISTRESS), pilnostní zpráva (URGENCY), bezpečnostní zpráva (SAFETY)",
        ),
        (
            "18. nejvyšší prioritu a absolutní přednost má zpráva",
            "tísňová (signál MAYDAY)",
        ),
        (
            "19. tísňové volání a tísňová zpráva se vysílají jen na rozkaz",
            "velitele nebo osoby odpovědné za loď nebo letadlo",
        ),
        (
            "20. mezinárodní VKV tísňový, bezpečnostní a volací kmitočet v radiotelefonii v námořní pohyblivé službě je",
            "156,8 MHz (kanál 16)",
        ),
        (
            "21. kanál 16 v pásmu VHF je v námořní pohyblivé službě určen k",
            "tísňovému a pilnostnímu volání, upozornění na bezpečnostní volání a k navázání spojení s následným přeladěním na pracovní kanál.",
        ),
        (
            "22. rádiové kmitočty z pásma 160 MHz spadají do pásma označovaného jako",
            "VHF",
        ),
        (
            "23. pátrací a záchrannou operaci na moři může ukončit",
            "velitel (řídící stanice) pátrací a záchranné operace",
        ),
        (
            "24. pohyblivým stanicím na moři nebo nad mořem je zakázáno provozovat",
            "rozhlasovou službu",
        ),
        (
            "25. služba u letadlové nebo lodní stanice podléhá nejvyšší pravomoci",
            "velitele nebo osoby, která je odpovědná za letadlo nebo loď",
        ),
        (
            "26. doba platnosti průkazů operátorů námořní pohyblivé služby LRC a SRC je stanovena na",
            "10 let při prvním vydání průkazu",
        ),
        (
            "27. o prodloužení doby platnosti průkazu odborné způsobilosti se žádá",
            "písemně, minimálně jeden měsíc před koncem platnosti průkazu",
        ),
        (
            "28. při žádosti o prodloužení platnosti průkazu je třeba také",
            "uhradit příslušný správní poplatek a doložit praxi v obsluze rádiových stanic",
        ),
        (
            "29. v případě, že doba platnosti průkazu již uplynula, může držitel průkazu žádat o nový průkaz",
            "v období do jednoho roku ode dne pozbytí platnosti průkazu",
        ),
        (
            "30. Doba platnosti průkazů operátorů námořní pohyblivé služby se na základě žádosti držitele prodlužuje o",
            "5 let",
        ),
        (
            "31. první znak nebo první dva znaky mezinárodní volací značky označují",
            "státní příslušnost stanice",
        ),
        (
            "32. stejná volací značka",
            "nemůže být přidělena dvěma nebo více provozovatelům stanic",
        ),
        (
            "33. inspekční orgány zemí, které pohyblivá stanice (letadlo, loď) navštíví",
            "mohou vyžadovat předložení průkazu operátora",
        ),
        (
            "34. Mezinárodní telekomunikační unie (ITU) je",
            "specializovanou organizací Organizace spojených národů pro oblast telekomunikací",
        ),
        (
            "35. Q-kódem se rozumí",
            "kódová skupina tří písmen začínající vždy písmenem Q, která má určitý konkrétní, mezinárodně dohodnutý význam",
        ),
        (
            "36. volací značkou je",
            "každé poznávací označení stanice přidělené dle Radiokomunikačního řádu, které umožňuje zjištění její totožnosti během vysílání",
        ),
        (
            "37. provozovatel stanice vysílá vlastní volací značku během  spojení",
            "předepsaným postupem minimálně na začátku a na konci",
        ),
        (
            "38. mezi členy Regionální úmluvy o radiotelefonní službě na vnitrozemských vodních cestách",
            "patří i Česká republika",
        ),
        (
            "39. vnitrozemský automatický identifikační  systém (Inland AIS)",
            "je součástí říčních informačních služeb a může být používán na vyhrazených rádiových kmitočtech",
        ),
        (
            "40. AIS transpondér je rádiová stanice umožňující",
            "příjem, vysílání a zpracování rádiového signálu vnitrozemského automatického identifikačního systému",
        ),
        (
            "41. maximální povolený výkon lodní radiostanice vysílající v pásmu VHF je:",
            "25 W.",
        ),
        (
            "42. Telekomunikační tajemství se týká",
            "všech osob, které znají obsah rádiových zpráv nebo se dověděly o jejich existenci či o zprávě, která byla doručena prostřednictvím radiokomunikační služby.",
        ),
        (
            "43. Každý, kdo se dozví informace o skutečnostech, které jsou předmětem telekomunikačního tajemství,",
            "je povinen zachovávat o nich mlčenlivost.",
        ),
        (
            "44. Předmětem telekomunikačního tajemství je zejména",
            "obsah zpráv přepravovaných nebo jinak zprostředkovaných telekomunikačními zařízeními a sítěmi s výjimkou zpráv určených veřejnosti.",
        ),
    ],
    "b": [
        (
            "1. oblast pokrytá signálem alespoň jedné pobřežní VKV radiotelefonní stanice, která zabezpečuje nepřetržitou pohotovost pro tísňová volání DSC v systému GMDSS, se označuje jako",
            "námořní oblast A1",
        ),
        (
            "2. RCC (Rescue Coordination Centre) je",
            "orgán zodpovědný za účinnou organizaci pátracích a záchranných služeb (SAR) a za koordinaci SAR zásahů v dané oblasti",
        ),
        (
            "3. zkratka DSC znamená",
            "Digital Selective Calling (digitální selektivní volání), tj. volání prostřednictvím digitálního přenosu signálu a s možností výběru volané stanice nebo stanic",
        ),
        (
            "4. jsou pro DSC určeny speciální kmitočty?",
            "pro DSC je pásmu VKV vyhrazen kanál č. 70, na němž je možné komunikovat pouze DSC, fonický provoz je zablokován",
        ),
        (
            "5. k označení identity lodě v rámci DSC provozu se používá",
            "devítimístný číselný kód MMSI (Maritime Mobile Service Identity)",
        ),
        (
            "6. dá se z MMSI lodě poznat pod jakou vlajkou pluje?",
            "ano, první tři číslice (MID) kódu lodě označují stát, v němž je loď registrována",
        ),
        (
            "7. jaké MMSI se použije při volání pobřežní stanice?",
            "pobřežní stanice se volají devítimístným kódem, v němž se před MID (trojčíslí přidělené státu, z jehož území pobřežní stanice pracuje a jež používají k identifikaci jeho lodě) předřadí dvě nuly",
        ),
        (
            "8. je možné se pomocí DSC spojit s definovanou skupinou lodí?",
            "DSC protokol umožňuje vyslat zprávu skupině lodí na podkladě použití přidělené skupinové MMSI. (např. lodě pod jednou vlajkou nebo lodě přítomné v určité geografické oblasti)",
        ),
        ("9. MID České republiky je", "270"),
        ("10. při volání skupiny lodí se před MID předřazuje", "jedna nula"),
        (
            "11. funkčnost VKV zařízení DSC se ověřuje",
            "pouze pomocí nabídky „SELF TEST“ se jednou za den prověřuje činnost transceiveru, „živé“ testování na kanálu 70 s jinou stanicí je zakázáno",
        ),
        (
            "12. jakým způsobem drží SOLAS lodě poslechové hlídky v oblasti A1?",
            "předpisy stanoví, že lodní radiostanice musí být schopna trvale přijímat tísňová a jiná volání DSC na kanálu 70 (v praxi se tento požadavek řeší použitím dvou VKV radiostanic, jedna sleduje fonický provoz, zejména kanál 16, druhá DSC kanál 70).",
        ),
        (
            "13. potvrzení běžného (rutinního) volání",
            "probíhá potvrzením nabídky spojení včetně nabídky čísla pracovního kanálu tlačítkem ENTER. Po jeho stisknutí je další komunikace automaticky přepojena na nabídnutý pracovní kanál.",
        ),
        (
            "14.   Aktivace tlačítka „Distress“ (aktivace DSC volání)",
            "stlačením tlačítka nepřetržitě po dobu 5-6 sekund, tlačítko je výrazně odlišeno a umístěno pod krytem",
        ),
        (
            "15. obsah tísňového volání DSC je následující:",
            "identifikační údaj, poziční informace, čas UTC a povaha tísně,",
        ),
        (
            "16. přednastavený obsah tísňového volání DSC se vysílá",
            "v situaci, kdy není čas na ruční vkládání dalších doplňujících údajů",
        ),
        (
            "17. způsob vkládání údajů o poloze do tísňového volání DSC",
            "pokud je do radiostanice předepsaným způsobem propojen výstup z přijímače GPS, je údaj o poloze včetně UTC aktualizován průběžně, jinak je možné vkládat tyto údaje ručně (dle instrukcí v manuálu stanice).",
        ),
        (
            "18. postup pro nastavení obsahu vysílání tísňového volání DSC",
            "v nabídce MENU zvolit DISTRESS jako stupeň priority volání, zkontrolovat nebo vložit údaje o poloze včetně UTC, případně vložit povahu tísně. Po odeslání se stanice v tísni automaticky přepne na 16. kanál.",
        ),
        (
            "19. opakování tísňového volání DSC",
            "radiostanice opakuje vysílání tísňového volání automaticky vždy po 4 minutách, dokud pobřežní stanice nezruší další vysílání automaticky potvrzením příjmu RECEIVED cestou DSC nebo není vysílání zrušeno samotnou stanicí v tísni.",
        ),
        (
            "20. Proč má příjem tísňového volání DSC přednostně potvrdit pobřežní stanice?",
            "protože disponuje optimálními technickými a organizačními předpoklady k řízení efektivní záchranné operace. Navíc sama může účinně aktivovat asistenci plavidel v okolí tísňové události včetně letecké podpory.",
        ),
        (
            "21. Potvrzení příjmu tísňového volání DSC typu „DISTRESS RELAY“ call od pobřežní stanice.",
            "po přepnutí stanice na 16. kanál odvysílat radiotelefonicky pobřežní stanici potvrzení příjmu s rekapitulací obsahu volání, uzavřít formulací RECEIVED MAYDAY RELAY a doplnit údaji o vlastní poloze, vzdálenosti a rychlosti plavby.",
        ),
        (
            "22. potvrzení tísňového volání DSC lodní stanicí",
            "přes to, že opakující se tísňové volání (akustickým alarmem) vybízí k okamžitému potvrzení jeho příjmu, sledovat tísňový provoz a na kanálu 16 potvrdit příjem teprve na podkladě rozhodnutí velitele lodi.",
        ),
        (
            "23. Účel tísňového volání DSC pobřežní stanicí typu DISTRESS ALERT RELAY.",
            "pobřežní stanice takto alarmuje lodě v oblasti tísně z důvodu ověření možnosti jejich operativní součinnosti v místě potřeby a využitelnosti jejich vybavení pro realizaci pomoci, v souladu s přípravou vlastní záchranné akce.",
        ),
        (
            "24. Vysílání DISTRESS ALERT RELAY lodní stanicí",
            "na podkladě rozhodnutí velitele loď vysílá radiotelefonicky obsah zachyceného tísňového DSC volání, pokud zjistí, že pobřežní stanice do 3 minut příjem nepotvrdila.",
        ),
        (
            "25. Jakou použije pobřežní stanice adresu u zprávy DISTRESS ALERT RELAY pro ALL SHIPS?",
            "žádnou, adresa není potřeba",
        ),
        (
            "26. Jakou použije pobřežní stanice adresu u zprávy určené pro konkrétní  loď (INDIVIDUAL STATION)?",
            "použije se MMSI této stanice",
        ),
        (
            "27. DSC volání DISTRESS ALERT RELAY vyslané pobřežní nebo lodní stanicí všem lodím potvrzují lodní stanice",
            "radiotelefonním provozem na kanálu 16",
        ),
        (
            "28. pilnostní zprávy a DSC",
            "pilnostní zprávy se ohlásí pilnostním voláním DSC na kanálu 70, v němž se uvede, na kterém kanálu se bude pilnostní zpráva následně vysílat radiotelefonem",
        ),
        (
            "29. potvrzování příjmu pilnostních volání DSC provozem",
            "příjem pilnostních volání DSC avizujících pilnostní zprávu na pracovním kanálu se nepotvrzuje, loď pouze přepne na ohlášený radiotelefonní kanál k vyslechnutí obsahu zprávy.",
        ),
        (
            "30. bezpečnostní zprávy a DSC",
            "bezpečnostní zprávy se nejprve ohlásí bezpečnostním voláním DSC na kanálu 70, v němž se uvede, na kterém kanálu se bude bezpečnostní zpráva následně vysílat radiotelefonem",
        ),
        (
            "31. potvrzování příjmu bezpečnostních volání DSC provozem",
            "příjem bezpečnostních volání DSC se na kanálu 70 zásadně nepotvrzuje, loď pouze přepne na ohlášený kanál a přijme bezpečnostní zprávu",
        ),
        (
            "32.  jaký EPIRB je předepsán pro GMDSS oblast A1?",
            "EPIRB s pracovní frekvencí 406 MHz pro systém COSPAS-SARSAT, nově varianta s vestavěným GPS a s vysíláním dohledávacího signálu 121,5 MHz pro leteckou součinnost.",
        ),
        (
            "33.  jak se aktivuje EPIRB?",
            "aktivuje se manuálně nebo automaticky po vynoření se z hloubky 4 m, v níž se při potápění lodě automaticky uvolní z držáku",
        ),
        (
            "34. co jsou NON-SOLAS lodě?",
            "jsou to lodě na něž se nevztahuje úmluva SOLAS, tzn. lodě, které nejsou určeny pro přepravu více než 12 cestujících (passenger ship) a nákladní lodě s nosností menší než 300 tun (patří sem i malá sportovní a rekreační plavidla)",
        ),
        (
            "44. při použití mezinárodní hláskovací abecedy se znak „@“ (tzv. zavináč) vyjádří výrazem:",
            "AT",
        ),
        (
            "45. PTT je označení tlačítka, jehož stisknutím u zapnuté radiostanice dojde",
            "k  umožnění vysílání řeči",
        ),
        ("46. správná zkratka pro „Mezinárodní námořní organizace“", "IMO"),
        (
            "47. správná zkratka pro „mezinárodní Úmluva o bezpečnosti lidského života na moři“",
            "SOLAS",
        ),
        ("48. správná zkratka pro „odpovídač pro účely pátrání a záchrany“", "SART"),
        ("49. správná zkratka pro „koordinovaný světový čas“", "UTC"),
        (
            "50. správná zkratka pro „poplatek za radiokomunikační služby poskytnuté na lodi“",
            "SC",
        ),
        ("51. správná zkratka pro „poplatek za služby pobřežní stanice“", "CC"),
        ("52. správná zkratka pro „částka za přenos po pozemních spojích“", "LL"),
        (
            "53. správná zkratka pro „identifikační číslo námořní pohyblivé služby",
            "MMSI",
        ),
        ("54. správná zkratka pro „rádiová bóje označující místo katastrofy“", "EPIRB"),
        ("55. výraz „RIJEKA RADIO“ znamená", "označení pobřežní stanice RIJEKA"),
        ("56. výraz „CALLSIGN“ znamená", "volací značku"),
        ("57. výraz „ACCOUNTING AUTHORITY“ znamená", "mezinárodní odúčtovna"),
        ("58. výraz „ROGER“ znamená", "„rozumím“ (při odpovědi na příkaz)"),
        ("59. výraz „LATITUDE“ znamená", "zeměpisná šířka"),
        ("60. výraz „LONGITUDE“ znamená", "zeměpisná délka"),
        ("61. výraz „DEGREE“ znamená", "stupeň"),
        ("62. Zprávy NAVTEX na kmitočtu 518 kHz jsou vysílány v jazyce", "anglickém"),
        ("63. Dosah stanice systému NAVTEX na kmitočtu 518 kHz činí", "200-400 NM"),
        (
            "64. Za účelem registrace EPIRBu COSPAS-SARSAT s naprogramovaným MMSI je třeba kontaktovat",
            "International Beacon Registration Database (IBRD)",
        ),
        (
            "65. Přesnost určení místa katastrofy z vysílání EPIRBu 406 MHz činí zhruba",
            "5 km",
        ),
        (
            "66. EPIRB 406 MHz se aktivuje manuálně nebo",
            "automaticky pomocí hydrostatické pojistky, když se loď potápí",
        ),
        (
            "67. Vysílání kompletní informace naprogramované v EPIRBu Cospas-Sarsat 406 MHz aktivovaného v případě tísně trvá",
            "0,5 sekundy a opakuje se po každých 50 sekundách",
        ),
        (
            "68. SART 9 GHz slouží k",
            "lokalizaci (finálnímu vyhledání) trosečníků na místě katastrofy",
        ),
        (
            "69. Jak může být zvětšen dosah transpondéru SART?",
            "SART by měl být umístěn co nejvýše a ve vertikální poloze",
        ),
        (
            "70. Tísňové volání DISTRESS ALERT vyslané omylem z EPIRBu v teritoriálních vodách zrušíme",
            "na kanálu 16 doporučenou radiotelefonní formulací “Cancel my distress alert of (time UTC)",
        ),
        ("71. Průkaz SRC opravňuje k obsluze zařízení pro kmitočty", "pouze VHF"),
        (
            "72. přeložte do češtiny (pište čitelně):",
            "At 0517 UTC in position 36 degrees 55 minutes 26 seconds north 11 degrees 38 minutes 15 seconds west - we have been in collision with an unknown drifting object, ship seriously damaged - stop - we are in actual danger - stop - urgently request assistance Odpověď:  V čase 05:17 UTC, na pozici 36 stupňů, 55 minut, 26 vteřin severní šířky a 11 stupňů, 38 minut, 15 vteřin západní délky jsme narazili na neznámý plovoucí objekt, loď vážně poškozena stop jsme ve vážném ohrožení stop naléhavě žádáme pomoc.",
        ),
        (
            "73. přeložte do češtiny (piště čitelně):",
            "At one five zero zero UTC in position five nautical miles exactly north of Cap Gris Nez Lighthouse - stop - crew member has fallen from mast and is badly injured stop - we need medical assistance Odpověď:  V čase 15:00 UTC na pozici 5 NM přesně na sever od majáku Cap Gris Nez stop člen posádky spadl ze stěžně a je vážně zraněn stop potřebujeme lékařskou pomoc.",
        ),
        (
            "74. přeložte do češtiny (piště čitelně):",
            "De North Foreland Radio:   at 2156 UTC at position 52.5 north 002.6 east - stop message from MS Aventicum/HBLI: nine pink painted containers reported overboard Odpověď:  Pobřežní stanice De North Foreland Radio: v čase 21:56 UTC na pozici 52,5 stupňů severní šířky a 2,6 stupňů východní délky stop zpráva z lodě MS Aventicum/HBLI: ohlášena ztráta (přes palubu) devíti kontejnerů růžové barvy.",
        ),
        (
            "75. přeložte do angličtiny (piště čitelně):",
            "V  12:50 UTC na pozici 51° 23` 15 `` N  002° 38` 25`` E, moje loď hoří, potřebuji okamžitou pomoc při hašení. Odpověď:  At one two five zero UTC in position 51 degrees 23 minutes 15 seconds north  002 degrees 38 minutes 25 seconds east, my ship is on fire, I need immediate fire- fighting assistance.",
        ),
        (
            "76. přeložte do angličtiny (piště čitelně):",
            "Na pozici 3 NM náměr 255º od jižního majáku ostrova Brijuni, stop, výbuch v motorovém prostoru stop moje loď je neovladatelná stop potřebuji odtáhnout. Odpověď:  In position three nautical miles, bearing two five five degrees from the southern lighthouse of Brijuni Island - stop an explosion in the engine room - stop - my ship is not under command  - stop - require a tow.",
        ),
        (
            "77. přeložte do angličtiny (piště čitelně):",
            "muž přes palubu, ztratili jsme člena posádky na pozici 06º 24,3' N 42º 36,7' W, čas 0450 UTC   stop   kurz 277 stupňů stop hledejte na oznámené pozici stop pečlivě pozorujte Odpověď:  Man Over Board, we have lost a crew member in position 06º 24,3' N 42º 36,7' W at 0450 UTC - stop - course 277 degrees -  stop - search on reported position - stop - keep sharp lookout.,",
        ),
        (
            "78. simplexní provoz je způsob provozu rádiové stanice, který",
            "umožňuje přenos zpráv na jednom rádiovém kanálu střídavě v obou směrech, např. pomocí ručního přepínání (příjem/vysílání), přičemž během vysílání zpráv není možný současný příjem zpráv",
        ),
        (
            "79. duplexní provoz je způsob provozu rádiové stanice, který",
            "umožňuje současný přenos zpráv oběma směry a vyžaduje současné využívání dvou kmitočtů",
        ),
    ],
    "c": [
        ("1. vodivost pevných látek je způsobena", "volnými elektrony v atomech látek"),
        (
            "2. provoz alternátoru bez připojení na akumulátor může způsobit",
            "zničení připojených zařízení",
        ),
        ("3. paralelně řazené akumulátory", "umožňují dodávat větší proud"),
        ("4. sériově řazené akumulátory", "se zapojují pro zvýšení dodávaného napětí"),
        ("5. jmenovité napětí článku olověného akumulátoru je", "2 V"),
        ("6. jmenovité napětí článku alkalického akumulátoru je", "1,2 V"),
        ("7. jmenovité napětí suchého galvanického článku je", "1,5 V"),
        ("8. suché galvanické články", "nelze dobíjet"),
        (
            "9. olověný akumulátor nabíjíme",
            "proudem (v A) o velikosti desetiny kapacity akumulátoru (v Ah)",
        ),
        ("10. k ochraně proti nadměrnému proudu slouží", "jistič"),
        (
            "11. antény dělíme podle směru vysílání nebo příjmu na",
            "směrové a všesměrové",
        ),
        ("12. všesměrová anténa má vyzařovací charakteristiku", "kruhovou"),
        (
            "13. všesměrová anténa musí přijímat nebo vysílat stejně všemi směry",
            "v horizontální rovině",
        ),
        (
            "14. půlvlnný dipól",
            "může být směrová i všesměrová anténa, záleží na jeho orientaci k zemskému povrchu",
        ),
        (
            "15. půlvlnný dipól umístěný rovnoběžně se zemským povrchem",
            "má v horizontální rovině osmičkovou vyzařovací charakteristiku",
        ),
        (
            "16. vztah mezi délkou vlny (λ) a kmitočtem (f), když c je rychlost světla, je",
            "f = c / λ",
        ),
        (
            "17. znakem F3E je označeno vysílání",
            "radiotelefonie s kmitočtovou modulací",
        ),
        (
            "18. který typ modulace mění kmitočet vysokofrekvenčního signálu v závislosti na přiváděném modulačním napětí",
            "kmitočtová modulace",
        ),
        (
            "19. rozsah ampérmetru se zvětšuje",
            "odporem paralelně zařazeným k ampérmetru (bočník)",
        ),
        (
            "20. ampérmetr a voltmetr se při měření zařazují",
            "ampérmetr do série se spotřebičem, voltmetr paralelně ke spotřebiči",
        ),
        (
            "21. v suchém, bezprašném prostředí považujeme za bezpečné napětí",
            "stejnosměrné do 60 V a střídavé do 25 V",
        ),
        (
            "22. při úrazu elektrickým proudem",
            "odstraníme postiženého z dosahu el. proudu, má-li nehmatný puls zahájíme masáž srdce a nedýchá-li, zavedeme umělé dýchání, zavoláme lékařskou pomoc.",
        ),
        (
            "23. funkce „SQUELCH“ VKV radiostanice je určena",
            "k potlačení slabších rušivých signálů včetně vlastního šumu přijímače.",
        ),
        ("24. Údaj elektrické napětí 2 V lze také zapsat", "2000 mV"),
        ("25. Kmitočet 406 MHz lze také zapsat", "0,406 GHz"),
        ("26. délka rádiové vlny v pásmu 160 MHz (VHF) je", "cca. 2 m"),
        ("27. Vztah mezi napětím (U), proudem (I) a odporem (R) je:", "U = R*I"),
        (
            "28. Vztah mezi výkonem (příkonem) (P), napětím (U) a proudem (I) je:",
            "P = U*I",
        ),
        ("29. Radiostanice odebírající z baterie 12 V proud 500 mA má příkon", "6 W"),
        ("30. Tři dobré vodiče elektřiny jsou", "měď, zlato, stříbro"),
        ("31. Čtyři dobré izolanty jsou", "sklo, vzduch, plast, porcelán"),
        (
            "32. Ke zdroji 10 V jsou připojeny dva odpory 10 Ω zapojené do série. Odebíraný příkon činí:",
            "5 W",
        ),
        (
            "33. Radiotechnická součástka je identifikována jako kondenzátor, pokud se její hodnota měří v",
            "pF",
        ),
    ],
}


if __name__ == "__main__":
    while True:
        print({key: f"{len(value)} questions" for key, value in QUESTIONS.items()})
        section = input(f"Which section ({', '.join(QUESTIONS.keys())})? ")
        if section not in QUESTIONS.keys():
            print(f"Only sections {', '.join(QUESTIONS.keys())} are allowed")
            sys.exit(1)

        for q_and_a in random.sample(QUESTIONS[section], k=len(QUESTIONS[section])):
            print(q_and_a[0])
            input("Enter...")
            print(q_and_a[1])
            print(80 * "-")

        print(
            f"You have finished all {len(QUESTIONS[section])} questions in section {section}. Congratulations!"
        )
