# Checklist Nuove Funzionalità

## 1. Toolbar Principale (compact_dual_profile_viewer.py)

### Pulsanti che dovresti vedere:
- [✓] 📏 Draw Lines - Disegno linee normali
- [✓] ⬜ Draw Polygon - **NUOVO** - Disegno poligoni con larghezza
- [✓] 📊 Create - Crea profili
- [✓] ➕ Add to Layer - Aggiunge al layer
- [✓] 🎲 3D - Apre visualizzatore 3D
- [✓] 💾 Export - Esporta dati
- [✓] 🗑️ Clear - Pulisce tutto
- [✓] ❓ Help - Aiuto
- [✓] 🖨️ Generate Layout - **NUOVO** - Genera layout professionale

## 2. Quando clicchi "🎲 3D"

### Dovresti vedere solo 2 opzioni:
- [✓] Geological Section View (PyVista)
- [✓] Geological Section View (Plotly)
- [✗] ~~Standard 3D View~~ - **RIMOSSO**

## 3. Nel Geological Section View (PyVista)

### Pannelli sulla destra:
1. **Section Controls**
   - Wall Thickness - Spessore muro
   - Vertical Scale - Scala verticale
   - Show Stratigraphic Layers - Mostra strati
   - Show Intersections - Mostra intersezioni

2. **Reference Plane**
   - Elevation - Altezza piano
   - Opacity - Opacità
   - Show Reference Plane - Mostra/nascondi

3. **Import Sections** - **NUOVO**
   - Section Layer dropdown
   - Refresh Layers button
   - Import Selected Layer button

4. **Section Attributes**
   - Tabella per attributi
   - Add Attribute button

5. **View Controls**
   - Top, Front, Side, 3D buttons

## 4. Quando clicchi "⬜ Draw Polygon" - **NUOVO**

### Dovresti vedere:
1. Dialog per scegliere modalità:
   - Rectangle
   - Polygon  
   - Freehand

2. Dialog per inserire larghezza in metri

3. Poi disegni sulla mappa:
   - Rectangle: 2 click
   - Polygon: click multipli + tasto destro
   - Freehand: trascinamento

## 5. Quando clicchi "➕ Add to Layer" con Multi-DEM

### Comportamento:
- **Prima**: Creava solo "Profile_Sections"
- **Ora**: Crea layer separati per ogni DEM:
  - Sections_DEM1
  - Sections_DEM2
  - etc.
- Raggruppa in "Profile_Sections_N"

## 6. Layer delle Sezioni

### Campi del layer:
- id
- label
- type
- section_group - **NUOVO**
- dem_name - **NUOVO**
- notes - **NUOVO**
- elevation_min - **NUOVO** (solo multi-DEM)
- elevation_max - **NUOVO** (solo multi-DEM)

### Colori:
- Rosso trasparente (alpha=180) per A-A'
- Blu trasparente (alpha=180) per B-B'

## 7. Layout Generator - **NUOVO**

Quando clicchi "🖨️ Generate Layout":
- Crea layout A3 landscape
- Include:
  - Mappa con sezioni
  - Grafici profili
  - Vista 3D (se disponibile)
  - Tabella statistiche
  - Scala, Nord, Legenda
  - Metadati progetto

## Problemi da Verificare:

1. **Import error risolto** - QgsRubberBand ora importato da qgis.gui ✓

2. **Se non vedi le nuove funzioni**:
   - Ricarica il plugin
   - Riavvia QGIS
   - Verifica nel log se ci sono altri errori

3. **Per il layout generator**:
   - L'errore Kaleido è gestito con fallback
   - Dovrebbe usare matplotlib se Plotly non funziona

## Come Testare:

1. **Test Poligoni**:
   ```
   Click ⬜ Draw Polygon
   → Scegli Rectangle
   → Inserisci 20m larghezza
   → Disegna rettangolo sulla mappa
   ```

2. **Test Import Sezioni**:
   ```
   Crea sezioni con Add to Layer
   → Apri 3D Geological View
   → Nel pannello Import Sections
   → Click Refresh Layers
   → Seleziona il layer
   → Click Import
   ```

3. **Test Multi-DEM**:
   ```
   Seleziona più DEM nella tab DEMs
   → Disegna sezioni
   → Click Add to Layer
   → Verifica che crei layer separati
   ```

Se qualcosa non funziona, controlla il QGIS Log Panel per errori specifici.