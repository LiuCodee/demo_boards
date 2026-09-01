# 把本模板推到 GitHub（给乐鑫维护者）

这份说明只给要**发布模板仓库**的人看。厂家请看仓库根目录的 `GETTING_STARTED.md`。

下面默认您还没有自己建过 GitHub 仓库。不需要先建空文件夹：模板文件已经在本地写好。

## 几个名字

| 名字 | 含义 |
|---|---|
| Git | 电脑上的版本记录工具。本目录执行 `git init` 之后，才有提交历史。 |
| GitHub | 存放 Git 仓库的网站。浏览器打开 github.com。 |
| 仓库（repository） | 一组文件加历史。本地一份，GitHub 上一份，用 `git push` 同步。 |
| Template repository | 一种特殊仓库。别人打开后可以点 **Use this template**，复制出属于自己的新仓库，而不必 Fork。 |

厂家之后的操作是：打开这个模板 → Use this template → 得到 `某公司_boards`。您现在要做的，只是把本地这份文件变成 GitHub 上的模板仓库。

## 第 1 步：GitHub 账号

1. 打开 <https://github.com/signup>，用公司邮箱注册，或使用已有账号登录。
2. 建议最终把模板放在乐鑫组织下，例如 `espressif/esp-vendor-boards-template`。第一次练习也可以先建在您的个人账号下，确认流程后再转到组织。

## 第 2 步：本机已有文件

模板路径：

```text
/home/liujinhong/esp/esp-vendor-boards-template
```

若该目录还不是 Git 仓库，在终端执行：

```bash
cd /home/liujinhong/esp/esp-vendor-boards-template
git init
git add .
git status
```

此时还不要 `git commit`，除非您准备好提交说明。需要提交时可以说一声，由助手按仓库规范提交。

## 第 3 步：在 GitHub 上新建空仓库

1. 登录后打开 <https://github.com/new>。
2. Repository name 填 `esp-vendor-boards-template`（可改，建议带 `template` 以免和厂家的 `*_boards` 混淆）。
3. Public。
4. **不要**勾选 Add a README、Add .gitignore、Choose a license。本地已经有这些文件，GitHub 再生成会冲突。
5. 点击 **Create repository**。

页面会给出一个空仓库地址，例如：

```text
https://github.com/YOUR_USER/esp-vendor-boards-template.git
```

## 第 4 步：把本地文件推上去

把 `YOUR_USER` 换成第 1 步的 GitHub 用户名或组织名：

```bash
cd /home/liujinhong/esp/esp-vendor-boards-template
git remote add origin https://github.com/YOUR_USER/esp-vendor-boards-template.git
git branch -M main
git push -u origin main
```

第一次 `git push` 会要求登录 GitHub。浏览器授权或 Personal Access Token 都可以。公司账号若开了 SSO，按提示授权。

推送成功后，刷新 GitHub 仓库页面，应能看到 `GETTING_STARTED.md`、`example_board/`、`.github/workflows/ci.yml`。

## 第 5 步：标记为 Template

1. 打开该仓库的 **Settings**。
2. 在 General 页顶部找到 **Template repository**，勾选。
3. 保存后，仓库页的绿色 Code 按钮旁边会出现 **Use this template**。

发给厂家的就是这个仓库链接。厂家只点 Use this template，不必 Fork，也不必改 GitHub Actions 文件。

## 第 6 步：自己先走一遍厂家流程（建议）

用另一个 GitHub 账号（或同一账号下另一个仓库名，例如 `demo_boards`）点 Use this template，按 `GETTING_STARTED.md` 配 Token、改一块板、合入 `main`。确认：

- 第一次合入 `main`（模板自带 `version: 0.7.0`）后，组件出现在 `https://components.espressif.com/components/<用户名>/demo_boards`。
- 之后没 bump `version` 时，upload 成功但注册库版本不变。
- bump 成 `0.7.1` 后再推 `main`，注册库会出现新版本。

本模板声明 Board Manager `>=0.7.0`。若注册库上还没有 0.7.0，CI 下限格会失败，需要等 0.7 发布，或临时把下限改成当前已发布版本做联调。

## 常见卡住的地方

- **push 被拒**：本地还没有 commit。先 `git add` 和 `git commit`，再 `git push`。
- **Use this template 按钮没有**：Settings 里未勾选 Template repository。
- **厂家上传 401**：Secret 名称必须是 `IDF_COMPONENT_API_TOKEN`，Token 必须来自同一 GitHub 账号登录的组件注册库。
- **厂家上传成功但 `idf.py bmgr -l` 看不到板**：仓库名不含 `boards`，或板目录超过扫描深度（板目录必须直接放在仓库根下）。
