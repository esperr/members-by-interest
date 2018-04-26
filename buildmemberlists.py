import os
import argparse
import xml.etree.ElementTree as etree
import json

parser = argparse.ArgumentParser(description='''Process a list of Bill status XML files downloaded from FDSys to produce the source files for use by members-by-interest.
        buildmemberlists.py is designed to process House and Senate Members into one file. Run it against all statuses for one congress to generate a file for that particular
        congress or against all available statuses to generate an inclusive file for all congresses. ''')
parser.add_argument("filespath", help="Path(s) to downloaded files -- separtate multiple paths with a [space]", nargs="+")

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
    congress = root.find('.//bill/congress').text
    congresses.add(congress)

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
congresses = set()

for path in args.filespath:
    walkpath(path)

if len(congresses) > 1:
    congress = "all"
else:
    congress = congresses.pop()

print members
with open("members" + "_" + congress + ".js", 'w') as outfile:
    json.dump(members, outfile)
