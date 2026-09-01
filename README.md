# ESP Board Manager 厂家板组件模板

[中文](README_CN.md)

This repository is an ESP Board Manager **board pack**: YAML board definitions that applications can download from the [ESP Component Registry](https://components.espressif.com).

## Use in an application

1. Install the helper once in your ESP-IDF Python environment:

   ```bash
   pip install esp-bmgr-assist
   ```

2. Add this board pack to the project (replace the namespace and name with your GitHub user name and this repository name):

   ```bash
   idf.py add-dependency "YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"
   ```

   The pack already depends on `espressif/esp_board_manager` (`>=0.7.0`). You do not need to add Board Manager again unless you want a tighter pin.

3. List and select a board:

   ```bash
   idf.py bmgr -l
   idf.py bmgr -b <board_name>
   idf.py build
   ```

## Supported boards

| Board | Chip | Notes |
|---|---|---|
| `example_board` | ESP32-S3 | Placeholder. Replace it with a real board before publishing. |

## Create or publish this pack

Vendors starting from this GitHub template should follow [GETTING_STARTED.md](GETTING_STARTED.md).
