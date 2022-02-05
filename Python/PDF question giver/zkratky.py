import random
import re

abbrevs = """
GMT - Greenwich mean time - čas na nultém poledníku
UTC - universal coordinated time - téměř totožné s GMT, čas je však referencován na atomové hodiny
LT - local time
CET - Central Europe Time / středoevropský (zimní) čas
UT - universal time - určený z rotace země, předchůdce GMT
ETD - Estimated Time of Departure
ETA - estimated time of arrival
GMDSS - Global Maritime Distress and Safety System / Globální námořní tisňový a bezpečnostní systém, systém bezpečnostních postupů, zařízení a komunikačních protokolů, používaných ke zvýšení bezpečnosti a usnadňují záchranu (lodě, čluny a letadla)
SAR - Search And Rescue - systém hledání a poskytování pomoci lidem, kteří jsou v nouzi nebo bezprostředním nebezpečí
PLB - Personal Locator Beacons - osobní lokalizační bóje je určena pro osobní potřebu a označuje osobu v nouzi
EPIRB - Emergency Position-Indicating Radio Beacon station - rádiová bóje označující místo aktivace
SOLAS - Úmluva o bezpečnosti lidského života na moři (International Convention for the Safety of Life at Sea) - 1974
NAVTEX - Navigational TelEX / navigační textové zprávy - systém pro přenos textových varovných, meteorologických a navigačních zpráv
SART - Search And Rescue Transponder - tísňový radarový odpovídač pro účely pátrání a záchrany
AIS - Automatic Identification System - automatický sledovací systém, který se používá v lodní dopravě
ITU - Mezinárodní telekomunikační unie (International Telecommunication Union) - specializovaná organizací Organizace spojených národů pro oblast telekomunikací
MPO - Ministerstvo průmyslu a obchodu - zajištění přidělení kmitočtových pásem
CEPT - Mezinárodní organizace - Evropská konference poštovních a telekomunikačních správ (Conférence européenne des administrations des postes et des télécommunications)
ATIS - Automatic Transmitter Identification System - identifikační kód automatického systému pro identifikaci rádiových stanic na vodních cestách, který se vyšle automaticky na vysílacím kanálu po uvolnění vysílacího tlačítka
""".strip()

all_abrevs = re.findall(r"^(\w+)\s+-\s+(.*)?$", abbrevs, flags=re.MULTILINE)
random.shuffle(all_abrevs)
for abbr, expl in all_abrevs:
    print(abbr)
    input("Enter...")
    print(expl)
    print(80 * "-")
