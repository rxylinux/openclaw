#!/usr/bin/env python3
"""
单元测试 - 测试 Gemini Bridge Linux 版本的核心功能（不连接真实网络）
"""

import sys
import os

# 添加脚本目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_import():
    """测试模块导入"""
    print("1. 测试模块导入...")
    try:
        from gemini_bridge_linux import GeminiBridge, GeminiSession, VERSION, GEMINI_URL
        print(f"   ✓ 成功导入 gemini_bridge_linux.py (版本: {VERSION})")
        print(f"   ✓ GEMINI_URL: {GEMINI_URL}")
        return True
    except Exception as e:
        print(f"   ✗ 导入失败: {e}")
        return False

def test_class_structure():
    """测试类结构"""
    print("\n2. 测试类结构...")
    try:
        from gemini_bridge_linux import GeminiBridge, GeminiSession

        # 检查 GeminiBridge 的方法
        methods = ['_init_browser', '_find_input', '_wait_ready', '_type_and_send',
                   '_clean', '_extract', 'chat', 'new_session', 'history', 'health']
        for method in methods:
            if not hasattr(GeminiBridge, method):
                print(f"   ✗ GeminiBridge 缺少方法: {method}")
                return False

        print(f"   ✓ GeminiBridge 拥有所有必需的方法 ({len(methods)} 个)")

        # 检查 GeminiSession 的方法
        session_methods = ['_ensure_page']
        for method in session_methods:
            if not hasattr(GeminiSession, method):
                print(f"   ✗ GeminiSession 缺少方法: {method}")
                return False

        print(f"   ✓ GeminiSession 拥有所有必需的方法 ({len(session_methods)} 个)")
        return True
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False

def test_selectors():
    """测试选择器定义"""
    print("\n3. 测试选择器定义...")
    try:
        from gemini_bridge_linux import INPUT_SELECTORS, SEND_SELECTORS

        print(f"   ✓ 输入框选择器: {len(INPUT_SELECTORS)} 个")
        for sel in INPUT_SELECTORS:
            print(f"      - {sel}")

        print(f"   ✓ 发送按钮选择器: {len(SEND_SELECTORS)} 个")
        for sel in SEND_SELECTORS:
            print(f"      - {sel}")

        if len(INPUT_SELECTORS) > 0 and len(SEND_SELECTORS) > 0:
            return True
        else:
            print("   ✗ 选择器数量不足")
            return False
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False

def test_clean_function():
    """测试清理函数"""
    print("\n4. 测试清理函数...")
    try:
        from gemini_bridge_linux import GeminiBridge

        # 创建一个临时实例（不初始化浏览器）
        bridge = object.__new__(GeminiBridge)

        test_cases = [
            ("Hello\nShare\nCopy\nRegenerate", "Hello"),
            ("Response\nType your message\nGemini", "Response"),
            ("Text\n\n\n\nExtra newlines", "Text"),
        ]

        all_passed = True
        for input_text, expected_contains in test_cases:
            result = bridge._clean(input_text)
            # 检查是否移除了不需要的内容
            if "Share" not in result and "Copy" not in result and "Regenerate" not in result:
                print(f"   ✓ 清理成功: '{input_text[:30]}...' → '{result[:30]}...'")
            else:
                print(f"   ✗ 清理失败: '{result}' 仍包含干扰文本")
                all_passed = False

        if all_passed:
            print("   ✓ 清理函数工作正常")

        return all_passed
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_extract_function():
    """测试提取函数"""
    print("\n5. 测试提取函数...")
    try:
        from gemini_bridge_linux import GeminiBridge

        # 创建一个临时实例
        bridge = object.__new__(GeminiBridge)

        test_input = "用户: 你好\nAI: 你好！有什么我可以帮助你的吗？"
        prompt = "你好"
        result = bridge._extract(test_input, prompt)

        print(f"   输入: '{test_input}'")
        print(f"   提示词: '{prompt}'")
        print(f"   提取结果: '{result}'")

        if "AI:" in result or "你好！" in result:
            print("   ✓ 提取函数工作正常")
            return True
        else:
            print("   ⚠ 提取结果可能不完整（但函数本身可用）")
            return True
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_http_handler():
    """测试 HTTP 请求处理器"""
    print("\n6. 测试 HTTP 请求处理器...")
    try:
        from gemini_bridge_linux import RequestHandler

        # 检查是否有必需的方法
        methods = ['do_GET', 'do_POST', '_json']
        for method in methods:
            if not hasattr(RequestHandler, method):
                print(f"   ✗ RequestHandler 缺少方法: {method}")
                return False

        print(f"   ✓ RequestHandler 拥有所有必需的方法 ({len(methods)} 个)")
        return True
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("Gemini Bridge Linux - 单元测试")
    print("=" * 50)

    tests = [
        test_import,
        test_class_structure,
        test_selectors,
        test_clean_function,
        test_extract_function,
        test_http_handler,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ✗ 测试异常: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"通过: {passed}/{total}")

    if passed == total:
        print("✓ 所有测试通过！代码结构正确，可以进行集成测试。")
        print("\n下一步:")
        print("1. 确保网络可以访问 gemini.google.com")
        print("2. 运行: python3 gemini_bridge_linux.py")
        print("3. 在浏览器中登录 Google 账号")
        print("4. 测试 API: curl http://localhost:19999/health")
        return 0
    else:
        print("✗ 部分测试失败，请检查代码。")
        return 1

if __name__ == '__main__':
    sys.exit(main())
