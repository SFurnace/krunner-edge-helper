# KDE KRunner Edge Bookmarks Plugin

一个用于 KDE Plasma 的 KRunner 插件，可以快速搜索和打开 Microsoft Edge 浏览器书签。

A KDE KRunner plugin for quickly searching and opening Microsoft Edge browser bookmarks.

## ✨ Features | 特性

- 🔍 **Fuzzy Search** | 模糊搜索 - Find bookmarks with partial matches
- 🇨🇳 **Chinese Pinyin Support** | 中文拼音支持 - Search Chinese bookmarks using pinyin
  - Full pinyin: `b zhongguo` → finds "中国"
  - Pinyin initials: `b zg` → finds "中国"
- ⚡ **Fast Performance** | 高性能 - Cached bookmarks with auto-reload
- 🎯 **Smart Ranking** | 智能排序 - Results ranked by relevance
- 🌐 **Edge Integration** | Edge 集成 - Works with Edge Flatpak and system installations

## 📋 Requirements | 系统要求

- KDE Plasma 5.12+
- Python 3.6+
- Microsoft Edge browser
- pip3 (Python package manager)

## 🚀 Installation | 安装

### Quick Install | 快速安装

```bash
cd krunner-edge-helper
./install.sh
```

The installation script will:
1. Install Python dependencies
2. Copy plugin files to `~/.local/share/krunner/dbusplugins/`
3. Install desktop file to `~/.local/share/kservices5/`
4. Restart KRunner

### Manual Install | 手动安装

```bash
# Install dependencies
pip3 install --user -r requirements.txt

# Create directories
mkdir -p ~/.local/share/krunner/dbusplugins
mkdir -p ~/.local/share/kservices5

# Copy files
cp edge_bookmarks_runner.py bookmark_parser.py search_engine.py \
   pinyin_matcher.py config.py ~/.local/share/krunner/dbusplugins/

cp plasma-runner-edge-bookmarks.desktop ~/.local/share/kservices5/

# Make executable
chmod +x ~/.local/share/krunner/dbusplugins/edge_bookmarks_runner.py

# Restart KRunner
kquitapp5 krunner
```

## 📖 Usage | 使用方法

1. Open KRunner: `Alt+Space` or `Alt+F2`
2. Type `b` followed by your search query
3. Select a bookmark from the results
4. Press `Enter` to open

### Examples | 示例

```
b github          # Search for "github"
b 中国            # Search for Chinese text
b zhongguo        # Search using full pinyin
b zg              # Search using pinyin initials
b python doc      # Fuzzy search
```

## ⚙️ Configuration | 配置

Edit `~/.local/share/krunner/dbusplugins/config.py` to customize:

```python
# Bookmark file location
DEFAULT_BOOKMARK_PATH = "~/.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Bookmarks"

# Trigger keyword (change from 'b' to your preference)
TRIGGER_KEYWORD = "b"

# Maximum number of results
MAX_RESULTS = 10

# Minimum fuzzy match score (0-100)
FUZZY_THRESHOLD = 60
```

### Finding Your Bookmark File | 查找书签文件

**Flatpak Edge:**
```bash
~/.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Bookmarks
```

**System Edge:**
```bash
~/.config/microsoft-edge/Default/Bookmarks
```

**Multiple Profiles:**
```bash
~/.config/microsoft-edge/Profile 1/Bookmarks
~/.config/microsoft-edge/Profile 2/Bookmarks
```

## 🔧 Troubleshooting | 故障排除

### Plugin not appearing in KRunner

```bash
# Check if desktop file is installed
ls ~/.local/share/kservices5/plasma-runner-edge-bookmarks.desktop

# Check if plugin files exist
ls ~/.local/share/krunner/dbusplugins/edge_bookmarks_runner.py

# Restart KRunner
kquitapp5 krunner
killall krunner
```

### No bookmarks found

```bash
# Verify bookmark file exists
ls -la ~/.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Bookmarks

# Check file permissions
chmod 644 ~/.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Bookmarks

# Test manually
python3 ~/.local/share/krunner/dbusplugins/edge_bookmarks_runner.py
```

### View logs

```bash
# Watch plugin logs
journalctl --user -f | grep edge_bookmarks

# Or check KRunner output
krunner --replace 2>&1 | grep -i edge
```

### Dependencies issues

```bash
# Reinstall dependencies
pip3 install --user --force-reinstall -r requirements.txt

# Check installed packages
pip3 list | grep -E "pypinyin|rapidfuzz|dbus-python|PyQt5"
```

## 🗑️ Uninstallation | 卸载

```bash
# Remove plugin files
rm -rf ~/.local/share/krunner/dbusplugins/edge_bookmarks_runner.py
rm -f ~/.local/share/krunner/dbusplugins/{bookmark_parser,search_engine,pinyin_matcher,config}.py

# Remove desktop file
rm -f ~/.local/share/kservices5/plasma-runner-edge-bookmarks.desktop

# Restart KRunner
kquitapp5 krunner
```

## 📝 Architecture | 架构

```
┌─────────────────┐
│    KRunner      │
└────────┬────────┘
         │ DBus
┌────────▼─────────────────────┐
│  edge_bookmarks_runner.py    │
│  (DBus Service)               │
└──┬──────────────┬────────────┘
   │              │
   ▼              ▼
┌──────────┐   ┌──────────────┐
│ bookmark │   │    search    │
│  parser  │   │    engine    │
└──────────┘   └──────┬───────┘
                      │
                      ▼
               ┌──────────────┐
               │   pinyin     │
               │   matcher    │
               └──────────────┘
```

## 🤝 Contributing | 贡献

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License | 许可证

MIT License - Feel free to use and modify

## 🙏 Acknowledgments | 致谢

- Built with [pypinyin](https://github.com/mozillazg/python-pinyin) for Chinese pinyin support
- Uses [RapidFuzz](https://github.com/maxbachmann/RapidFuzz) for fast fuzzy matching
- Inspired by the KDE KRunner plugin ecosystem

## 📮 Support | 支持

If you encounter any issues, please:
1. Check the troubleshooting section above
2. Review the logs: `journalctl --user -f | grep edge_bookmarks`
3. Test manually: `python3 ~/.local/share/krunner/dbusplugins/edge_bookmarks_runner.py`

---

**Enjoy快速搜索！Happy Searching! 🚀**
