# ESP Board Manager 厂家板组件维护指南

[English](VENDOR_GUIDE.md)

本指南用于从本 GitHub 模板创建厂家板组件仓库、适配板卡和配置 CI。发布后的组件说明请维护在 [README_CN.md](README_CN.md)。

## 1. 创建和配置仓库

1. 在 GitHub 打开[模板仓库](https://github.com/LiuCodee/boards-template)，选择 **Use this template** → **Create a new repository**。
![从 GitHub 模板创建仓库](image.png)
2. 选择个人 GitHub 账号或公司 Organization，填写仓库名，并选择 **Public**。
3. 克隆新仓库：

   ```bash
   git clone git@github.com:YOUR_NAMESPACE/REPOSITORY_NAME.git
   cd REPOSITORY_NAME
   ```

4. 运行 `python scripts/initialize_board_pack.py` 脚本，逐项输入厂商名称、namespace、组件名、组件描述和版权持有人，输入回车可采用默认值，运行结束自动更新 README、`idf_component.yml`、`LICENSE` 和 CI。
5. 使用 GitHub 账号登录 [ESP 组件注册库](https://components.espressif.com)，创建具有 `write:components` scope 的 API Token。
6. 在 GitHub 仓库中打开 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，创建名为 `IDF_COMPONENT_API_TOKEN` 的 Secret 并填入刚才创建的 Token。

## 2. 适配板子并发布

先准备开发板资料：原理图、硬件功能说明，以及现有工程中的板级初始化代码（如有）。

建议优先在 AI 工具中配置 [ESP Pilot MCP](https://mcp.espressif.com/#esp-pilot-mcp)，并将上述资料提供给 AI，辅助创建或迁移板卡配置。如果 MCP 介绍页无法访问，可直接将 `https://mcp.esp-pilot.espressif.com/mcp` 提供给 AI 助手进行配置。

如需手动调整或创建配置，请参考 [创建开发板指南](https://docs.espressif.com/projects/esp-board-manager/zh_CN/latest/create-board/index.html) 选择合适的方法。

添加开发板后，运行 `python scripts/update_supported_boards_table.py` 更新两份 README 的开发板表。脚本不会修改已有表格内容，只会将新开发板的板名和芯片追加到表格末尾。

通过 Pull Request 提交开发板改动。CI 会对每块开发板在声明的 Board Manager 最低支持版本、最新版本以及 ESP-IDF `v5.5.4`、`latest` 的组合中进行兼容性检查，并生成和编译所有受支持的组合。

正式发布前，请检查以下内容：

- 删除 `example_board/`，并添加真实开发板。
- 更新 `idf_component.yml` 、 `README.md` 和 `README_CN.md` 中的厂商名称、组件说明和开发板列表等信息。
- 所有 CI 矩阵项通过。

确认无误后，从 `.github/workflows/ci.yml` 的 upload 命令中删除 `--dry-run`，再合入 `main` 或推送 `v*` tag 发布新版本。

## 注意事项

### 组件命名空间

首次使用 GitHub 账号登录 ESP 组件注册库时，系统会自动创建与 GitHub 用户名相同的默认 namespace，无需另行申请:

```text
GitHub：user/demo_boards  →  组件注册库：user/demo_boards
```

如果需要使用公司名称或其他指定 namespace，请在 ESP 组件注册库右上角账号菜单的 **Permissions** → **Namespace Requests** 中申请。申请通过后，使用具有该 namespace 发布权限的账号创建 Token。

### 仓库和开发板目录

- 仓库名必须包含 `boards`，并且只使用小写字母、数字和下划线，例如 `acme_boards`。
- 开发板目录相对仓库根目录最多支持三层嵌套。CI 会扫描并测试这三层范围内的所有开发板：

  ```text
  example_board/
  audio/esp32_s3_speaker/
  display/round/esp32_p4_screen/
  ```

- 每个开发板目录名必须与 `board_info.yaml` 中的 `board` 字段一致。第四层及更深层的目录不会被发现。
- 保留 `idf_component.yml` 中的 `esp_board_manager`、`board_manager` 和 `boards` 三个 `tags` 值，以便后续自动发现板卡组件。可以新增标签，但不要删除这三个标签。

### 许可证

本模板采用 Apache-2.0。对新建内容，将 `LICENSE` 中的 `CHANGE_ME` 替换为版权持有人，通常为公司法定名称。引入第三方内容时，保留并遵守原有版权声明和许可证。

### 发布版本

组件版本号须遵循 [ESP-IDF Component Manager 版本规则](https://docs.espressif.com/projects/idf-component-manager/en/latest/reference/versioning.html)。`.github/workflows/ci.yml` 的 upload job 默认使用 `compote component upload --dry-run` 验证认证和打包，不会创建公开版本。`--allow-existing` 会阻止 workflow 覆盖已存在的版本。

初始化脚本默认保留 upload 命令中的 `${{ github.repository_owner }}`。仅当输入的 namespace 与仓库所有者不同时，脚本才会将该参数改为固定的自定义 namespace。
