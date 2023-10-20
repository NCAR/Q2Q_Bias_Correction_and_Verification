import numpy as np
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, HOURLY, MONTHLY
import pdb

def input_filename_def(centerdata,indomain,idate=None,sdate=None,edate=None):
    #change this directory name where the realtime gfs data will be stored
    gfs_raw_nomads_dir='/Users/eriddle/work/data/India/realtime_sample_data/gfs/raw/'
    filedata=[]
    center=centerdata['center_name']
    if center in ['cmcRT_hires_raw']:
        basedir=cmc_raw_dir+center+'/'
        for li,lead in enumerate(centerdata['fcstlist']):
            fname=basedir+lead+'.grb2'
            filedata.append({'basedir':basedir,'filename':fname,\
            'ens_i':0,'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead)})
    elif center in ['gfs_1hr','gfs_3hr']: #Looks for gfs raw realtime data (downloaded straight from Nomads)
        basedir=gfs_raw_nomads_dir
        for li,lead in enumerate(centerdata['fcstlist']):
            fname=basedir+idate.strftime('%Y%m%d%H')+'_'+lead+'.grb2'
            filedata.append({'basedir':basedir,'filename':fname,\
                'ens_i':0,'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead,li=li)})
    elif center in ['gfs_ncar_ds84p1']: #raw NCAR archive of 0.25 degree gfs
        basedir=gfs_raw_ncar_dir+'/'+idate.strftime('%Y')+'/'+idate.strftime('%Y%m%d')+'/'
        for li,lead in enumerate(centerdata['fcstlist']):
            fname=basedir+'gfs.0p25.'+idate.strftime('%Y%m%d%H')+'.'+lead+'.grib2'
            filedata.append({'basedir':basedir,'filename':fname,\
                'ens_i':0,'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead,li=li)})
    elif center in ['wrf_belize']: #Archive of WRF runs for Belize
        basedir=belizewrf_raw_dir+'/'+idate.strftime('%Y')+'/'+idate.strftime('%Y%m%d%H')+'/'
        for li,lead in enumerate(centerdata['fcstlist']):
            fname=basedir+idate.strftime('%y%m%d%H')+'00_wrfout_arw_d02.grb2'+lead+'0000'
            filedata.append({'basedir':basedir,'filename':fname,\
                'ens_i':0,'lead_i':li,'lead_str':lead,'keys':input_key_def(center,lead=lead,li=li)})
    elif center in ['IMDgefs']: #IMD and GFSIndia forecasts
        basedir=india_forecast_realtime_dir+'/'+center+'/raw/'+idate.strftime('%Y')+'/'+idate.strftime('%Y%m%d%H')+'/'
        fname=basedir+'gefsrain0p125_'+idate.strftime('%Y%m%d%H')+'.grib2'
        filedata.append({'basedir':basedir,'filename':fname,'keys':input_key_def(center)})
    elif center in ['IMDgfs']: #IMD and GFSIndia forecasts
        basedir=india_forecast_realtime_dir+'/'+center+'/raw/'+idate.strftime('%Y')+'/'+idate.strftime('%Y%m%d%H')+'/'
        fname=basedir+'gfsrain_'+idate.strftime('%Y%m%d%H')+'.grib'
        filedata.append({'basedir':basedir,'filename':fname,'keys':input_key_def(center)})
    return filedata

def catchment_def(catchname):
    #Defines catchments that are used in the analysis
    catchments=\
        {'BelizeCatchments_orig':\
            {'belize_0p1deg':'Correspondence_Files/cf_Belize0p1deg_to_BelizeCatchments.npz',\
            'ncatch':12,'shapefile':'shapefiles/river_basins_eth.shp','joinid_index':0}}

    if catchname in catchments:
        return catchments[catchname]
    else:
        print('Catchment name not defined')
        return None

def grid_def(gridname):
    #Defines grids that are used in the analysis
    grids={
            'global_0p15deg_reversed':\
                {'lats':np.linspace(-90,90,1201,endpoint=True),\
                 'lons':np.linspace(-180,179.85,2400,endpoint=True),\
                 'nlats':1201,\
                 'nlons':2400},\
            'belize_0p1deg':\
                {'lats':np.linspace(15.85,18.85,31,endpoint=True),\
                 'lons':np.linspace(270.35,272.35,21,endpoint=True),\
                 'nlats':31,\
                 'nlons':21},\
            'global_0p125deg':\
                {'lats':np.linspace(-90.0,90,1441,endpoint=True),\
                 'lons':np.linspace(0,359.875,2880,endpoint=True),\
                 'nlats':1441,\
                 'nlons':2880},\
            'belize_wrf_0p05deg':\
                {'lats':np.array([13.918 , 13.963502 , 14.008994 , 14.054478 , 14.099953 ,\
                           14.145418 , 14.190874 , 14.236321 , 14.28176  , 14.3271885,\
                           14.372608 , 14.418019 , 14.463421 , 14.508813 , 14.554195 ,\
                           14.599568 , 14.644933 , 14.690288 , 14.735633 , 14.780969 ,\
                           14.826295 , 14.871612 , 14.916919 , 14.962216 , 15.007505 ,\
                           15.052784 , 15.098053 , 15.143312 , 15.188561 , 15.233802 ,\
                           15.279032 , 15.324253 , 15.369463 , 15.414664 , 15.459855 ,\
                           15.505036 , 15.550208 , 15.595369 , 15.640521 , 15.685662 ,\
                           15.730794 , 15.775916 , 15.821028 , 15.866129 , 15.911221 ,\
                           15.956302 , 16.001373 , 16.046434 , 16.091484 , 16.136524 ,\
                           16.181555 , 16.226576 , 16.271585 , 16.316584 , 16.361574 ,\
                           16.406553 , 16.45152  , 16.496479 , 16.541426 , 16.586363 ,\
                           16.63129  , 16.676205 , 16.721111 , 16.766006 , 16.81089  ,\
                           16.855764 , 16.900627 , 16.945478 , 16.99032  , 17.035152 ,\
                           17.079971 , 17.12478  , 17.16958  , 17.214367 , 17.259144 ,\
                           17.303911 , 17.348665 , 17.39341  , 17.438143 , 17.482866 ,\
                           17.527576 , 17.572277 , 17.616966 , 17.661646 , 17.706312 ,\
                           17.750969 , 17.795612 , 17.840246 , 17.884869 , 17.929482 ,\
                           17.974081 , 18.01867  , 18.063248 , 18.107813 , 18.152369 ,\
                           18.196913 , 18.241444 , 18.285965 , 18.330475 , 18.374971 ,\
                           18.419458 , 18.463934 , 18.508396 , 18.552849 , 18.59729  ,\
                           18.641718 , 18.686134 , 18.73054  , 18.774935 , 18.819317 ,\
                           18.863686 , 18.908045 , 18.952393 , 18.996727 , 19.04105  ,\
                           19.085361 , 19.129662 , 19.173948 , 19.218225 , 19.26249  ,\
                           19.30674  , 19.35098  , 19.395208 , 19.439425 , 19.483627 ,\
                           19.52782  , 19.572    , 19.616167 , 19.660322 , 19.704466 ,\
                           19.748598 , 19.792717 , 19.836823 , 19.880919 , 19.925    ]),\
                 'lons':np.linspace(269.009,274.448,117,endpoint=True),\
                 'nlats':135,\
                 'nlons':117},\
            'belize_0p25deg':\
                {'lats':np.linspace(13.75,20.0,30,endpoint=True),\
                 'lons':np.linspace(-91.25,-85.5,24,endpoint=True),\
                 'nlats':30,\
                 'nlons':24},\
            'india_0p25deg':\
                {'lats':np.linspace(6.5,38.5,129,endpoint=True),\
                 'lons':np.linspace(66.5,100.0,135,endpoint=True),\
                 'nlats':129,\
                 'nlons':135},\
            'global_0p25deg':\
                {'lats':np.linspace(-90,90,721,endpoint=True),\
                 'lons':np.linspace(0,359.75,1440,endpoint=True),\
                 'nlats':721,\
                 'nlons':1440}}

    if gridname in grids:
        return grids[gridname]
    else:
        print('Grid name not defined')
        return None

def input_key_def(center,ens=None,lead=None,li=None):
    if center in ['gfs_1hr']:
        keys={'lonkey':'lon_0','latkey':'lat_0'}
        acvals1=['']*6+[str(r) for r in range(1,7)]*19
        acvals2=['']*6+['h']*114
        varkeylist=['APCP_P8_L1_GLL0_acc'+r+s for r,s in zip(acvals1,acvals2)]
        if li is None:
            keys['varkey']=varkeylist
        elif type(li) is int:
            keys['varkey']=varkeylist[li]
    elif center in ['gfs_3hr']:
        keys={'lonkey':'longitude','latkey':'latitude','varkey':'tp'}
        #keys={'lonkey':'lon_0','latkey':'lat_0'}
        #acvals1=['']*2+[str(r) for r in range(3,7,3)]*39
        #acvals2=['']*2+['h']*78
        #varkeylist=['APCP_P8_L1_GLL0_acc'+r+s for r,s in zip(acvals1,acvals2)]
        #if li is None:
        #    keys['varkey']=varkeylist
        #elif type(li) is int:
        #    keys['varkey']=varkeylist[li]
    elif center in ['IMDgefs']:
        keys={'lonkey':'longitude','latkey':'latitude','leadkey':'step','varkey':'unknown'}
    elif center in ['IMDgfs']:
        keys={'lonkey':'longitude','latkey':'latitude','leadkey':'step','varkey':'tp'}
    elif center in ['gfs_ncar_ds84p1']:
        keys={'lonkey':'lon_0','latkey':'lat_0'}
        acvals1=['']*2+[str(r) for r in range(3,7,3)]*39
        acvals2=['']*2+['h']*78
        varkeylist=['APCP_P8_L1_GLL0_acc'+r+s for r,s in zip(acvals1,acvals2)]
        if li is None:
            keys['varkey']=varkeylist
        elif type(li) is int:
            keys['varkey']=varkeylist[li]
    elif center in ['wrf_belize']:
        keys={'lonkey':'longitude','latkey':'latitude','varkey':'tp'}
    #    varkeylist=['APCP_P8_L1_GME0_acc']+['APCP_P8_L1_GME0_acc1h']*83
    #    if li is None:
    #        keys['varkey']=varkeylist
    #    elif type(li) is int:
    #        keys['varkey']=varkeylist[li]
    elif center in ['cmcRT_hires_raw']:
        keys={'lonkey':'lon_0','latkey':'lat_0','varkey':'APCP_P8_L1_GLL0_acc'}

    else:
        print('Center not found')
        keys=None
    return keys

def center_def(center):
    c={}
    if  center in ['gfs_1hr']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=['f'+str(num).zfill(3) for num in range(1,121,1)]
        tstep=1
        c={'center_name':center,'center_category':'nomads','ingrid':'global_0p25deg',\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum_gfs_mixed','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.25}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']+c['timestep']#Lead measureing to beginning of accum period

    if  center in ['gfs_3hr']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=['f'+str(num).zfill(3) for num in range(3,243,3)]
        tstep=3
        c={'center_name':center,'center_category':'nomads','ingrid':'global_0p25deg',\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum_gfs_mixed','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.25}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']#Lead measuring to beginning of accum period

    if  center in ['gfs_ncar_ds84p1']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=['f'+str(num).zfill(3) for num in range(3,175,3)]
        tstep=3
        c={'center_name':center,'center_category':'ncar','ingrid':'global_0p25',\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum_gfs_mixed','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.25}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']#Leads measuring to beginning of accum period

    if  center in ['wrf_belize']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        fcstlist=['f'+str(num).zfill(2) for num in range(1,85,1)]
        tstep=1
        c={'center_name':center,'center_category':'belize','ingrid':'belize_wrf_0p05deg',\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'resolution':0.01}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']#Lead measuring to beginning of acc period

    if  center in ['IMDgefs']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        tstep=3600*6*1000000000
        c={'center_name':center,'center_category':'imd','ingrid':'global_0p125deg',\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_onefile','file_dimension_type':'3D_lead',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'ns',\
            'nens':1,'nfcst':40,'resolution':0.0125}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']#Lead measuring to beginning of acc period

    if  center in ['IMDgfs']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        tstep=3600*3*1000000000
        c={'center_name':center,'center_category':'imd','ingrid':'global_0p125deg',\
            'latdir':'NtoS','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_onefile','file_dimension_type':'3D_lead',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'ns',\
            'nens':1,'nfcst':81,'resolution':0.0125}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']#Lead measuring to beginning of acc period

    if  center in ['cmcRT_hires_raw']:
        #list of strings that specify all ensemble members and lead times in the individual file names
        tstep=3
        fcstlist=[str(num).zfill(3) for num in range(3,243,3)]
        c={'center_name':center,'center_category':'cmcftp','ingrids':['global_0p15deg_reversed'],\
            'latdir':'StoN','infile_keys':input_key_def(center),\
            'infile_format':'grb2','type':'forecast_manyfiles','file_dimension_type':'2D',\
            'missingdata':1e20,'multiplier':1,'mindata':-3,'maxdata':40000,\
            'units':'kg m-2','accumtype':'accum','timestep':tstep,'lead_unit':'hours',\
            'fcstlist':fcstlist,'nens':1,\
            'nfcst':len(fcstlist),'ensdata':'one_variable','resolution':0.15}
        c['leads']=np.arange(0,c['nfcst'])*c['timestep']#Lead measuring to beginning of acc period

    return c
