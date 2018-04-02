import os
import argparse
import xml.etree.ElementTree as etree
import json

parser = argparse.ArgumentParser(description='Process a list of XML files downloaded from FDSys to produce a Sankey diagram')
parser.add_argument("filespath", help="Path to downloaded files", nargs="+")

def makememberlist( membernodes ):
  for item in membernodes:
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
            member['firstname'] = item.find('firstName').text
            member['party'] = item.find('party').text
            member['state'] = item.find('state').text
            if item.find('district') is not None:
                member['district'] = item.find('district').text
            members.append(member)

def walkpath( path ):
    listing = os.listdir(path)
    tree = etree.parse(path + "\\" + listing[0])
    root = tree.getroot()

    for infile in listing:
      filepath = path + "\\" + infile
      tree = etree.parse(filepath)
      root = tree.getroot()
      sponsornodes = root.findall('.//sponsors/item')
        #allsponsors = root.findall('.//sponsors/item')
      makememberlist( sponsornodes )
      if root.findall('.//cosponsors/item'):
        allcosponsors = root.findall('.//cosponsors/item')
        makememberlist( allcosponsors )

args = parser.parse_args()
print args.filespath

members = []

for path in args.filespath:
    walkpath(path)

print members
with open("members.js", 'w') as outfile:
    json.dump(members, outfile)
