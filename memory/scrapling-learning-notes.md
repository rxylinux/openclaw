# Scrapling 仓库学习笔记

## 📋 项目信息

**仓库**: https://github.com/D4Vinci/Scrapling
**简介**: 自适应 Web Scraping 框架，从单个请求到大规模爬取
**作者**: Karim Shoair
**许可证**: BSD-3-Clause

---

## 🎯 核心功能

### 1. Spider 框架（类似 Scrapy）

**特点**:
- 🕷️ 类似 Scrapy 的 Spider API
  - 使用 start_urls 定义起始 URL
  - 使用异步 parse 回调
  - 使用 Request/Response 对象

- ⚡ 并发爬取
  - 可配置并发限制
  - 每域节流
  - 下载延迟

- 🔄 多会话支持
  - HTTP 请求和隐身 headless 浏览器的统一接口
  - 在单个 spider 中通过 ID 路由到不同会话

- 💾 暂停 & 恢复
  - 基于检查点的爬取持久化
  - 按 Ctrl+C 优雅关闭
  - 重新启动从停止处恢复

- 📡 流式模式
  - 通过 spider.stream() 实时流式传输抓取的项目
  - 适合 UI、管道和长时间运行的爬取

- 🛡️ 阻止请求检测
  - 自动检测和重试被阻止的请求
  - 可自定义逻辑

- 📦 内置导出
  - 通过 hooks 和自己的管道导出
  - 内置的 JSON/JSONL 导出

**代码示例**:
```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "demo"
    start_urls = ["https://example.com/"]

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {
                "title": item.css('h2::text').get()
            }

MySpider().start()
```

### 2. 高级网站获取

#### HTTP 请求
```python
from scrapling.fetchers import Fetcher, FetcherSession

# 快速且隐蔽的 HTTP 请求
with FetcherSession(impersonate='chrome') as session:
    # 使用最新的 Chrome TLS 指纹
    page = session.get('https://example.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text').getall()
```

**特点**:
- ⚡ 快速且隐蔽的 HTTP 请求
- 可模拟浏览器的 TLS 指纹、headers 和使用 HTTP/3
- 会话支持（FetcherSession、StealthySession、DynamicSession）

#### 动态加载
```python
from scrapling.fetchers import DynamicFetcher, DynamicSession

# 使用 Playwright 的 Chromium 和 Google 的 Chrome 进行完整的浏览器自动化
with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    # 保持浏览器打开直到完成
    page = session.fetch('https://example.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()').getall()
```

**特点**:
- 🔄 动态网站获取
- 💾 完整的浏览器自动化
- 🛡️ 高级隐身能力和指纹欺骗
- 轻松绕过所有类型的 Cloudflare 的 Turnstile/Interstitial

#### 反机器人绕过
```python
from scrapling.fetchers import StealthyFetcher, StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    # 保持浏览器打开直到完成
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a').getall()

# 或者使用一次性请求风格，它会为此请求打开浏览器，完成后关闭
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a').getall()
```

**特点**:
- 高级隐身能力
- 指纹欺骗
- 可以轻松绕过 Cloudflare Turnstile

#### 会话管理
- 持久会话支持（跨请求的 cookie 和状态管理）
- FetcherSession、StealthySession、DynamicSession 类

#### 代理轮换
- 内置 ProxyRotator，支持循环或自定义轮换策略
- 跨所有会话类型的每请求代理覆盖

#### 域名阻止
- 在基于浏览器的获取器中阻止对特定域及其子域的请求

#### 异步支持
- 跨所有获取器和专用异步会话类的完整异步支持

### 3. 自适应抓取 & AI 集成

#### 智能元素跟踪
```python
products = p.css('.product', auto_save=True)  # 抓取在网站设计更改后能生存的数据

# 如果网站结构发生变化，传递 `adaptive=True`
products = p.css('.product', adaptive=True)  # 以查找它们！
```

**特点**:
- 🔄 智能元素跟踪：使用智能相似性算法在网站更改后重新定位元素
- 🎯 智能灵活选择：CSS 选择器、XPath 选择器、基于过滤器的搜索、文本搜索、正则表达式搜索等
- 🔍 查找相似元素：自动定位与找到的元素相似的元素
- 🤖 MCP 服务器：内置的 MCP 服务器用于 AI 辅助的 Web Scraping 和数据提取

#### AI 集成

MCP 服务器功能强大的、自定义功能，利用 Scrapling 在将内容传递给 AI（Claude/Cursor 等）之前提取目标内容，从而加快操作并减少 token 使用。

**演示视频**: https://www.youtube.com/watch?v=qyFk3ZNwOxE

### 4. 高性能 & 经过实战测试的架构

**特点**:
- 🚀 闪电般快速：优化性能，超过大多数 Python 抓取库
- 🔋 内存高效：优化的数据结构和延迟加载，以最小的内存占用
- ⚡ 快速 JSON 序列化：比标准库快 10 倍
- 🏗️ 经过实战测试：不仅 Scrapling 有 92% 的测试覆盖和完整的类型提示覆盖，而且在过去一年中每天被数百名 Web Scrapers 使用。

**性能基准测试（5000 个嵌套元素）**:

| 库 | 时间 (ms) | vs Scrapling |
|-----|----------|--------------|
| Scrapling | 2.02 | 1x |
| Parsel/Scrapy | 2.04 | 1.01x |
| Raw Lxml | 2.54 | 1.257x |
| PyQuery | 24.17 | ~12x |
| Selectolax | 82.63 | ~41x |
| MechanicalSoup | 1549.71 | ~767x |
| BS4 with Lxml | 1584.31 | ~784x |
| BS4 with html5lib | 3391.91 | ~1679x |

**元素相似性 & 文本搜索性能**:

| 库 | 时间 (ms) | vs Scrapling |
|-----|----------|--------------|
| Scrapling | 2.39 | 1x |
| AutoScraper | 12.45 | 5.209x |

所有基准都代表 100 多次运行的平均值。详见 benchmarks.py 获取方法论。

### 5. 开发者/Web Scraper 友好体验

#### 交互式 Web Scraping Shell

特点：
- 🎯 Scrapling 集成的可选内置 IPython shell
- 快捷方式和新工具来加速 Web Scraping 脚本开发
- 将 curl 请求转换为 Scrapling 请求
- 在浏览器中查看请求结果

#### 从终端直接使用

**启动交互式 Web Scraping shell**:
```bash
scrapling shell
```

**直接从终端使用（无需编写代码行）**:
```bash
# 可选地，你可以在不编写一行代码的情况下使用 Scrapling 来抓取 URL！
scrapling extract get 'https://example.com' content.md
```

#### 丰富的导航 API

特点：
- 🛠️ 高级 DOM 遍历：使用 parent、sibling 和 child 导航方法
- 🧬 增强的文本处理：内置正则、清理方法和优化的字符串操作
- 📝 自动选择器生成：为任何元素生成强大的 CSS/XPath 选择器

#### 熟悉的 API

- 与 Scrapy/BeautifulSoup 相同的伪元素（在 Scrapy/Parsel 中使用）
- 📘 完整的类型提示：完整的类型提示以获得出色的 IDE 支持和代码补全
- 🐳 准备好 Docker 镜像：每次发布时自动构建并推送所有浏览器的 Docker 镜像

---

## 📖 安装和使用

### 安装

```bash
pip install scrapling
```

这个安装只包括解析器引擎及其依赖，不包括任何获取器或命令行依赖。

### 可选依赖

```bash
# 如果要使用任何以下额外功能，需要安装获取器及其类：
pip install "scrapling[fetchers]"

# 正常安装
scrapling install

# 强制重新安装
scrapling install --force
```

这会下载所有浏览器，及其系统依赖和指纹操作依赖。

### Docker

```bash
# 从 DockerHub 拉取镜像
docker pull pyd4vinci/scrapling

# 或者从 GitHub 注册表下载
docker pull ghcr.io/d4vinci/scrapling:latest
```

---

## 🎓 学习要点

### 1. 架构设计

**分层架构**:
- **Spider 层**: 定义爬取逻辑
- **Fetcher 层**: 负责实际的 HTTP/浏览器请求
- **Parser 层**: 解析和元素提取
- **Session 层**: 管理会话、cookie、状态

**模块化设计**:
- 每个组件职责清晰
- 易于扩展和自定义
- 支持多种使用场景

### 2. 性能优化策略

**解析器优化**:
- 优化的数据结构
- 延迟加载
- 快速序列化

**获取器优化**:
- 连接池
- 异步处理
- 代理轮换

**缓存策略**:
- 会话复用
- 浏览器实例管理
- 资源禁用选项

### 3. 反反爬虫策略

**隐身能力**:
- TLS 指纹模拟
- Headers 欺骗
- 浏览器指纹

**绕过机制**:
- Cloudflare Turnstile/Interstitial 绕过
- 代理轮换
- 域名阻止

**自适应行为**:
- 随机延迟
- 请求速率限制
- 失败重试

### 4. 开发者体验

**易用性**:
- 熟悉的 API（Scrapy/BeautifulSoup 风格）
- 完整的类型提示
- 丰富的错误处理

**开发工具**:
- 交互式 shell
- 自动选择器生成
- 元素相似性检测

---

## 🔍 可借鉴的设计模式

### 1. 统一接口

**Spider API**:
- 统一的 Request/Response 对象
- 异步回调机制
- 支持多种获取器类型

**Fetcher API**:
- 统一的接口设计（Fetcher、StealthyFetcher、DynamicFetcher）
- 会话管理（FetcherSession、StealthySession、DynamicSession）

### 2. 灵活的配置系统

**基于装饰器的配置**:
- 会话级别的配置
- 请求级别的覆盖
- 多种配置选项（impersonate、headless、network_idle 等）

### 3. 健壮的错误处理

**自动重试**:
- 阻止请求检测
- 自动重试机制
- 自定义重试逻辑

**优雅降级**:
- 多种获取器选项
- 动态切换
- 失败处理

### 4. 扩展性设计

**插件式架构**:
- Fetchers 作为可选组件
- 可自定义选择器策略
- 支持自定义管道

**钩子系统**:
- 预处理钩子
- 后处理钩子
- 导出钩子

---

## 📊 性能数据对比

### 解析速度
- Scrapling: 2.02ms
- Parsel/Scrapy: 2.04ms
- Raw Lxml: 2.54ms
- 其他库: 24ms - 3391ms

**结论**:
- Scrapling 在解析速度上与 Scrapy/Parsel 相当
- 比其他库快 10-1700 倍

### 元素查找和文本搜索
- Scrapling: 2.39ms
- AutoScraper: 12.45ms

**结论**:
- Scrapling 在元素查找上比 AutoScraper 快 5 倍

---

## 💡 适用场景

### 适合
- ✅ 大规模爬取
- ✅ 需要反爬虫绕过
- ✅ 动态网站
- ✅ AI 辅助抓取
- ✅ 需要会话管理

### 不太适合
- ❌ 简单的小型抓取任务（可能过于复杂）
- ❌ 不需要反爬虫的场景
- ❌ 资源受限的环境（浏览器占用较多资源）

---

## 🎯 核心价值

1. **性能**: 极快的解析速度，优化的资源使用
2. **隐身**: 强大的反爬虫绕过能力
3. **灵活性**: 支持多种获取器策略和会话管理
4. **易用性**: 熟悉的 API，丰富的开发工具
5. **可扩展**: 模块化设计，插件式架构
6. **实战测试**: 经过大量实际使用验证

---

## 📝 相关资源

- **文档**: https://scrapling.readthedocs.io
- **GitHub**: https://github.com/D4Vinci/Scrapling
- **Discord**: https://discord.gg/EMgGbDceNQ
- **Twitter**: https://x.com/Scrapling_dev

---

*记录时间: 2026-03-01*
*研究目的: 学习 Web Scraping 框架设计*
