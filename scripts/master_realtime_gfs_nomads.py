import forecast_preprocess
from datetime import datetime
import os

date=datetime(2021,6,27,0,0) #Date to run (sample data, for now.  Will be realtime)
obs='IMDobs' #Observations to use as reference
model='gfs' #
realtime_acc=3
archive_acc=24
acc_str='hr'
data_dir_base='/Users/eriddle/work/data/India/' #Main data directory
grid='india_0p25deg' #Common grid to be used in analysis (defined in definitions.py file)
obs_archive_file=data_dir_base+'/archives/'+obs+'_'+grid+'_'+str(archive_acc)+acc_str+'_20160101_to_20191231.nc'
forecast_archive_file=data_dir_base+'/archives/'+model+'_'+grid+'_'+str(archive_acc)+acc_str+'_20160101_to_20201231.nc'

realtime_modelkey=model+'_'+str(realtime_acc)+acc_str #Forecast model to be used, details about the input files from this model are given in the definitions.py file
diagnostic_plots=True #If true, then diagnostic plots will be created
if diagnostic_plots:
    diag_plot_dir=data_dir_base+'/diagnostic_plots/'+model+'/'
    if not os.path.exists(diag_plot_dir):
        os.makedirs(diag_plot_dir)
#Also modify the start of definitions.py to supply the directories where the raw input forecast files are stored. 

#Regridding parameters.   
regrid_in={}
regrid_in['regrid_type']='conservative' #Use conservative for going from a fine to course grid #Use biliear for going from a course to fine grid
regrid_in['forecast_key']=realtime_modelkey 
regrid_in['model']=model
regrid_in['output_grid']=grid
regrid_in['input_acc']=realtime_acc #Input data is 3 hour averages
regrid_in['output_acc']=archive_acc #Output data is 24 hour averages
regrid_in['out_data_dir']=data_dir_base+'/realtime_sample_data/'+model+'/regridded/'
regrid_in['out_data_fn']=data_dir_base+'/realtime_sample_data/'+model+'/regridded/'+model+'_'+grid+'_'+str(archive_acc)+acc_str+'_'+date.strftime('%Y%m%d%H')+'.nc'
regrid_in['diagnostics']=diagnostic_plots
regrid_in['diag_plots_dir']=diag_plot_dir

#Quantile mapping parameters.   
#Make sure the archive files from the observations and the model are correct 
q2q_in={}
q2q_in['obs_archive_file']=obs_archive_file
q2q_in['forecast_archive_file']=forecast_archive_file
q2q_in['diurnal_cycle_filter']=False #Perform bias correction only on same hour of day
q2q_in['seasonal_cycle_filter']=False #Perform bias correction only on same month of the year
q2q_in['out_data_dir']=data_dir_base+'/realtime_sample_data/'+model+'/q2q_corrected/'
q2q_in['out_data_fn']=data_dir_base+'/realtime_sample_data/'+model+'/q2q_corrected/'+model+'_'+grid+'_'+str(archive_acc)+acc_str+'_'+date.strftime('%Y%m%d%H')+'.nc'
q2q_in['diagnostics']=diagnostic_plots
q2q_in['diag_plots_dir']=diag_plot_dir
q2q_in['date']=date
q2q_in['acc_period_str']=str(archive_acc)+acc_str
q2q_in['forecast_model']=model #'wrf_belize','gfs_ncar_ds85p1','gfs_hires_3hrly','cmc'

ds_out=forecast_preprocess.regrid_forecast(date,regrid_in)
forecast_preprocess.bias_correct_forecast(q2q_in,ds_out)
