# >>> artcraft-lab (managed block: up.sh configure replaces it)
# Appended to seahub_settings.py by up.sh. Exactly the configuration the Re-Foundation
# Report §5 targets, except that docx/xlsx/pdf/dxf are routed to the bridge (upstream WordCraft,
# GridCraft, PdfCraft, CADCraft bundles) so the real slice exercises the ArtCraft editors;
# Unverified office formats have no replacement route yet. ONLYOFFICE is retired.
ENABLE_ONLYOFFICE = False

ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'http://bridge:8778/wopi/discovery.xml'
OFFICE_WEB_APP_FILE_EXTENSION = ('docx', 'xlsx', 'pdf', 'dxf', 'svg', 'figcraft')
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('docx', 'xlsx', 'pdf', 'dxf', 'svg', 'figcraft')
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60
# <<< artcraft-lab
