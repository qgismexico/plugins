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

class LandCoverChange:

	def __init__(self):
		pass
	
	# reference classification name
	def classificationReferenceLayerName(self):
		cfg.refClssfctnNm = cfg.ui.classification_reference_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference classification name: " + unicode(cfg.refClssfctnNm))
					
	# start land cover change calculation
	def landCoverChangeAction(self):			
		self.landCoverChange()
		
	# start land cover change calculation
	def landCoverChange(self, batch = "No", referenceRaster = None, newRaster = None, rasterOutput = None):
		if batch == "No":
			# input
			refRstr = cfg.utls.selectLayerbyName(cfg.refClssfctnNm, "Yes")
			try:
				refRstrSrc = refRstr.source()
				rstrCheck = "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				rstrCheck = "No"
			newRstr = cfg.utls.selectLayerbyName(cfg.newClssfctnNm, "Yes")
			try:
				newRstrSrc = newRstr.source()
				rstrCheck = "Yes"
			except Exception, err:
				# logger
				cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
				rstrCheck = "No"
		else:
			refRstrSrc = referenceRaster
			newRstrSrc = newRaster
			if cfg.osSCP.path.isfile(refRstrSrc) and cfg.osSCP.path.isfile(newRstrSrc):
				rstrCheck = "Yes"
			else:
				rstrCheck = "No"
		# check if numpy is updated
		try:
			cfg.np.count_nonzero([1,1,0])
		except Exception, err:
			# logger
			cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
			cfg.mx.msgErr26()
			return "No"
		if rstrCheck == "No":
			cfg.mx.msg4()
		else:
			# open input with GDAL
			refRstrDt = cfg.gdalSCP.Open(refRstrSrc, cfg.gdalSCP.GA_ReadOnly)
			newRstrDt = cfg.gdalSCP.Open(newRstrSrc, cfg.gdalSCP.GA_ReadOnly)
			# check projections
			refRstrProj = refRstrDt.GetProjection()
			newRstrProj = newRstrDt.GetProjection()
			if refRstrProj != newRstrProj:
				cfg.mx.msg9()
			else:
				if batch == "No":
					rstrOut = cfg.utls.getSaveFileName(None , cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", "Save land cover change raster output"), "", "*.tif")
				else:
					rstrOut = rasterOutput
				if len(rstrOut) > 0:
					if batch == "No":
						cfg.uiUtls.addProgressBar()
						# disable map canvas render for speed
						cfg.cnvs.setRenderFlag(False)
					chngRstPath = rstrOut
					chngRstPath = chngRstPath.replace('\\', '/')
					chngRstPath = chngRstPath.replace('//', '/')
					tblOut = cfg.osSCP.path.dirname(chngRstPath) + "/" + cfg.osSCP.path.basename(chngRstPath)
					tblOut = cfg.osSCP.path.splitext(tblOut)[0] + ".csv"
					if unicode(chngRstPath).endswith(".tif"):
						pass
					else:
						chngRstPath = chngRstPath + ".tif"
					# combination finder
					# band list
					bLR = cfg.utls.readAllBandsFromRaster(refRstrDt)
					cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
					cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
					o = cfg.utls.processRaster(refRstrDt, bLR, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
					cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
					refRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)	
					# band list
					bLN = cfg.utls.readAllBandsFromRaster(newRstrDt)
					cfg.rasterBandUniqueVal = cfg.np.zeros((1, 1))
					cfg.rasterBandUniqueVal = cfg.np.delete(cfg.rasterBandUniqueVal, 0, 1)
					o = cfg.utls.processRaster(newRstrDt, bLN, None, "No", cfg.utls.rasterUniqueValues, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, None, "UniqueVal")
					for b in range(0, len(bLR)):
						bLR[b] = None
					refRstrDt = None
					for b in range(0, len(bLN)):
						bLN[b] = None
					newRstrDt = None		
					cfg.rasterBandUniqueVal = cfg.np.unique(cfg.rasterBandUniqueVal).tolist()
					newRasterBandUniqueVal = sorted(cfg.rasterBandUniqueVal)
					cmb = list(cfg.itertoolsSCP.product(refRasterBandUniqueVal, newRasterBandUniqueVal))
					cmbntns = {}
					# expression builder
					n = 1
					e = []
					for i in cmb:
						if cfg.unchngMaskCheck is False and str(i[0]) == str(i[1]):
							pass
						else:
							e.append("cfg.np.where( (a == " + str(i[0]) + ") & (b == " + str(i[1]) + "), " + str(n) + ", 0)")
							cmbntns["combination_" + str(i[0]) + "_"+ str(i[1])] = n
							n = n + 1
					# virtual raster
					tPMN = cfg.tmpVrtNm + ".vrt"
					# date time for temp name
					dT = cfg.utls.getTime()
					tPMD = cfg.tmpDir + "/" + dT + tPMN
					tPMN2 = dT + cfg.calcRasterNm + ".tif"
					tPMD2 = cfg.tmpDir + "/" + tPMN2
					bList = [refRstrSrc, newRstrSrc]
					bandNumberList = [1, 1]
					vrtCheck = cfg.utls.createVirtualRaster2(bList, tPMD, bandNumberList, "Yes", "No", 0, "No", "No")
					# open input with GDAL
					rD = cfg.gdalSCP.Open(tPMD, cfg.gdalSCP.GA_ReadOnly)
					# output rasters
					oM = []
					oM.append(tPMD2)
					oMR = cfg.utls.createRasterFromReference(rD, 1, oM, cfg.NoDataVal, "GTiff", cfg.rasterDataType, 0, None, cfg.rasterCompression)
					# band list
					bL = cfg.utls.readAllBandsFromRaster(rD)
					# calculation
					variableList = [["im1", "a"], ["im2", "b"]]
					o = cfg.utls.processRaster(rD, bL, None, "No", cfg.utls.bandCalculationMultipleWhere, None, oMR, None, None, 0, None, cfg.NoDataVal, "No", e, variableList, "No")
					# logger
					cfg.utls.logCondition(str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "change raster output: " + unicode(chngRstPath))
					# close GDAL rasters
					for b in range(0, len(oMR)):
						oMR[b] = None
					for b in range(0, len(bL)):
						bL[b] = None
					rD = None
					if cfg.rasterCompression != "No":
						try:
							cfg.utls.GDALCopyRaster(tPMD2, chngRstPath, "GTiff", cfg.rasterCompression, "DEFLATE -co PREDICTOR=2 -co ZLEVEL=1")
							cfg.osSCP.remove(tPMD2)
						except Exception, err:
							cfg.shutilSCP.copy(tPMD2, chngRstPath)
							cfg.osSCP.remove(tPMD2)
							# logger
							if cfg.logSetVal == "Yes": cfg.utls.logToFile(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					else:
						cfg.shutilSCP.copy(tPMD2, chngRstPath)
						cfg.osSCP.remove(tPMD2)
					# # save combination to table
					try:
						l = open(tblOut, 'w')
					except:
						return "No"
					t = cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'ChangeCode') + "	" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'ReferenceClass') + "	" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'NewClass') + "	" + cfg.QtGuiSCP.QApplication.translate("semiautomaticclassificationplugin", 'PixelSum') + str("\n")
					try:
						t = t.encode(cfg.sysSCP.getfilesystemencoding())
					except:
						pass
					l.write(t)
					# change stats
					rDC = cfg.gdalSCP.Open(chngRstPath, cfg.gdalSCP.GA_ReadOnly)
					bLC = cfg.utls.readAllBandsFromRaster(rDC)
					for i in cmb:
						try:
							v = cmbntns["combination_" + str(i[0]) + "_"+ str(i[1])]
							combOK = "Yes"
						except:
							combOK = "No"
						if combOK == "Yes":
							cfg.rasterBandPixelCount = 0
							o = cfg.utls.processRaster(rDC, bLC, None, "No", cfg.utls.rasterEqualValueCount, None, None, None, None, 0, None, cfg.NoDataVal, "No", None, v, "value " + str(v))
							t = str(v) + "	" + str(i[0]) + "	" + str(i[1]) + "	" + str(cfg.rasterBandPixelCount) + str("\n")
							l.write(t)
					l.close()
					for b in range(0, len(bLC)):
						bLC[b] = None
					rDC = None
					# open csv
					try:
						f = open(tblOut)
						if cfg.osSCP.path.isfile(tblOut):
							changeTxt = f.read()
							cfg.ui.change_textBrowser.setText(str(changeTxt))
					except Exception, err:
						# logger
						cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " ERROR exception: " + str(err))
					# add raster to layers
					cfg.iface.addRasterLayer(unicode(chngRstPath), unicode(cfg.osSCP.path.basename(chngRstPath)))
					rstr = cfg.utls.selectLayerbyName(unicode(cfg.osSCP.path.basename(chngRstPath)), "Yes")
					cfg.utls.rasterSymbolGeneric(rstr)	
					cfg.uiUtls.updateBar(100)
					if batch == "No":
						# enable map canvas render
						cfg.cnvs.setRenderFlag(True)
						cfg.utls.finishSound()
						cfg.ui.toolBox_landCoverChange.setCurrentIndex(1)
						cfg.uiUtls.removeProgressBar()
					# logger
					cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "finished")
						
	# state of checkbox for mask unchanged
	def maskUnchangedCheckbox(self):
		if cfg.ui.mask_unchanged_checkBox.isChecked() is True:
			cfg.unchngMaskCheck = True
		else:
			cfg.unchngMaskCheck = False
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), " checkbox set: " + str(cfg.unchngMaskCheck))
	
	# new classification name
	def newClassificationLayerName(self):
		cfg.newClssfctnNm = cfg.ui.new_classification_name_combo.currentText()
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference classification name: " + unicode(cfg.newClssfctnNm))
	
	# refresh reference classification name
	def refreshClassificationReferenceLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.classification_reference_name_combo.clear()
		# reference classification name
		cfg.refClssfctnNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.classification_reference_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "reference classification layers refreshed")
	
	# refresh new classification name
	def refreshNewClassificationLayer(self):
		ls = cfg.lgnd.layers()
		cfg.ui.new_classification_name_combo.clear()
		# new classification name
		cfg.newClssfctnNm = None
		for l in ls:
			if (l.type()==QgsMapLayer.RasterLayer):
				if l.bandCount() == 1:
					cfg.dlg.new_classification_layer_combo(l.name())
		# logger
		cfg.utls.logCondition(str(__name__) + "-" + str(cfg.inspectSCP.stack()[0][3])+ " " + cfg.utls.lineOfCode(), "new classification layers refreshed")