# Append to seahub_settings.py (Seafile CE or Pro, Seahub >= 13 for non-office extensions), then
# restart Seahub. Only the extensions listed here go to the bridge; ONLYOFFICE keeps the rest.
ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'https://craft.example.org/wopi/discovery.xml'   # the bridge's public URL
OFFICE_WEB_APP_FILE_EXTENSION = ('dxf', 'svg')                            # view through the bridge
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('dxf', 'svg')                       # edit through the bridge
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60                                     # default is 12 h
# If ONLYOFFICE is enabled, remove these extensions from ONLYOFFICE_FILE_EXTENSION /
# ONLYOFFICE_EDIT_FILE_EXTENSION: Seahub checks OFFICE_WEB_APP first, per extension.
# PDF: Seahub shows its own viewer first; the bridge is reached with ?edit_pdf=true on the file URL.
