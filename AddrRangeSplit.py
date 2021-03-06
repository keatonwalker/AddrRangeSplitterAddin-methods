'''
Created on Aug 22, 2015

@author: kwalker
'''
import arcpy, math, time
print "imports"
class WholeRoad(object):
    
    def __init__(self, lineGeometry, L_F_Add, L_T_Add, R_F_Add, R_T_Add):
        self.lineGeometry = lineGeometry
        self.leftFromAddr = self.setAddrRangeValue(L_F_Add)
        self.leftToAddr = self.setAddrRangeValue(L_T_Add)
        self.rightFromAddr = self.setAddrRangeValue(R_F_Add)
        self.rightToAddr = self.setAddrRangeValue(R_T_Add)
        self.startSide = None
        self.endSide = None
        self.id = None
        
    def setId(self, idNum):
        self.id = idNum
        
    def setAddrRangeValue(self, addr):
        if addr is None:
            print "Bad addr value"
            return None 
        else:
            return float(addr)
        
    def getStartAndEndSideRoads(self, splitPntX, splitPntY):
        selectPnt = arcpy.Point(splitPntX, splitPntY)
        query = self.lineGeometry.queryPointAndDistance(selectPnt, use_percentage = True)
        print query
        #splitPnt = query[0]
        startSidePercent = query[1]
        endSidePercent = 1 - startSidePercent
        
        startSideSegment = self.lineGeometry.segmentAlongLine(0,  startSidePercent, use_percentage = True)
        endSideSegment = self.lineGeometry.segmentAlongLine(startSidePercent,  1, use_percentage = True)
        
        startLFrom, startLTo, startRFrom, startRTo = self.getStartAddrRangeValues(startSidePercent)
        endLFrom,  endLTo,  endRFrom,  endRTo = self.getEndAddrRangeValues(max(startLFrom, startLTo), max(startRFrom, startRTo))
        
        print "Start side new addr range: {}, {}, {}, {}".format(startLFrom, startLTo, startRFrom, startRTo)
        print "End side new addr range: {}, {}, {}, {}".format(endLFrom,  endLTo,  endRFrom,  endRTo)
        #print self.getEndAddrRangeValues(startRoadNewLeftEnd, startRoadNewRightEnd)
        
        startRoad = SplitRoad(startSideSegment, startLFrom, startLTo, startRFrom, startRTo, isStartSide = True)
        endRoad = SplitRoad(endSideSegment, endLFrom,  endLTo,  endRFrom,  endRTo, isStartSide = False)
        
        return (startRoad, endRoad)
        
    def _calculateNewRange(self, currentRange, lengthPercent):
        #currentRange = abs(fromValue - toValue)        
        newRange = round(currentRange * lengthPercent)
        
        return newRange
    
    def _caclulateNewEndValue(self, non_updatedFromOrToValue, newRange, maxOfRange):
        currentEvenOddAdjusment = non_updatedFromOrToValue %  2
        
        newEndValue = non_updatedFromOrToValue + newRange
        newEndEvenOddAdjusment = abs((newEndValue % 2) - currentEvenOddAdjusment)
        newEndValue += newEndEvenOddAdjusment
        
        if newEndValue >= maxOfRange:
            newEndValue -= 4
        
        if newEndValue < 0:
            newEndValue = 0
     
        return newEndValue
    
    def getStartAddrRangeValues(self, lenPercentage):
        newLFrom = 0
        newLTo = 0
        leftAddrRange = abs(self.leftFromAddr - self.leftToAddr)
        leftAddrRange = self._calculateNewRange(leftAddrRange, lenPercentage)
        
        newRFrom = 0
        newRTo = 0
        rightAddrRange = abs(self.rightFromAddr - self.rightToAddr)
        rightAddrRange = self._calculateNewRange(rightAddrRange, lenPercentage)
        
        if self.leftFromAddr == 0 and self.leftToAddr == 0 and self.rightFromAddr == 0 and self.rightToAddr == 0:
                    return (0, 0, 0, 0)
                
        else:
            
            if self.leftFromAddr < self.leftToAddr:
                newLTo = self._caclulateNewEndValue(self.leftFromAddr, leftAddrRange, max(self.leftFromAddr, self.leftToAddr))
                newLFrom = self.leftFromAddr    
            else:
                newLFrom = self._caclulateNewEndValue(self.leftToAddr, leftAddrRange, max(self.leftFromAddr, self.leftToAddr))
                newLTo = self.leftToAddr   
            
            if self.rightFromAddr < self.rightToAddr:
                newRTo = self._caclulateNewEndValue(self.rightFromAddr, rightAddrRange, max(self.rightFromAddr, self.rightToAddr))
                newRFrom = self.rightFromAddr 
      
            else:
                newRFrom = self._caclulateNewEndValue(self.rightToAddr, rightAddrRange, max(self.rightFromAddr, self.rightToAddr))
                newRTo = self.rightToAddr
                
        return (newLFrom, newLTo, newRFrom, newRTo)
        
    
    def getEndAddrRangeValues(self, startRoadNewLeftEnd, startRoadNewRightEnd):
        adjustValue = 2
        maxLeft = max(self.leftFromAddr, self.leftToAddr)
        maxRight = max(self.rightFromAddr, self.rightToAddr)
        if self.leftFromAddr == 0 and self.leftToAddr == 0 and self.rightFromAddr == 0 and self.rightToAddr == 0:
            adjustValue = 0                    
        
        if self.leftFromAddr < self.leftToAddr:
            newLFrom = startRoadNewLeftEnd + adjustValue
            if newLFrom >= maxLeft:
                print "Segment too short to divide address range."
            newLTo = maxLeft
            #print startRoadNewLeftEnd     
        else:
            newLTo = startRoadNewLeftEnd  + adjustValue
            if newLTo >= maxLeft:
                print "Segment too short to divide address range."
            newLFrom = maxLeft
            #print startRoadNewLeftEnd     
        
        if self.rightFromAddr < self.rightToAddr:
            newRFrom  = startRoadNewRightEnd  + adjustValue
            if newRFrom >= maxLeft:
                print "Segment too short to divide address range."                        
            newRTo = maxRight
            #print startRoadNewRightEnd      
        else:
            newRTo = startRoadNewRightEnd  + adjustValue
            if newRTo>= maxLeft:
                print "Segment too short to divide address range."                    
            newRFrom = maxRight
            #print startRoadNewRightEnd  
        
        return (newLFrom, newLTo, newRFrom, newRTo)  
            
    
    def getIndexOfSplitPoint(self):
        pass
    
    def _distanceFormula(self, x1 , y1, x2, y2):
        d = math.sqrt((math.pow((x2 - x1),2) + math.pow((y2 - y1),2)))
        return d
    
class SplitRoad(WholeRoad):
    
    def __init__(self, lineGeometry, L_F_Add, L_T_Add, R_F_Add, R_T_Add, isStartSide):
        WholeRoad.__init__(self, lineGeometry, L_F_Add, L_T_Add, R_F_Add, R_T_Add)
        self.isStartSide = isStartSide
        
    def getInsertRow(self):
        pass
        
    
class Config(object):
    
    def __init__ (self):
        self.srcFieldNames = []
        self.srcRow = None
        self.geometryField = "SHAPE@"
        self.leftFromField = "L_F_ADD" 
        self.leftToField = "L_T_ADD"
        self.rightFromField = "R_F_ADD"
        self.rightToField = "R_T_ADD"
        
    def getFieldIndex(self, fieldName):
        return self.srcFieldNames.index(fieldName)
    
    def cleanSrcRow(self):
        shapeIndex = self.getFieldIndex('Shape')
        del self.srcFieldNames[shapeIndex]
        del self.srcRow[shapeIndex]
        
        shapeLenIndex = self.getFieldIndex('Shape_Length')
        del self.srcFieldNames[shapeLenIndex]
        del self.srcRow[shapeLenIndex]
        
    
    def createInsertRow(self, lineGeometry, leftFrom, leftTo, rightFrom, rightTo):
        print "geofield index: {}".format(self.getFieldIndex(self.geometryField))
        insertRow = list(self.srcRow)
        insertRow[self.getFieldIndex(self.geometryField)] = lineGeometry 
        insertRow[self.getFieldIndex(self.leftFromField)] = leftFrom 
        insertRow[self.getFieldIndex(self.leftToField)] = leftTo
        insertRow[self.getFieldIndex(self.rightFromField)] = rightFrom
        insertRow[self.getFieldIndex(self.rightToField)] = rightTo
        
        return insertRow
    
    def deleteRoadById (self, id, inFc):
        layer = "testing"
        arcpy.MakeFeatureLayer_management (inFc, layer)
        arcpy.SelectLayerByAttribute_management (layer, "NEW_SELECTION", "OBJECTID = {}".format(id))
        arcpy.DeleteFeatures_management(layer)
    
    
if __name__ == "__main__":

    inFc = "C:\GIS\Work\AddRangeSplit.gdb\SingleTestRoad"
    fieldNames = ["SHAPE@", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD", "OID@", "*"]
    configUtil = Config()
    wholeRoad = None
    startSideRoad = None 
    endSideRoad = None
    with arcpy.da.SearchCursor(inFc, fieldNames, explode_to_points = False) as cursor:
        for row in cursor:
            configUtil.srcFieldNames = list(cursor.fields)
            configUtil.srcRow = list(row)
            configUtil.cleanSrcRow()
            wholeRoad = WholeRoad(row[configUtil.getFieldIndex("SHAPE@")], 
                          row[configUtil.getFieldIndex("L_F_ADD")], 
                          row[configUtil.getFieldIndex("L_T_ADD")], 
                          row[configUtil.getFieldIndex("R_F_ADD")], 
                          row[configUtil.getFieldIndex("R_T_ADD")])
            
            wholeRoad.setId(row[configUtil.getFieldIndex("OID@")])
            break
    
    splitTime = time.time()
    startSideRoad, endSideRoad = wholeRoad.getStartAndEndSideRoads(428705.77, 4332011.096)
    print"split time: {}".format(time.time() - splitTime)
#     print wholeRoad.lineGeometry.spatialReference.factoryCode
#     print endSideRoad.lineGeometry.spatialReference.factoryCode
    
    insTime = time.time()    
    insCursor = arcpy.da.InsertCursor(inFc, configUtil.srcFieldNames)
    startSideRow = configUtil.createInsertRow(startSideRoad.lineGeometry, 
                                                 startSideRoad.leftFromAddr, 
                                                 startSideRoad.leftToAddr, 
                                                 startSideRoad.rightFromAddr, 
                                                 startSideRoad.rightToAddr)
    startSideId = insCursor.insertRow(startSideRow)
    
    endSideRow = configUtil.createInsertRow(endSideRoad.lineGeometry, 
                                                 endSideRoad.leftFromAddr, 
                                                 endSideRoad.leftToAddr, 
                                                 endSideRoad.rightFromAddr, 
                                                 endSideRoad.rightToAddr)
    print endSideRow
    endSideId = insCursor.insertRow(endSideRow)
    del insCursor
    
    #configUtil.deleteRoadById(wholeRoad.id, inFc)
    
    print"ins time: {}".format(time.time() - insTime)
    
    print "Start ID: {}, End ID: {}".format(startSideId, endSideId)
    
    
    
            
            