9/16/2022

Running JupyterLab in the ArcGIS Pro conda environment.

Initial setup:

	Make sure that the arcgis python environment is visible from Jupyter:
		https://support.esri.com/en/technical-article/000019210
			  
		(arcgispro-py3-clone) >python -m ipykernel install --user --name arcgispro-py3-clone --display-name "Python (arcgispro-py3-clone)"
			Installed kernelspec arcgispro-py3-clone in AppData\Roaming\jupyter\kernels\arcgispro-py3-clone
		(arcgispro-py3-clone) >jupyter-lab

		Install nodejs 5+ and npm before continuing:
			>conda install -c esri nodejs ipympl
			
		Enable extensions for Jupyter-lab:
			>jupyter labextension install arcgis-map-ipywidget
			
		Now you can select arcgispro-py3-clone conda environment from within Jupyter Lab.
		
We will do this to test some of the capabilities of the libraries, and avoid messing up Esri Notebooks.

	Typical method for launching Jupyter Lab:
		(arcgispro-py3-clone) >cd notebooks
		(arcgispro-py3-clone) >jupyter-lab