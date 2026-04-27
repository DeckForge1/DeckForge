# DeckForge

**Desktop Mode, Unleashed.**

DeckForge is a Steam Deck desktop optimizer built with PySide6.

## Features
- Performance Tuning — CPU governor, swappiness, GPU profile
- RGB Control — Full OpenRGB integration
- ChromaSync — Screen-reactive RGB at ~24fps via ffmpeg pipe
- Process Manager — Kill KDE bloat to free RAM
- Profiles — Performance / Balanced / Battery Saver presets

## Requirements
- Steam Deck SteamOS Desktop Mode
- OpenRGB Flatpak: flatpak install org.openrgb.OpenRGB
- pip install PySide6 openrgb-python pillow numpy --break-system-packages

## Install
git clone https://github.com/YOURUSERNAME/DeckForge
cd DeckForge
python3 main.py

## Tested Devices
- Logitech G502 HERO
- Razer BlackWidow Chroma Tournament Edition

## License
MIT
