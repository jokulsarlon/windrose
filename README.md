# WindRose - Wind Rose Generator for QGIS

**WindRose** is a QGIS plugin that generates wind rose diagrams from point locations using the [Open-Meteo](https://open-meteo.com/) historical weather API. It supports interactive point selection, manual coordinate input, monthly data filtering, multiple visual styles, and SVG export.

## Features

- **Point Input Options**:
  - Click on the map to select a point (automatically converted to WGS84).
  - Manually enter longitude/latitude.
- **Data Parameters**:
  - Select year (2000–2100).
  - Choose month (or full year).
  - Wind height: 10m, 80m, 120m, 180m (as supported by Open-Meteo).
- **Visual Styles**:
  - Predefined color schemes: Default, Warm, Cold.
  - Graph styles: Sector-based (filled sectors) or Concentric-circles (adds circular reference lines).
  - Sector faces are automatically categorized by parity (white for even, black for odd) with black outlines.
- **Output**:
  - Generate layers directly in QGIS (point, frequency table, sector polygons, outline, coordinate lines, optional circles).
  - Export the combination of sector faces, outline, and coordinate lines as an SVG file.
- **Multi‑point & Multi‑time**:
  - Each generated rose gets a unique group name (e.g., `WindRose-2024-03-51.5258_-0.1576`) to avoid overwriting previous results.

## Requirements

- **QGIS** ≥ 3.28 (LTR recommended)
- Python packages: `requests`, `numpy` (both are usually already present in QGIS; if not, install via OSGeo4W Shell).

## Installation

### From GitHub (manual)
1. Download the latest release or clone the repository.
2. Copy the `WindRose` folder into your QGIS plugin directory:
   - **Windows**: `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS and enable the plugin via `Plugins` → `Manage and Install Plugins`.

### Using QGIS Plugin Manager (future)
Once the plugin is accepted into the official repository, it will be available directly from the Plugin Manager.

## Usage

1. Click the **WindRose** toolbar button to open the dialog.
2. Choose a point:
   - Click **Map Pick** and then click on the map.
   - Or click **Manual Input** and enter coordinates.
3. Set the data parameters: year, month (or full year), and wind height.
4. Customize the output style:
   - Color scheme, graph style, and opacity.
   - Check **Add to QGIS project** to create layers.
   - Check **Export SVG** and specify a file path to save a vector graphic.
5. Click **Generate**. A new group with all rose layers will appear in the Layers panel.

The SVG export includes the sector faces, the closed outline, and the coordinate lines, rendered on a white background.

## License

This plugin is released under the **GNU General Public License v3.0** or later. See the [LICENSE](LICENSE) file for details.

## Credits

- Weather data provided by [Open-Meteo.com](https://open-meteo.com)
- Developed by [Your Name/Organization]

## Contributing

Bug reports, feature requests, and pull requests are welcome via [GitHub Issues](../../issues).
