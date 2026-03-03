# Star Office UI - 像素办公室看板

**研究日期**: 2026-03-02
**仓库地址**: https://github.com/ringhyacinth/Star-Office-UI
**作者**: Ring Hyacinth (@ring_hyacinth), Simon Lee (@simonxxoo)
**许可证**: Code MIT / Art Assets 非商用

---

## 项目简介

**Star Office UI** 是一个面向多 Agent 协作的像素办公室看板：

> 一个实时更新的"像素办公室仪表盘"：你的 AI 助手（和你邀请的其他 Agent）会根据状态自动走到不同位置（休息区/工作区/bug区），你还能看到他们昨天的工作小记。

### 核心价值

- **可视化工作状态** - 直观看到"谁在做什么、昨天做了什么、现在是否在线"
- **多 Agent 协作** - 支持邀请其他 Agent 加入办公室，实时展示多 Agent 状态
- **移动端友好** - 手机端可直接查看状态
- **公网访问** - 快速部署对外访问

---

## 核心功能

### 1. 状态可视化

支持 6 种状态，自动映射到办公室不同区域：

| 状态 | 区域 | 说明 |
|------|------|------|
| idle | 休息区 (breakroom) | 待命中，随时准备服务 |
| writing | 写作区 (writing) | 正在写作/整理文档 |
| researching | 写作区 (writing) | 正在研究/搜索 |
| executing | 写作区 (writing) | 正在执行任务 |
| syncing | 写作区 (writing) | 同步进度中 |
| error | 错误区 (error) | 发现问题，排查中 |

### 2. "昨日小记"微型总结

- 前端展示"昨日小记"卡片
- 后端从 `memory/*.md` 中读取昨天（或最近可用）的记录
- 做基础脱敏后展示
- 智能提取核心要点（2-3个关键点）
- 随机附带一句睿智语录

### 3. 多 Agent 机制

- **邀请访客加入**: 通过 join key 加入
- **状态推送**: 访客可持续 push 自己状态到办公室看板
- **自动清理**: 超时未批准/未推送自动离线
- **并发控制**: 同一个 key 最多 3 人同时在线

### 4. 移动端适配

- 移动设备可直接打开与查看状态
- 适合外出时快速查看

### 5. 公网访问

- 推荐使用 Cloudflare Tunnel 快速公网化
- 也可以使用自己的公网域名/反向代理方案

---

## 技术栈

### 后端

- **Python 3** + **Flask 3.0.2**
- 轻量级 RESTful API
- 状态文件存储（JSON）
- 线程安全（join-agent 关键区）

### 前端

- **HTML** + **JavaScript** (无框架)
- 像素艺术风格界面
- 实时状态更新
- 版本缓存破坏（Cache busting）

### 依赖

```
flask==3.0.2
```

**仅一个依赖！非常轻量。**

---

## 快速开始

### 30 秒一键启动

```bash
# 1) 下载仓库
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI

# 2) 安装依赖
python3 -m pip install -r backend/requirements.txt

# 3) 准备状态文件（首次）
cp state.sample.json state.json

# 4) 启动后端
cd backend
python3 app.py
```

打开：http://127.0.0.1:18791

### 切换主 Agent 状态（示例）

```bash
# 工作中 → 去办公桌
python3 set_state.py writing "正在整理文档"

# 同步中
python3 set_state.py syncing "同步进度中"

# 报错中 → 去 bug 区
python3 set_state.py error "发现问题，排查中"

# 待命 → 回休息区
python3 set_state.py idle "待命中"
```

---

## API 接口

### 1. 健康检查

**GET** `/health`

```json
{
  "status": "ok",
  "timestamp": "2026-03-02T09:00:00"
}
```

### 2. 主 Agent 状态

**GET** `/status`

```json
{
  "state": "idle",
  "detail": "待命中...",
  "progress": 0,
  "updated_at": "2026-03-02T09:00:00"
}
```

### 3. 设置主 Agent 状态

**POST** `/set_state`

```json
{
  "state": "writing",
  "detail": "正在整理文档"
}
```

### 4. 获取多 Agent 列表

**GET** `/agents`

返回所有 Agent 的状态列表（自动清理超时的 Agent）

### 5. 访客加入

**POST** `/join-agent`

```json
{
  "name": "助手名称",
  "state": "idle",
  "detail": "",
  "joinKey": "ocj_starteam01"
}
```

### 6. 访客推送状态

**POST** `/agent-push`

```json
{
  "agentId": "agent_xxx",
  "joinKey": "ocj_starteam01",
  "state": "writing",
  "detail": "正在帮主人整理文档",
  "name": "助手名称"
}
```

### 7. 访客离开

**POST** `/leave-agent`

```json
{
  "agentId": "agent_xxx",
  "name": "助手名称"
}
```

### 8. 批准 Agent

**POST** `/agent-approve`

```json
{
  "agentId": "agent_xxx"
}
```

### 9. 拒绝 Agent

**POST** `/agent-reject`

```json
{
  "agentId": "agent_xxx"
}
```

### 10. 昨日小记

**GET** `/yesterday-memo`

```json
{
  "success": true,
  "date": "2026-03-01",
  "memo": "· 完成了XX任务\n· 正在进行YY项目\n\n「工欲善其事，必先利其器。」"
}
```

---

## 状态文件结构

### state.json (主 Agent 状态)

```json
{
  "state": "idle",
  "detail": "等待任务中...",
  "progress": 0,
  "updated_at": "2026-02-26T00:00:00"
}
```

### agents-state.json (多 Agent 列表)

```json
[
  {
    "agentId": "star",
    "name": "Star",
    "isMain": true,
    "state": "idle",
    "detail": "待命中，随时准备为你服务",
    "updated_at": "2026-03-02T09:00:00",
    "area": "breakroom",
    "source": "local",
    "joinKey": null,
    "authStatus": "approved",
    "authExpiresAt": null,
    "lastPushAt": null
  },
  {
    "agentId": "agent_xxx",
    "name": "助手名称",
    "isMain": false,
    "state": "writing",
    "detail": "在整理热点日报...",
    "updated_at": "2026-03-02T09:00:00",
    "area": "writing",
    "source": "remote-openclaw",
    "joinKey": "ocj_starteam01",
    "authStatus": "approved",
    "authExpiresAt": "2026-03-03T09:00:00",
    "lastPushAt": "2026-03-02T09:00:00",
    "avatar": "guest_role_1"
  }
]
```

### join-keys.json (接入密钥)

```json
{
  "keys": [
    {
      "key": "ocj_starteam01",
      "used": false,
      "usedBy": null,
      "usedByAgentId": null,
      "usedAt": null,
      "maxConcurrent": 3,
      "reusable": true
    }
  ]
}
```

---

## 核心机制

### 1. 状态归一化

兼容多种状态名称输入：

| 输入 | 归一化后 |
|------|---------|
| working, busy, write | writing |
| run, running, execute, exec | executing |
| sync | syncing |
| research, search | researching |
| idle, writing, researching, executing, syncing, error | 保持原样 |

### 2. 自动空闲机制

- 如果上次更新时间超过 `ttl_seconds`（默认 300 秒/5 分钟）
- 且当前状态是工作状态（writing/researching/executing）
- 自动切换回 `idle` 状态
- 避免 UI 卡在某个工作状态

### 3. 隐私清理

昨日小记会自动脱敏：
- 移除 OpenID（`ou_[a-f0-9]+`）
- 移除 User ID（`user_id="[^"]+"`）
- 移除路径（`/root/[^"\s]+`）
- 移除 IP 地址（`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`）
- 移除邮箱（`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`）
- 移除手机号（`1[3-9]\d{9}`）

### 4. 睿智语录库

随机附带一句古典诗词或名言：

```
「工欲善其事，必先利其器。」
「不积跬步，无以至千里；不积小流，无以成江海。」
「知行合一，方可致远。」
「业精于勤，荒于嬉；行成于思，毁于随。」
「路漫漫其修远兮，吾将上下而求索。」
...
```

### 5. 并发控制

- 同一个 join key 最多 3 个 Agent 同时在线
- 超过 5 分钟未推送自动标记为 offline
- 超时未批准自动 leave

---

## 公网访问

### 推荐：Cloudflare Tunnel

```bash
cloudflared tunnel --url http://127.0.0.1:18791
```

会得到一个 `https://xxx.trycloudflare.com` 链接，可以直接分享。

### 其他方案

- Nginx/Caddy 反向代理
- 自有域名
- 其他隧道工具（ngrok、frp 等）

---

## 邀请其他 Agent 加入

### 步骤 1: 主人邀请

1. 下载 `office-agent-push.py`
2. 告诉其他 Agent 接入密钥（join key）
3. 等待其他 Agent 加入

### 步骤 2: 其他 Agent 加入

```bash
python3 office-agent-push.py \
  --agent-id "agent_xxx" \
  --name "助手名称" \
  --join-key "ocj_starteam01" \
  --base-url "https://你的办公室地址"
```

### 步骤 3: 周期推送状态

其他 Agent 每隔一段时间推送一次状态：

```bash
python3 office-agent-push.py --push writing "正在帮主人整理文档"
```

---

## 项目结构

```
Star-Office-UI/
├── backend/
│   ├── app.py              # Flask 后端服务
│   ├── requirements.txt     # 依赖清单
│   └── run.sh             # 启动脚本
├── frontend/
│   ├── index.html         # 主页面
│   ├── join.html          # 加入页面
│   ├── invite.html        # 邀请页面
│   ├── layout.js         # 布局逻辑
│   └── assets/           # 像素美术资产
├── docs/
│   └── screenshots/       # 截图
├── office-agent-push.py   # 远程 Agent 状态推送工具
├── set_state.py          # 本地状态设置工具
├── state.sample.json     # 状态文件模板
├── join-keys.json        # 接入密钥配置
├── SKILL.md             # Skill 文档
├── README.md            # 项目说明
└── LICENSE              # MIT 许可证
```

---

## 美术资产使用说明

### 访客角色资产来源

访客角色动画使用了 **LimeZu** 的免费资产：

- Animated Mini Characters 2 (Platformer) [FREE]
- https://limezu.itch.io/animated-mini-characters-2-platform-free

请在二次发布/演示时保留来源说明，并遵守原作者许可条款。

### 主角色（宝石海星）说明

- "宝石海星"（Starmie）是任天堂《宝可梦》系列中的角色 IP，不是本项目原创 IP
- 本项目仅为非商用二创/粉丝创作
- 选择这个角色，是因为"宝石海星"与作者名字"海辛"在中文发音上有谐音趣味
- 任天堂、宝可梦、"宝石海星"均为任天堂/宝可梦公司的商标或注册商标

### 商用限制（重要）

| 内容 | 许可 |
|------|------|
| 代码/逻辑 | MIT License（可商用） |
| 美术资产 | **非商用**（仅学习/演示用途） |

**如果你要商用，请务必制作并替换成你自己的原创美术资产。**

---

## 本次更新内容

相比早期基础版，本次发布新增/升级重点：

1. ✅ 新增多 Agent 机制（/join-agent, /agent-push, /leave-agent, /agents）
2. ✅ 新增"昨日小记"接口与前端展示（/yesterday-memo）
3. ✅ 状态体系更完整（支持 syncing, error 等状态可视化）
4. ✅ 场景与角色动画升级（补充大量像素动画资产，含访客角色）
5. ✅ 文档与 Skill 重写（更适合外部程序员快速上手）
6. ✅ 清理发布结构（去除临时文件/缓存/日志，降低阅读门槛）
7. ✅ 补充开源声明（代码 MIT、美术资产非商用）

---

## 扩展思路

欢迎基于这个框架扩展：

1. **更丰富的状态语义与自动编排**
   - 更多状态类型
   - 状态转换规则
   - 自动工作流

2. **多房间/多团队协作地图**
   - 多个办公室场景
   - 团队分组
   - 跨房间协作

3. **任务看板、时间线、日报自动生成**
   - 任务追踪
   - 时间线视图
   - 自动生成日报

4. **更完整的访问控制与权限体系**
   - 用户认证
   - 权限管理
   - 操作审计

---

## 常见问题

### Q1: 为什么角色选了宝石海星？

A: 宝石海星是宝可梦的 IP，不是原创的；选它是因为和作者名字"海辛"在中文里有谐音趣味，这是一个非商用的粉丝创作，仅供学习演示。

### Q2: 我可以商用吗？

A: 代码玩法可以基于 MIT 用，但美术资产（包括角色/场景）禁止商用；如果你要商用，请务必换成你自己的原创美术资产。

### Q3: 其他龙虾怎么加入？

A: 用 join key 加入，然后持续推送状态就行；仓库里有 `office-agent-push.py` 可以给其他龙虾用。

### Q4: 如何修改状态超时时间？

A: 在 `state.json` 中添加 `"ttl_seconds": 300` 字段（默认 300 秒）。

### Q5: 昨日小记从哪里读取？

A: 从 `../memory/YYYY-MM-DD.md` 文件读取（相对于项目根目录），自动找昨天或最近可用的记录。

---

## 个人评价

### 优势 ✅

1. **像素艺术风格** - 独特的视觉体验
2. **轻量级部署** - 仅依赖 Flask，易于安装
3. **多 Agent 支持** - 真正的多 Agent 协作
4. **移动端友好** - 随时随地查看状态
5. **隐私保护** - 自动脱敏，保护敏感信息
6. **自动清理** - 超时 Agent 自动离线，不占资源
7. **智能归一化** - 兼容多种状态名称输入
8. **睿智语录** - 提升用户体验

### 限制 ⚠️

1. **美术资产非商用** - 商用需替换原创资产
2. **无数据库** - 使用 JSON 文件存储，不适合大规模部署
3. **单机部署** - 没有分布式架构支持
4. **权限简单** - 仅基础的 join key 验证

### 适用场景

**强烈推荐**：
- ✅ 个人 AI 助手状态可视化
- ✅ 多 Agent 协作演示
- ✅ 学习 Flask 和前后端分离
- ✅ 像素艺术风格 UI 参考
- ✅ 快速原型验证

**不太适合**：
- ❌ 大规模企业部署（单机限制）
- ❌ 需要复杂权限管理
- ❌ 需要数据持久化和备份

---

## 总结

### 关键要点

1. **可视化是核心价值**
   - 把 AI 工作状态变成直观的像素动画
   - 让人"看到"而不是"想象" AI 在做什么

2. **多 Agent 协作是亮点**
   - 支持 join key 机制
   - 状态推送和自动清理
   - 并发控制和权限验证

3. **轻量级部署**
   - 仅一个依赖（Flask）
   - JSON 文件存储
   - 30 秒启动

4. **用户体验优秀**
   - 像素艺术风格
   - 昨日小记 + 睿智语录
   - 移动端适配
   - 自动脱敏保护隐私

### 技术亮点

1. **自动空闲机制** - 避免状态卡死
2. **智能归一化** - 兼容多种输入
3. **隐私清理** - 自动脱敏
4. **并发控制** - 线程安全
5. **版本缓存破坏** - 避免前端缓存

### 最终评价

**Star Office UI 是一个设计精巧的多 Agent 协作可视化工具。**

它成功地把抽象的 AI 工作状态变成了直观的像素动画，让用户能够"看到"AI 在做什么、昨天做了什么、现在是否在线。

虽然美术资产不能商用，但代码逻辑可以自由使用，对于想要快速搭建 AI Agent 可视化界面的用户来说，是一个非常好的起点。

---

## 快速参考

### 安装

```bash
git clone https://github.com/ringhyacinth/Star-Office-UI.git
cd Star-Office-UI
python3 -m pip install -r backend/requirements.txt
cp state.sample.json state.json
cd backend && python3 app.py
```

### 访问

- 本地: http://127.0.0.1:18791
- 公网: Cloudflare Tunnel

### 状态切换

```bash
python3 set_state.py writing "正在整理文档"
python3 set_state.py idle "待命中"
```

### 公网访问

```bash
cloudflared tunnel --url http://127.0.0.1:18791
```

---

*研究完成时间: 2026-03-02*
*研究状态: ✅ 完成*
