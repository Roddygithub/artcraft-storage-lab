"""The default zero-patch candidate must keep lab-only ports and PPTX out."""
import ast
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
editors = json.loads((root / 'lab/real-seafile/editors.json').read_text())
assert set(editors) == {'wordcraft', 'gridcraft', 'pdfcraft', 'cadcraft', 'vectorcraft', 'figcraft'}
extensions = {ext for entry in editors.values() for ext in entry['extensions']}
assert extensions == {'docx', 'xlsx', 'pdf', 'dxf', 'svg', 'figcraft'}

def settings(path):
    return {node.targets[0].id: ast.literal_eval(node.value)
            for node in ast.parse(path.read_text()).body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and (node.targets[0].id.endswith('_EXTENSION') or node.targets[0].id == 'ENABLE_ONLYOFFICE')}

lab = settings(root / 'lab/real-seafile/seahub_settings.extra.py')
for name in ('OFFICE_WEB_APP_FILE_EXTENSION', 'OFFICE_WEB_APP_EDIT_FILE_EXTENSION'):
    assert set(lab[name]) == extensions
assert lab['ENABLE_ONLYOFFICE'] is True
assert 'pptx' in lab['ONLYOFFICE_FILE_EXTENSION']
assert 'pptx' in lab['ONLYOFFICE_EDIT_FILE_EXTENSION']
deploy = settings(root / 'deploy/bridge/seahub_settings.example.py')
shipped = json.loads((root / 'deploy/bridge/editors.json').read_text())
assert {ext for entry in shipped.values() for ext in entry['extensions']} == set(deploy['OFFICE_WEB_APP_FILE_EXTENSION'])
assert deploy['OFFICE_WEB_APP_EDIT_FILE_EXTENSION'] == deploy['OFFICE_WEB_APP_FILE_EXTENSION']
print('PASS: zero-patch candidate scope, consistent discovery, PPTX on ONLYOFFICE')

# Execute the pure HTTP predicate without importing network runner state.
import re
source = ast.parse((root / 'lab/real-seafile/run_slice.py').read_text())
node = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'onlyoffice_page_ready')
namespace = {'re': re}
exec(compile(ast.Module(body=[node], type_ignores=[]), '<onlyoffice predicate>', 'exec'), namespace)
ready = namespace['onlyoffice_page_ready']
assert ready("api/documents/api.js; err: ''")
assert not ready("api/documents/api.js; err: 'Office Online failed'")
assert not ready("api/documents/api.js")
assert not ready("err: ''")
print('PASS: ONLYOFFICE HTTP gate rejects blocking Seahub error')

nginx = (root / 'deploy/bridge/nginx.conf.example').read_text()
dockerfile = (root / 'deploy/bridge/Dockerfile').read_text()
assert 'access_log off;' in nginx
assert not any('add_header X-Frame-Options' in line for line in nginx.splitlines())
assert '--access-logfile' not in dockerfile and '--access-logformat' not in dockerfile
print('PASS: deployment omits capability-bearing access logs and conflicting frame header')
