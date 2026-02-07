# Changelog

## v1.0.0 - Initial Release

### Features
- ✅ Edge bookmark parser for Chromium JSON format
- ✅ Fuzzy search with rapidfuzz
- ✅ Chinese pinyin matching (full pinyin + initials)
- ✅ KDE Plasma 6 KRunner integration via DBus
- ✅ Configurable trigger keyword (default: "b")
- ✅ Automatic bookmark file monitoring and reload
- ✅ Support for Flatpak Edge bookmarks

### Technical Details
- DBus interface: org.kde.krunner1
- Match signature: a(sssida{sv})
- Async callback-based result delivery
- 767 bookmarks indexed

### Installation
Run `./install.sh` to install the plugin.

### Usage
1. Press Alt+Space or Alt+F2 to open KRunner
2. Type: `b <search term>`
3. Select bookmark from results
4. Press Enter to open in Edge browser

### Known Issues
None

