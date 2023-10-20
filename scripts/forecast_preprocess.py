import os
import sys
import numpy as np
import definitions
import read_input_file_xarray
from datetime import datetime
from datetime import timedelta 
import pdb
import xarray as xr
import matplotlib #ADDED

def regrid_forecast(date,p):
    if p['use_cartopy']:
        import plotting_utils
#regrid forecast and consolidate into netcdf in uniform format
    print(date)
     #read in raw model data
    c=definitions.center_def(p['forecast_key'])
    try:
        data=read_input_file_xarray.read_input_files(p['forecast_key'],c['ingrid'],idate=date)
        if c['lead_unit']=='ns':
            data['vardata']['fcstlead']=data['vardata']['fcstlead']/3600/1000000000
        start_date=[date+timedelta(seconds=float(h*3600)) for h in data['vardata']['fcstlead']]
        data_available=True
        if np.sum(~data['vardata']['var'].mask)==0:
            print('Problem getting data for: ')
            print(date)
            data_available=False
    except:
        print('Problem getting data for: ')
        print(date)
        data_available=False
            
    if data_available==True:
        lats=data['vardata']['lat']
        lons=data['vardata']['lon']
        Precipitation=xr.DataArray(data=data['vardata']['var'],dims=["ens","starttime","lat","lon"],\
                    coords=dict(ens=("ens",[0]),starttime=("starttime",start_date),lat=("lat",lats),\
                    lon=("lon",lons)))
    #Resample the time dimension
        if p['input_acc']!=p['output_acc']:
            precip=Precipitation.resample(starttime=str(p['output_acc'])+'H').mean()
            dates=precip.starttime.values
            leads=np.full(len(dates),-999)
            for i,d in enumerate(dates):
                lead=(d-dates[0]).astype('timedelta64[h]').astype('float')
                leads[i]=lead
            ds_in=xr.Dataset(data_vars=dict(Precipitation=(["ens","lead","lat","lon"],precip.values),\
                        start_date=(["lead"],dates)),\
                        coords=dict(ens=("ens",[0]),lead=("lead",leads),lat=("lat",lats),\
                        lon=("lon",lons)))
        else:
            ds_in=xr.Dataset(data_vars=dict(Precipitation=(["ens","lead","lat","lon"],data['vardata']['var']),\
                        start_date=(["lead"],start_date)),\
                        coords=dict(ens=("ens",[0]),lead=("lead",data['vardata']['fcstlead']),lat=("lat",lats),\
                        lon=("lon",lons)))

    #Resample spatial dimension
    domain=p['output_grid']
    #if p['diagnostics']:
    #    if p['use_cartopy']:
    #        plotting_utils.basic_map_gridplot(ds_in.Precipitation[0,5,:,:],p['diag_plots_dir']\
    #           +'raw_'+p['model']+'_'+date.strftime('%Y%m%d%H')+'_lead5.png',10)
    #    else:
    #        ds_in.Precipitation[0,5,:,:].plot()
    lats_out=definitions.grid_def(domain)['lats']
    lons_out=definitions.grid_def(domain)['lons']
    ds_out_ref=xr.Dataset({'lat':(['lat'],lats_out),'lon':(['lon'],lons_out)})
    ds_out=ds_in.interp_like(ds_out_ref)
    ds_out=ds_out.assign(start_date=ds_in.start_date)
    if p['diagnostics']:
        if p['use_cartopy']:
               plotting_utils.basic_map_gridplot(ds_out.Precipitation[0,5,:,:],p['diag_plots_dir']\
                   +'regridded_'+p['model']+'_'+date.strftime('%Y%m%d%H')+'_lead5.png',10)
        else:
            ds_out.Precipitation[0,5,:,:].plot()
    if not os.path.exists(p['out_data_dir']):
        os.makedirs(p['out_data_dir'])
    ds_out.to_netcdf(p['out_data_fn'])
    return ds_out

def q2q(modclim,modclimhour,modclimmon,obsclim,obsclimhour,obsclimmon,fcst,\
        fcsthour,fcstmon,diurnal_cycle_filter,seasonal_cycle_filter):
    if diurnal_cycle_filter:
        modclim=modclim[modclimhour==fcsthour] 
        obsclim=obsclim[obsclimhour==fcsthour]
        modclim=modclim[modclimmon==fcstmon] 
        obsclim=obsclim[obsclimmon==fcstmon]
    if seasonal_cycle_filter & diurnal_cycle_filter:
        modclim=modclim[(modclimmon==fcstmon)&(modclimhour==fcsthour)] 
        obsclim=obsclim[(obsclimmon==fcstmon)&(obsclimmon==fcstmon)]
    modclim=modclim[~np.isnan(modclim)]
    obsclim=obsclim[~np.isnan(obsclim)]
    if ((len(obsclim)==0)|(len(modclim)==0)):
        q2q_corrected=np.nan
    else:
        #Changed segment below to add most recent version of code dealing with zeros better
        first_index=np.searchsorted(np.sort(modclim),fcst,side='left')
        last_index=np.searchsorted(np.sort(modclim),fcst,side='right')
        indval=np.random.choice(np.arange(first_index,last_index+1),1)
        percentile=100*((indval)/len(modclim))
        q2q_corrected=np.percentile(obsclim,percentile)
    return q2q_corrected

def bias_correct_forecast(q2qin,forecast_data):
    if q2qin['use_cartopy']:
        import plotting_utils
    obs_clim_fn=q2qin['obs_archive_file']
    obs_clim=xr.open_dataset(obs_clim_fn)
    model_clim_fn=q2qin['forecast_archive_file']
    model_clim=xr.open_dataset(model_clim_fn)
    q2qdat=xr.Dataset(data_vars={"model_clim":(["clim_idate","lead","lat","lon"],\
            np.squeeze(model_clim.Precipitation).values),\
            "model_clim_start_date":(["clim_idate","lead"],model_clim.start_date.values),\
            "model_forecast":(["lead","lat","lon"],np.squeeze(forecast_data.Precipitation).values),\
            "model_forecast_start_date":(["lead"],forecast_data.start_date.values),\
            "obs_clim":(["obs_date","lat","lon"],obs_clim.Precipitation.values)},\
            coords={"lon":model_clim.lon.values,"lat":model_clim.lat.values,"lead":model_clim.lead.values,\
            "clim_idate":model_clim.initialization_date.values,"obs_date":obs_clim.start_date.values})
    #get months and hours from arrays to use to filter the data
    dcf=q2qin['diurnal_cycle_filter']
    scf=q2qin['seasonal_cycle_filter']
    fcsthr=q2qdat.model_forecast_start_date.dt.hour
    fcstmn=q2qdat.model_forecast_start_date.dt.month
    modclimhr=q2qdat.model_clim_start_date.dt.hour
    modclimmn=q2qdat.model_clim_start_date.dt.month
    obshr=q2qdat.obs_date.dt.hour
    obsmn=q2qdat.obs_date.dt.month
    pcp_new=xr.apply_ufunc(q2q,q2qdat.model_clim,modclimhr,modclimmn,\
                        q2qdat.obs_clim,obshr,obsmn,q2qdat.model_forecast,fcsthr,fcstmn,dcf,scf,\
                        input_core_dims=[['clim_idate'],['clim_idate'],\
                        ['clim_idate'],['obs_date'],['obs_date'],['obs_date'],[],[],[],[],[]],vectorize=True)
    fn=q2qin['out_data_fn']
    ds=xr.Dataset({'Precipitation':(['time','lat','lon'],pcp_new.values,{'units':'mm/hr'})},\
        coords={'lat':(['lat'],pcp_new.lat.values,{'units':'degrees_north'}),
                'lon':(['lon'],pcp_new.lon.values,{'units':'degrees_east'}),
                'forecast_time':(['time'],pcp_new.lead.values,{'units':'hours since '\
                +q2qin['date'].strftime('%Y-%m-%d %H:00')})})
    ds.attrs['Conventions']='CF-1.7'
    ds.attrs['title']='Forecast model run with bias correction'
    ds.attrs['source']=q2qin['forecast_model']
    ds.attrs['history']=str(datetime.utcnow())+' Python'
    ds.attrs['comment']='This file has been bias corrected using '+\
        q2qin['obs_archive_file']+' and '+q2qin['forecast_archive_file']+\
        '.  Diurnal filtering was set to '+str(dcf)+' and seasonal filtering was set to '+str(scf)
    ds.Precipitation.attrs['long_name'] = 'Forecast Total Precipitation in the '+\
        q2qin['acc_period_str']+'period *following* forecast_time, normalized to mm/hr'
    ds.Precipitation.attrs['standard_name'] = 'precipitation_amount'
    if not os.path.exists(q2qin['out_data_dir']):
        os.makedirs(q2qin['out_data_dir'])
    ds.to_netcdf(fn,format='NETCDF4')
    if q2qin['diagnostics']:
        if q2qin['use_cartopy']:
            plotting_utils.basic_map_gridplot(ds.Precipitation[5,:,:],q2qin['diag_plots_dir']+\
                        'q2qcorrected_'+q2qin['forecast_model']+'_'+q2qin['date'].strftime('%Y%m%d%H')+\
                        'q2qcorrected_'+q2qin['forecast_model']+'_'+q2qin['date'].strftime('%Y%m%d%H')+\
                        '_lead5.png',10)
        else:
            #CHANGED SEGMENT BELOW to use new colormap and scaling
            cmap = matplotlib.colormaps['gist_ncar']  # Color ramp suitable for precipiation
            cmap.set_under('lightgrey')               # Set values of zero precipitation to whiteh
            ds.Precipitation[5,:,:].plot(cmap=cmap,vmin=0.001,vmax=5)
    return ds
