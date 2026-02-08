# KRunner Edge Helper 架构文档

## 📐 项目结构

遵循最佳实践的清晰目录结构：

```
krunner-edge-helper/
├── src/                          # 源代码目录
│   ├── krunner_edge_helper.py    # 主入口 (DBus 服务)
│   ├── bookmark_parser.py        # 书签解析器
│   ├── search_engine.py          # 搜索引擎
│   ├── pinyin_matcher.py         # 拼音匹配器
│   └── config.py                 # 配置文件
├── service/                      # 服务配置文件
│   ├── org.kde.krunner.edgehelper.service    # DBus 服务定义
│   └── krunner-edge-helper.desktop           # KRunner 插件描述
├── docs/                         # 文档目录
├── tests/                        # 测试目录
├── install.sh                    # 安装脚本
├── uninstall.sh                  # 卸载脚本
├── restart_plugin.sh             # 重启脚本
├── requirements.txt              # Python 依赖
└── README.md
```

## 📦 安装后目录结构

插件安装结构（KDE Plasma 6）：

```
~/.local/share/krunner/dbusplugins/
├── krunner-edge-helper.desktop   # ✅ Desktop 文件在 dbusplugins 根目录（KDE 6 要求）
└── krunner-edge-helper/          # ✅ 源码在独立子目录
    ├── krunner_edge_helper.py
    ├── bookmark_parser.py
    ├── config.py
    ├── search_engine.py
    ├── pinyin_matcher.py
    └── __pycache__/

~/.local/share/dbus-1/services/
└── org.kde.krunner.edgehelper.service

```

**重要**：对于 KDE Plasma 6，DBus 插件的 desktop 文件必须放在 `~/.local/share/krunner/dbusplugins/` 根目录，而不是 `kservices5/` 或插件子目录内。

**为什么使用子目录？**
- ✅ 避免文件名冲突（如 `config.py`, `search_engine.py`）
- ✅ 方便管理和卸载（删除整个目录即可）
- ✅ 遵循 Linux 包管理最佳实践
- ✅ 支持多插件共存

## 🔧 命名规范

所有组件使用统一的命名前缀：

| 组件 | 名称 |
|------|------|
| **项目名** | `krunner-edge-helper` |
| **DBus 服务名** | `org.kde.krunner.edgehelper` |
| **DBus 对象路径** | `/EdgeHelper` |
| **KDE 插件 ID** | `krunner-edge-helper` |
| **主程序** | `krunner_edge_helper.py` |
| **安装目录** | `~/.local/share/krunner/dbusplugins/krunner-edge-helper/` |
| **日志文件** | `/tmp/krunner_edge_helper.log` |

**命名约定**：
- 目录/文件名：使用 kebab-case (`krunner-edge-helper`)
- Python 文件：使用 snake_case (`krunner_edge_helper.py`)
- DBus 服务：使用点分命名 (`org.kde.krunner.edgehelper`)

## 🏗️ 技术架构

### DBus 通信流程

```
┌─────────────────────────────────────┐
│  KRunner (Alt+Space)                │
│  用户输入: "b eo cls"               │
└───────────────┬─────────────────────┘
                │ 1. 检测插件
                │ 2. 调用 Match() 方法
                ↓
┌─────────────────────────────────────┐
│  Session Bus (会话总线)             │
│  org.kde.krunner.edgehelper         │
│  /EdgeHelper                        │
└───────────────┬─────────────────────┘
                │ 3. DBus 消息传递
                ↓
┌─────────────────────────────────────┐
│  krunner_edge_helper.py             │
│  - 解析查询                          │
│  - 调用搜索引擎                      │
│  - 返回结果                          │
└───────────────┬─────────────────────┘
                │ 4. 加载数据
                ↓
┌─────────────────────────────────────┐
│  Edge 书签文件 (JSON)               │
│  ~/.var/app/com.microsoft.Edge/...  │
└─────────────────────────────────────┘
```

### 核心组件

#### 1. krunner_edge_helper.py
**职责**：DBus 服务主体
- 实现 `org.kde.krunner1` 接口
- 提供 `Match()` 和 `Run()` 方法
- 管理 GLib 主循环

**关键代码**：
```python
SERVICE_NAME = "org.kde.krunner.edgehelper"
OBJECT_PATH = "/EdgeHelper"
IFACE = "org.kde.krunner1"

class KRunnerEdgeHelper(dbus.service.Object):
    @dbus.service.method(IFACE, in_signature='s', out_signature='a(sssida{sv})')
    def Match(self, query: str, ok_callback, err_callback):
        # 搜索逻辑
```

#### 2. search_engine.py
**职责**：多关键词搜索算法
- 空格分隔多关键词
- 所有关键词必须匹配 (AND 逻辑)
- 分层匹配：精确 → 单词 → 前缀 → 拼音 → 子串

#### 3. bookmark_parser.py
**职责**：解析 Edge 书签 JSON
- 读取 Chromium 格式书签
- 递归遍历文件夹
- 提取标题、URL、路径

#### 4. pinyin_matcher.py
**职责**：中文拼音支持
- 全拼匹配：`liushuixian` → `流水线`
- 首字母匹配：`lsx` → `流水线`
- 混合文本支持：`EdgeOne 流水线`

## 🔐 DBus 接口规范

### Match 方法

```python
@dbus.service.method(
    'org.kde.krunner1',
    in_signature='s',           # 输入：字符串
    out_signature='a(sssida{sv})'  # 输出：结构体数组
)
def Match(query: str, ok_callback, err_callback):
    pass
```

**返回格式**：
```python
(
    "bookmark_0_https://example.com",  # ID (string)
    "EdgeOne 流水线",                   # 显示文本 (string)
    "internet-web-browser",            # 图标 (string)
    95,                                # relevance 整数 (int32)
    0.95,                              # relevance 浮点 (double)
    {                                  # 属性字典 (dict)
        "subtext": "文件夹 | URL",
        "urls": ["https://example.com"]
    }
)
```

### Run 方法

```python
@dbus.service.method(
    'org.kde.krunner1',
    in_signature='ss',  # (match_id, action_id)
    out_signature=''    # 无返回值
)
def Run(match_id: str, action_id: str):
    # 从 match_id 提取 URL
    # 打开浏览器
```

## 🔄 部署流程

### 安装 (install.sh)

1. **停止旧进程**：杀死所有 `krunner_edge_helper.py` 进程
2. **清理缓存**：删除整个 `krunner-edge-helper/` 目录
3. **安装依赖**：`pip3 install -r requirements.txt`
4. **复制文件**：
   - 源码 → `~/.local/share/krunner/dbusplugins/krunner-edge-helper/`
   - 服务 → `~/.local/share/dbus-1/services/`
   - 桌面 → `~/.local/share/kservices5/`
5. **替换占位符**：`USER_HOME_PLACEHOLDER` → 实际家目录
6. **启动服务**：后台运行 Python 进程
7. **验证**：检查进程是否存活

### 卸载 (uninstall.sh)

1. **停止进程**：杀死所有实例
2. **删除目录**：删除 `krunner-edge-helper/` 整个目录
3. **删除服务文件**：清理 DBus 和 KDE 配置
4. **删除日志**：清理临时文件
5. **重启 KRunner**：使更改生效

### 重启 (restart_plugin.sh)

1. **停止进程**
2. **清理缓存**：删除 `__pycache__`
3. **启动服务**
4. **测试 DBus**：使用 `dbus-send` 验证
5. **重启 KRunner**

## 🐛 关键问题解决

### Python 缓存问题

**问题**：更新代码后旧逻辑仍在运行
- Python 将 `.py` 编译为 `.pyc` 字节码
- 运行中的进程使用已缓存的模块
- 即使源码改了，进程还在用旧字节码

**解决方案**：
```bash
# 1. 杀死所有进程
ps aux | grep krunner_edge_helper.py | awk '{print $2}' | xargs kill

# 2. 清空缓存
rm -rf ~/.local/share/krunner/dbusplugins/krunner-edge-helper/__pycache__

# 3. 启动新进程
python3 ~/.local/share/krunner/dbusplugins/krunner-edge-helper/krunner_edge_helper.py &
```

### 多进程问题

**问题**：重复安装导致多个进程同时运行
**影响**：多个版本同时响应查询，结果不确定

**解决方案**：
- `install.sh` 开头就杀死所有旧进程
- 使用循环确保杀死所有 PID
- 等待 2 秒确保进程完全退出

## 🎯 设计原则

1. **单一职责**：每个文件只负责一件事
2. **命名一致**：统一使用 `krunner-edge-helper` 前缀
3. **隔离部署**：使用子目录避免冲突
4. **完整清理**：卸载时删除所有相关文件
5. **容错处理**：脚本具有幂等性，可重复执行
6. **进程管理**：严格控制进程生命周期

## 📚 相关文档

- [搜索算法详解](SEARCH_ALGORITHM.md)
- [主 README](../README.md)
- [更新日志](CHANGELOG.md)

---

**最后更新**: 2026-02-08  
**版本**: 1.0
