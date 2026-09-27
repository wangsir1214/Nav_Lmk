# Error Log

## 2026-09-26

- 初始 `gh auth status` 曾报告旧 token 失效；随后认证状态恢复，私有仓库已成功创建并 push，故该阻塞已解除。
- 本轮未发现新的实验运行错误；Qwen 尚未在本地执行。

## 2026-09-27

- 用户服务器截图显示 `/home/wangyq/Nav_Lmk/third_party`，而本地工作区、Git 历史和同步包均无该目录；来源和创建者无法仅凭本地证据确定。已要求服务器只读检查 `stat`、文件时间、Git 状态和历史，不删除或移动。
- 服务器尚未拉取 `01_Navigational_Landmarkness_Cognitive_Map/sync/`；已新增首次同步说明和阻塞处理规则。

## 2026-09-24 - 本地路径可用性

- 当前普通会话无法看到 `Z:` 映射盘，`Get-ChildItem Z:\wangyq\outputs\Paris_local_v1_20260923` 返回 `Cannot find drive`。后续设计核对使用已保存且核验的本地审计副本与服务器交接归档；这不表示 NAS 文件缺失。服务器执行仍使用 `/home/nas/wangyq/...`，不需重新扫盘或重跑 baseline。

## 2026-09-24 - 服务器基线续检与报告范围

- 普通受限会话看不到Z映射盘；经审批的正常用户会话定点只读NAS成功，没有递归扫盘或修改NAS。
- 既有本地验收报告把主分析概括为每题1或2P，实际为8题1P、34题2P、2题3P；文字已纠正，服务器数据和冻结标签本身正确。
- 原baseline_summary按area_id只有paris_arc一组；本地按冻结道路成对设计补做报告层三子片区汇总。该问题不改变检索分数。
- /home/wangyq任务日志不在Z映射范围；424特征全量hash、CUDA smoke等需原始文件归档。本轮实测全部212个VLAD，复用上次6个patch/6个PNG抽查证据，未声称全量模型复现。
- Python控制台中文显示异常，改用ensure_ascii=True确认原人审文本UTF-8完好；冻结CSV未改。多文件补丁报告未找到锚点后，定点回读确认前三文件已写入，剩余文件单独补齐，避免重复写入。

## 2026-09-24 - AnyLoc词典入口修订

- 原SharePoint单文件和文件夹链接均返回HTTP 404；该下载路线已停止，不使用HTML错误页或非匹配词典。
- AnyLoc/DINO Release v1固定urban中心下载和本地SHA/结构检查通过；服务器仍需在其PyTorch环境完成正式加载验证。

## 2026-09-23 - Pilot 0 服务器交接包 v2.1 验收

- 目标环境未将`python`加入PATH，首次单测、编译和冻结检查均未启动；改用项目记录的Python 3.12.14绝对路径后完成，10项单测、编译、17项题库校验均通过。
- 代码复核发现`pilot0_score.py`使用`hashlib`却未导入；新增端到端评分测试后修复并验证。
- 特征提取器原先在服务器预检前创建输出目录。若预检失败会留下存在的空目录并阻止脚本重试；已调整为预检通过后再创建。
- 当前无未解决的本地交付代码失败。服务器路径访问、下载、全量预处理与GPU运行尚未尝试。

## 2026-09-23 - 人工复核回收与 baseline 准备

- 最终检查发现WORKLOG和RESULTS_SUMMARY本轮段落重复，已只删除逐字相同的第二份并验证唯一性。中文检查字符串受PowerShell管道编码影响，改为Unicode转义后定位正常；ERROR_LOG直接写入遇PermissionError，改用文件补丁完成。冻结题库与交付包不受影响。
- 首次工具JS数组语法失败，未执行实际操作，修正后继续。控制台中文初始编码异常，使用UTF-8输出后正常，源文件未损坏。
- 官方小型文本初次普通网络访问遇Win10013；限定官方来源的只读扩展访问成功。DINOv2源码路径首次漏dinov2/前缀产生404，修正后5个文件及commit/hash均获取成功；未下载或执行模型。
- 合并读取输出曾截断，改读相关文件首尾和目标段落。git status确认当前目录不是Git工作树；未初始化或上传。
- 通用人审gate标记R123/R125需要边界裁决，原报告按原样保留。v1已逐对处理并通过17项完整校验；无未解决数据结构错误，4个无P query显式剔除，不属于工具故障。
- 仍待服务器验证真实权重/词典/环境及前向实现。单人辅助审核、规则负例和小规模开发抽样是证据边界；不阻止本轮完整图开发基线，不支持独立确认性benchmark声明。

## 2026-09-23 - Pilot 0 本地执行与当前限制

- 旧spreadsheets技能路径不存在，已改读插件目录；广泛读取截断后聚焦重读关键内容。
- 普通进程看不到Z盘；已授权具体源路径的只读扩展访问成功。索引/图片读取和一处日志补丁的自动审批曾超时，按提示重试；不是判定数据丢失或行动不安全。
- 一处task脚本缩进错误和生成HTML时的工具JS嵌套模板语法错误，均在有效产物生成前修复，后续运行通过。
- 初稿负例距离过远，在看图和模型结果前按元数据改为三片区的邻近不同街段，当前N最低88.60m。
- 31对候选P出现侧视重叠不足/重复立面等疑点，保持待人工；全部关系禁用评分。
- 内置浏览器file URL被Browser URL安全策略拒绝；未换通道、代理或本地服务器绕过。图卡已目视检查、页面语法/资源检查通过，实际交互未验证，提供CSV+图卡备用。
- 一次日志补丁因首行BOM未匹配，改用已有日期标题锚点。29项数据检查及6项回收门槛测试通过，无未解决数据结构失败。

## 2026-09-22 - HTML 新要求同步

- Python 初次打印中文受输出编码影响；改用 `sys.stdout.reconfigure(encoding='utf-8')` 后正常。
- 创建 `_audit_work/chat_sync_20260922` 临时提取目录返回 PermissionError；改为只读解析并在会话内保存提取正文，没有生成该目录或改写源 HTML。
- 初版清理 KaTeX 展示节点时遗漏公式；检查源 HTML 后提取 `data-math-source`，重新解析并读完修复后的正文。合并读取曾触发输出截断，关键内容按字符区间重读。
- 普通受限 `Test-Path` 对 Z 路径返回 false；在用户授权范围内以路径限定只读方式复核成功，数据并未据此判为丢失。
- `git rev-parse --show-toplevel` 返回 not a git repository；这是后续 GitHub 交接待建立项，不是数据或模型实验错误。
- 文档同步后发现 PROJECT_CONTEXT、EXPERIMENT_DESIGN、CODEX_TASKS、DECISIONS 的新入口重复；已精确去重并校验八份入口／状态文档本轮段落各一个。两份对话的论文解释和模型发布说法未外部核验；不作为已核验来源事实。未运行实验，无新增模型故障。

## 2026-09-22 - 数据关系回顾

- 一次 `rg` 检索引用不存在的 `_audit_outputs/data_asset_inventory.md`，返回 os error 2；枚举实际目录后改读 `repo_inventory.md`、`data_manifest.yaml`、`data_schema_report.md`，已解决。
- 广泛文件列表与合并读取曾触发输出截断；改为聚焦读取关键报告和表头。
- 首次日志补丁无法匹配 WORKLOG 首行标题，校验失败；改用已存在的日期标题作为插入锚点重试。
- 写后发现 WORKLOG 与 RESULTS_SUMMARY 的本轮段落重复，已按本轮标题精确去重；四份日志各保留一个本轮段落，历史段落保留。
- 去重命令对 ERROR_LOG 的额外说明写入遇到 Access denied；改用定点补丁补记，原日志内容仍在。
- 未运行数据处理或模型实验；未重新验证远端挂载状态。历史数据质量问题沿用既有记录。

## 2026-09-17 - Feasibility v2

### Resolved execution issues

- Legacy dependency loader unavailable; supported MCP loader succeeded.
- Bundled Python lacked pyproj. Sandbox install failed with WinError10013/network restrictions; approved scoped install succeeded into project-only feasibility_deps (pyproj3.7.2/certifi2026.7.22).
- First large apply_patch approval timed out without creating a file. Verified absence, then smaller relative-path patches succeeded.
- Sandbox output writing raised PermissionError for new CSV; scoped elevated script execution succeeded. Source files untouched.
- Sandbox Z checks unavailable; elevated scoped reads verified Paris assets. C:/Users/Admin environment-discovery listing denied, not pursued.
- A multi-file log patch reported a context failure after partial application; retries duplicated the two current-session log sections. Mechanical title-scoped cleanup retained one 2026-09-17 section per file and preserved all other historical entries.

### Remaining scientific/data issues

- All selected routes mix months; main_03 includes2012. Same month does not prove same weather/session.
- API and historical original positions differ by up to9.01m among selected panos. Both retained, no surveyed accuracy assumed.
-5m distinct-observation count is a spatial proxy, not visual duplicate detection or a memory measure.
- main_11 has1non-return departure; main_07/arc_control_03 need road-sign/OSM consistency checks.
- Construction/glare/seasonal changes remain. Replacement observations, candidate stability/functionality, route-aligned stimuli, human approval and usage/publication permissions are unverified.
- No model API called, no interventions generated, no formal experiment run.

Detailed earlier audit issues are in `_audit_outputs/ERROR_LOG.md`.

## Unresolved

- The exact final graph file and Paris graph-building cells are now identified,
  but the command/tool that created the snapped `Line_Points_1/2.shp` geometry is
  still missing. The snapping rule is reproduced from data, not from execution history.
- New route maneuvers remain provisional until user/teacher confirmation.
- Historical UrbanNav checkpoint/config/fixed-episode replay is not reproducible.
- Historical code contains literal service credentials that must be revoked and
  moved to secure runtime configuration.
- Final six-dimension human suitability scores are not complete.
- The current four-view batch-generation script and JPEG parameters remain missing;
  only the output orientation/FOV relation is verified.

## Resolved

- Z-drive data are accessible through user-approved, path-scoped, read-only
  sandbox-external commands; core assets have been scanned.
- Fixed-view orientation has been verified by pixel and geographic-anchor tests.
- Valid UTF-8 candidate JSON passes strict Python parsing. PowerShell 5 requires
  explicit `-Encoding UTF8` to avoid false parse failures on French road names.
- Candidate validation passes for 15 routes, 120 panos, 480 fixed-view images,
  120 heading records, and 30 review boards.
- `Paris_check_for_Codex.zip` final graph hash/version chain and point-coordinate
  lineage have been audited; the Shapefile console encoder now handles French text.
- Official Google Tile/Static/JavaScript Street View definitions have been checked.

## 2026-08-03 transient command issues

- A PowerShell ZIP search used a pipe after `finally`, causing a parser error;
  the corrected command was then too slow because of repeated array concatenation.
  It was replaced by `_audit_work/trace_projection_calls.py`.
- A property name guessed for `Measure-Object` did not exist; rerunning against
  the actual `left/right` fields produced max weight delta `2.12e-12`.
- The previously supplied Desktop `UrbanNav_neo_fromPC.zip` path is no longer
  present. Earlier extracted source and audit reports remain in the workspace.
- The literal `python` command was not on PATH in an earlier audit step; all
  reproducible Python commands use the bundled absolute runtime path.
- The first expanded review CSV draft had 26 values for a 27-column header. The
  validation caught all 15 rows; one missing blank field was inserted and the
  final file has 15 valid 27-column rows.
- Windows `rg` rejected shell-style `*.md` path globs; the search was rerun with
  `-g '*.md'` and completed normally.

## 2026-09-09 interpretation session

- No new data, model, or external state was changed.
- The remaining scientific gaps are unchanged: human route/task review,
  route-aligned projection provenance, metric-CRS snapping recheck, and the
  security rotation of historical credentials.
