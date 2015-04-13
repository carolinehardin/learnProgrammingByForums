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

#find-replace fixing the double quotes (needed for the URL grabbing) screws up the rows, so use the original double quote one in counting rows
inputRawCSV = config.get('global', 'inputRawCSV')

with open(inputCSV,'r') as inputFile:
	#parse the input csv using beautiful soup
	soup = BeautifulSoup(inputFile)
	linkPile = [a.attrs.get('href') for a in soup.find_all('a')]
	
#pretty print the output to see what we've got so far
#pp.pprint(linkPile)
print "We found " + str(len(linkPile)) + " total number of links"

#create a dictionary to keep the resource names in and count the number of appearences
print "Building dictionary...."
resources = {} 

#look at every link in the pile
for linkCandidate in linkPile:
	#pp.pprint(linkCandidate)
	baseUrl = " "
	
	try:
		#we only want the hostname
		baseUrl = urlparse(linkCandidate).hostname 
		
	except: #we get some non-url text somehow. 
		print 'Skip this:' 
		print linkCandidate

	# if it's not empty
	if not baseUrl is None:
		# extract the TLD
		resourceFound = tldextract.extract(baseUrl).domain 
		#check each name against this list to see if it's new
		if resources.has_key(resourceFound): 
			#if in list, increment count
			resources[resourceFound] = (resources[resourceFound]+1)  
		else:
			#if not in list, add it 
			resources[resourceFound] = 1 

#seed the dictionary with the most commonly used resources listed on the reddit FAQ
	resources.update({'RubyMonk':0, 'tryruby':0, 'Hackety Hack':0,'Codecademy':0,'Codeacademy':0,'Eloquent JavaScript':0, 'CaveOfProgramming':0, 'Udemy':0,'Try Python':0, 'learnpython':0, 'Crunchy':0,  'coursera':0, 'udacity':0, 'edX':0 })

print "Dictionary complete. "
pp.pprint(resources)

#create an empty list for collecting results
csvOutput = []
csvOutput.append(fieldnames)

#now go back through the file and find how many times in all text each resources shows up. Count by comments, not total appearences.
#i.e., if someone talks about 'stackoverflow' three times in a single comment, it is only counted once.
#this will run slow!

	
for key in resources:
	#change to unicode to avoid parsing problems. add spaces to get discreet keys, not parts of words
	unicodeKey = " " + key.encode('utf-8') + " "
		
	totalCount = 0

	#we are counting by the row as each row is a comment
	with open(inputRawCSV,'rb') as inputFile:
		reader = csv.reader(inputFile)
		for row in reader:
			#the second column has the body text. get it in lower case
			bodyText = row[1].lower()
			
			if((bodyText.count(unicodeKey))>0):
				totalCount += 1
		
	#now that we've gone through each row, add it to the output.
	csvOutput.append([key,resources[key], totalCount])
	
#finally, save the CSV file
print "Writing results to CSV file...."

with open(outputCSV, 'w+') as csvfile:
	csvwrite = csv.writer(csvfile)
	for row in csvOutput:
		csvwrite.writerow(row)
print "Complete. Results can be found in " + outputCSV
	 



