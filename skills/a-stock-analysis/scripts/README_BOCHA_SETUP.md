# 博查API配置完成报告

## ✅ API密钥配置状态

**API密钥**: `sk-b6fb1f3d3a1949fb92583bc8ad6715df` ✅ 有效

**测试结果**: API连接成功，但需要领取免费资源包

---

## 🔑 配置方式（选择其中一种）

### 方式1：临时配置（推荐用于测试）

```bash
# 在当前终端会话中设置
export BOCHA_API_KEY=sk-b6fb1f3d3a1949fb92583bc8ad6715df

# 验证配置
echo $BOCHA_API_KEY
```

### 方式2：永久配置（推荐用于长期使用）

```bash
# 运行一键配置脚本
cd /Volumes/solid\ hard\ disk/github/rxylinux/openclaw/skills/a-stock-analysis/scripts
./setup_bocha_key.sh

# 或者手动添加到 ~/.zshrc（macOS默认）
echo 'export BOCHA_API_KEY=sk-b6fb1f3d3a1949fb92583bc8ad6715df' >> ~/.zshrc
source ~/.zshrc

# 或者手动添加到 ~/.bash_profile（Linux）
echo 'export BOCHA_API_KEY=sk-b6fb1f3d3a1949fb92583bc8ad6715df' >> ~/.bash_profile
source ~/.bash_profile
```

### 方式3：使用 .env 文件（适用于Python项目）

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，已包含你的API密钥
# 在Python中加载：
# from dotenv import load_dotenv
# load_dotenv()
```

---

## ⚠️ 重要：需要领取免费资源包

### 错误信息
```json
{
  "code": "403",
  "message": "You do not have enough money or package quota"
}
```

### 解决步骤

1. **登录博查开放平台**
   - 访问：https://open.bocha.cn
   - 使用你的账号登录

2. **领取免费资源包**
   - 进入「控制台」或「资源包管理」
   - 找到「免费资源包」或「新用户礼包」
   - 点击「领取」

3. **查看资源包状态**
   - 确认已领取成功
   - 查看剩余调用次数

4. **重新测试**
   ```bash
   python3 test_bocha.py
   ```

---

## 📝 API使用示例

### 示例1：搜索股票基本信息
```bash
python3 bocha_search.py 002472 双环传动 --basic
```

### 示例2：搜索最新新闻
```bash
python3 bocha_search.py 002472 双环传动 --news
```

### 示例3：综合搜索
```bash
python3 bocha_search.py 002472 双环传动
```

---

## 🔍 验证配置

### 步骤1：验证环境变量
```bash
# 检查API密钥是否设置
echo $BOCHA_API_KEY

# 应该显示: sk-b6fb1f3d3a1949fb92583bc8ad6715df
```

### 步骤2：运行测试脚本
```bash
cd /Volumes/solid\ hard\ disk/github/rxylinux/openclaw/skills/a-stock-analysis/scripts
python3 test_bocha.py
```

### 步骤3：查看测试结果
- ✅ 成功：显示搜索结果
- ❌ 失败：检查是否已领取资源包

---

## 📚 相关文档

- **API文档**: [BOCHA_API_GUIDE.md](BOCHA_API_GUIDE.md)
- **官方文档**: https://bocha-ai.feishu.cn/wiki/HmtOw1z6vik14Fkdu5uc9VaInBb
- **开放平台**: https://open.bocha.cn

---

## 🆘 常见问题

### Q1: 403错误 "You do not have enough money"
**A**: 需要登录 https://open.bocha.cn 领取免费资源包

### Q2: 如何查看剩余调用次数？
**A**: 登录开放平台 → 控制台 → 资源包管理

### Q3: API密钥会过期吗？
**A**: 不会过期，但可以随时重新生成

### Q4: 超出免费额度后怎么办？
**A**: 可以购买付费资源包，按需付费

---

## 📞 技术支持

- **博查官网**: https://bocha.cn
- **开放平台**: https://open.bocha.cn
- **技术文档**: https://bocha-ai.feishu.cn

---

**配置时间**: 2026-02-23
**API密钥**: sk-b6fb1f3d3a1949fb92583bc8ad6715df
**状态**: ✅ 密钥有效，需领取资源包
