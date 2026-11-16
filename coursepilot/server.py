from __future__ import annotations
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import secrets
import threading
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from .engine import HERE, Session, load_case
from .providers import DEFAULT_MODELS, model_for, provider_options


class App:
    def __init__(self, output, model, effort, case_path=None, provider_name='codex', attach_servers=()):
        self.output, self.model, self.effort = Path(output).resolve(), model, effort
        self.sessions = {}
        self.lock = threading.Lock()
        self.token = secrets.token_urlsafe(32)
        self.case_path=case_path
        self.provider_name=provider_name
        self.case,self.fixture=load_case(case_path)
        self.cases={}
        for key,name,label in [('a','aditya_a.json','Case A · Requirements'),('b','hudson_b.json','Case B · Corrections'),('c','approval_v2.json','Case C · Approval')]:
            path=HERE/'cases'/name
            if path.exists():
                try:case,fixture=load_case(path)
                except (OSError,ValueError,KeyError):
                    if key=='a':continue
                    raise
                if case['id'].startswith('TEMPLATE'):continue
                if key=='a' and (not case.get('steps') or not case.get('success')):continue
                self.cases[key]={'key':key,'label':label,'path':path,'case':case,'fixture':fixture}
        self.default_case=next((k for k,v in self.cases.items() if v['case']['id']==self.case['id']),None)
        if self.default_case is None:
            self.default_case='custom'
            self.cases['custom']={'key':'custom','label':self.case['title'],'path':case_path,'case':self.case,'fixture':self.fixture}
        self.records={}
        self.legacy={}
        roots=[self.output,HERE/'browser-runs',HERE/'runs',HERE/'case-b-runs',HERE/'provider-checks',HERE/'interface-checks']
        for root in roots:
            if not root.exists():continue
            for config_path in root.rglob('config.json'):
                try:
                    config=json.loads(config_path.read_text(encoding='utf-8'))
                    if config.get('schema_version')==2 and config.get('run_id')==config_path.parent.name and (config_path.parent/'assessment.json').exists():
                        self.records[config['run_id']]=config_path.parent
                except (ValueError,OSError):continue
        # Optional bridge keeps an already-open conversation alive during migration.
        for base in attach_servers:
            parsed=urlparse(base)
            if parsed.scheme!='http' or parsed.hostname not in ('127.0.0.1','localhost') or not parsed.port or parsed.path not in ('','/') or parsed.query or parsed.fragment or parsed.username:
                raise ValueError('Attached servers must be explicit loopback HTTP addresses.')
            base=base.rstrip('/')
            try:
                token=self.remote(base,'/api/bootstrap')['token']
                for sid,folder in self.records.items():
                    config=json.loads((folder/'config.json').read_text(encoding='utf-8'))
                    if not config.get('finalized'):
                        try:
                            view=self.remote(base,'/api/session?id='+sid)
                            if not view.get('finalized'):self.legacy[sid]=(base,token)
                        except (URLError,ValueError):pass
            except (URLError,ValueError):pass

    @staticmethod
    def remote(base,path,data=None,token=None):
        headers={'X-CoursePilot-Token':token} if token else {}
        if data is not None:headers['Content-Type']='application/json'
        request=Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
        with urlopen(request,timeout=5) as response:return json.load(response)

    def case_info(self,key=None):
        key=key or self.default_case
        if key=='a' and key not in self.cases:raise ValueError('Case A is not ready to run yet.')
        if key not in self.cases:raise ValueError('Unknown case.')
        return self.cases[key]

    def case_list(self):
        rows=[{'key':v['key'],'label':v['label'],'id':v['case']['id'],'title':v['case']['title'],
               'steps':len(v['case']['steps']),'ready':True} for v in self.cases.values()]
        if 'a' not in self.cases:
            rows.append({'key':'a','label':'Case A · Requirements','id':'A-pending','title':'Aditya’s required-course and preference case','steps':0,'ready':False})
        return sorted(rows,key=lambda c:c['key'])

    def get_session(self,sid):
        if sid in self.sessions:
            view={**self.sessions[sid].view(),'read_only':False}
            view['can_recover']=self.recoverable(view)
            return view
        if sid in self.legacy:
            base,_=self.legacy[sid]
            try:return {**self.remote(base,'/api/session?id='+sid),'read_only':False}
            except URLError: self.legacy.pop(sid,None)
        folder=self.records.get(sid)
        if folder is None:return None
        read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
        config,assessment,trace,reward=map(read,['config.json','assessment.json','trajectory.json','reward.json'])
        events=trace['events']
        chat=[{'role':'user' if e['actor']=='user' else 'assistant','message':e['message'],
               'reports':e.get('reports',[]),'timestamp':e['timestamp']}
              for e in events if e['kind']=='message' and e['actor'] in ('user','agent')]
        stages=[e.get('stage',0) for e in events if e['kind']=='message' and e['actor']=='user']
        view={'id':sid,'agent':config['agent'],'mode':config['mode'],'status':config['status'],
                'busy':False,'finalized':config.get('finalized',False),'read_only':True,'error':config.get('error'),
                'stage':max(stages,default=0),'case_id':config['case_id'],'case_title':config['case']['title'],
                'inference':config['agent_model'],'tasks':config['user_stages'],'chat':chat,
                'state':assessment['state'],'metrics':reward,'output_folder':str(folder),
                'events':[{k:e[k] for k in ('sequence','kind','actor','timestamp')} for e in events[-20:]]}
        audit=folder.parent/'case-b-summary.json'
        if audit.exists():
            rows=json.loads(audit.read_text(encoding='utf-8')).get('runs',[])
            match=next((row for row in rows if row['run_id']==sid),None)
            if match:view['audited_metrics']=match.get('audited_core_metrics')
        view['notice']=config.get('continuation',{}).get('note','')
        view['can_recover']=self.recoverable(view)
        return view

    @staticmethod
    def recoverable(view):
        return bool(not view.get('finalized') and view.get('mode')=='human' and view.get('status')=='error'
                    and view.get('case_id')=='B-correction-preservation-v1'
                    and 'Native Claude tool draft_plan' in (view.get('error') or ''))

    def recover(self,sid):
        from .recovery import recover_saved_draft
        with self.lock:
            view=self.get_session(sid)
            if not view or not self.recoverable(view):raise ValueError('This run has no supported saved-response recovery.')
            folder=self.sessions[sid].output if sid in self.sessions else self.records[sid]
            self.sessions[sid]=recover_saved_draft(folder)
            self.legacy.pop(sid,None)
            return self.get_session(sid)

    def run_list(self):
        ids=set(self.records)|set(self.sessions)
        rows=[]
        for sid in sorted(ids,reverse=True):
            try:
                view=self.get_session(sid)
                if view is None:continue
                rows.append({k:view[k] for k in ('id','case_id','case_title','agent','mode','status','finalized','read_only')}
                            | {'model':view['inference']['model_version'],'provider':view['inference'].get('provider',''),
                               'user_turns':view['metrics']['user_turns']})
            except (ValueError,OSError,KeyError):continue
        return rows

    def create(self, data):
        agent, mode = data.get('agent','baseline'), data.get('mode','human')
        if agent not in ('baseline','controlled') or mode not in ('human','simulated'): raise ValueError('Invalid condition or mode.')
        provider=data.get('provider',self.provider_name)
        model=model_for(provider,data.get('model') or (self.model if provider==self.provider_name else None))
        selected=self.case_info(data.get('case_key'))
        session = Session(self.output, agent, mode, model, self.effort,case_path=selected['path'],provider_name=provider)
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
                key=parse_qs(urlparse(self.path).query).get('case',[app.default_case])[0]
                try:selected=app.case_info(key) if not(key=='a' and 'a' not in app.cases) else {'key':'a','case':None,'fixture':None}
                except ValueError:self.reply(404,{'error':'Unknown case.'});return
                self.reply(200,{'token':app.token,'fixture':selected['fixture'],'case':selected['case'],
                                'case_key':selected['key'],'cases':app.case_list(),
                                'provider':app.provider_name,'model':model_for(app.provider_name,app.model),
                                'providers':provider_options()})
            elif path == '/api/runs':self.reply(200,app.run_list())
            elif path == '/api/session':
                sid = parse_qs(urlparse(self.path).query).get('id',[''])[0]
                view=app.get_session(sid)
                self.reply(200,view) if view else self.reply(404,{'error':'Run not found.'})
            elif path in ('/','/runs','/cases/a','/app.js','/style.css','/chat.css','/chat-format.js','/presentation.js') or path in [p for k in app.cases for p in ('/cases/'+k,'/cases/'+k+'/new')] or (path.startswith('/runs/') and path[6:] in (set(app.records)|set(app.sessions))):
                name = {p:p[1:] for p in ('/app.js','/style.css','/chat.css','/chat-format.js','/presentation.js')}.get(path,'index.html')
                mime = 'text/html; charset=utf-8' if name.endswith('.html') else 'text/css; charset=utf-8' if name.endswith('.css') else 'text/javascript; charset=utf-8'
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
                if self.path == '/api/recover':self.reply(200,app.recover(data.get('id')));return
                if data.get('id') in app.legacy and self.path in ('/api/message','/api/finish'):
                    base,token=app.legacy[data['id']]
                    self.reply(200,app.remote(base,self.path,data,token));return
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
    parser.add_argument('--output',type=Path,default=HERE/'browser-runs')
    parser.add_argument('--case',type=Path,help='Extra/default case JSON; built-in cases share the same site.')
    parser.add_argument('--attach-server',action='append',default=[],help='Keep an existing loopback server conversation reachable from this site.')
    args = parser.parse_args()
    app = App(args.output,args.model,args.effort,args.case,args.provider,args.attach_server)
    server = ThreadingHTTPServer(('127.0.0.1',args.port),handler_for(app))
    print(f'CoursePilot: http://127.0.0.1:{args.port}\nFictional records only. Press Ctrl+C to stop.',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__ == '__main__': main()
