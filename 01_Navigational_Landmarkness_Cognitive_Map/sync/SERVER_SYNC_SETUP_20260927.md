# 服务器首次同步说明

本文件只处理轻量 GitHub 同步，不创建或搬运图像、模型权重、patch cache 或大型结果。

路径分工以 `PATH_STORAGE_POLICY_20260927.md` 为准：`/home/wangyq/Nav_Lmk` 放代码和轻量文件，`/home/nas/wangyq` 放权重、图像、patch cache 和大型结果。

服务器项目路径：`/home/wangyq/Nav_Lmk`。

## 首次检查

```bash
cd /home/wangyq/Nav_Lmk
git rev-parse --is-inside-work-tree
git remote -v
git status --short
```

如果 `origin` 已指向 `https://github.com/wangsir1214/Nav_Lmk.git`，且工作区没有未提交改动，执行：

```bash
git pull --ff-only origin main
test -f 01_Navigational_Landmarkness_Cognitive_Map/sync/SERVER_CODEX_HANDOFF_20260926.md
```

如果仓库不是 Git 工作树或没有 `origin`，不要在现有项目上强行初始化、覆盖或删除文件；回报 `BLOCKED`，并保留当前目录状态。可由用户或管理员将 GitHub 仓库安全克隆到独立临时目录后，再把同步目录复制到项目中。

## third_party 说明

`third_party` 不属于本地 `Nav_Lmk` Git 提交，也不属于本同步包。不要删除、移动或纳入本实验，除非先确认其内容和用途。要追溯其来源，仅做只读检查：

```bash
cd /home/wangyq/Nav_Lmk
stat third_party
find third_party -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM:%TS %p\\n' | sort | head -50
git status --short --untracked-files=all -- third_party
git log --all --oneline -- third_party
```

将检查结果写入本轮服务器日志；不要根据目录名称推断它是本地 Codex 创建的。
