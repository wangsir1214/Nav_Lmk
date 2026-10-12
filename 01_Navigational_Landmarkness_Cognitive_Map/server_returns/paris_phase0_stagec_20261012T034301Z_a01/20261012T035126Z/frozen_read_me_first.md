# Phase 0 Stage B → C 冻结交接

状态：FROZEN_PRE_INTERVENTION_NOT_EXPERIMENT_RESULT。本目录不包含遮挡推理结果。

- 原定 20 个 query view：18 个旧 Full 检索正确（primary_full_correct），2 个旧 Full 失败（diagnostic_full_failure）。分类仅由既有 DINOv2+VLAD Full 排名决定，与候选几何是否可行无关。
- 20 行人审均为 ACCEPT；其中 jqMbtUb4csuPJ3XDhARbOQ__v3 由用户于 2026-10-12 明确确认后补入。补前 SHA-256 为 8c2e1dc022ae1e28bb84279093dbfaa5cb41c2cf2d4765bc2b7f755ec0757116；补后哈希在执行清单中。ACCEPT 仅认可候选可见、框/描述可接受，不能解除几何门槛。
- 可执行 16 个，全部来自 primary；11 个按预设顺序用 c1，5 个因 c1 几何失败用 c2。覆盖六条道路，hard/medium/easy 为 4/8/4。两道 primary、两道 diagnostic 的两个候选均未通过几何门槛，本轮不做遮挡。应报告主分析 16/18 几何可执行比例，不能把 16 充作原 18。
- stagec_execution_manifest.json 是唯一可执行的框和原图清单；stageb_disposition_all20.json 记录 20 题去向；MINIMAL_HUMAN_QC_frozen.csv 保留人工记录。不得从审核表临时重选框。
- 八个控制框落到同图另一候选区域，用户已记录并接受该配置；它们不与当前被遮的候选重叠。后续保留混杂标记，不因效果而换框。
- SERVER_CODEX_STAGE_C_PROMPT.txt 是服务器交接指令。先将本地冻结包白名单提交并推送 main，再向服务器交付。
