# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 提供操作本代码库的指导。

## 项目概述

KRunner Edge Helper 是一个 KDE Plasma KRunner 插件，通过 DBus 实现 Microsoft Edge 书签搜索。使用 Python 3 编写，提供多层级文本匹配、拼音匹配和使用历史排序功能。

## 开发命令

### 安装依赖
```bash
pip3 install --user -r requirements.txt
```

### 运行测试
```bash
# 运行所有测试
python3 tests/test_history.py
python3 tests/test_search.py
python3 tests/test.py

# 运行单个测试文件
python3 tests/test_history.py
```

### 安装 / 卸载
```bash
bash install.sh      # 安装插件到 ~/.local/share/krunner/dbusplugins/
bash uninstall.sh    # 移除所有已安装文件
bash restart_plugin.sh  # 代码修改后重启插件
```

### 调试
```bash
# 查看日志
cat /tmp/krunner_edge_helper.log

# 检查插件是否运行
ps aux | grep krunner_edge_helper

# 手动测试 DBus 接口
dbus-send --session --print-reply --dest=org.kde.krunner.edgehelper /EdgeHelper org.kde.krunner1.Match string:"b test"

# 重启 KRunner (KDE6)
kquitapp6 krunner
# 或 KDE5
kquitapp5 krunner
```

## 架构

### KDE Plasma 6 DBus 插件结构

插件使用 KDE 的 DBus runner 接口：
- **服务名**: `org.kde.krunner.edgehelper`
- **对象路径**: `/EdgeHelper`
- **接口**: `org.kde.krunner1`

安装结构（KDE Plasma 6 要求）：
```
~/.local/share/krunner/dbusplugins/
├── krunner-edge-helper.desktop    # 必须在根目录，不能在子目录
└── krunner-edge-helper/           # 源代码放在子目录
    ├── krunner_edge_helper.py
    └── ...

~/.local/share/dbus-1/services/
└── org.kde.krunner.edgehelper.service
```

### 核心组件

**krunner_edge_helper.py**: DBus 服务，实现 `Match()` 和 `Run()` 方法。加载书签并以 KRunner 格式返回匹配结果。

**search_engine.py**: 多关键词搜索，使用 AND 逻辑。匹配层级：精确匹配 → 单词边界 → 前缀 → 拼音 → 子串。与 history_manager 集成以排序结果。

**bookmark_parser.py**: 递归解析 Chromium 书签 JSON 格式。返回 Bookmark 命名元组列表（name, url, folder）。

**pinyin_matcher.py**: 使用 pypinyin 支持中文拼音。支持全拼和首字母（如 "lsx" 匹配 "流水线"）。

**history_manager.py**: 跟踪每个查询的用户选择。使用频率因子（对数尺度）和时间衰减（30天半衰期）计算权重。数据存储在 `history.json` 中。

### 数据流

```
KRunner Match() 调用
    ↓
解析查询（移除触发词 "b "）
    ↓
如果文件修改则重新加载书签
    ↓
SearchEngine.search() → 按关键词过滤 → 评分匹配
    ↓
应用历史奖励权重
    ↓
返回格式化匹配结果给 KRunner
```

### 关键配置 (config.py)

- `TRIGGER_KEYWORD = "b"`: 激活插件的前缀
- `DEFAULT_BOOKMARK_PATH`: Edge 书签文件位置
- `MAX_RESULTS = 10`: 返回给 KRunner 的结果数
- `FUZZY_THRESHOLD = 60`: 最低匹配分数
- `HISTORY_*`: 历史功能设置

## 开发注意事项

**Python 缓存问题**: 代码修改后，务必运行 `restart_plugin.sh` 清除 `__pycache__` 并重启进程。运行中的进程使用缓存的字节码。

**多实例问题**: 如果插件行为异常，用 `ps aux | grep krunner_edge_helper` 检查是否有多个进程，重启前全部终止。

**DBus 调试**: 如果插件未在 KRunner 中显示，检查：
1. 进程正在运行
2. DBus 服务文件存在且路径正确
3. Desktop 文件在 `dbusplugins/` 根目录（不在子目录）
4. 运行 `restart_plugin.sh` 测试 DBus 连通性

**添加功能**: `search_engine.py` 中的搜索层级使用显式布尔标志。分数为 0-100 的整数。历史奖励（最高20分）在文本匹配后添加。
