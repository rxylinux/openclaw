#!/usr/bin/env python3
"""
gemini_bridge.py v1 — Talk to Gemini via Chrome automation (macOS)

Chrome 支持 AppleScript `do JavaScript`，类似 Safari。

前置条件:
  Chrome 已登录 gemini.google.com
  Chrome > 允许 Apple Events (系统设置 > 隐私与安全性 > 自动化)

用法:
  python3 gemini_bridge.py --port 19999
  curl -X POST http://localhost:19999/chat -d '{"prompt":"hello"}'
"""
import json,time,threading,re,argparse,subprocess,uuid
from http.server import HTTPServer,BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

GEMINI_URL='https://gemini.google.com'
VERSION='v1'

# Gemini 输入框选择器
INPUT_SELECTORS=['textarea[placeholder*="输入"]','div[contenteditable="true"]','[data-test-id="prompt-textarea"]']
# 发送按钮选择器
SEND_SELECTORS=['button[aria-label*="发送"]','button[aria-label*="send"]','button[data-test-id="send-button"]']

class GeminiSession:
    """管理单个 Gemini 会话（对应一个 Chrome 标签页）"""
    def __init__(self, session_id):
        self.session_id = session_id
        self.lock = threading.Lock()

class GeminiBridge:
    def __init__(self):
        self.sessions = {}  # session_id -> GeminiSession
        self.lock = threading.Lock()
        self.default_session = None

    def _osa(self,script,timeout=30):
        """执行 AppleScript"""
        r=subprocess.run(['osascript','-e',script],capture_output=True,text=True,timeout=timeout)
        if r.returncode!=0:
            raise RuntimeError(f'osascript: {r.stderr.strip()[:200]}')
        return r.stdout.strip()

    def _js(self,js,timeout=30):
        """在 Chrome 当前标签页执行 JS"""
        esc=js.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
        return self._osa(f'tell application "Google Chrome" to do JavaScript "{esc}" in current tab of front window',timeout)

    def _ensure_gemini(self):
        """导航到 gemini.google.com 如果不在那里"""
        try:
            url=self._osa('tell application "Google Chrome" to get URL of current tab of front window')
        except:
            url=''
        if 'gemini.google.com' not in url:
            self._osa(f'tell application "Google Chrome" to set URL of current tab of front window to "{GEMINI_URL}"')
            time.sleep(4)

    def _find_input(self):
        """查找输入框"""
        for sel in INPUT_SELECTORS:
            r=self._js(f"!!document.querySelector('{sel}')")
            if r=='true':
                return sel
        return None

    def _wait_ready(self,timeout=20):
        """等待页面就绪"""
        start=time.time()
        while time.time()-start<timeout:
            sel=self._find_input()
            if sel:
                return sel
            time.sleep(0.5)
        return None

    def _type_and_send(self,text,input_sel):
        """输入文本并发送"""
        # 激活 Chrome
        self._osa('tell application "Google Chrome" to activate')
        time.sleep(0.3)

        # 聚焦输入框并插入文本
        safe=text.replace('\\','\\\\').replace("'","\\'").replace('\n','\\n').replace('\r','')
        self._js(f"""(()=>{{
            const el=document.querySelector('{input_sel}');
            if(!el)return'NO';
            el.focus();
            if(el.tagName==='TEXTAREA'){{
                el.value='';
            }}else{{
                el.textContent='';
            }}
            document.execCommand('insertText',false,'{safe}');
            return'OK';
        }})()""")
        time.sleep(0.5)

        # 点击发送按钮
        for btn_sel in SEND_SELECTORS:
            r=self._js(f"(()=>{{const b=document.querySelector('{btn_sel}');if(b&&!b.disabled){{b.click();return'OK'}};return'NO'}})()")
            if 'OK' in str(r):
                return True

        # 回退方案：发送 Enter
        self._js(f"document.querySelector('{input_sel}')?.dispatchEvent(new KeyboardEvent('keydown',{{key:'Enter',code:'Enter',keyCode:13,bubbles:true}}))")
        return True

    def _get_body(self):
        """获取页面文本"""
        return self._js('document.body.innerText',timeout=15)

    def _clean(self,text):
        """清理 Gemini UI 干扰"""
        # 移除 UI 提示
        for m in ['\nEnter a prompt','\nType your message','\nGemini','\nShare','\nCopy','\nRegenerate']:
            i=text.rfind(m)
            if i>0:
                text=text[:i]
        # 移除时间戳
        text=re.sub(r'\n[0-9]+(\.[0-9]+)?s\n','\n',text)
        # 移除按钮文字
        text=re.sub(r'\n(Share|Copy|Regenerate|New chat|Settings).*','',text)
        # 合并多余空行
        text=re.sub(r'\n{3,}','\n\n',text)
        return text.strip()

    def _extract(self,body,prompt):
        """从响应中提取 AI 回复"""
        marker=prompt[:60]
        parts=body.split(marker)
        after=parts[-1] if len(parts)>=2 else body
        return self._clean(after)

    def chat(self,prompt,timeout=120,session_id=None):
        """发送聊天请求"""
        session=self._get_session(session_id)
        with session.lock:
            return self._chat(prompt,timeout)

    def _chat(self,prompt,timeout):
        """内部聊天实现"""
        try:
            self._ensure_gemini()
            sel=self._wait_ready()
            if not sel:
                return {'status':'error','error':'input not found'}

            body_before=self._get_body()
            self._type_and_send(prompt,sel)

            # 轮询直到响应稳定
            start=time.time()
            last=''
            stable=0

            while time.time()-start<timeout:
                time.sleep(2)
                body=self._get_body()

                # 响应出现且稳定
                if body!=body_before and body==last:
                    stable+=1
                    if stable>=3:
                        return {
                            'status':'ok',
                            'response':self._extract(body,prompt),
                            'elapsed':round(time.time()-start,1)
                        }
                else:
                    stable=0
                last=body

            # 超时
            resp=self._extract(last,prompt) if last else ''
            return {
                'status':'timeout',
                'response':resp,
                'elapsed':round(time.time()-start,1)
            }
        except Exception as e:
            return {'status':'error','error':str(e)}

    def new_session(self):
        """创建新会话（新标签页）"""
        try:
            self._osa(f'tell application "Google Chrome" to make new tab with properties {{URL:"{GEMINI_URL}"}}')
            time.sleep(3)
            return {'status':'ok'}
        except Exception as e:
            return {'status':'error','error':str(e)}

    def history(self):
        """读取当前会话历史"""
        try:
            body=self._get_body()
            return {
                'status':'ok',
                'content':self._clean(body),
                'raw_length':len(body)
            }
        except Exception as e:
            return {'status':'error','error':str(e)}

    def health(self):
        """健康检查"""
        try:
            url=self._osa('tell application "Google Chrome" to get URL of current tab of front window')
            return {
                'status':'ok',
                'url':url,
                'on_gemini':'gemini.google.com' in url,
                'version':VERSION
            }
        except:
            return {
                'status':'error',
                'error':'chrome not reachable',
                'version':VERSION
            }

    def _get_session(self,session_id):
        """获取或创建会话"""
        with self.lock:
            if session_id is None:
                session_id='default'
            if session_id not in self.sessions:
                self.sessions[session_id]=GeminiSession(session_id)
            return self.sessions[session_id]

bridge=None

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass

    def _json(self,status,data):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data,ensure_ascii=False).encode())

    def do_POST(self):
        try:
            content_length=int(self.headers.get('Content-Length',0))
            body=self.rfile.read(content_length).decode('utf-8')
            data=json.loads(body) if body else {}
        except:
            self.send_response(400)
            self.end_headers()
            return

        if self.path=='/chat':
            prompt=data.get('prompt','')
            timeout=data.get('timeout',120)
            session_id=data.get('session_id')

            if not prompt:
                self._json(400,{'error':'prompt required','status':'error'})
                return

            ts=time.strftime('%H:%M:%S')
            print(f'[{ts}] >> {prompt[:80]}',flush=True)

            try:
                r=bridge.chat(prompt,timeout,session_id)
                self._json(200,r)
                print(f'[{ts}] << [{r.get("status")}] {str(r.get("response",r.get("error","")))[:80]}',flush=True)
            except Exception as e:
                self._json(500,{'error':str(e),'status':'error'})

        elif self.path=='/new':
            try:
                r=bridge.new_session()
                self._json(200,r)
            except Exception as e:
                self._json(500,{'error':str(e),'status':'error'})

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path=='/health':
            self._json(200,bridge.health())

        elif self.path=='/history':
            try:
                self._json(200,bridge.history())
            except Exception as e:
                self._json(500,{'error':str(e),'status':'error'})

        else:
            self.send_response(404)
            self.end_headers()

class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
    daemon_threads=True

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=19999)
    parser.add_argument('--host',type=str,default='127.0.0.1')
    args=parser.parse_args()

    bridge=GeminiBridge()

    print(f'Gemini Bridge {VERSION} :{args.port}',flush=True)
    print('前置: Chrome > 设置 > 隐私与安全性 > 自动化 > 允许 Google Chrome',flush=True)
    print(f'访问: http://{args.host}:{args.port}/health',flush=True)

    ThreadedHTTPServer((args.host,args.port),RequestHandler).serve_forever()
