#include info from https://archive.org/details/stackexchange
import os, logging, praw, HTMLParser, ConfigParser, pprint, csv, sys, re

from bs4 import BeautifulSoup
from urlparse import urlparse
from tldextract import tldextract
from collections import Counter

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
mentionsCSV = config.get('global', 'mentionsCSV')

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
candidateAndBaseURL = [] #this is for debugging purposes, it is helpful to see the orignial link and the derived tld

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
	
		#store these values for debugging purposes
		candidateAndBaseURL.append([linkCandidate, resourceFound])
	
		#check each name against this list to see if it's new
		if resources.has_key(resourceFound): 
			#if in list, increment count
			resources[resourceFound] = (resources[resourceFound]+1)  
		else:
			#if not in list, add it 
			resources[resourceFound] = 1 
			
	

#seed the dictionary with the most commonly used resources listed on the reddit FAQ
	resources.update({'rubymonk':0, 'tryruby':0, 'hackety hack':0,'codecademy':0,'codeacademy':0,'eloquent javascript':0, 'caveofprogramming':0, 'udemy':0,'try python':0, 'learnpython':0, 'crunchy':0,  'coursera':0, 'udacity':0, 'edx':0 })

print "Dictionary complete. "
pp.pprint(resources)

#create an empty list for collecting results
csvOutput = []
csvOutput.append(fieldnames)

#now go back through the file and find how many times in all text each resources shows up. Count by comments, not total appearences. To make sure this works,  opened the .csv file in LibreCalc and did a 'find a replace' for \n, checking the 'regular expression' box 
#i.e., if someone talks about 'stackoverflow' three times in a single comment, it is only counted once.
#Also note: it helps to do a find-replace for 'stack overflow' and replace with 'stackoverflow' for mentions count
#this will run slow!

#count the number of appearences per resource key
keyCounts = Counter()

#count progress through all the comments
lineCounter = 0

with open(mentionsCSV,'rb') as inputFile:
	
	#for every line of text in file
	for textComment in inputFile:
		#for every resource URL previously found
		for key in resources:
			
			#change to unicode to avoid parsing problems. add spaces to get discreet keys, not parts of words
			unicodeKey = " " + key.encode('utf-8') + " "
		
			#make sure we are in lower case for everything
			unicodeKey = unicodeKey.lower()
			
			#\b is for word boundary - we don't want to match to parts of words or 
			#python and learnpythonthehardway will get mixed up
			searchString = "\\b" + unicodeKey + "\\b" 
			
			#if they key is found, increment the counter. flag=re.I is for case insensitive
			if re.search(searchString, textComment , flags=re.I):
				keyCounts[unicodeKey] += 1
		
		#track progress
		lineCounter += 1
		if (lineCounter % 1000) == 0:
			print "\rlines: " + str(lineCounter)
	
	''' #old way
for key in resources:
	#change to unicode to avoid parsing problems. add spaces to get discreet keys, not parts of words
	unicodeKey = " " + key.encode('utf-8') + " "
		
	#make sure we are in lower case for everything
	unicodeKey = unicodeKey.lower()
		
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
'''
	
#finally, save the CSV file
print "Writing results to CSV file...."

with open(outputCSV, 'w+') as csvfile:
	csvwrite = csv.writer(csvfile)
	for row in csvOutput:
		csvwrite.writerow(row)
print "Complete. Results can be found in " + outputCSV
	 



