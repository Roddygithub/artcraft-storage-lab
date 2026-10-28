#!/usr/bin/env python3
"""A deterministic empty synthetic canvas, no blobs or external files."""
import json,pathlib,zipfile,hashlib
manifest={'format_version':1,'generator':'GR-082 synthetic smoke','document':{
'id':82,'name':'GR-082 synthetic','size':{'width':64,'height':64},'resolution_dpi':72.0,
'mode':'Rgb','depth':'U8','icc_profile':None,'layers':[],'channels':[],
'guides':{'horizontal':[],'vertical':[]},'selection':None,
'metadata':{'xmp':None,'exif':None,'psd_resources':[],'psd_global_blocks':[]},
'global_light':{'angle':120.0,'altitude':30.0}}}
p=pathlib.Path(__file__).with_name('synthetic.pcraft')
with zipfile.ZipFile(p,'w') as z:
 z.writestr(zipfile.ZipInfo('manifest.json',(2026,1,1,0,0,0)),json.dumps(manifest,separators=(',',':')))
print(p.name,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
