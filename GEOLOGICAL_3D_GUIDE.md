# Guida Visualizzazione Geologica 3D

## Nuove Funzionalità

### 1. Visualizzazione Sezioni Geologiche
Ora quando clicchi sul pulsante "🎲 3D", ti viene chiesto di scegliere tra:
- **Standard 3D View**: Vista 3D classica con linee
- **Geological Section View**: Vista geologica con muri e strati

### 2. Caratteristiche della Vista Geologica

#### Muri 3D
- Le due linee parallele (A-A' e B-B') formano un muro 3D
- Il muro ha spessore regolabile con lo slider "Wall Thickness"
- Rappresenta una vera sezione geologica/archeologica

#### Strati Stratigrafici
- Se hai selezionato più DEM, vengono visualizzati come strati diversi
- Ogni strato ha un colore diverso
- Puoi attivare/disattivare con "Show Stratigraphic Layers"

#### Intersezioni
- Se crei più sezioni che si incrociano (es. muri perpendicolari)
- Le intersezioni vengono evidenziate in rosso
- Mostra esattamente come i muri si intersecano nello spazio 3D

#### Piano di Riferimento
- Puoi aggiungere un piano orizzontale di riferimento
- Regolabile in elevazione (utile per livelli archeologici)
- Opacità regolabile

### 3. Controlli Disponibili

**Section Controls:**
- Wall Thickness: Spessore del muro (1-100m)
- Vertical Scale: Esagerazione verticale (1.0x - 5.0x)
- Show Stratigraphic Layers: Mostra/nascondi strati
- Show Intersections: Mostra/nascondi intersezioni

**Reference Plane:**
- Elevation: Altezza del piano di riferimento
- Opacity: Trasparenza del piano
- Show Reference Plane: Mostra/nascondi piano

**Layer Attributes:**
- Puoi aggiungere attributi e note per ogni strato
- Assegnare nomi significativi (es. "Strato Romano", "Riempimento medievale")
- Scegliere colori personalizzati per ogni strato

### 4. Workflow Esempio

1. **Disegna le sezioni** nel viewer principale
2. **Seleziona più DEM** se vuoi vedere differenze stratigrafiche
3. **Crea i profili** con il pulsante Create
4. **Apri il 3D** e scegli "Geological Section View"
5. **Regola i parametri**:
   - Spessore muro per la tua scala
   - Esagerazione verticale per evidenziare le differenze
6. **Aggiungi attributi** agli strati identificati
7. **Esporta** il modello 3D in STL/OBJ/VTK

### 5. Applicazioni

- **Archeologia**: Visualizzare sezioni di scavo, muri, stratigrafie
- **Geologia**: Sezioni geologiche, faglie, strati
- **Ingegneria**: Sezioni di terreno per costruzioni
- **Ambientale**: Variazioni del terreno nel tempo (con DEM multi-temporali)

### 6. Tips

- Per muri che si intersecano, disegna le sezioni in modo che si incrocino sulla mappa
- Usa DEM di epoche diverse per vedere l'evoluzione del terreno
- Il piano di riferimento è utile per marcare quote specifiche
- Esporta in STL per stampa 3D delle sezioni

## Risoluzione Problemi

**Non vedo gli strati:**
- Assicurati di aver selezionato più DEM nella tab "DEMs"
- Attiva "Show Stratigraphic Layers"

**Le intersezioni non appaiono:**
- Le sezioni devono effettivamente incrociarsi nello spazio 3D
- Attiva "Show Intersections"

**Il 3D è troppo schiacciato/esagerato:**
- Regola "Vertical Scale" per la giusta proporzione