import os
import sys
import numpy as np
#sys.stderr=open('/home/waterworld/python/downloads/nomads_err.txt','w')
import definitions
from datetime import datetime
from datetime import timedelta
import pdb
import copy
import requests

download_flag=True
times2try=5
#Download NOMADS files
centers=['gfs']
indomain='global_0p25deg'

url_base='https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file='
fcsthrs=[0,6,12,18]
outfile_base='/Users/eriddle/work/data/India/realtime_sample_data/gfs/raw/'
if not os.path.exists(outfile_base):
            os.makedirs(outfile_base)
grid=definitions.grid_def(indomain)
if download_flag is True:
    for center in centers:
        #Remove older grb files if there are any there
        os.system('/bin/rm '+outfile_base+'/*.grb2')
        date=len(fcsthrs)*[datetime.now().replace(hour=0,minute=0,microsecond=0)]
        for j,fh in enumerate(fcsthrs):
            today=datetime.now().replace(hour=fh,minute=0,second=0,microsecond=0)
            today=today-timedelta(days=1)
            date[j]=today
            #Download forecast from NOMADS server
            fcstlist=['f'+str(num).zfill(3) for num in range(1,121,1)]+['f'+str(num).zfill(3) for num in range(123,243,3)]
            wgetout=np.zeros(len(fcstlist))
            for i,f_str in enumerate(fcstlist):
                outfile=outfile_base+'/'+today.strftime('%Y%m%d%H')+'_'+f_str+'.grb2'
                print(outfile)
#                if i>140:
#                    pdb.set_trace()
                fn=url_base+center+'.t'+today.strftime('%H')+'z.pgrb2.0p25.'+f_str+\
                    '&lev_surface=on&var_APCP=on&leftlon='\
                    +str(int(grid['lons'][0]))+'&rightlon='+str(int(grid['lons'][-1]))+'&toplat='\
                    +str(int(grid['lats'][-1]))+'&bottomlat='\
                    +str(int(grid['lats'][0]))+'&dir=%2F'+center+'.'+today.strftime('%Y%m%d')\
                    +'%2F'+today.strftime('%H')+'%2Fatmos'
                gotfile=False
                attempts=0
                datetotry='today'
                while attempts < times2try:
                    try:
                        req=requests.get(fn,timeout=10)
                        if req.status_code == requests.codes.ok:
                            f=open(outfile,'wb')
                            for chunk in req.iter_content(100000):
                                f.write(chunk)
                            f.close()
                            attempts=times2try
                            gotfile=True
                        elif req.status_code == 404:
                            if datetotry=='today':
                                datetotry=='yesterday'
                                print('File not available, trying previous day')
                                #If file not available, try downloading previous day instead
                                yesterday=today-timedelta(days=1)
                                full_dir=url_base+center+'.'+yesterday.strftime('%Y%m%d')+'/'+yesterday.strftime('%H')
                                fn=url_base+center+'.t'+yesterday.strftime('%H')+'z.pgrb2.0p25.'+f_str+\
                                '&lev_surface=on&var_APCP=on&leftlon='\
                                +str(grid['lons'][0])+'&rightlon='+str(grid['lons'][-1])+'&toplat='+str(grid['lats'][-1])+'&bottomlat='\
                                +str(grid['lats'][0])+'&dir=%2F'+center+'.'+yesterday.strftime('%Y%m%d')\
                                +'%2F'+yesterday.strftime('%H')
                                outfile=outfile_base+centerkey+'/'+yesterday.strftime('%Y%m%d%H')+'_'+f_str+'.grb2'
                                date[j]=yesterday
                            elif datetotry=='yesterday':
                                print('Previous day not available, skipping date')
                                attempts=times2try
                        #req=requests.get(fn,timeout=5)
                        #if req.status_code == requests.codes.ok:
                        #    f=open(outfile,'wb')
                        #    for chunk in req.iter_content(100000):
                        #        f.write(chunk)
                        #    f.close()
                        #    gotfile=True
                        #else:
                    except:
                        attempts+=1
                        print('Download failed, attempts: '+str(attempts))
