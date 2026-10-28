# S1 Runtime Contract — 候选冻结审核

来源：`urbannav_ur85_s1_env_r1_20261027T024829Z_a01`；实际 adapter SHA-256：`d8af5cce993f3872b449edd4c1eaa185e38950a0854fecb2adc6a8a7b198c29d`。本文件仅交接已测试的环境约定，不授权运行 PPO。

## 输入与证据范围

候选 JSONL 保留 24 个草案 ID/顺序。坐标、Goal、yaw、距离及每个端点 16 张图的元数据来自机器记录。数据文件 basename/哈希、原源码相对文件/哈希和依赖版本在 S1_ENV_AUDIT_EVIDENCE.json 中。部署时把 image_asset_id 与 basename 绑定到本地受控资产根目录，并核对哈希；公开文件不包含内部绝对路径。

原图通过实际 PanoGraph.build_graph/set_BFS_graph 构建；中心 `NWV8UKuA1ODMKcudL8_BTA`，depth=30，550 节点/549 边。位置与距离使用 SHP lat/lon 属性（度），JSON pos 顺序为 lon/lat，geometry 原 CRS 为 EPSG:3857，仅用于溯源。

## Goal、朝向、观察与动作

2D Goal 顺序为 normalized_lat、normalized_lon，原观察 dtype 为 float64。范围为 lat [48.8696,48.8782]、lon [2.2853,2.3053]；分量计算 (coordinate-min)/(max-min)，不裁剪。未来 PPO dtype 转换未在本轮联调。

初始 internal yaw 用原 ConstrainAngle(180, API heading)：低于 -180 加 360，高于 180 减 360，保留端点；北为 0、顺时针正。图像选择以 (yaw-heading) mod 360 距 0,22.5,...,360 最近的下标，等距取列表首项，360 下标转为 0。24 个初始 view index 均为 0；未穷尽验证所有角度 tie。

图名为 pano_id 加 `_00.jpg` 至 `_15.jpg`。原 84×84 JPEG 用 OpenCV BGR 读取，HWC→CHW、uint8 0–255；环境不 resize、转 RGB 或归一化。本轮没有运行 CNN。

动作 0 前进、1 -22.5°、2 -67.5°、3 +22.5°、4 +67.5°。前进调用原 move_to_neighbor，在 3-hop 范围内按环绕角差严格 <30° 选最近候选，无候选停留。距离为原 Haversine，地球半径 6371000m。实际移动与停留已测；静态连通不是完整动作路径可执行证明。

## 固定目标、reward 与终止

初始距离必须严格 >100m。每题固定 start/goal/yaw，reset 清状态，Goal 保持不变。奖励幅度由原 _shortest_paths(fixed_goal,fixed_start) 路径计数初始化，不以配置常数或猜测数值替代。每步直接使用原 _compute_reward：访问记忆、100/200m 半径与改善 shaping 保留。

首次距离严格 <100m 成功；恰好 100m 不成功，即使此时取得完整 shaping reward。旋转、停留等所有动作均计步，1000 动作即上限；同一步成功优先于 timeout。不自动换 Goal/reset/下一题，终态后拒绝 step。无效输入/缺图单列，不计作导航失败。

动态证据仅为 3 个原生状态、31 次预定动作，另有隔离标量边界用例。Timeout 用计数器 998 加两个动作核验，未执行 1000 步导航。

## 待本地确认

候选 seed 的确切整数来自原草案；本次未执行每题 Python/NumPy/Torch seed 接线或策略采样，标为 PENDING_S1A_RNG_INTEGRATION_REVIEW。24 条核心环境输入无缺失；21 题未实测 reward 幅度是派生输出缺少逐题测量，公开 null，不猜测填值。正式冻结应确认原初始化规则和未来运行时记录要求。

固定单目标、禁止自动 reset、成功/timeout 顺序以及 YAML depth=50 到批准 UR-85 depth=30 的覆盖需在冻结记录中明确。PPO 模型、循环状态与采样 runner 的完整 Full rollout 另行授权和联调。本次停止于 READY_FOR_LOCAL_S1A_FREEZE_REVIEW。

## 实际 adapter 代码快照（仅供审核）

以下为哈希对应的完整 s1_fixed_goal_r1.py；调用方和测试入口哈希另列于 evidence。归档阶段没有执行此代码。

```python
"""Environment-only shim. Delegates graph, pixels, actions and reward to legacy code."""
import math
import numpy as np
import pano_data
import pano_graph
import urbannav_vec
import courier_game

class LazyImages(dict):
    def __init__(self,dataset):super().__init__();self.dataset=dataset
    def __missing__(self,panoid):
        if panoid not in self.dataset.allowed_panos:raise ValueError('Image pano outside audited runtime graph')
        images=pano_data.Dataset.fetch(self.dataset,panoid)
        for index,image in images.items():
            if image is None or image.shape!=(84,84,3) or image.dtype!=np.uint8:
                raise ValueError(f'Invalid historical JPEG: {panoid}_{index:02d}.jpg')
        self[panoid]=images
        return images

class BoundedDataset(pano_data.Dataset):
    def __init__(self,image_root,allowed_panos):
        # Original constructor preloads the whole Paris library; intentionally not called.
        self.perspective_path=str(image_root)
        self.allowed_panos=set(allowed_panos)
        self.images_dict=LazyImages(self)
        self.images_depth_dict={}

class FixedGoalGame(courier_game.CourierGame):
    def __init__(self,config,start,goal):
        super().__init__(config)
        self.fixed_start=start;self.fixed_goal=goal
        self.success=False
    def on_reset(self,env):
        if env._current_pano_id!=self.fixed_start:raise ValueError('Fixed start mismatch')
        self._current_goal_id=self.fixed_goal
        self._current_start_id=self.fixed_start
        distance=env._pano_graph_.distance_between_panos(self.fixed_start,self.fixed_goal)
        if not math.isfinite(distance) or distance<=100:raise ValueError('Invalid episode: initial distance must exceed 100 m')
        self._min_distance_reached=distance
        self._initial_distance_to_goal=distance
        self._prev_distance_to_goal=distance
        self._visited_panos=set();self._num_steps_this_goal=0
        self.current_goal_traj=[];self._success_inverse_path_len=[]
        self._found_goal=False;self.success=False;self._timed_out=False;self._reward_step=0
        # Keep the historical amplitude calculation; no random goal sampling.
        self._shortest_path,self._reward_current_goal=self._shortest_paths(env,self.fixed_goal,self.fixed_start)
    def get_reward(self,env):
        if self._current_goal_id!=self.fixed_goal:raise ValueError('Goal changed unexpectedly')
        reward,legacy_found=super()._compute_reward(env)
        self.success=env._pano_graph_.distance_between_panos(env._current_pano_id,self.fixed_goal)<100
        self._found_goal=self.success
        self._num_steps_this_goal+=1
        self.current_goal_traj.append(env._current_pano_id)
        self._reward_step=reward
        return reward
    def done(self):return self.success
    def get_info(self,env):
        return {'current_pano_id':env._current_pano_id,'current_goal_id':self.fixed_goal,
                'remaining_distance_m':env._pano_graph_.distance_between_panos(env._current_pano_id,self.fixed_goal),
                'success':self.success,'steps':env._frame_count,'reward_current_goal':self._reward_current_goal,
                'reward_step':self._reward_step,'scope':'environment-only interface smoke'}

class FixedGoalEnv(urbannav_vec.UrbanNav):
    def __init__(self,config,graph,dataset,start,goal,initial_yaw,max_steps=1000):
        self.frozen_graph=graph
        self.fixed_start=start;self.fixed_goal=goal;self.initial_yaw=float(initial_yaw)
        self.max_steps=max_steps
        if not math.isfinite(self.initial_yaw):raise ValueError('Nonfinite yaw')
        if start not in graph.street_view_graph or goal not in graph.street_view_graph:raise ValueError('Unknown pano')
        game=FixedGoalGame(config,start,goal)
        super().__init__(config['dataset_path'],config,game,dataset)
        self._auto_reset=False
    def set_pano_graph(self):
        # Graph was already constructed by the exact original build_graph/set_BFS_graph.
        self._pano_graph_=self.frozen_graph
        self._graph=self.frozen_graph.get_graph()
    def reset(self):
        self._start_pano_id=self.fixed_start;self._current_pano_id=self.fixed_start
        self._reward=0;self._done=False;self._info={};self.rotation_pitch_=0
        # Actual original reset initializes counters and calls our fixed-game on_reset.
        super().reset()
        self.rotation_yaw_=urbannav_vec.ConstrainAngle(180,self.initial_yaw)
        return self._get_observation(),{}
    def step(self,action):
        if self._done:raise RuntimeError('Episode already terminal; no auto-reset')
        if isinstance(action,(bool,np.bool_)) or not isinstance(action,(int,np.integer)) or not 0<=int(action)<5:
            raise ValueError('Action must be an integer 0..4')
        obs,reward,legacy_done,truncated,info=super().step(np.array([[action]],dtype=np.int64))
        success=bool(self._game.success)
        timeout=bool(self._frame_count>=self.max_steps and not success)
        self._done=success or timeout
        info.update(success=success,timeout=timeout,termination='success' if success else 'timeout' if timeout else None)
        return obs,reward,success,timeout,info

def state(env):
    pg=env._pano_graph_;pano=env._current_pano_id;yaw=env.GetYaw();heading=pg.get_heading(pano)
    return {'pano':pano,'coords':pg.get_coords(pano),'yaw':yaw,'heading':heading,
            'view_index':pano_data.find_nearest_angle_index(yaw-heading),'goal':env._game.goal_id,'step':env._frame_count}
```
