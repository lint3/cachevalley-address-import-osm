import ogr2osm
import logging

datasource_parameter = '../addr_newton.gpkg'

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
  
  # For when the unit ID comes before unit type, for example Basement Apartment
  unitIdExceptions = {
    'MAIN':'Main',
    'REAR':'Rear',
    'UPPR':'Upper',
    'BSMT':'Basement'}
    
  def fixme(self, tags, attrs, message):
    if 'fixme' in tags:
      tags['fixme'] = tags['fixme'] + " Also, " + message
    else:
      tags['fixme'] = "Automated Import: " + message
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
      if requiredTag not in tags:
        logger.warning("Saw feature missing " + requiredTag + " tag")
        return False
    
    return True
    
    
  def filter_tags(self, attrs):
    tags = {}
    
    # House Number Tag
    tags['addr:housenumber'] = attrs['AddNum']
      # Add house number suffix if necessary (1/2, etc.)
    if attrs['AddNumSuff'] != '':
      tags['addr:housenumber'] += ' ' + attrs['AddNumSuff']
      tags["UGRC:address_type"] = 'secondary'
    
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
    
    # Unit tags
    unitTag = []
    uT = attrs['UnitType']
    uI = attrs['UnitID']
    
    if uT != '' and uI == '': # Unit Type but no ID, addr:unit is Type
      if uT in self.unitTypeExpand:
        unitTag.append(self.unitTypeExpand[uT])
      else:
        unitTag.append(uT)
        
    elif uT == '' and uI != '': # Unit ID but no Type, addr:unit is ID
      if uI in self.unitIdExceptions:
        unitTag.append(self.unitIdExceptions[uI])
      else:
        unitTag.append(uI.title())
        
    elif uT != '' and uI != '': # Both unit Type and ID
      if uI in self.unitIdExceptions: # Add ID first in these exception cases
        unitTag.append(self.unitIdExceptions[uI])
        
        if uT in self.unitTypeExpand:
          unitTag.append(self.unitTypeExpand[uT])
        else:
          unitTag.append(uT.title())
          
      else: # Otherwise add Type first
        if uT in self.unitTypeExpand:
          unitTag.append(self.unitTypeExpand[uT])
        else:
          unitTag.append(uT.title())
        unitTag.append(uI)
    
        
    # Do nothing if neither type nor ID
    
    if unitTag:
      tags["addr:unit"] = ' '.join(unitTag)
      tags["UGRC:address_type"] = 'secondary'
    
    # Other Required Tags
    tags["addr:city"] = attrs['City'].title().removesuffix("City").strip()
    tags["addr:postcode"] = attrs['ZipCode']
    tags["addr:state"] = attrs['State']
    tags['addr:country'] = 'US'
    tags['UGRC:import_uuid'] = attrs['OBJECTID']
    if len(tags['UGRC:import_uuid']) < 2:
      logger.warning("Something is amiss")

    # Name tag
    if attrs['LandmarkNa'] != '':
      tags['name'] = attrs['LandmarkNa'].title()
      
    # Primary is default value
    if "UGRC:address_type" not in tags:
      tags["UGRC:address_type"] = 'primary'
    
    if not self.tagCheck(tags, attrs['FullAdd']):
      self.fixme(tags, attrs, "Missing one or more required address tags")
    return tags
    
  def ensureDictKeysAreLists(self, d):
    result = {}
    for key in d:
      if not isinstance(d[key], list):
        result[key] = [d[key]]
      else:
        result[key] = d[key]
    return result
    

  def merge_tags(self, geometry_type, tags_existing, tags_new):
    
    tags_existing = self.ensureDictKeysAreLists(tags_existing)
    
    never_merge_tags = [
      "addr:unit",]
    
    always_merge_tags = [
      "UGRC:import_uuid" ]
    
    for new_key in tags_new:
      
      if new_key in tags_existing and (new_key in never_merge_tags or new_key in always_merge_tags):
        # They both have the tag
        for exist_value in tags_existing[new_key]:
          
          # And the value matches
          if tags_new[new_key] == exist_value:
            pass
          
          # One of them doesn't have a value, and nothing on blacklist, so OK to merge
          if (tags_new[new_key] == '' or exist_value == '') and new_key not in never_merge_tags:
            pass
          
          if new_key in never_merge_tags:
            return None
            
          # Conflicting values
          if tags_new[new_key] != exist_value:
            if new_key not in always_merge_tags:
              # Not in whitelist
              return None
            else:
              pass
      
      elif new_key not in tags_existing and new_key in never_merge_tags:
        return None # Never merge

    for exist_key in tags_existing:
      if exist_key in tags_new:
        pass # This case already covered
      if exist_key in never_merge_tags:
        return None
      

    tags_existing['UGRC:address_type'] = ['primary']
    tags_new['UGRC:address_type'] = 'primary'
    return ogr2osm.TranslationBase.merge_tags(self, geometry_type, tags_existing, tags_new)


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
