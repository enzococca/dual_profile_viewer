# Multi-Section Layout Feature

## ✅ Implemented Features

### 1. **Section Memory Storage**
The plugin now stores all created sections with their plots:
- `self.all_sections` - List containing all section data
- Each section stores:
  - `profile_data` - Complete profile information
  - `section_number` - Sequential section ID
  - `plot_html` - Plotly HTML (if using web view)
  - `plot_image` - PNG image path for layout

### 2. **Automatic Plot Generation**
When creating a layout:
- Generates plot images for ALL stored sections
- Each section gets its own PNG file
- Uses matplotlib to avoid Chrome/Kaleido issues

### 3. **Multi-Page Layout**
The layout generator now:
- Creates an overview page (Page 1) with current/last section
- Adds one page per section for detailed analysis
- Each page includes:
  - Section title (e.g., "SECTION 2 ANALYSIS")
  - Full 4-panel plot for that section
  - Section metadata (DEM name, samples, offset)

## 📋 How It Works

### Drawing Multiple Sections:
```
1. Draw first section → Create profiles
2. Draw second section → Create profiles
3. Draw third section → Create profiles
...
Each section is automatically stored in memory
```

### Creating Layout:
```
1. Click 🖨️ Generate Layout
2. Plugin automatically:
   - Generates plots for ALL sections
   - Creates multi-page layout
   - Page 1: Overview with map and latest section
   - Page 2+: One page per section with plots
```

## 🎯 Layout Structure

### Page 1 - Overview:
- Title and metadata
- Location map showing all sections
- Current/latest section plots
- 3D view (if available)
- Statistics table
- Scale bar, north arrow, legend

### Page 2+ - Section Details:
- Section title (e.g., "SECTION 1 ANALYSIS")
- 4-panel plot specific to that section:
  - Overlapped profiles
  - Elevation differences
  - Profile A-A'
  - Profile B-B'
- Section information:
  - Section ID
  - DEM used
  - Number of samples
  - Offset distance

## 💡 Usage Example

1. **Create Multiple Sections:**
   - Draw and create 3 different profile sections
   - Each automatically stored in memory

2. **Generate Layout:**
   - Click 🖨️ Generate Layout
   - Message shows: "Layout created with 3 section(s) across 3 page(s)"

3. **Result:**
   - Page 1: Overview with map and section 3
   - Page 2: Detailed plots for section 1
   - Page 3: Detailed plots for section 2
   - Page 4: Detailed plots for section 3

## 🔧 Technical Details

### Storage Implementation:
```python
# Each section stored as:
section_data = {
    'profile_data': {...},      # Complete profile data
    'section_number': 1,        # Sequential ID
    'plot_html': '<html>...',   # Plotly HTML
    'plot_image': '/tmp/plot.png'  # Generated PNG
}
```

### Clear Function:
The Clear button (🗑️) now also:
- Clears `all_sections` list
- Resets `section_count` to 0
- Removes all stored plots

## Notes:
- Sections persist until Clear is clicked
- Each section's plots are generated at 300 DPI
- Layout automatically adapts to number of sections
- All sections use the same DEM settings as when created