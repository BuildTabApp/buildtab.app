"""Capture the offline fixture; select the matching Duo pose in Device Hub first."""
import argparse,subprocess,time
from pathlib import Path
from PIL import Image,ImageStat
p=argparse.ArgumentParser();p.add_argument('--device',required=True);p.add_argument('--app',required=True);p.add_argument('--profile',required=True,choices=['iphone','ipad','duo-outer','duo-inner']);p.add_argument('--display',default='1');p.add_argument('--routes',nargs='+',default=['dashboard','project','expense','materials','time','pricing','spending','expenses','export','dark']);a=p.parse_args()
root=Path(__file__).resolve().parent.parent;bundle='app.buildtab.listingdemo'
def sim(*args,check=True):return subprocess.run(['xcrun','simctl',*args],check=check)
sim('install',a.device,a.app)
sim('status_bar',a.device,'override','--time','9:41','--dataNetwork','wifi','--wifiMode','active','--wifiBars','3','--batteryState','charged','--batteryLevel','100')
sim('ui',a.device,'content_size','large')
out=root/'en-US/raw'/a.profile;out.mkdir(parents=True,exist_ok=True)
for route in a.routes:
 sim('terminate',a.device,bundle,check=False)
 sim('launch',a.device,bundle,'-AppleLanguages','(en-US)','-AppleLocale','en_US','-screenshotRoute',route,'-appearanceMode','Dark' if route=='dark' else 'Light','-screenshotLandscape','YES' if a.profile=='duo-inner' else 'NO')
 path=out/(route+'.png')
 expected={'iphone':(1320,2868),'ipad':(2064,2752),'duo-outer':(1398,2034),'duo-inner':(2853,2007)}[a.profile]
 for attempt in range(6):
  time.sleep(8 if attempt==0 else 4)
  sim('io',a.device,'screenshot','--display='+a.display,'--mask=ignored',str(path))
  with Image.open(path) as im:
   valid=im.size==expected and max(ImageStat.Stat(im.convert('RGB')).stddev)>3
  if valid:break
  print('Waiting for display to settle',route,attempt+1,flush=True)
 assert valid,('Display size or blank capture',path)
 print('Captured',a.profile,route,flush=True)
sim('terminate',a.device,bundle,check=False)
