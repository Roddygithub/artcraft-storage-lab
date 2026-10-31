# >>> artcraft-lab (managed block: up.sh configure replaces it)
# Appended to seahub_settings.py by up.sh. Exactly the configuration the Re-Foundation
# Report §5 targets, except that docx/xlsx/pdf/dxf are routed to the bridge (upstream WordCraft,
# GridCraft, PdfCraft, CADCraft bundles) so the real slice exercises the ArtCraft editors;
# the ODF formats and the rest stay on ONLYOFFICE. An operator picks per extension.
ENABLE_ONLYOFFICE = True
ONLYOFFICE_APIJS_URL = 'http://onlyoffice/web-apps/apps/api/documents/api.js'
ONLYOFFICE_FILE_EXTENSION = ('doc', 'ppt', 'xls', 'odt', 'fodt', 'odp', 'fodp', 'ods', 'fods')
ONLYOFFICE_EDIT_FILE_EXTENSION = ('odt', 'odp', 'ods')
ONLYOFFICE_JWT_SECRET = '__ONLYOFFICE_JWT_SECRET__'

ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'http://bridge:8778/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx', 'pptx', 'deckcraft', 'pdf', 'dxf', 'svg', 'vectorcraft', 'figcraft', 'fig', 'scraft', 'scraftz', 'pcraft', 'png', 'webp', 'designcraft', 'drawio')
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('docx', 'xlsx', 'pptx', 'deckcraft', 'pdf', 'dxf', 'svg', 'vectorcraft', 'figcraft', 'fig', 'scraft', 'scraftz', 'pcraft', 'png', 'webp', 'designcraft', 'drawio')
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60
# <<< artcraft-lab
