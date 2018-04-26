import os
import argparse
import xml.etree.ElementTree as etree
import json

parser = argparse.ArgumentParser(description='''Process a list of Bill status XML files downloaded from FDSys to produce the source files for use by members-by-interest.
        buildsubjectlists.py will generate both policyareasbymember and subjectsbymember files in one pass, but is intended to be run against statuses for *one* chamber at a time
        (House only or Senate only). Run it against statuses for one chamber and congress to generate a file for that particular congress or against all available statuses for a chamber
        to generate an inclusive file for all congresses. ''')
parser.add_argument("filespath", help="Path(s) to downloaded files -- separtate multiple paths with a [space]", nargs="+")

dictSubjects = {}
allPolicies = {}
congresses = set()
chambers = set()
#test vars go here!
testme = []

def addSubject(subject, sponsors, cosponsors, type):
    if type == "policy":
        rootdict = allPolicies
    else:
        rootdict = dictSubjects
    #policyarea = policy.text.replace(" ","_")
    if subject not in rootdict:
        rootdict[subject] = {}
    if "total" in rootdict[subject]:
        rootdict[subject]["total"] += 1
    else:
        rootdict[subject]["total"] = 1
    for item in sponsors:
        bioidnode = item.find('bioguideId')
        if bioidnode is not None:
            bioid = bioidnode.text
            if bioid not in rootdict[subject]:
                rootdict[subject][bioid] = {}
            if "sponsored" in rootdict[subject][bioid]:
                rootdict[subject][bioid]["sponsored"] += 1
            else:
                rootdict[subject][bioid]["sponsored"] = 1
    for item in cosponsors:
        withdrawn = item.find('sponsorshipWithdrawnDate').text
        if withdrawn is None:
            bioidnode = item.find('bioguideId')
            if bioidnode is not None:
                bioid = bioidnode.text
                if bioid not in rootdict[subject]:
                    rootdict[subject][bioid] = {}
                if "cosponsored" in rootdict[subject][bioid]:
                    rootdict[subject][bioid]["cosponsored"] += 1
                else:
                    rootdict[subject][bioid]["cosponsored"] = 1

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
        allsponsors = root.findall('.bill/sponsors/item')
        allcosponsors = root.findall('.bill/cosponsors/item')
        policynode = root.find('.//policyArea/name')
        if policynode is not None:
            policy = policynode.text.replace(" ","_")
            addSubject(policy, allsponsors, allcosponsors, "policy")
        allsubjects = root.findall('.//billSubjects/legislativeSubjects/item')
        for subitem in allsubjects:
            subject = subitem.find('name').text.replace(" ","_")
            addSubject(subject, allsponsors, allcosponsors, "legsubject")

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

print len(testme)
with open("policyareasbymember_" + str(congress) + "_" + chamber + ".js", 'w') as outfile:
    json.dump(allPolicies, outfile)

with open("subjectsbymember_" + str(congress) + "_" + chamber + ".js", 'w') as outfile:
    json.dump(dictSubjects, outfile)
