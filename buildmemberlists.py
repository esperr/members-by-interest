import os
import argparse
import xml.etree.ElementTree as etree
import json

parser = argparse.ArgumentParser(description='Process a list of XML files downloaded from FDSys to produce a Sankey diagram')
parser.add_argument("filespath", help="Path to downloaded files")
args = parser.parse_args()
print args.filespath

members = []

#path = 'C:\Users\hksr4262\Documents\hr_statuses'
path = args.filespath
listing = os.listdir(path)
tree = etree.parse(path + "\\" + listing[0])
root = tree.getroot()
congress = root.find('.//bill/congress').text
billType = root.find('.//bill/billType').text
if billType[0] == "h" or billType[0] == "H":
    chamber = "house"
if billType[0] == "s" or billType[0] == "S":
    chamber = "senate"
print congress
print billType
print chamber

def makememberlist( membernodes ):
  for item in allsponsors:
      member = {}
      bioidnode = item.find('bioguideId')
      if bioidnode is not None:
        id = bioidnode.text
        if any(member['bioid'] == id for member in members):
            break
        else:
            member['bioid'] = bioidnode.text
            member['fullname'] = item.find('fullName').text
            member['lastname'] = item.find('lastName').text
            member['party'] = item.find('party').text
            member['state'] = item.find('state').text
            if item.find('district') is not None:
                member['district'] = item.find('district').text
            members.append(member)

for infile in listing:
  #print "current file is:" + infile
  filepath = path + "\\" + infile
  tree = etree.parse(filepath)
  root = tree.getroot()
  allsponsors = root.findall('.//sponsors/item')
  makememberlist( allsponsors )

  allcosponsors = root.findall('.//cosponsors/item')
  makememberlist( allcosponsors )

print members
#json.dumps(members)
with open("members_" + str(congress) + "_" + billType + ".js", 'w') as outfile:
    json.dump(members, outfile)
#f = open("members_" + str(congress) + "_" + billType + ".js", 'w')
#f.write(members)
#f.close()
