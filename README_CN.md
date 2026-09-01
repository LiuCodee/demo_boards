# ESP Board Manager 厂家板组件模板

[English](README.md)

本仓库是一份 ESP Board Manager **板组件**：用 YAML 描述开发板，应用可以从 [ESP 组件注册库](https://components.espressif.com) 下载后选板。

## 在应用工程中使用

1. 在已激活的 ESP-IDF Python 环境中安装一次辅助工具：

   ```bash
   pip install esp-bmgr-assist
   ```

2. 将本板组件加入工程（把命名空间和组件名换成您的 GitHub 用户名和本仓库名）：

   ```bash
   idf.py add-dependency "YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
   ```

   本组件已经依赖 `espressif/esp_board_manager`（`>=0.7.0`）。除非您要收紧版本，否则不必再单独添加 Board Manager。

3. 列出并选择开发板：

   ```bash
   idf.py bmgr -l
   idf.py bmgr -b <board_name>
   idf.py build
   ```

## 支持的开发板

| 开发板 | 芯片 | 说明 |
|---|---|---|
| `example_board` | ESP32-S3 | 占位示例。正式发布前请替换为真实开发板。 |

## 创建或发布本组件

从本 GitHub 模板新建仓库的厂家，请按 [GETTING_STARTED.md](GETTING_STARTED.md) 操作。
