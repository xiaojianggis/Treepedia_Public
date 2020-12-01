# This function is used to collect the metadata of the GSV panoramas based on the sample point shapefile

# Copyright(C) Xiaojiang Li, Ian Seiferling, Marwa Abdulhai, Senseable City Lab, MIT 

def GSVpanoMetadataCollector(samplesFeatureClass,num,ouputTextFolder, key):
    '''
    This function is used to call the Google API url to collect the metadata of
    Google Street View Panoramas. The input of the function is the shpfile of the create sample site, the output
    is the generate panoinfo matrics stored in the text file
    
    Parameters: 
        samplesFeatureClass: the shapefile of the create sample sites
        num: the number of sites proced every time
        ouputTextFolder: the output folder for the panoinfo
        
    '''
    
    import xmltodict
    import ogr, osr
    import time
    import os,os.path
    import sys
    import json


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
    # batch = featureNum/num    
    batch = int(featureNum/num + 0.5)

    print(batch)
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
                

                # get the meta data of panoramas 
                # urlAddress = r'http://maps.google.com/cbk?output=xml&ll=%s,%s&key=%s'%(lat,lon,key)
                urlAddress = r'https://maps.googleapis.com/maps/api/streetview/metadata?size=600x300&location=%s,%s&heading=-45&pitch=42&fov=110&key=%s'%(lon, lat, key)
                time.sleep(0.1)
                

                # using different url reading method in python2 and python3
                if sys.version_info[0] == 2:
                    # from urllib2 import urlopen
                    import urllib
                    
                    metaData = urllib.urlopen(urlAddress).read()
                    
                if sys.version_info[0] == 3:
                    import urllib.request
                    
                    request = urllib.request.Request(urlAddress)
                    metaData = urllib.request.urlopen(request).read()

                
                data = json.loads(metaData)
                panoDate = data['date']
                panoId = data['pano_id']
                panoLat = data['location']['lat']
                panoLon = data['location']['lng']

                # print ('The coordinate (%s,%s), panoId is: %s, panoDate is: %s')%(panoLon,panoLat,panoId, panoDate)
                lineTxt = 'panoID: %s panoDate: %s longitude: %s latitude: %s\n'%(panoId, panoDate, panoLon, panoLat)
                panoInfoText.write(lineTxt)
            
        panoInfoText.close()


# ------------Main Function -------------------    
if __name__ == "__main__":

    import os, os.path
    import sys
    import argparse


    parser = argparse.ArgumentParser(
        description="parameters"
    )

    parser.add_argument(
        "--inputshp",
        required=True,
        type=str,
        help="the path of the shapefile"
    )

    parser.add_argument(
        "--outdir",
        default="mosaic-mrt.tif",
        help="the output dir for the meta txt file",
        type=str,
    )

    parser.add_argument(
        "--key",
        default="",
        help="Google Street View key",
        type=str,
    )


    args = parser.parse_args()
    inputshp = args.inputshp
    outdir = args.outdir
    key = args.key

    print(inputshp, outdir, key)
    GSVpanoMetadataCollector(inputshp, 1000, outdir, key)
    
    
    ## call example
    # python metadataCollector.py \
    #         --inputshp='/Users/senseablecity/Dropbox (MIT)/ResearchProj/treepedia/cities-proj/Oakland/OaklandSlowStreets/SlowStreets_points/SS_20m.shp' \
    #         --outdir='/Users/senseablecity/Dropbox (MIT)/ResearchProj/treepedia/cities-proj/Oakland/OaklandSlowStreets/SlowStreets_points' \
    #         --key='AIzaSyBrqEg7VCawLlnyoWW2MrXKIuPtv13MRj8'
    
    