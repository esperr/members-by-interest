import os
import argparse
import xml.etree.ElementTree as etree
import json
import requests
from StringIO import StringIO
from zipfile import ZipFile

# Generates a structured Member file for use with # Members by Interest. Grabs current members
# from files downloaded from the Clerks' offices, and then supplements that data with sponsoring and cosponsoring members from earlier congresses.
# This version takes no arguments, as it is scheduled to be repalced after March with an automatic process.

currentcongress = "116"
pastcongresses = ['113', '114', '115']
housetypes = ["hres", "hr", "hjres", "hconres"]
senatetypes = ["sres", "sjres", "sconres", "s"]


def grabHouse():
    tree = etree.parse('housemembers.xml')
    root = tree.getroot()
    allreps = root.findall('.members/member')
    for rep in allreps:
        bioid = rep.find('member-info/bioguideID').text
        party = rep.find('member-info/party').text
        district = rep.find('member-info/district').text
        sortname = rep.find('member-info/namelist').text
        officialname = rep.find('member-info/official-name').text
        if officialname:
            fullname = officialname
        else:
            firstname = rep.find('member-info/firstname').text
            lastname = rep.find('member-info/lastname').text
            if firstname and lastname:
                fullname = firstname + " " + lastname
        state = rep.find('member-info/state').get("postal-code")
        #state = statenode
        members['House'][bioid] = {}
        members['House'][bioid]['Sortname'] = sortname
        members['House'][bioid]['Fullname'] = fullname
        members['House'][bioid][currentcongress] = {}
        members['House'][bioid][currentcongress]['State'] = state
        members['House'][bioid][currentcongress]['Party'] = party
        members['House'][bioid][currentcongress]['District'] = district

def grabSenate():
    tree = etree.parse('senatemembers.xml')
    root = tree.getroot()
    allreps = root.findall('.//member')
    for rep in allreps:
        bioid = rep.find('./bioguide_id').text
        party = rep.find('./party').text
        firstname = rep.find('./first_name').text
        lastname = rep.find('./last_name').text
        sortname = lastname + ', ' + firstname
        fullname = firstname + ' ' + lastname
        state = rep.find('./state').text
        members['Senate'][bioid] = {}
        members['Senate'][bioid]['Sortname'] = sortname
        members['Senate'][bioid]['Fullname'] = fullname
        members['Senate'][bioid][currentcongress] = {}
        members['Senate'][bioid][currentcongress]['State'] = state
        members['Senate'][bioid][currentcongress]['Party'] = party

def grabstatuses(targets, chamber):
    for target in targets:
        result = requests.get(target)
        if result.status_code == 200:
            zf = ZipFile(StringIO(result.content))
            for myname in zf.namelist():
                myfile = zf.read(myname)
                root = etree.fromstring(myfile)
                congress = root.find('.bill/congress').text
                allsponsors = root.findall('.bill/sponsors/item')
                makememberlist( allsponsors, chamber, congress )
                allcosponsors = root.findall('.bill/cosponsors/item')
                makememberlist( allcosponsors, chamber, congress )


def makememberlist( membernodes, chamber, congress ):
    if chamber == "house":
      memberroot = members['House']
    else:
      memberroot = members['Senate']
    for item in membernodes:
        bioidnode = item.find('bioguideId')
        if bioidnode is not None:
            id = bioidnode.text
            if id not in memberroot:
                memberroot[id] = {}
                firstname = item.find('firstName').text.lower()
                firstname = firstname.capitalize()
                lastname = item.find('lastName').text.lower()
                lastname = lastname.capitalize()
                sortname = lastname + ', ' + firstname
                fullname = firstname + ' ' + lastname
                memberroot[id]['Sortname'] = sortname
                memberroot[id]['Fullname'] = fullname
        memberroot[id][congress] = {}
        party = item.find('party').text
        state = item.find('state').text
        memberroot[id][congress]['State'] = state
        memberroot[id][congress]['Party'] = party
        if item.find('district') is not None:
            district = item.find('district').text
            if chamber == "house":
                memberroot[id][congress]['District'] = district


#args = parser.parse_args()
#print args.filespath

members = {}
members['House'] = {}
members['Senate'] = {}
members['Congresses'] = [113,114,115,116]
grabHouse()
grabSenate()
housetargets = []
senatetargets = []

for location in housetypes:
    for congress in pastcongresses:
        zipurl = "https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS/" + congress + "/" + location + "/BILLSTATUS-" + congress + "-" + location + ".zip"
        housetargets.append(zipurl)

grabstatuses(housetargets, "house")

for location in senatetypes:
    for congress in pastcongresses:
        zipurl = "https://www.gpo.gov/fdsys/bulkdata/BILLSTATUS/" + congress + "/" + location + "/BILLSTATUS-" + congress + "-" + location + ".zip"
        senatetargets.append(zipurl)

grabstatuses(senatetargets, "senate")

with open("allmembers", 'w') as outfile:
    json.dump(members, outfile)
