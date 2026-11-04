"""Render BuildTab-branded compositions around unmodified simulator captures."""
from pathlib import Path
import subprocess,json,html,sys
from PIL import Image
root=Path(__file__).resolve().parent.parent
shots=json.loads((root/'source/metadata.json').read_text())
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
for profile,(w,h,iw,top) in {'iphone':(1320,2868,1050,480),'ipad':(2064,2752,1640,500),'duo-outer':(1398,2034,1030,450),'duo-inner':(2853,2007,2050,500)}.items():
 if len(sys.argv)>1 and profile not in sys.argv[1:]:continue
 pages=root/'en-US/source'/profile;pages.mkdir(parents=True,exist_ok=True)
 output=root/'en-US/final'/profile;output.mkdir(parents=True,exist_ok=True)
 for n,shot in enumerate(shots,1):
  raw=root/'en-US/raw'/profile/(shot['route']+'.png')
  with Image.open(raw) as im:assert im.size==(w,h),(raw,im.size)
  title=html.escape(shot['title']).replace('\n','<br>');subtitle=html.escape(shot['subtitle'])
  inner=profile in ('ipad','duo-inner');left=150 if inner else 90;headline=116 if inner else 96
  page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>{shot['route']}</title><style>
@font-face{{font-family:DM;src:url(../../../source/fonts/DMSans-Bold.woff2);font-weight:700}}
@font-face{{font-family:DM;src:url(../../../source/fonts/DMSans-Regular.woff2);font-weight:400}}
*{{box-sizing:border-box}}html,body{{margin:0;width:{w}px;height:{h}px;overflow:hidden;background:#2D2D2D;color:#F2F2F7;font-family:DM}}
body{{background:radial-gradient(ellipse at 90% 90%,#57412b 0,transparent 60%),#2D2D2D}}
.brand{{position:absolute;left:{left}px;top:40px;color:#E8A33C;font-size:30px;font-weight:700;letter-spacing:2px}}
.tag{{position:absolute;right:45px;top:42px;color:#C8C8CC;font-size:23px}}
h1{{position:absolute;left:{left}px;top:108px;margin:0;font:700 {headline}px/1.06 DM;letter-spacing:-2px}}
p{{position:absolute;left:{left+3}px;top:{385 if inner else 340}px;margin:0;font:400 {42 if inner else 34}px/1.3 DM;color:#F0B95A}}
img{{position:absolute;left:{(w-iw)//2}px;top:{top}px;width:{iw}px;height:auto;border-radius:36px;box-shadow:0 20px 70px #0006}}
</style><div class="brand">BUILDTAB</div><div class="tag">Sample data · Pro features shown</div><h1>{title}</h1><p>{subtitle}</p><img src="../../raw/{profile}/{shot['route']}.png" alt="BuildTab {shot['route']}"></html>'''
  src=pages/f'{n:02d}-{shot["route"]}.html';src.write_text(page)
  dest=output/f'{n:02d}-{shot["route"]}.png'
  subprocess.run([chrome,'--headless','--no-sandbox','--hide-scrollbars','--disable-gpu','--no-first-run','--force-device-scale-factor=1',f'--user-data-dir=/tmp/buildtab-listing-chrome-{profile}',f'--window-size={w},{h}','--virtual-time-budget=1000',f'--screenshot={dest}',src.as_uri()],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  with Image.open(dest) as im:im.convert('RGB').save(dest)
  print('Rendered',profile,shot['route'],flush=True)
