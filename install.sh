#!/bin/bash
echo "=== DeckForge Installer ==="
echo "Installing dependencies..."

# Enable flatpak if needed
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

# Install OpenRGB
flatpak install -y flathub org.openrgb.OpenRGB 2>/dev/null || echo "OpenRGB already installed"

# Install OpenRGB udev rules
curl -fsSL https://openrgb.org/releases/release_0.9/openrgb-udev-install.sh | sudo bash

# Install Python deps
pip install PySide6 openrgb-python pillow numpy --break-system-packages

# Install scrot
sudo sed -i 's/^SigLevel.*/SigLevel = Never/' /etc/pacman.conf
sudo pacman -S --noconfirm scrot ffmpeg
sudo sed -i 's/^SigLevel.*/SigLevel = Required DatabaseOptional/' /etc/pacman.conf

# Clone DeckForge
mkdir -p ~/DeckForge
curl -fsSL https://raw.githubusercontent.com/DeckForge1/DeckForge/main/main.py -o ~/DeckForge/main.py

# Desktop shortcut
cat > ~/.local/share/applications/deckforge.desktop << 'DESK'
[Desktop Entry]
Name=DeckForge
GenericName=Steam Deck Optimizer
Exec=bash -c "flatpak run org.openrgb.OpenRGB & sleep 6 && python3 /home/deck/DeckForge/main.py"
Icon=preferences-desktop
Terminal=false
Type=Application
Categories=Utility;System;
Keywords=rgb;performance;steamdeck;
DESK

# Autostart OpenRGB
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/openrgb.desktop << 'AUTO'
[Desktop Entry]
Name=OpenRGB
Exec=bash -c "flatpak run org.openrgb.OpenRGB & sleep 8 && flatpak run org.openrgb.OpenRGB --device 0 --mode Direct && flatpak run org.openrgb.OpenRGB --device 1 --mode Direct"
Type=Application
X-KDE-autostart-phase=1
AUTO

echo ""
echo "=== Done! Run with: python3 ~/DeckForge/main.py ==="
echo "Or find DeckForge in your app menu."
