# 博查API永久配置完成

## ✅ 配置状态

**配置时间**: 2026-02-23
**API密钥**: sk-b6fb1f3d3a1949fb92583bc8ad6715df
**Shell类型**: Oh My Zsh
**配置文件**: ~/.zshrc
**状态**: ✅ 已永久配置并验证成功

---

## 📝 配置详情

### 已添加到 ~/.zshrc

```bash
# 博查API密钥 - 配置时间: 2026-02-23
export BOCHA_API_KEY=sk-b6fb1f3d3a1949fb92583bc8ad6715df
```

### 如何使配置生效

**方式1：重新加载配置文件（推荐）**
```bash
source ~/.zshrc
```

**方式2：重新打开终端窗口**
- 关闭当前终端
- 打开新的终端窗口
- Oh My Zsh 会自动加载配置

---

## 🧪 验证配置

### 验证步骤

1. **检查环境变量**
   ```bash
   echo $BOCHA_API_KEY
   # 应该显示: sk-b6fb1f3d3a1949fb92583bc8ad6715df
   ```

2. **运行测试脚本**
   ```bash
   cd /Volumes/solid\ hard\ disk/github/rxylinux/openclaw/skills/a-stock-analysis/scripts
   python3 test_bocha.py
   ```

3. **测试实际搜索**
   ```bash
   # 搜索双环传动基本信息
   python3 bocha_search.py 002472 双环传动 --basic

   # 搜索最新新闻
   python3 bocha_search.py 002472 双环传动 --news
   ```

---

## 🚀 使用示例

### 基本用法

```bash
# 进入脚本目录
cd /Volumes/solid\ hard\ disk/github/rxylinux/openclaw/skills/a-stock-analysis/scripts

# 综合搜索（获取所有信息）
python3 bocha_search.py 002472 双环传动

# 仅搜索基本信息
python3 bocha_search.py 002472 双环传动 --basic

# 仅搜索财务数据
python3 bocha_search.py 002472 双环传动 --financial

# 仅搜索最新新闻
python3 bocha_search.py 002472 双环传动 --news
```

### 在Python中使用

```python
import os
import sys
sys.path.append('/Volumes/solid hard disk/github/rxylinux/openclaw/skills/a-stock-analysis/scripts')

from bocha_search import StockInfoSearcher

# 初始化搜索器（会自动读取环境变量）
searcher = StockInfoSearcher()

# 搜索股票信息
results = searcher.comprehensive_search('002472', '双环传动')

# 查看结果
import json
print(json.dumps(results, indent=2, ensure_ascii=False))
```

---

## 📊 API特性

| 特性 | 说明 |
|------|------|
| **响应速度** | 0.15秒极速响应 |
| **返回结果** | 最多50条 |
| **时间范围** | 支持day/week/month/year/noLimit |
| **文本摘要** | 自动生成搜索结果摘要 |
| **数据合规** | 国内合规，数据不出海 |
| **AI友好** | 专为AI应用设计 |

---

## 📚 相关文档

- **API使用指南**: [BOCHA_API_GUIDE.md](BOCHA_API_GUIDE.md)
- **官方文档**: https://bocha-ai.feishu.cn/wiki/HmtOw1z6vik14Fkdu5uc9VaInBb
- **开放平台**: https://open.bocha.cn

---

## 🔧 配置管理

### 查看当前配置

```bash
# 查看配置文件（Oh My Zsh）
cat ~/.zshrc | grep BOCHA

# 查看环境变量
echo $BOCHA_API_KEY
```

### 更新API密钥

如果需要更换API密钥：

1. 编辑配置文件（Oh My Zsh）
   ```bash
   nano ~/.zshrc
   # 或
   vim ~/.zshrc
   # 或使用 VSCode
   code ~/.zshrc
   ```

2. 找到并修改这一行：
   ```bash
   export BOCHA_API_KEY=your_new_api_key_here
   ```

3. 保存后重新加载：
   ```bash
   source ~/.zshrc
   ```

### 删除配置

如果不再需要博查API：

1. 编辑配置文件（Oh My Zsh）
   ```bash
   nano ~/.zshrc
   # 或
   vim ~/.zshrc
   # 或使用 VSCode
   code ~/.zshrc
   ```

2. 删除包含 BOCHA_API_KEY 的行

3. 重新加载配置
   ```bash
   source ~/.zshrc
   ```

---

## ⚠️ 注意事项

1. **Oh My Zsh 用户**
   - 配置文件位于 `~/.zshrc`
   - 每次打开终端会自动加载
   - 修改后需要 `source ~/.zshrc` 生效

2. **资源包管理**
   - 定期检查：https://open.bocha.cn
   - 及时领取免费资源包
   - 关注剩余调用次数

3. **API密钥安全**
   - 不要将API密钥上传到公开仓库
   - 不要分享给他人
   - 定期更换密钥

4. **使用限制**
   - 注意API调用频率
   - 避免短时间内大量请求
   - 合理使用缓存机制

---

## 🆘 常见问题

### Q: 每次打开终端都要 source 吗？
A: 不需要。配置已添加到 ~/.zshrc，Oh My Zsh 每次打开新终端会自动加载。

### Q: 为什么在当前终端还要 source？
A: 因为当前终端是在配置之前打开的，所以需要手动加载一次。重新打开终端后就不需要了。

### Q: 如何确认我使用的是 Oh My Zsh？
A: 在终端输入 `echo $SHELL`，如果输出 `/bin/zsh` 就说明你在使用 Zsh。

### Q: 如何查看剩余调用次数？
A: 登录 https://open.bocha.cn → 控制台 → 资源包管理

### Q: 超出免费额度怎么办？
A: 可以购买付费资源包，按需付费，价格实惠。

---

**配置完成时间**: 2026-02-23
**Shell类型**: Oh My Zsh
**配置文件**: ~/.zshrc
**下次需要更新时**: 手动编辑 ~/.zshrc 或运行 `code ~/.zshrc`
