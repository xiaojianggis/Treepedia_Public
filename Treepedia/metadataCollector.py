
# This function is used to collect the metadata of the GSV panoramas based on the sample point shapefile

# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT 

def GSVpanoMetadataCollector_gdal(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import urllib
    import xmltodict
    import ogr, osr
    import time
    import os,os.path
    import sys

    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)

    driver = ogr.GetDriverByName('ESRI Shapefile')

    # change the projection of shapefile to the WGS84
    dataset = driver.Open(samplesFeatureClass)
    layer = dataset.GetLayer()

    sourceProj = layer.GetSpatialRef()
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)

    # loop all the features in the featureclass
    feature = layer.GetNextFeature()
    featureNum = layer.GetFeatureCount()
    batch = int(featureNum/num + 0.5)

    for b in range(batch):
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum

        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)

        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue

        time.sleep(1)

        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer.GetFeature(i)        
                geom = feature.GetGeometryRef()

                # trasform the current projection of input shapefile to WGS84
                #WGS84 is Earth centered, earth fixed terrestrial ref system
                geom.Transform(transform)
                lon = geom.GetX()
                lat = geom.GetY()
                key = r'' #Input Your Key here 

                # get the meta data of panoramas 
                urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)

                time.sleep(0.05)
                # the output result of the meta data is a xml object
                # using different url reading method in python2 and python3
                if sys.version_info[0] == 2:
                    # from urllib2 import urlopen
                    import urllib

                    metaData = urllib.urlopen(urlAddress).read()

                if sys.version_info[0] == 3:
                    import urllib.request

                    request = urllib.request.Request(urlAddress)
                    metaData = urllib.request.urlopen(request).read()

                data = xmltodict.parse(metaData)

                # in case there is not panorama in the site, therefore, continue
                if data['panorama']==None:
                    continue
                else:
                    panoInfo = data['panorama']['data_properties']

                    # get the meta data of the panorama
                    panoDate = panoInfo['@image_date']
                    panoId = panoInfo['@pano_id']
                    panoLat = panoInfo['@lat']
                    panoLon = panoInfo['@lng']

                    print ('The coordinate (%s,%s), panoId is: %s, panoDate is: %s'%(panoLon,panoLat,panoId, panoDate))
                    lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s\n'%(panoId, panoDate, panoLon, panoLat)
                    panoInfoText.write(lineTxt)

        panoInfoText.close()


def GSVpanoMetadataCollector_fiona(samplesFeatureClass,num,ouputTextFolder):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    import urllib
    import xmltodict
    import fiona
    import time
    import os,os.path
    import sys
    
    if not os.path.exists(ouputTextFolder):
        os.makedirs(ouputTextFolder)

    layer = fiona.open(samplesFeatureClass)
    featureNum = len(list(layer))


    batch = int(featureNum/num + 0.5)
    for b in range(batch):
        # for each batch process num GSV site
        start = b*num
        end = (b+1)*num
        if end > featureNum:
            end = featureNum

        ouputTextFile = 'Pnt_start%s_end%s.txt'%(start,end)
        ouputGSVinfoFile = os.path.join(ouputTextFolder,ouputTextFile)

        # skip over those existing txt files
        if os.path.exists(ouputGSVinfoFile):
            continue

        time.sleep(1)

        with open(ouputGSVinfoFile, 'w') as panoInfoText:
            # process num feature each time
            for i in range(start, end):
                feature = layer[i]

                # trasform the current projection of input shapefile to WGS84
                #WGS84 is Earth centered, earth fixed terrestrial ref system
                coord = feature['geometry']['coordinates']
                lon = coord[0]
                lat = coord[1]
                
                # get the meta data of panoramas 
                urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s'%(lat,lon)

                time.sleep(0.05)
                # the output result of the meta data is a xml object
                # using different url reading method in python2 and python3
                if sys.version_info[0] == 2:
                    # from urllib2 import urlopen
                    import urllib

                    metaData = urllib.urlopen(urlAddress).read()

                if sys.version_info[0] == 3:
                    import urllib.request

                    request = urllib.request.Request(urlAddress)
                    metaData = urllib.request.urlopen(request).read()

                data = xmltodict.parse(metaData)

                # in case there is not panorama in the site, therefore, continue
                if data['panorama']==None:
                    continue
                else:
                    panoInfo = data['panorama']['data_properties']

                    # get the meta data of the panorama
                    panoDate = panoInfo['@image_date']
                    panoId = panoInfo['@pano_id']
                    panoLat = panoInfo['@lat']
                    panoLon = panoInfo['@lng']

                    print ('The coordinate (%s,%s), panoId is: %s, panoDate is: %s'%(panoLon,panoLat,panoId, panoDate))
                    lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s\n'%(panoId, panoDate, panoLon, panoLat)
                    panoInfoText.write(lineTxt)

        panoInfoText.close()
        
        

# ------------Main Function -------------------    
if __name__ == "__main__":
    import os, os.path
    
    root = 'MYPATH/spatial-data'
    inputShp = os.path.join(root,'Cambridge40m.shp')
    outputTxt = root
    
    GSVpanoMetadataCollector(inputShp,1000,outputTxt)

