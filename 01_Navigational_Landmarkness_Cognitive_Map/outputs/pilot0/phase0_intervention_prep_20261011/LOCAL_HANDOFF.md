# 本地 Phase 0 准备交付

状态：**可送服务器执行Stage A的本地候选提议包，需核对下方实际GitHub提交状态。**本轮尚无任何新Qwen/DINO实验结果，且没有候选/人工bbox审核。

## 已固定

- 原任务：paris_local_v1_20260923，44 query、168 reference、82 P/6160 N/1150 I；本包不改标签或gallery。
- 开发批次：selection_manifest.json中18个Full正确视图，覆盖12个query pano、6道路，hard/medium/easy = 5/8/5；另2个Full失败视图作为diagnostic。两组共20张，单图Qwen最多20次正常请求，格式错误允许每图最多一次重试。Qwen请求只从独立的proposal_input_only.json读取图像ID/哈希；selection_manifest.json中的rank/margin只用于离线分层和结果分析。
- 输入级候选与3个等尺寸几何controls的转换和遮挡程序为scripts/phase0_intervention_geometry.py；本轮不做descriptor-only干预。
- 固定readout是原P/N/I规则下的M、positive rank、top1及候选对control的U。后续轻量分数表可由scripts/phase0_score_interventions.py本地分析。

## 已验证

- local_cache_preflight.json：168份reference VLAD哈希、20张原640 JPEG哈希、对应20张448 PNG哈希和逐像素缩放一致性、VLAD centers哈希，全部PASS。原4.55GB权重只核对保存的provenance记录，未在本地重新哈希；服务器仍需运行时验证。
- scripts/test_phase0_intervention_geometry.py：三个本地CPU检查通过。用一张旧Full的168分数复制为四种合成mask，score脚本返回零U并通过rank合同；这不是干预结果。
- 原冻结任务目录和保存的完整pair_scores当前不属于Git跟踪文件，服务器需复用其已有NAS/旧任务副本；如果缺失，应停止并单独补交经哈希核验的轻量源，不能从新选择清单推断gold。

## 顺序

1. 只白名单提交/推送本目录的 selection_manifest.json、proposal_input_only.json、local_cache_preflight.json、PHASE0_PROTOCOL.md、QWEN_QUERY_PROPOSAL_V1.txt、SERVER_CODEX_STAGE_A_PROMPT.txt，以及新增的选题、输入导出、缓存预检、几何遮挡、评分和几何检查脚本。不要把已有大量本地未提交文件一起提交。
2. 发给服务器的短指令就是SERVER_CODEX_STAGE_A_PROMPT.txt；只有远端存在上述commit后方可执行。Stage A仅Qwen提议并返回，禁止mask/DINO。
3. 拉回候选轻量结果。本地按既定规则生成overlay/controls并发给用户做技术QC，记录每题合格/排除，不根据效应选框。
4. 审核冻结后再写Stage C具体服务器指令，届时核对权重/词典/原Full等价，再运行四种遮挡与固定observer。

未在此处自动触发服务器、修改GitHub或做Phase 1新题。现有route-replay分支和结果保持不变。
