# 厂家上手

用本模板创建自己的板组件仓库后，按下面 5 步完成第一次发布。GitHub Actions 已经写好，不必改 workflow。

## 开始前

- 用**个人 GitHub 账号**创建仓库。组件注册库的默认 namespace 就是这个 GitHub 用户名。先不要建在 GitHub Organization 下，否则用户名和 namespace 对不上，上传会失败。
- 新仓库名必须包含 `boards`，只使用小写字母、数字、下划线，例如 `acme_boards`。ESP Board Manager 只自动扫描名称里带 `boards` 的组件。
- 开发板目录名、`board_info.yaml` 里的 `board` 字段必须一致，同样只允许小写字母、数字、下划线，不能用中划线。

## 第 1 步：用模板建仓库

在 GitHub 上打开本模板仓库，点击 **Use this template** → **Create a new repository**，仓库名填 `yourcompany_boards`。

克隆到本地：

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/yourcompany_boards.git
cd yourcompany_boards
```

## 第 2 步：注册组件注册库并保存 Token

1. 用**同一个** GitHub 账号打开 [components.espressif.com](https://components.espressif.com) 并登录。
2. 右上角用户名 → **Tokens** → **Create**，复制 Token。
3. 打开 GitHub 仓库 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**。
4. Name 填 `IDF_COMPONENT_API_TOKEN`，Secret 填刚才的 Token。

不要把 Token 写进仓库文件，也不要发到聊天软件。

## 第 3 步：换成自己的开发板

1. 删除或改名 `example_board/`。
2. 对照原理图编写 `board_info.yaml`、`board_peripherals.yaml`、`board_devices.yaml`。可用 Cursor，本仓库已预置 MCP：`https://mcp.esp-pilot.espressif.tools/mcp`。引脚和地址必须对照原理图确认。
3. 也可使用网页工具 <https://board-manager.espressif.com>。
4. 把 `LICENSE` 末尾的 `CHANGE_ME` 改成公司名，更新 `README.md` / `README_CN.md` 里的开发板列表。
5. 需要更高版本的 Board Manager 能力时，只改根目录 `idf_component.yml` 里的：

   ```yaml
   espressif/esp_board_manager:
     version: ">=0.7.0"
   ```

   把 `0.7.0` 抬到实际需要的下限。CI 会自动读这个下限，并再测当前最新 Board Manager。不要去改 `.github/workflows/ci.yml`。

本地先验证：

```bash
pip install esp-bmgr-assist
cd /path/to/your_idf_project
# 在工程 main/idf_component.yml 里用 override_path 指向本仓库，然后：
idf.py bmgr -l
idf.py bmgr -b <board_name>
idf.py build
```

## 第 4 步：合入 main

把改动推到 `main`（或先开 Pull Request，绿了再合）。

CI 会对仓库里每一块开发板，在 ESP-IDF `v5.5.4` 和 `latest` 上，分别用 Board Manager 下限版本和最新版本执行 `idf.py bmgr -b` 和编译。任一路失败都不能合入，包括 `latest`。

新仓库第一次合入 `main` 时，当前 `version`（模板是 `0.7.0`，与 Board Manager 对齐）还不存在，会发第一次。之后同一 `version` 再合入，upload 会跳过，不会覆盖。这是故意的：允许先合入未发布的改动。

## 第 5 步：发布组件

确认要给应用使用时：

1. 更新 `CHANGELOG.md`。
2. 把根目录 `idf_component.yml` 的 `version` 从 `0.7.0` 改成新版本（例如 `0.7.1`）。
3. 提交并推到 `main`。

上传 job 发现该版本尚未存在，就会发到：

`https://components.espressif.com/components/<github用户名>/<仓库名>`

同一 `version` 不能覆盖。发错只能再发一个新版本号。

应用侧添加：

```bash
idf.py add-dependency "YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
```

## 不要改

- `.github/workflows/ci.yml`
- `CMakeLists.txt`（保持 `idf_component_register()`）
- 不要把 `esp_board_manager` 源码拷进本仓库
- 不要把原理图、大二进制放进要上传的组件包（`.github/` 和 `ci/` 已排除）
