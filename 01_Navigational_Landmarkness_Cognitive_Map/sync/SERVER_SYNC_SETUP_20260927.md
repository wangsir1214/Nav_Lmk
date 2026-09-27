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

如果现有项目不是 Git 工作树或没有 `origin`，不要在现有项目上执行 `git init`、`git clone`、覆盖或删除文件。使用下面的非 Git 同步模式：先将 GitHub 仓库克隆到独立临时目录，只把 `01_Navigational_Landmarkness_Cognitive_Map/sync/` 同步到现有项目；记录临时 clone 的 commit 作为 `sync_source_commit`，之后不在现有项目目录执行 `git pull`。

```bash
tmp_dir="$(mktemp -d /tmp/nav_lmk_sync.XXXXXX)"
git clone --depth 1 https://github.com/wangsir1214/Nav_Lmk.git "$tmp_dir"
sync_src="$tmp_dir/01_Navigational_Landmarkness_Cognitive_Map/sync"
sync_dst="/home/wangyq/Nav_Lmk/01_Navigational_Landmarkness_Cognitive_Map/sync"
test -f "$sync_src/SERVER_CODEX_HANDOFF_20260926.md"
if [ -e "$sync_dst" ]; then
  diff -qr "$sync_src" "$sync_dst" || { echo "BLOCKED: existing sync directory differs"; exit 2; }
else
  mkdir -p "$(dirname "$sync_dst")"
  cp -a "$sync_src" "$sync_dst"
fi
git -C "$tmp_dir" rev-parse HEAD
```

如果服务器无法访问 GitHub，则由用户手动上传整个本地 `sync/` 目录到同一 `sync_dst`，保留文件名；上传后记录 `manual_upload`，不要初始化现有项目的 Git 仓库。

如果 `sync_dst` 已存在且需要安装用户明确指定的新同步提交，不要直接删除旧目录。先保留可恢复备份，再替换同步目录：

```bash
backup_dir="/home/wangyq/Nav_Lmk_sync_backup_$(date -u +%Y%m%dT%H%M%SZ)"
mv "$sync_dst" "$backup_dir"
mkdir -p "$(dirname "$sync_dst")"
cp -a "$sync_src" "$sync_dst"
echo "sync_backup=$backup_dir"
```

该更新模式只适用于已明确指定的新同步提交；旧目录保留，不纳入实验运行路径。

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
