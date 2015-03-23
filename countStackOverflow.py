#include info from https://archive.org/details/stackexchange
import os, logging, praw, HTMLParser, ConfigParser, pprint, csv, sys

from bs4 import BeautifulSoup
from urlparse import urlparse
from tldextract import tldextract

print "StackOverflow Research Scraper v0.1"
print "============================"

'''
Grab the config file (we're gonna need it later on)
'''
try:
	config = ConfigParser.ConfigParser()
	config.read(os.path.dirname(os.path.realpath(__file__)) + '/settingsSO.conf')
	assert(config.get('global', 'inputcsv'))
	print "Settings parsed correctly."
except ConfigParser.NoSectionError:
	print "Your config file does not appear to be valid. Please verify that settings.conf exists."
	
#make a pretty printer for use later
pp = pprint.PrettyPrinter(indent=4)

#log events to stackOverflowScraper.log
LOG_FILENAME = config.get('global', 'logfile')
LOG_LEVEL = config.get('global', 'loglevel')
logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVEL)

#we need this to unescape the escaped characters
soParse = HTMLParser.HTMLParser() 

#create file for saving the stackoverflow stuff to
outputCSV = config.get('global', 'outputcsv')

# put together a dictionary for building the CSV file
# resource, number of links, number of mentions
fieldnames = ['resource', 'number of links', 'number of mentions']

#get the input csv which was created at http://data.stackexchange.com/stackoverflow/
#using query select Id as [Post Link], Body, Score from Posts where (Title like '%get started%' OR Title like '% learn %') and ParentId is null
inputCSV = config.get('global', 'inputcsv')
with open(inputCSV,'r') as inputFile:
	#parse the input csv using beautiful soup
	soup = BeautifulSoup(inputFile)
	#find all a href link tags
	linkPile = soup.find_all('a')

#pretty print the output to see what we've got so far
#pp.pprint(linkPile)
print "We found " + str(len(linkPile)) + " total number of links"

print "Building dictionary...."
#create a dictionary to keep the resource names in and count the number of appearences
resources = {} 

#look at every link in the pile
for linkCandidate in linkPile:

	try:
		#get the anchor text
		anchorText = linkCandidate.findNext('a').text 
		print anchorText
		# we only want the hostname
		baseUrl = urlparse(anchorText).hostname 
	except: #we get some non-url text somehow
		print 'Skip this:' 
		print linkCandidate

	# if it's not empty
	if baseUrl:
		# extract the TLD
		resourceFound = tldextract.extract(baseUrl).domain 
		#check each name against this list to see if it's new
		if resources.has_key(resourceFound): 
			#if in list, increment count
			resources[resourceFound] = (resources[resourceFound]+1)  
		else:
			resources[resourceFound] = 1  #if not in list, add it 

print "Dictionary complete. "
pp.pprint(resources)

#create an empty list for collecting results
csvOutput = []
csvOutput.append(fieldnames)

#now go back through the file and find how many times in all text each resources shows up

with open(inputCSV,'r') as inputFile:
	allText = inputFile.read()
	for key in resources:
		totalCount = 0
		totalCount = allText.count(key.encode('utf-8'))
		csvOutput.append([key,resources[key], totalCount])
		
#finally, save the CSV file
print "Writing results to CSV file...."
with open(outputCSV, 'w+') as csvfile:
	csvwrite = csv.writer(csvfile)
	for row in csvOutput:
		csvwrite.writerow(row)
print "Complete. Results can be found in " + outputCSV
	 



