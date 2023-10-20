import matplotlib as mp2
import os
import numpy as np
import matplotlib.pyplot as plt
import pdb
from datetime import datetime
from datetime import timedelta

use_cartopy=False
if use_cartopy:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    from cartopy.io.shapereader import Reader

def basic_map_gridplot(dat,fn,plev_max,lon_key='lon',lat_key='lat',order='latlon',plottype='contour', use_cartopy=use_cartopy):
    p_lev=np.arange(0,plev_max,plev_max/20)
    fig=plt.figure()
    if order == 'latlon':
        lats,lons=np.meshgrid(dat[lat_key],dat[lon_key])
    elif order == 'lonlat':
        lons,lats=np.meshgrid(dat[lon_key],dat[lat_key])
    if use_cartopy:
        ax=plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([dat[lon_key][0],dat[lon_key][-1],dat[lat_key][0],dat[lat_key][-1]],crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE, linewidth=2)
        ax.add_feature(cfeature.BORDERS, linewidth=1)
    else:
        ax=plt.axes()
    data=np.swapaxes(dat.values,0,1)
    if plottype == 'contour':
        if use_cartopy:
            contours=ax.contourf(lons,lats,data,
    				levels=p_lev,
    				transform=ccrs.PlateCarree(),
    				extend='both')
        else:
            contours=ax.contourf(lons,lats,data,
                    levels=p_lev,
                    extend='both')
        cb=fig.colorbar(contours,ax=ax,shrink=0.6)
    if plottype == 'mesh':
        if use_cartopy:
            contours=ax.pcolormesh(lons,lats,data,
                                    transform=ccrs.PlateCarree())
        else:
            contours=ax.pcolormesh(lons,lats,data)

    #cb.ax.tick_params(labelsize=5)
    plt.show()
    #plt.savefig(fn)
    #plt.close()

def plot_shapefile(shpfn,plotfn,lats,lons,use_cartopy=use_cartopy):
    if use_cartopy:
        ax=plt.axes(projection=ccrs.PlateCarree())
        ax.set_extent([-89.5,-88.7,16.4,17.2],crs=ccrs.PlateCarree())
        #ax.set_extent([-89.6,-87.7,15.8,18.9],crs=ccrs.PlateCarree())
        shape_feature=cfeature.ShapelyFeature(Reader(shpfn).geometries(),ccrs.PlateCarree(),edgecolor='red',facecolor='none')
        ax.add_feature(shape_feature,linewidth=2)
        ax.add_feature(cfeature.COASTLINE, linewidth=2)
        ax.add_feature(cfeature.BORDERS, linewidth=1)
    else:
        ax=plt.axes()
    ax.gridlines(draw_labels=True)

    plt.savefig(plotfn)
    plt.close()
