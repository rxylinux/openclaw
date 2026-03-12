#!/usr/bin/env python3
"""
gemini_bridge_linux.py v1 — Talk to Gemini via Playwright (Linux/Windows)

跨平台版本，使用 Playwright 自动化浏览器（Chrome/Chromium）

前置条件:
  pip install playwright
  playwright install chromium

  需要提前登录 gemini.google.com 并保持登录状态

用法:
  python3 gemini_bridge_linux.py --port 19999
  curl -X POST http://localhost:19999/chat -d '{"prompt":"hello"}'
"""
import json, time, threading, re, argparse, uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

GEMINI_URL = 'https://gemini.google.com'
VERSION = 'v1-linux'
BROWSER_TYPE = 'chromium'  # 可改为 'firefox' 或 'webkit'

# Gemini 输入框选择器
INPUT_SELECTORS = [
    'textarea[placeholder*="输入"]',
    'div[contenteditable="true"]',
    '[data-test-id="prompt-textarea"]',
    'textarea[aria-label*="输入"]'
]
# 发送按钮选择器
SEND_SELECTORS = [
    'button[aria-label*="发送"]',
    'button[aria-label*="send"]',
    'button[data-test-id="send-button"]',
    'button[type="submit"]'
]

class GeminiSession:
    """管理单个 Gemini 会话（对应一个浏览器 Context/标签页）"""
    def __init__(self, session_id, browser_context):
        self.session_id = session_id
        self.lock = threading.Lock()
        self.context = browser_context
        self.page = None
        self._ensure_page()

    def _ensure_page(self):
        """确保有活跃的页面"""
        if not self.page or self.page.is_closed():
            self.page = self.context.new_page()
            self.page.goto(GEMINI_URL, wait_until='domcontentloaded')
            time.sleep(2)

class GeminiBridge:
    def __init__(self, headless=False):
        self.sessions = {}  # session_id -> GeminiSession
        self.lock = threading.Lock()
        self.default_session = None
        self.headless = headless
        self.playwright = None
        self.browser = None
        self._init_browser()

    def _init_browser(self):
        """初始化 Playwright 浏览器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox'] if not self.headless else []
        )

        # 使用持久化上下文以保持登录状态
        self.default_context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

    def _find_input(self, page):
        """查找输入框"""
        for sel in INPUT_SELECTORS:
            try:
                elem = page.query_selector(sel)
                if elem and elem.is_visible():
                    return sel
            except:
                continue
        return None

    def _wait_ready(self, page, timeout=20):
        """等待页面就绪"""
        start = time.time()
        while time.time() - start < timeout:
            sel = self._find_input(page)
            if sel:
                return sel
            time.sleep(0.5)
        return None

    def _type_and_send(self, page, text, input_sel):
        """输入文本并发送"""
        # 清空并输入文本
        page.focus(input_sel)
        page.fill(input_sel, '')

        # 使用 type 确保文本正确输入
        page.type(input_sel, text, delay=10)
        time.sleep(0.5)

        # 尝试点击发送按钮
        for btn_sel in SEND_SELECTORS:
            try:
                btn = page.query_selector(btn_sel)
                if btn and btn.is_enabled() and btn.is_visible():
                    btn.click()
                    return True
            except:
                continue

        # 回退方案：按 Enter
        page.keyboard.press('Enter')
        return True

    def _clean(self, text):
        """清理 Gemini UI 干扰"""
        # 移除 UI 提示
        for m in ['\nEnter a prompt', '\nType your message', '\nGemini', '\nShare', '\nCopy', '\nRegenerate', '输入', '发送']:
            i = text.rfind(m)
            if i > 0:
                text = text[:i]

        # 移除时间戳
        text = re.sub(r'\n[0-9]+(\.[0-9]+)?s\n', '\n', text)

        # 移除按钮文字
        text = re.sub(r'\n(Share|Copy|Regenerate|New chat|Settings|输入|发送|分享|复制|重新生成).*', '', text, flags=re.IGNORECASE)

        # 合并多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _extract(self, body, prompt):
        """从响应中提取 AI 回复"""
        marker = prompt[:60]
        parts = body.split(marker)
        after = parts[-1] if len(parts) >= 2 else body

        # 尝试从最后一个换行符后提取（去除用户输入）
        lines = after.split('\n')
        for i, line in enumerate(lines):
            if line.strip() and i > 0:
                return '\n'.join(lines[i:]).strip()

        return after.strip()

    def chat(self, prompt, timeout=120, session_id=None):
        """发送聊天请求"""
        session = self._get_session(session_id)
        with session.lock:
            return self._chat(session, prompt, timeout)

    def _chat(self, session, prompt, timeout):
        """内部聊天实现"""
        try:
            page = session.page
            page.goto(GEMINI_URL, wait_until='domcontentloaded')
            time.sleep(1)

            sel = self._wait_ready(page)
            if not sel:
                return {'status': 'error', 'error': 'input not found'}

            body_before = page.evaluate('() => document.body.innerText')
            self._type_and_send(page, prompt, sel)

            # 轮询直到响应稳定
            start = time.time()
            last = ''
            stable = 0
            wait_time = 0

            while time.time() - start < timeout:
                time.sleep(2)
                wait_time += 2

                try:
                    body = page.evaluate('() => document.body.innerText')

                    # 响应出现且稳定
                    if body != body_before and body == last:
                        stable += 1
                        if stable >= 3:
                            return {
                                'status': 'ok',
                                'response': self._extract(body, prompt),
                                'elapsed': round(time.time() - start, 1)
                            }
                    else:
                        stable = 0

                    last = body
                except Exception as e:
                    # 页面可能还在加载，继续等待
                    pass

            # 超时
            resp = self._extract(last, prompt) if last else ''
            return {
                'status': 'timeout',
                'response': resp,
                'elapsed': round(time.time() - start, 1)
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def new_session(self):
        """创建新会话（新的 Context）"""
        try:
            new_context = self.browser.new_context(
                viewport={'width': 1280, 'height': 800}
            )
            new_session_id = str(uuid.uuid4())[:8]
            self.sessions[new_session_id] = GeminiSession(new_session_id, new_context)
            return {'status': 'ok', 'session_id': new_session_id}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def history(self):
        """读取当前会话历史"""
        try:
            default_session = self._get_session(None)
            page = default_session.page
            if not page or page.is_closed():
                page = default_session.context.new_page()
                page.goto(GEMINI_URL, wait_until='domcontentloaded')
                default_session.page = page

            body = page.evaluate('() => document.body.innerText')
            return {
                'status': 'ok',
                'content': self._clean(body),
                'raw_length': len(body)
            }
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def health(self):
        """健康检查"""
        try:
            if not self.browser or self.browser.is_connected() == False:
                return {
                    'status': 'error',
                    'error': 'browser not connected',
                    'version': VERSION
                }

            # 检查是否有可用的页面
            default_session = self._get_session(None)
            page = default_session.page

            url = page.url if page and not page.is_closed() else 'none'

            return {
                'status': 'ok',
                'url': url,
                'on_gemini': 'gemini.google.com' in url,
                'version': VERSION,
                'browser': 'chromium'
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'version': VERSION
            }

    def _get_session(self, session_id):
        """获取或创建会话"""
        with self.lock:
            if session_id is None:
                session_id = 'default'

            if session_id not in self.sessions:
                self.sessions[session_id] = GeminiSession(session_id, self.default_context)

            return self.sessions[session_id]

    def cleanup(self):
        """清理资源"""
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass

bridge = None

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _json(self, status, data):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
        except:
            self.send_response(400)
            self.end_headers()
            return

        if self.path == '/chat':
            prompt = data.get('prompt', '')
            timeout = data.get('timeout', 120)
            session_id = data.get('session_id')

            if not prompt:
                self._json(400, {'error': 'prompt required', 'status': 'error'})
                return

            ts = time.strftime('%H:%M:%S')
            print(f'[{ts}] >> {prompt[:80]}', flush=True)

            try:
                r = bridge.chat(prompt, timeout, session_id)
                self._json(200, r)
                print(f'[{ts}] << [{r.get("status")}] {str(r.get("response", r.get("error", "")))[:80]}', flush=True)
            except Exception as e:
                self._json(500, {'error': str(e), 'status': 'error'})

        elif self.path == '/new':
            try:
                r = bridge.new_session()
                self._json(200, r)
            except Exception as e:
                self._json(500, {'error': str(e), 'status': 'error'})

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self._json(200, bridge.health())

        elif self.path == '/history':
            try:
                self._json(200, bridge.history())
            except Exception as e:
                self._json(500, {'error': str(e), 'status': 'error'})

        else:
            self.send_response(404)
            self.end_headers()

# 使用单线程 HTTP 服务器，避免 Playwright 线程问题
class SingleThreadHTTPServer(HTTPServer):
    allow_reuse_address = True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=19999)
    parser.add_argument('--host', type=str, default='127.0.0.1')
    parser.add_argument('--headless', action='store_true', help='运行在无头模式（后台）')
    args = parser.parse_args()

    global bridge
    bridge = GeminiBridge(headless=args.headless)

    print(f'Gemini Bridge {VERSION} :{args.port}', flush=True)
    print(f'浏览器: Chromium ({"无头模式" if args.headless else "有头模式"})', flush=True)
    print(f'访问: http://{args.host}:{args.port}/health', flush=True)
    print('', flush=True)
    print('提示:', flush=True)
    print('1. 首次运行时，浏览器窗口会打开 gemini.google.com', flush=True)
    print('2. 请手动登录 Google 账号', flush=True)
    print('3. 后续会话会自动保持登录状态', flush=True)
    print('', flush=True)

    try:
        SingleThreadHTTPServer((args.host, args.port), RequestHandler).serve_forever()
    except KeyboardInterrupt:
        print('\n正在关闭...', flush=True)
        bridge.cleanup()
        print('已关闭', flush=True)

if __name__ == '__main__':
    main()
