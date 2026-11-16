import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from unittest.mock import patch

from coursepilot.server import App,handler_for
from coursepilot.tests.test_domain import FakeProvider


class WorkspaceRoutingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.app=App(self.tmp.name,None,'medium')

    def new_run(self,key):
        with patch('coursepilot.engine.make_provider',return_value=FakeProvider()):
            return self.app.create({'case_key':key,'mode':'human'})

    def serve(self,app=None):
        server=ThreadingHTTPServer(('127.0.0.1',0),handler_for(app or self.app))
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        return 'http://127.0.0.1:'+str(server.server_port)

    def test_each_case_creates_its_own_correct_task_without_mixing_conversations(self):
        b=self.new_run('b');c=self.new_run('c')
        self.assertEqual(2,len(b['tasks']));self.assertEqual(5,len(c['tasks']))
        self.assertNotEqual(b['id'],c['id'])
        self.assertNotEqual(b['case_id'],c['case_id'])
        self.assertEqual([],self.app.get_session(c['id'])['chat'])
        self.assertIn(b['id'],[r['id'] for r in self.app.run_list()])

    def test_saved_snapshot_is_read_only_after_server_restart(self):
        b=self.new_run('b')
        reloaded=App(self.tmp.name,None,'medium')
        view=reloaded.get_session(b['id'])
        self.assertTrue(view['read_only'])
        self.assertEqual(b['case_id'],view['case_id'])
        self.assertIsNone(reloaded.get_session('../../other-file'))
        base=self.serve(reloaded)
        request=Request(base+'/api/message',data=json.dumps({'id':b['id'],'message':'anything'}).encode(),
                        headers={'Content-Type':'application/json','X-CoursePilot-Token':reloaded.token})
        with self.assertRaises(HTTPError) as error:urlopen(request)
        self.assertEqual(404,error.exception.code)

    def test_direct_routes_and_case_bootstrap_work_on_one_server(self):
        b=self.new_run('b');base=self.serve()
        for path in ['/','/cases/a','/cases/b','/cases/b/new','/cases/c','/runs','/runs/'+b['id']]:
            with urlopen(base+path) as response:self.assertEqual(200,response.status)
        with urlopen(base+'/api/bootstrap?case=b') as response:data=json.load(response)
        self.assertEqual(2,len(data['case']['steps']))
        self.assertEqual({'a','b','c'},{c['key'] for c in data['cases']})
        self.assertFalse(next(c for c in data['cases'] if c['key']=='a')['ready'])
        with self.assertRaisesRegex(ValueError,'not ready'):self.app.create({'case_key':'a'})
        with self.assertRaises(HTTPError):urlopen(base+'/runs/../../auth.json')

    def test_existing_live_conversation_can_continue_through_explicit_loopback_bridge(self):
        view=self.new_run('b')
        def remote(base,path,data=None,token=None):
            if path=='/api/bootstrap':return {'token':'private-bridge-token'}
            return view
        with patch.object(App,'remote',side_effect=remote):
            migrated=App(self.tmp.name,None,'medium',attach_servers=['http://127.0.0.1:8766'])
            resumed=migrated.get_session(view['id'])
            self.assertFalse(resumed['read_only'])
            self.assertEqual(view['id'],resumed['id'])
            self.assertEqual(view['state'],resumed['state'])
            self.assertNotIn('private-bridge-token',json.dumps(migrated.run_list()))

    def test_bridge_cannot_target_an_external_host(self):
        with patch.object(App,'remote') as remote:
            with self.assertRaises(ValueError):
                App(self.tmp.name,None,'medium',attach_servers=['https://example.com'])
            remote.assert_not_called()


if __name__=='__main__':unittest.main()
