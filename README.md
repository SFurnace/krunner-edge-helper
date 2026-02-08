# KRunner Edge Helper

> 一个用于在 KDE Plasma 的 KRunner 中搜索 Microsoft Edge 书签的插件

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-green)](https://www.python.org/)

## ✨ 特性

- 🔍 **多关键词搜索** - 支持空格分隔的多个关键词，所有关键词必须匹配 (AND 逻辑)
- 🇨🇳 **拼音搜索** - 支持中文拼音全拼和首字母搜索（如 `lsx` → `流水线`）
- ⚡ **智能匹配** - 分层匹配算法：精确 → 单词边界 → 前缀 → 拼音 → 子串
- 📁 **文件夹搜索** - 同时搜索书签标题和所属文件夹名称
- 🎯 **精确排序** - 按匹配质量智能排序结果
- 🚀 **零冲突** - 独立子目录安装，不与其他插件冲突

## 🚀 快速开始

```bash
git clone https://github.com/yourusername/krunner-edge-helper.git
cd krunner-edge-helper
bash install.sh
```

使用：
1. 按 `Alt+Space` 打开 KRunner
2. 输入 `b github` 搜索书签
3. 按 `Enter` 打开选中的书签

## 📚 搜索示例

```bash
b github              # 搜索包含 "github" 的书签
b eo cls              # 同时包含 "eo" 和 "cls" (AND逻辑)
b lsx                 # 拼音首字母搜索 "流水线"
b edge 文档            # 混合中英文搜索
```

## ⚙️ 配置

编辑 `~/.local/share/krunner/dbusplugins/krunner-edge-helper/config.py`：

```python
# 书签文件路径
DEFAULT_BOOKMARK_PATH = "~/.var/app/com.microsoft.Edge/config/microsoft-edge/Default/Bookmarks"

# 触发关键词
TRIGGER_KEYWORD = "b"

# 最大结果数
MAX_RESULTS = 10
```

## 🔧 管理

```bash
bash restart_plugin.sh    # 重启插件
bash uninstall.sh         # 卸载插件
cat /tmp/krunner_edge_helper.log  # 查看日志
```

## 📁 项目结构

```
krunner-edge-helper/
├── src/                          # 源代码
│   ├── krunner_edge_helper.py    # DBus服务主体
│   ├── bookmark_parser.py        # 书签解析器
│   ├── search_engine.py          # 搜索引擎
│   ├── pinyin_matcher.py         # 拼音匹配
│   └── config.py                 # 配置文件
├── service/                      # 服务配置
│   ├── org.kde.krunner.edgehelper.service
│   └── krunner-edge-helper.desktop
├── docs/                         # 文档
│   ├── ARCHITECTURE.md           # 架构说明
│   └── SEARCH_ALGORITHM.md       # 搜索算法
├── install.sh                    # 安装脚本
├── uninstall.sh                  # 卸载脚本
└── restart_plugin.sh             # 重启脚本
```

## 🛠️ 故障排除

### 插件未显示

```bash
ps aux | grep krunner_edge_helper  # 检查进程
bash restart_plugin.sh             # 重启插件
kquitapp5 krunner                  # 重启KRunner (KDE5)
kquitapp6 krunner                  # 重启KRunner (KDE6)
```

### 搜索无结果

1. 检查书签文件路径是否正确
2. 确认 Edge 已经保存过书签
3. 查看日志：`cat /tmp/krunner_edge_helper.log`

### 代码更新后结果不变

```bash
bash uninstall.sh  # 完全卸载
bash install.sh    # 重新安装
```

## 📚 详细文档

- [架构文档](docs/ARCHITECTURE.md) - DBus服务、目录结构、命名规范
- [搜索算法](docs/SEARCH_ALGORITHM.md) - 匹配层级、评分规则

## 📄 许可证

MIT License

## 🙏 致谢

- [KDE Plasma](https://kde.org/plasma-desktop/) - KRunner 框架
- [pypinyin](https://github.com/mozillazg/python-pinyin) - 拼音转换
- [rapidfuzz](https://github.com/maxbachmann/RapidFuzz) - 模糊匹配
