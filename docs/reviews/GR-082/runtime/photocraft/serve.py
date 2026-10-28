#!/usr/bin/env python3
"""Serve only synthetic harness/fixture and built bundle on loopback; no gateway."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
runtime=Path(__file__).resolve().parent
bundle=Path('/home/roddy/.cache/artcraft-storage-lab/upstream-refresh-sources/photocraft/dist/web')
class Handler(SimpleHTTPRequestHandler):
 def translate_path(self,path):
  name=path.split('?',1)[0].lstrip('/')
  if name in ('host.html','synthetic.pcraft'):return str(runtime/name)
  return str(bundle/name) if name and '/' not in name and '..' not in name else str(bundle/'index.html')
server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
print('http://127.0.0.1:'+str(server.server_port)+'/host.html',flush=True)
server.serve_forever()
