# -*- coding: utf-8 -*-
"""
/**************************************************************************************************************************
 SemiAutomaticClassificationPlugin

 The Semi-Automatic Classification Plugin for QGIS allows for the supervised classification of remote sensing images, 
 providing tools for the download, the preprocessing and postprocessing of images.

							 -------------------
		begin				: 2012-12-29
		copyright			: (C) 2012-2017 by Luca Congedo
		email				: ing.congedoluca@gmail.com
**************************************************************************************************************************/
 
/**************************************************************************************************************************
 *
 * This file is part of Semi-Automatic Classification Plugin
 * 
 * Semi-Automatic Classification Plugin is free software: you can redistribute it and/or modify it under 
 * the terms of the GNU General Public License as published by the Free Software Foundation, 
 * version 3 of the License.
 * 
 * Semi-Automatic Classification Plugin is distributed in the hope that it will be useful, 
 * but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
 * FITNESS FOR A PARTICULAR PURPOSE. 
 * See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with 
 * Semi-Automatic Classification Plugin. If not, see <http://www.gnu.org/licenses/>. 
 * 
**************************************************************************************************************************/

"""

from qgis.core import *
from qgis.gui import *
cfg = __import__(str(__name__).split(".")[0] + ".core.config", fromlist=[''])

class ErosionRaster:

	def __init__(self):
		pass
		
	# value text changed
	def textChanged(self):		
		self.checkValueList()
		
	# check value list
	def checkValueList(self):
		try:
			# class value list
			valueList = cfg.utls.textToValueList(cfg.ui.erosion_classes_lineEdit.text())
			cfg.ui.erosion_classes_lineEdit.setStyleSheet("color : green")
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
		except Exception, err:
			cfg.ui.erosion_classes_lineEdit.setStyleSheet("color : red")
			valueList = []
			# logger
			cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
		return valueList
		
	# erosion classification
	def erosionClassificationAction(self):
		self.erosionClassification()
		
	# erosion classification
	def erosionClassification(self, batch = "No", rasterInput = None, rasterOutput = None):
		# class value list
		valueList = self.checkValueList()
		if len(valueList) > 0:
			if batch == "No":
				d = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save output"), "", "Image (*.tif)")
			else:
				d = rasterOutput
			if len(d) > 0:
				d = d.replace('\\', '/')
				d = d.replace('//', '/')
				sN = cfg.osSCP.path.basename(unicode(d))
				if unicode(sN).endswith(".tif"):
					outputRaster = d
				else:
					nm = cfg.osSCP.path.splitext(sN)[0]
					outputRaster = cfg.osSCP.path.dirname(d) + '/' + nm + ".tif"
				if batch == "No":
					cfg.uiUtls.addProgressBar()
					cfg.cnvs.setRenderFlag(False)
					raster = cfg.ui.erosion_raster_name_combo.currentText()
					r = cfg.utls.selectLayerbyName(raster, "Yes")
				else:
					r = "No"
				if r is not None:
					if batch == "No":
						rSource = r.source()
					else:
						if cfg.osSCP.path.isfile(rasterInput):
							rSource = rasterInput
						else:
							return "No"
					cfg.uiUtls.updateBar(40)
					# open input with GDAL
					rD = cfg.gdalSCP.Open(rSource, cfg.gdalSCP.GA_ReadOnly)
					# band list
					bL = cfg.utls.readAllBandsFromRaster(rD)
					input = rD
					if rD is None:
						cfg.mx.msg4()
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + (cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " None raster")
						if batch == "No":
							cfg.uiUtls.removeProgressBar()
							cfg.cnvs.setRenderFlag(True)
						return "No"
					size =  cfg.ui.erosion_threshold_spinBox.value()
					connect = cfg.ui.erosion_connection_combo.currentText()
					struct = cfg.utls.create3x3Window(connect)
					for s in range(0, size):
						# date time for temp name
						dT = cfg.utls.getTime()
						tPMD = cfg.tmpDir + "/" + dT + "erosion" + str(s) + ".tif"
						tempRasterList = []
						tempRasterList.append(tPMD)
						# create rasters
						oMR = cfg.utls.createRasterFromReference(rD, 1, tempRasterList, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0,  None, "No", "DEFLATE21")
						o = cfg.utls.processRaster(input, bL, None, "No", cfg.utls.rasterErosion, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", struct, valueList, "erosion ")
						# boundaries
						o = cfg.utls.processRasterBoundaries(input, bL, None, "No", cfg.utls.rasterErosionBoundaries, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", struct, valueList, "erosion ", 2)
						# close GDAL rasters
						for b in range(0, len(oMR)):
							oMR[b] = None
						for b in range(0, len(bL)):
							bL[b] = None
						rD = None
						# open input with GDAL
						rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
						# band list
						bL = cfg.utls.readAllBandsFromRaster(rD)
						input = rD
					for b in range(0, len(bL)):
						bL[b] = None
					rD = None
					# copy raster
					if cfg.rasterCompression != "No":
						try:
							cfg.utls.GDALCopyRaster(tPMD, outputRaster, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
						except Exception, err:
							cfg.shutilSCP.copy(tPMD, outputRaster)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					else:
						cfg.shutilSCP.copy(tPMD, outputRaster)
					if cfg.osSCP.path.isfile(outputRaster):
						oR = cfg.utls.addRasterLayer(outputRaster, cfg.osSCP.path.basename(outputRaster))
					if r != "No":
						cfg.utls.copyRenderer(r, oR)
					if batch == "No":
						cfg.utls.finishSound()
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
				else:
					if batch == "No":
						cfg.uiUtls.removeProgressBar()
						cfg.cnvs.setRenderFlag(True)
					cfg.utls.refreshClassificationLayer()
					cfg.mx.msgErr9()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "Error raster not found")
				# logger
				cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode())
			