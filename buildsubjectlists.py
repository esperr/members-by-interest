import functools
import logging
import json
#import urllib
#import urlfetch
import requests
import time
from StringIO import StringIO
from zipfile import ZipFile
import xml.etree.ElementTree as etree
import os
import argparse


parser = argparse.ArgumentParser(description='''Fetches and parses zipped XML Bill status files from FDSys in order to
build the data structures for Members by Interest ''')
parser.add_argument("congress", help="Number of congress, or 'all' for all available congresses")
parser.add_argument("chamber", help="Chamber, 'house' or 'senate'")


localtime = time.asctime( time.localtime(time.time()) )
congresses = ['113', '114', '115']
housetypes = ["hres", "hr", "hjres", "hconres"]
housetypes2 = ["hres"]
senatetypes = ["sres", "sjres", "sconres", "s"]

testfetch = []
allHeadings = {}
dictSubjects = {}
allPolicies = {}

args = parser.parse_args()
congresschoice = args.congress
chamber = args.chamber

#congress= "113"
#chamber = "senate"

targetList = []
if chamber == "house":
    locationList = housetypes
if chamber == "senate":
    locationList = senatetypes

if congresschoice == "all":
    for location in locationList:
        for congress in congresses:
            zipurl = "https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS/" + congress + "/" + location + "/BILLSTATUS-" + congress + "-" + location + ".zip"
            targetList.append(zipurl)
else:
    for location in locationList:
        zipurl = "https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS/" + congresschoice + "/" + location + "/BILLSTATUS-" + congresschoice + "-" + location + ".zip"
        targetList.append(zipurl)


def fetchZips(targetList):
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

    def parseZip(zf):
        for myname in zf.namelist():
            myfile = zf.read(myname)
            root = etree.fromstring(myfile)
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
            #testfetch.append(allsponsors)

    testfetch = []
    allHeadings = {}
    dictSubjects = {}
    allPolicies = {}

    for target in targetList:
        try:
            #validate_certificate = 'true'
            result = requests.get(target)
            if result.status_code == 200:
                zf = ZipFile(StringIO(result.content))
                parseZip(zf)
            else:
                return result.status_code
        except urlfetch.Error:
                logging.exception('Caught exception fetching url')

    with open("policyareasbymember_" + str(congresschoice) + "_" + chamber + ".js", 'w') as outfile:
        json.dump(allPolicies, outfile)

    with open("subjectsbymember_" + str(congresschoice) + "_" + chamber + ".js", 'w') as outfile:
        json.dump(dictSubjects, outfile)

    return "All done!"


writeme = fetchZips(targetList)
print writeme
