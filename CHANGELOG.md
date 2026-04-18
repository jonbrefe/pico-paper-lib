# Changelog

All notable changes to this project will be documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] — 2026-04-18

### Added

- `Display` class — mono (1-bit) canvas with full and partial refresh
- `Display4Gray` class — 4-grayscale canvas (black, dark gray, light gray, white)
- Landscape (296×128, default) and portrait (128×296) orientation support
- Drawing primitives: lines, rectangles, rounded rectangles, circles, ellipses, triangles, polygons
- Line styles: solid, dashed, dotted, thick
- Text rendering with two built-in fonts: 5×7 (`font_small`) and 8×8 (`font_medium`)
- Text alignment: left, center, right, text-in-rect, word-wrap
- Spanish character support (Á, É, Í, Ó, Ú, Ñ, ü)
- UI widgets: bordered panel, progress bar, table, badge, divider
- Column-major and row-major bitmap icon rendering
- Deep sleep / wake power management
- `mip` package manifest for easy installation over WiFi
- SSD1680 technical reference documentation
- Examples: hello_world, dashboard, fonts_demo, grayscale_demo
