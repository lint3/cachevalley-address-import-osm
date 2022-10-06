import ogr2osm
import logging

datasource_parameter = '../testing/addr_logan_subset.gpkg'

class CacheAddrTranslation(ogr2osm.TranslationBase):
  
  logger = logging.getLogger('ogr2osm')
    
  dirExpand = {
    'N':'North',
    'E':'East',
    'S':'South',
    'W':'West',
    'NULL':'' }
  
  streetTypeExpand = {
    'ALY':'Alley',
    'BLVD':'Boulevard',
    'COR':'Corner',
    'CRES':'Crescent',
    'ESTS':'Estates',
    'FWY':'Freeway',
    'HWY':'Highway',
    'LN':'Lane',
    'PARK':'Park',
    'PLZ':'Plaza',
    'RDG':'Ridge',
    'RUN':'Run',
    'TRCE':'Trace',
    'WAY':'Way',
    'AVE':'Avenue',
    'CYN':'Canyon',
    'CT':'Court',
    'XING':'Crossing',
    'EXPY':'Expressway',
    'GLN':'Glen',
    'HL':'Hill',
    'LOOP':'Loop',
    'PKWY':'Parkway',
    'PT':'Point',
    'RD':'Road',
    'SQ':'Square',
    'TRL':'Trail',
    'BAY':'Bay',
    'CTR':'Center',
    'CV':'Cove',
    'DR':'Drive',
    'FLT':'Flat',
    'GRV':'Grove',
    'HOLW':'Hollow',
    'MNR':'Manor',
    'PASS':'Pass',
    'RAMP':'Ramp',
    'RTE':'Route',
    'ST':'Street',
    'VW':'View',
    'BND':'Bend',
    'CIR':'Circle',
    'CRK':'Creek',
    'EST':'Estate',
    'FORK':'Fork',
    'HTS':'Heights',
    'JCT':'Junction',
    'MDW':'Meadow',
    'PL':'Place',
    'RNCH':'Ranch',
    'ROW':'Row',
    'TER':'Terrace',
    'VLG':'Village' }
  
  # See https://wiki.openstreetmap.org/wiki/Key:addr:*#Detailed_subkeys
  unitTypeExpand = {
    'NULL':'',
    'BSMT':'Basement',
    'FL':'Floor',
    'FRNT':'Front',
    'HNGR':'Hangar',
    'LOWR':'Lower',
    'OFC':'Office',
    'RM':'Room',
    'SPC':'Space',
    'STE':'Suite',
    'TRLR':'Trailer',
    'UPPR':'Upper' }
    
  def fixme(self, tags, attrs, message):
    if 'FIXME' in tags:
      tags['FIXME'] = tags['FIXME'] + " Also, " + message
    else:
      tags['FIXME'] = "Automated Import: " + message
      # Also add additional context
      tags['note'] = ("Address System: " + attrs['AddSystem'] +
                      ", Object ID: " + attrs['OBJECTID'] +
                      ", County ID: " + attrs['CountyID'] +
                      ", Type: " + attrs['PtType'] +
                      ", Parcel ID: " + attrs['ParcelID'] +
                      ", USNG: " + attrs['USNG'])
    
  def tagCheck(self, tags, fullAddress):
    requiredTags = [
      "addr:housenumber",
      "addr:street",
      "addr:postcode",
      "addr:city",
      "addr:country",
      "addr:state",
      "UGRC:import_uuid" ]
    
    for requiredTag in requiredTags:
      if not requiredTag in tags:
        logger.warning("Saw feature missing " + requiredTag + " tag")
        return False
    
    logger.info("Feature " + fullAddress + " passed tagCheck")
    
    return True
    
    
  def filter_tags(self, attrs):
    tags = {}
    
    # House Number Tag
    tags['addr:housenumber'] = attrs['AddNum']
      # Add house number suffix if necessary (1/2, etc.)
    if attrs['AddNumSuff'] != '':
      tags['addr:housenumber'] += ' ' + attrs['AddNumSuff']
    
    # Street Tag
    streetTag = ''
    if attrs['PrefixDir'] != '':
      streetTag += self.dirExpand[attrs['PrefixDir']]
    streetTag += ' ' + attrs['StreetName'].title() # StreetName is required
    if attrs['StreetType'] != '':
      streetTag += ' ' + self.streetTypeExpand[attrs['StreetType']]
    elif attrs['SuffixDir'] != '':
      streetTag += ' ' + self.dirExpand[attrs['SuffixDir']]
    else: # Either Street Type ("Ave", etc.) or suffix ("East") is required
      logger.warning("Saw feature (ObjectID " + attrs['OBJECTID'] + ") with PrefixDir " + attrs['PrefixDir'] + " but no StreetType or SuffixDir")
      self.fixme(tags, attrs, 'This feature has no street type or suffix')
    tags["addr:street"] = streetTag
    
    # Unit tags - Type
    unitTag = []
    if attrs['UnitType'] != '':
      if attrs['UnitType'] in self.unitTypeExpand:
        unitTag.append(self.unitTypeExpand[attrs['UnitType']])
      else:
        unitTag.append(attrs['UnitType'].title())
    # Unit tags - ID
    if attrs['UnitID'] != '':
      unitTag.append(attrs['UnitID'])
    if unitTag:
      tags["addr:unit"] = ' '.join(unitTag)
    
    # Other Required Tags
    tags["addr:city"] = attrs['City'].title()
    tags["addr:postcode"] = attrs['ZipCode']
    tags["addr:state"] = attrs['State']
    tags['addr:country'] = 'US'
    tags['UGRC:import_uuid'] = attrs['OBJECTID']

    # Name tag
    if attrs['LandmarkNa'] != '':
      tags['name'] = attrs['LandmarkNa'].title()
    
    if not self.tagCheck(tags, attrs['FullAdd']):
      self.fixme(tags, attrs, "Missing one or more required address tags")
    return tags








logger = logging.getLogger('ogr2osm')
logger.setLevel(logging.WARNING)
logger.addHandler(logging.StreamHandler())

query = ''
output_file = '.'.join(datasource_parameter.split('.')[:-1]) + '.osm'

translation_object = CacheAddrTranslation()
datasource = ogr2osm.OgrDatasource(translation_object)
datasource.open_datasource(datasource_parameter)
datasource.set_query(query)

osmdata = ogr2osm.OsmData(translation_object)
osmdata.process(datasource)

datawriter = ogr2osm.OsmDataWriter(output_file)
osmdata.output(datawriter)





    
    
