# AntennaTestHelper

*以下内容由AI生成，请注意鉴别。*

天线测量数据处理与方向图分析工具（PySide6 + PySide6-Fluent-Widgets + matplotlib / numpy / scipy / scikit-rf）。

本文档说明**如何把本工程打包成可独立运行的 Windows 程序**（`pyside6-deploy` + Nuitka standalone），以及打包过程中最容易踩的坑。

> **一句话结论：打包必须用 python.org 官方的 CPython 3.13 建 venv 来做，不能用 conda 环境里的 Python。**

---

## 1. 开发运行

| 任务 | 命令 |
|------|------|
| 运行程序 | `D:\Miniconda\envs\Pyside\python.exe main.py` |
| 安装依赖 | `D:\Miniconda\envs\Pyside\python.exe -m pip install -r requirements.txt` |
| 编译检查 | `D:\Miniconda\envs\Pyside\python.exe -m py_compile (Get-ChildItem -Recurse -Filter *.py -Name)` |

日常开发用 conda 环境没问题，**只有打包不能用它**（原因见第 2 节）。

---

## 2. 打包前必读：为什么不能用 conda 的 Python

用 conda 环境（`D:\Miniconda\envs\Pyside`，Anaconda 构建的 Python 3.13.18）作为 Nuitka standalone 的基座时，打出来的程序**任何 C 扩展一 import 就会崩**：

| 实验（Nuitka 4.1.1 + MSVC，条件完全相同） | 基座解释器 | 结果 |
|---|---|---|
| `import ctypes` | Anaconda 3.13.18（MSC v.1942） | `0xC0000409`，进程直接 abort |
| `import numpy` | Anaconda 3.13.18 | 同样的 `0xC0000409` |
| `import ctypes` + `_sqlite3` | **python.org CPython 3.13.17**（MSC v.1944） | 正常输出，退出码 0 |
| `import numpy` | **python.org CPython 3.13.17** | 正常输出，退出码 0 |

唯一变量就是解释器的构建来源，所以就这个 abort 而言：

- 和 numpy / Qt / 编译器无关；换 `--zig`、降 numpy 版本、改 OpenBLAS 环境变量都**无效**；
- 唯一可靠的修法是**换基座解释器**。

典型症状：双击 `main.exe` 闪退无窗口，命令行里只看到 Nuitka 打印
`A segmentation fault has occurred`，或进程退出码是 `0xC0000005` / `0xC0000409`。

### 换好解释器之后还有第二个坑：Nuitka 必须 ≥ 4.2

基座换成官方 CPython 后，程序**仍然会崩**，但现象变了：这次崩在 `import scipy.sparse`（读地址 0）。原因是 scipy 1.18 改了子模块的懒加载机制，而 Nuitka 4.1.x 不认识它：

| 条件（scipy 1.18.1 + CPython 3.13.17 + 同一个 MSVC） | 结果 |
|---|---|
| Nuitka **4.1.1** | `import scipy.sparse` → 段错误（退出码 3） |
| Nuitka **4.3.5** | 同一脚本 `scipy.sparse / numpy.ma / numpy.fft / scipy.io` 全部导入成功，退出码 0 |

[Nuitka 4.2 发布说明](https://nuitka.net/posts/nuitka-release-42.html) 的 Package Support 一节写着 “Standalone: Added support for newer scipy.”，且没有 backport 回 4.1.x。**所以本项目固定 `Nuitka==4.3.5`**（spec 的 `packages` 字段）。

最小复现（不带 Qt，约 16 分钟编完）：`import numpy` → `import scipy` → `import scipy.sparse`，能崩就说明是 Nuitka 版本问题。

---

## 3. 准备打包用的 Python（python.org CPython 3.13）

已测试可用：**CPython 3.13.17 x64**。任选一种方式安装，注意不要用 conda 装出来的 Python。

### 方式 A：官方安装包（推荐）

1. 下载 <https://www.python.org/downloads/windows/> 的 Python 3.13.x 64-bit 安装包；
2. 安装时选择 **Install for me only**（无需管理员），可勾选 `py launcher`；
3. 记下安装路径，例如 `C:\Users\<你>\AppData\Local\Programs\Python\Python313\python.exe`。

### 方式 B：NuGet 免安装包（不写注册表、可整个删掉）

```powershell
$root = "D:\py313"
New-Item -ItemType Directory -Force -Path $root | Out-Null
$ver = "3.13.17"
curl.exe -L --ssl-no-revoke -o "$root\python.$ver.nupkg" `
  "https://api.nuget.org/v3-flatcontainer/python/$ver/python.$ver.nupkg"
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("$root\python.$ver.nupkg", "$root\cpython")

# 解释器在：$root\cpython\tools\python.exe
& "$root\cpython\tools\python.exe" -c "import sys; print(sys.version)"
```

> 本机目前已有可用的 `D:\_pyorg313\venv`（CPython 3.13.17 + 全部依赖 + Nuitka 4.3.5），可直接跳到第 5 节复用。

---

## 4. 创建 venv 并安装依赖

```powershell
# 用第 3 节装好的官方解释器创建 venv（路径按需修改）
& "D:\py313\cpython\tools\python.exe" -m venv "D:\py313\venv"
$vp = "D:\py313\venv\Scripts\python.exe"

# 依赖版本全部锁定在 requirements.txt 里
& $vp -m pip install --upgrade pip
& $vp -m pip install -r "D:\AntennaTestHelper\requirements.txt"
& $vp -m pip install "Nuitka==4.3.5"
```

确认无误：

```powershell
& $vp -c "import sys, PySide6, qfluentwidgets, numpy, scipy, skrf; print(sys.version.split()[0], PySide6.__version__)"
```

### 版本锁定

| 包 | 版本 |
|---|---|
| PySide6 | 6.12.0 |
| PySide6-Fluent-Widgets | 1.11.3 |
| matplotlib | 3.11.2 |
| numpy | 2.5.4 |
| scipy | 1.18.1 |
| scikit-rf | 2.2.0 |
| Nuitka | 4.3.5（**必须 ≥ 4.2**，4.1.x 不支持 scipy 1.18） |
| Python | 3.13.x（python.org 构建） |

### Visual Studio 环境

打包需要 **MSVC**（Python 3.13 上 Nuitka 已禁止 `--mingw64`），要求：

- Visual Studio（Community 版即可）勾选「使用 C++ 的桌面开发」，本机验证版本为 VS 18 / MSVC 14.5x；
- 同一台机器上装好 **Windows SDK**（本机为 10.0.28000.0）。

---

## 5. 生成 `pysidedeploy.spec`

`pysidedeploy.spec` 是**本机文件、已 gitignore**；仓库里提交的是可移植模板 `pysidedeploy.spec.template`。

```powershell
cd D:\AntennaTestHelper
Copy-Item pysidedeploy.spec.template pysidedeploy.spec
```

然后只改两处，其余保持不动：

| 配置项 | 填什么 |
|---|---|
| `[python] python_path` | 上一步 venv 的解释器，如 `D:\py313\venv\Scripts\python.exe` |
| `[app] icon` | **同一个** Python 里的图标：`<venv>\Lib\site-packages\PySide6\scripts\deploy_lib\pyside_icon.ico` |

模板里已经写好的部分（不要改）：

| 配置项 | 值 | 原因 |
|---|---|---|
| `[app] exec_directory` | `release` | 产物不与源码混在一起 |
| `[nuitka] mode` | `standalone` | `onefile` 每次启动要往 `%TEMP%` 解压约 170 MB，且 `config/config.json` 不持久 |
| `[nuitka] extra_args` | `--noinclude-qt-translations --include-data-dir=assets=assets --include-data-dir=config=config` | 程序用相对路径读 `assets/*.png`，不打包就显示不出图 |

如果机器上装了多个 Visual Studio 版本，可在 `extra_args` 末尾追加 `--msvc=latest` 明确指定。

**打包前确认 `assets/` 和 `config/` 都存在**：`assets/` 已入库；`config/` 被 gitignore，新克隆的仓库需要先放好 `config/config.json`，否则 `--include-data-dir=config=config` 会失败。

---

## 6. 执行打包

```powershell
cd D:\AntennaTestHelper
Remove-Item -Recurse -Force release\AntennaTestHelper.dist -ErrorAction SilentlyContinue

# 注意用 venv 里的 pyside6-deploy，而不是 conda 环境里的
& "D:\py313\venv\Scripts\pyside6-deploy.exe" -c pysidedeploy.spec --no-install
```

- `--no-install`：跳过「按 spec 里的 `packages` 再 pip 安装一遍」，也避免非交互环境下的 `Proceed? [Y/n]` 报错；Nuitka 已装在 venv 里。
- 完整构建约 **40 分钟**（1342 个 C 文件），中间产物在 `deployment/`，可用 clcache 加速二次构建。

---

## 7. 验证产物

```powershell
# 双击或命令行启动
D:\AntennaTestHelper\release\AntennaTestHelper.dist\main.exe
```

判断标准：**窗口正常弹出、能切换各个页面、2D/3D 方向图能显示出图片**。

无头验证（不弹窗，只确认不崩）：

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
Start-Process .\release\AntennaTestHelper.dist\main.exe
Start-Sleep -Seconds 10
Get-Process main -ErrorAction SilentlyContinue | Select-Object Id, Responding
```

进程仍在且 `Responding = True` 即为通过；如果 10 秒内进程消失，说明打包仍有问题，去看第 9 节。

### 产物结构

```
release\AntennaTestHelper.dist\
├── main.exe          # ~138 MB
├── assets\           # 图片资源（相对路径加载，必须在 exe 同级）
├── config\           # config.json
├── *.dll             # python313.dll / vcruntime / Qt
└── PySide6\plugins\  # Qt 插件（platforms\qwindows.dll 等）
```

整个 `AntennaTestHelper.dist` 目录一起分发；**不要只拷 `main.exe`**。

---

## 8. 打包检查清单

1. 用 python.org CPython 3.13 建的 venv，**不是** conda 的 Python；
2. 该 venv 已装齐 `requirements.txt` + `Nuitka==4.3.5`；
3. `pysidedeploy.spec` 的 `python_path` / `icon` 指向这个 venv；
4. `assets/`、`config/config.json` 都存在；
5. 用 **venv 里的** `pyside6-deploy.exe`，并带 `--no-install`；
6. 打完先跑一次 `main.exe` 确认窗口能弹出、图片能显示。

---

## 9. 常见错误速查

| 现象 | 原因 | 处理 |
|---|---|---|
| `A segmentation fault has occurred`；退出码 `0xC0000005` / `0xC0000409`；双击闪退 | 基座是 conda 的 Python，打包后任何 C 扩展 import 都会 abort | 换成 python.org CPython 3.13 的 venv 重新打包 |
| `FATAL: Error, scons environment variable 'CC' is not set` 或 `Windows SDK must be installed in Visual Studio` | Nuitka 缓存的 MSVC 环境里不含 Windows SDK（常见于先装 VS、后装 SDK） | 结束所有构建进程，删除 `%LOCALAPPDATA%\Nuitka\Nuitka\Cache\scons-msvc-config\content-*.json` 后重跑 |
| `FATAL: Error, cannot use '--mingw64' on Python version 3.13 or higher` | Nuitka 在 Python 3.13 上不再支持 MinGW | 去掉 `--mingw64`，改用 MSVC（可加 `--msvc=latest`） |
| `EOFError: EOF when reading a line` + `Proceed? [Y/n]` | 非交互环境下 `pyside6-deploy` 要求确认 | 命令加 `--no-install`（或 `-f`） |
| `Unable to find dumpbin` | 依赖检查工具缺失，不影响构建 | 可忽略 |
| `No project file found in the current directory` | 工程没有 `.pyproject`，走默认配置 | 可忽略 |
| 程序能启动但界面图片空白 | 缺少 `--include-data-dir=assets=assets`，或 exe 不在 dist 根目录运行 | 检查 `extra_args`，并确认 `assets/` 与 `main.exe` 同级 |
| 启动就报配置读取失败 | `config/config.json` 没打包进去 | 确认 `config/` 存在并已包含在 `extra_args` 中 |
| `import scipy.sparse` 段错误 / 退出码 3（已换成官方 CPython 仍崩） | Nuitka 4.1.x 不认识 scipy 1.18 的新子模块懒加载机制 | Nuitka 升到 ≥ 4.2（本项目用 4.3.5），spec 的 `packages` 和 venv 都要改 |
| `RuntimeError: [DEPLOY] Finding module import failed on file ...\release\_xx\main.py` | `pyside6-deploy` 会递归扫描项目目录下所有 `.py`，把试验/复现脚本当成了项目代码 | 试验脚本放项目外（如 `D:\_nvtest`），项目内只保留应用代码 |
| 换 numpy / zig / OpenBLAS 环境变量都好不了（C 扩展一 import 就 abort） | 基座是 conda 的 Python | 换 python.org CPython 3.13 的 venv 重新打包 |

---

## 10. 备注

- `ui_*.py` 由 `pyside6-uic` 从同名 `.ui` 生成，不要手改。
- 程序要求从 dist 根目录启动（资源、配置均用相对路径）。
- `release/`、`deployment/`、`config/`、`pysidedeploy.spec` 均已 gitignore；仓库里的 `pysidedeploy.spec.template` 是给新机器用的模板。
