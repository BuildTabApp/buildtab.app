"""Validate and package the Duo screenshot sets; does not upload anything."""
from pathlib import Path
import json,zipfile,shutil,hashlib
from PIL import Image,ImageDraw
root=Path(__file__).resolve().parent.parent;base=root/'en-US';report=[]
gallery=['<!doctype html><meta charset="utf-8"><title>BuildTab screenshots</title><style>body{font:16px system-ui;background:#222;color:#eee;padding:24px}section{display:flex;overflow:auto;gap:20px}img{height:360px}a{color:#F0B95A}h2{margin-top:48px}</style><h1>BuildTab 2026.8.2 (3) — iPhone, iPad and iPhone Duo</h1><p>Original simulator captures, branded compositions, and upload ZIPs. Prepared locally; not uploaded. The mixed set alternates inner and outer screens, with each feature appearing once.</p>']
for profile,size in {'iphone':(1320,2868),'ipad':(2064,2752),'duo-inner':(2853,2007),'duo-outer':(1398,2034)}.items():
 files=sorted((base/'final'/profile).glob('*.png'));assert len(files)==10,(profile,len(files))
 gallery.append(f'<h2>{profile}</h2><section>')
 sheet=Image.new('RGB',(1500,1000 if profile!='duo-inner' else 520),'#eeeeee');draw=ImageDraw.Draw(sheet);row=sheet.height//2
 for i,p in enumerate(files):
  with Image.open(p) as im:
   assert im.size==size and im.mode=='RGB',(p,im.size,im.mode)
   im.thumbnail((280,row-40));sheet.paste(im,((i%5)*300+(300-im.width)//2,(i//5)*row+30))
  draw.text(((i%5)*300+10,(i//5)*row+8),p.stem,fill='black')
  report.append({'file':str(p.relative_to(root)),'width':size[0],'height':size[1],'mode':'RGB','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  rel=p.relative_to(root);gallery.append(f'<a href="{rel}"><img src="{rel}"><br>{p.stem}</a>')
 gallery.append('</section>');sheet.save(base/f'preview-{profile}.jpg')
 with zipfile.ZipFile(base/f'{profile}-app-store.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in files:z.write(p,p.name)
mixed=base/'final/duo-mixed';mixed.mkdir(parents=True,exist_ok=True)
for n in range(1,11):
 profile='duo-inner' if n%2 else 'duo-outer';p=next((base/'final'/profile).glob(f'{n:02d}-*.png'));shutil.copy2(p,mixed/p.name)
with zipfile.ZipFile(base/'duo-mixed-app-store.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(mixed.glob('*.png')):z.write(p,p.name)
gallery.append('<h2>Mixed upload set (10 images)</h2><section>')
for p in sorted(mixed.glob('*.png')):
 rel=p.relative_to(root);gallery.append(f'<a href="{rel}"><img src="{rel}"><br>{p.stem}</a>')
gallery.append('</section>')
(root/'preview.html').write_text(''.join(gallery))
(root/'source/validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('Validated 40 opaque PNGs; created five ZIPs and preview.html')
