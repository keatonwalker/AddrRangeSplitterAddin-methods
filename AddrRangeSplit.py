'''
Created on Aug 22, 2015

@author: kwalker
'''
import arcpy, math

class WholeRoad(object):
    
    def __init__(self, lineGeometry, field, L_F_Add, L_T_Add, R_F_Add, R_T_Add):
        self.lineGeometry = lineGeometry
        self.leftFromAddr = self.setAddrRangeValue(L_F_Add)
        self.leftToAddr = self.setAddrRangeValue(L_T_Add)
        self.rightFromAddr = self.setAddrRangeValue(R_F_Add)
        self.rightToAddr = self.setAddrRangeValue(R_T_Add)
        self.startSide = None
        self.endSide = None
        self.field = field
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
        
        print self.getStartAddrRangeValues(startSidePercent)
        print self.getStartAddrRangeValues(endSidePercent)
        
        startRoad = SplitRoad(startSideSegment, "", isStartSide = True)
        endRoad = SplitRoad(endSideSegment, "", isStartSide = False)
        
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
            else:
                newLFrom = self._caclulateNewEndValue(self.leftToAddr, leftAddrRange, max(self.leftFromAddr, self.leftToAddr))   
            
            if self.rightFromAddr < self.rightToAddr:
                newRTo = self._caclulateNewEndValue(self.rightFromAddr, rightAddrRange, max(self.rightFromAddr, self.rightToAddr)) 
      
            else:
                newRFrom = self._caclulateNewEndValue(self.rightToAddr, rightAddrRange, max(self.rightFromAddr, self.rightToAddr))
                
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
    
    def __init__(self, lineGeometry, field, isStartSide):
        WholeRoad.__init__(self, lineGeometry, field)
        self.isStartSide = isStartSide
        
    def getInsertRow(self):
        pass
        
    
        
    
if __name__ == "__main__":

    inFc = r"C:\GIS\Work\TempStuff\TestRoads.gdb\TestRoads_1"
    fieldNames = ["SHAPE@", "L_F_ADD", "L_T_ADD", "R_F_ADD", "R_T_ADD"]
    with arcpy.da.SearchCursor(inFc, fieldNames, explode_to_points = False) as cursor:
        for row in cursor:
            print row
            r = WholeRoad(row[0], "fuckin", row[1], row[2], row[3], row[4])
            r.getStartAndEndSideRoads(417768.916, 4518470.792)
            