# pprint

### setup

pip install pyyaml


### modules

pprint:
- update
- ticket:
  - postscript - moving in
  - bitmap - to move in
  - PDF - todo
- payment - to move in
- fiscal - to move in
- feedback - to move in


## PLP faili struktuur

PLP fail on viis, kuidas edastada BOst pileteid müüvasse arvutisse piletite infot ja fiskaalinfot. 
Pileti müümine BOs tähendab PLP faili genereerimist ja selle allalaadimise protseduuri käivitamist. 

### Struktuur

- ‘Üldinfo’
  - PLP versioon e info struktuuri versioon (semantiline versioneerimine)
  - Feedbacki info: token, url ja operation token
  - Printimise Draiveri enda ja tema update’i info: draiveri versiooni nimi ja allalaadimise url. 
  - Tehingu info: müügipunkti info ja tehingu aeg.
- Piletite info
  - Piletiprinteri info juhuks, kui printerit pole kirjeldatud iga pileti juures eraldi. 
  - Piletid
    - Pilet 1
      - Layout
      - Printer
      - Müügi aeg
      - Kõik piletile trükitavad muutujad
    - Pilet 2
    - jne
- Fiskaalinfo
  - Üldinfo: operatsioon (müük, tagasiost jne), tehingu number, kaardimakse seaded.
  - Fiskaalprinteri info
  - Makse info
    - Makse tüüp (sularaha, kaardimakse, kinkepilet, vms) ja kogusumma
      - Makse komponendid antud tüübiga: Komponent 1: hulk, tk hind, nimi, jne
      - Komponent 2
      - jne
    - Makse tüüp
      - Makse komponendid antud tüübiga
      - jne
