# Previous reward 历史语义

保存的 experiments_deepmind_real.py:evaluate() 位于119–233行。eval_prev_rewards仅在150行以torch.zeros(num_processes,1)初始化，循环不更新；Step 1的228步与正式1576步证据均为零。原模型启用previous_reward分支，此处不能假设与训练时reward输入相同。

研究者已明确批准Step 2继续此行为：model_previous_reward=0；environment_reward使用原生实际奖励，独立记录；previous action、双GRU、reset mask按历史接口逐步更新。冻结协议中笼统的“更新previous reward”按此有证据的具体实施说明解释，未改冻结清单、历史代码或权重。

轻量轨迹分别提供model_previous_reward与environment_reward。成功由实际距离严格<100m判断，Episode Reward仅作辅助。未尝试把实际奖励反馈模型或修复历史语义。
