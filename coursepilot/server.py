from __future__ import annotations
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import secrets
import threading
from urllib.parse import urlparse, parse_qs

from .engine import HERE, Session, load_case
from .providers import DEFAULT_MODELS, model_for, provider_options


class App:
    def __init__(self, output, model, effort, case_path=None, provider_name='codex'):
        self.output, self.model, self.effort = Path(output).resolve(), model, effort
        self.sessions = {}
        self.lock = threading.Lock()
        self.token = secrets.token_urlsafe(32)
        self.case_path=case_path
        self.provider_name=provider_name
        self.case,self.fixture=load_case(case_path)

    def create(self, data):
        agent, mode = data.get('agent','baseline'), data.get('mode','human')
        if agent not in ('baseline','controlled') or mode not in ('human','simulated'): raise ValueError('Invalid condition or mode.')
        provider=data.get('provider',self.provider_name)
        model=model_for(provider,data.get('model') or (self.model if provider==self.provider_name else None))
        session = Session(self.output, agent, mode, model, self.effort,case_path=self.case_path,provider_name=provider)
        with self.lock: self.sessions[session.id] = session
        if mode == 'simulated': threading.Thread(target=session.simulate, daemon=True).start()
        return session.view()


def handler_for(app):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args): pass

        def reply(self, status, data, mime='application/json; charset=utf-8'):
            content = json.dumps(data,ensure_ascii=False).encode() if mime.startswith('application/json') else data
            self.send_response(status)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(content)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'self'")
            self.end_headers()
            self.wfile.write(content)

        def do_GET(self):
            path = urlparse(self.path).path
            if path == '/api/bootstrap':
                self.reply(200,{'token':app.token,'fixture':app.fixture,'case':app.case,
                                'provider':app.provider_name,'model':model_for(app.provider_name,app.model),
                                'providers':provider_options()})
            elif path == '/api/session':
                sid = parse_qs(urlparse(self.path).query).get('id',[''])[0]
                session = app.sessions.get(sid)
                self.reply(200,session.view()) if session else self.reply(404,{'error':'Session not found. Start a new session.'})
            elif path in ('/','/app.js','/style.css'):
                name = {'/':'index.html','/app.js':'app.js','/style.css':'style.css'}[path]
                mime = {'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[name]
                self.reply(200,(HERE/'static'/name).read_bytes(),mime)
            else: self.reply(404,{'error':'Not found'})

        def do_POST(self):
            if self.headers.get('X-CoursePilot-Token') != app.token:
                self.reply(403,{'error':'Refresh this page before making a request.'}); return
            origin = self.headers.get('Origin')
            expected = 'http://' + self.headers.get('Host','')
            if origin and origin != expected:
                self.reply(403,{'error':'Cross-origin requests are not accepted.'}); return
            try:
                length = int(self.headers.get('Content-Length','0'))
                if not 0 < length <= 50000: raise ValueError('Invalid request size.')
                data = json.loads(self.rfile.read(length))
                if not isinstance(data,dict): raise ValueError('Expected a JSON object.')
                if self.path == '/api/new': self.reply(200,app.create(data)); return
                session = app.sessions.get(data.get('id'))
                if session is None: self.reply(404,{'error':'Session not found.'}); return
                if self.path == '/api/message':
                    if session.mode != 'human': raise ValueError('This session is being driven by the simulated student.')
                    result = session.student(data.get('message',''),data.get('intent','chat'),data.get('target',''),data.get('stage'))
                    self.reply(200,result)
                elif self.path == '/api/finish':
                    with session.lock:
                        if session.mode == 'simulated' and not session.frozen:
                            session.env.paused = True
                            session.epoch += 1
                            session.status = 'stopping'
                        else: session.finish()
                    self.reply(200,session.view())
                else: self.reply(404,{'error':'Not found'})
            except (ValueError,TypeError,KeyError) as exc: self.reply(400,{'error':str(exc)})
            except Exception as exc: self.reply(500,{'error':f'{type(exc).__name__}: {exc}'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description='CoursePilot local browser evaluation')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--provider',choices=DEFAULT_MODELS,default='codex')
    parser.add_argument('--model',help='Provider-specific model; defaults to gpt-6.1-sol or sonnet.')
    parser.add_argument('--effort',default='medium',choices=['low','medium','high'])
    parser.add_argument('--output',type=Path,default=HERE/'runs')
    parser.add_argument('--case',type=Path,help='Case JSON; defaults to the approval case.')
    args = parser.parse_args()
    app = App(args.output,args.model,args.effort,args.case,args.provider)
    server = ThreadingHTTPServer(('127.0.0.1',args.port),handler_for(app))
    print(f'CoursePilot: http://127.0.0.1:{args.port}\nFictional records only. Press Ctrl+C to stop.',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__': main()
