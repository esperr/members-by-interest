import os
import argparse
import xml.etree.ElementTree as etree
import json

parser = argparse.ArgumentParser(description='Process a list of XML files downloaded from FDSys to produce a Sankey diagram')
parser.add_argument("filespath", help="Path to downloaded files", nargs="+")

def walkpath( path ):
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
    congresses.add(congress)
    print chamber
    chambers.add(chamber)

    for infile in listing:
      #print "current file is:" + infile
      filepath = path + "\\" + infile
      tree = etree.parse(filepath)
      root = tree.getroot()
      #allcommittees = root.findall('.//committees/billCommittees/item')
      allsponsors = root.findall('.//sponsors/item')
      allcosponsors = root.findall('.//cosponsors/item')
      allsubjects = root.findall('.//billSubjects/legislativeSubjects/item')
      policynode = root.find('.//policyArea/name')
      if policynode is not None:
          policyarea = policynode.text.replace(" ","_")
          if policyarea not in allPolicies:
              allPolicies[policyarea] = {}
          if "total" in allPolicies[policyarea]:
              allPolicies[policyarea]["total"] += 1
          else:
              allPolicies[policyarea]["total"] = 1
          for item in allsponsors:
              bioidnode = item.find('bioguideId')
              if bioidnode is not None:
                  bioid = bioidnode.text
                  if bioid not in allPolicies[policyarea]:
                      allPolicies[policyarea][bioid] = {}
                  if "sponsored" in allPolicies[policyarea][bioid]:
                      allPolicies[policyarea][bioid]["sponsored"] += 1
                  else:
                      allPolicies[policyarea][bioid]["sponsored"] = 1
          for item in allcosponsors:
              bioidnode = item.find('bioguideId')
              if bioidnode is not None:
                  bioid = bioidnode.text
                  if bioid not in allPolicies[policyarea]:
                      allPolicies[policyarea][bioid] = {}
                  if "cosponsored" in allPolicies[policyarea][bioid]:
                      allPolicies[policyarea][bioid]["cosponsored"] += 1
                  else:
                      allPolicies[policyarea][bioid]["cosponsored"] = 1
      for subitem in allsubjects:
          subject = subitem.find('name').text.replace(" ","_")
          if subject not in dictSubjects:
              dictSubjects[subject] = {}
              if "total" in dictSubjects[subject]:
                  dictSubjects[subject]["total"] += 1
              else:
                  dictSubjects[subject]["total"] = 1
              for item in allsponsors:
                  bioidnode = item.find('bioguideId')
                  if bioidnode is not None:
                      bioid = bioidnode.text
                      if bioid not in dictSubjects[subject]:
                          dictSubjects[subject][bioid] = {}
                      if "sponsored" in dictSubjects[subject][bioid]:
                          dictSubjects[subject][bioid]["sponsored"] += 1
                      else:
                          dictSubjects[subject][bioid]["sponsored"] = 1
              for item in allcosponsors:
                  bioidnode = item.find('bioguideId')
                  if bioidnode is not None:
                      bioid = bioidnode.text
                      if bioid not in dictSubjects[subject]:
                          dictSubjects[subject][bioid] = {}
                      if "cosponsored" in dictSubjects[subject][bioid]:
                          dictSubjects[subject][bioid]["cosponsored"] += 1
                      else:
                          dictSubjects[subject][bioid]["cosponsored"] = 1

dictSubjects = {}
allPolicies = {}
congresses = set()
chambers = set()

args = parser.parse_args()
print args.filespath

for path in args.filespath:
    walkpath(path)

if len(congresses) > 1:
    congress = "all"
else:
    congress = congresses.pop()

if len(chambers) > 1:
    print "Error: there are statuses for more than one chamber!"
else:
    chamber = chambers.pop()

with open("policyareasbymember_" + str(congress) + "_" + chamber + ".js", 'w') as outfile:
    json.dump(allPolicies, outfile)

with open("subjectssbymember_" + str(congress) + "_" + chamber + ".js", 'w') as outfile:
    json.dump(dictSubjects, outfile)
