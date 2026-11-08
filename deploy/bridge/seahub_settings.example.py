# Append to seahub_settings.py (Seafile CE or Pro, Seahub >= 13 for non-office extensions), then
# restart Seahub. Only the extensions listed here go to the bridge; ONLYOFFICE keeps the rest.
ENABLE_OFFICE_WEB_APP = True
OFFICE_WEB_APP_BASE_URL = 'https://craft.example.org/wopi/discovery.xml'   # the bridge's public URL
OFFICE_WEB_APP_FILE_EXTENSION = ('dxf',)                            # view through the bridge
ENABLE_OFFICE_WEB_APP_EDIT = True
OFFICE_WEB_APP_EDIT_FILE_EXTENSION = ('dxf',)                       # edit through the bridge
WOPI_ACCESS_TOKEN_EXPIRATION = 30 * 60                                     # default is 12 h
# Keep existing ONLYOFFICE settings unchanged; do not disable ONLYOFFICE.
# DOCX/XLSX/PDF are opt-in: add the chosen extensions to BOTH tuples above and add their
# editor entries to editors.json as documented in README.md. WOPI takes precedence for
# those extensions; all other existing ONLYOFFICE routes remain in place.
# PDF: Seahub shows its own viewer first; the bridge is reached with ?edit_pdf=true on the file URL.
