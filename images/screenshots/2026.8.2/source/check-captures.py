"""OCR checks supplement visual review; compile ocr.swift first."""
import json,subprocess,argparse,hashlib
from pathlib import Path
from PIL import Image,ImageStat
p=argparse.ArgumentParser();p.add_argument('--ocr',required=True);p.add_argument('--routes',nargs='+');p.add_argument('--profiles',nargs='+');a=p.parse_args();root=Path(__file__).resolve().parent.parent
expected={'dashboard':['Dashboard','Total Spend'],'project':['Walnut writing desk','139.08'],'expense':['Hardwax oil','4.20'],'materials':['Materials','Walnut board'],'time':['Time Entries','Apply the first coat'],'pricing':['Pricing','Suggested Price','411.05'],'spending':['Spending Details','Budget'],'expenses':['Expenses','Walnut boards'],'export':['Export','CSV'],'dark':['Dashboard','Total Spend']}
report=[]
for profile,size in {'iphone':(1320,2868),'ipad':(2064,2752),'duo-outer':(1398,2034),'duo-inner':(2853,2007)}.items():
 if a.profiles and profile not in a.profiles:continue
 for route,words in expected.items():
  if a.routes and route not in a.routes:continue
  file=root/'en-US/raw'/profile/(route+'.png')
  with Image.open(file) as im:
   assert im.size==size,(file,im.size)
   if route=="dark":assert ImageStat.Stat(im.convert("L")).mean[0]<100,("Expected dark appearance",file)
  result=json.loads(subprocess.check_output([a.ocr,str(file)],text=True,timeout=45));text=' '.join(result['text'])
  missing=[word for word in words if word.lower() not in text.lower()]
  report.append({'file':str(file.relative_to(root)),'text':result['text'],'missing':missing,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
  print('Checked',profile,route,missing,flush=True)
if a.routes or a.profiles:
 old=json.loads((root/'source/capture-validation.json').read_text())
 checked={r['file'] for r in report}
 report.extend(r for r in old if r['file'] not in checked)
(root/'source/capture-validation.json').write_text(json.dumps(report,indent=2)+'\n')
failed=[r for r in report if r['missing']]
for r in failed:print(r['file'],r['missing'])
assert not failed,'Review failed captures'
print(f'All {len(report)} captures contain the expected app screens')
