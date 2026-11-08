# Production-tuned Seahub settings for the bridge
# Shorter token TTL = faster permission revocation, but more CheckFileInfo calls.
# Use this if you want tighter security; default (30 min) is fine for most.

ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'https://craft.example.org/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('dxf', 'docx', 'xlsx', 'pdf')
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('dxf', 'docx', 'xlsx', 'pdf')
WOPI_ACCESS_TOKEN_EXPIRATION = 5 * 60   # 5 minutes — aggressive; bridge re-checks CheckFileInfo before each PutFile