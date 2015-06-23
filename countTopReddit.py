import os, logging, praw, HTMLParser, ConfigParser, pprint, csv,re
from bs4 import BeautifulSoup
from urlparse import urlparse
from tldextract import tldextract

print "Reddit Research Scraper TOP v0.1"
print "============================"

try:
  config = ConfigParser.ConfigParser()
  config.read(os.path.dirname(os.path.realpath(__file__)) + '/settingsR-TOP.conf')
  assert(config.get('global', 'outputCSV'))
  print "Settings parsed correctly."
except ConfigParser.NoSectionError:
  print "Your config file does not appear to be valid. Please verify that settings.conf exists."

#make a pretty printer for use later
pp = pprint.PrettyPrinter(indent=4)  

# we need this to unescape the escaped characters
redditParse = HTMLParser.HTMLParser()

# log events to redditScraper.log with debug level logging
LOG_FILENAME = config.get('global', 'logfile')
LOG_LEVEL = config.get('global', 'loglevel')
logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVEL)

# create files for saving the reddit stuff to
outputCSV  = config.get('global', 'outputCSV')
commentsCSV	= config.get('global', 'commentsCSV')
commentsFixedCSV	= config.get('global', 'commentsFixedCSV')

# put together a dictionary for building the CSV file
# resource, number of links, number of mentions
fieldnames = ['resource', 'number of links', 'number of mentions']


'''
#let's grab the stuff from reddit using praw
reddit = praw.Reddit(user_agent='linux:ResearchRedditScraper:v0.1 (by /u/plzHowDoIProgram)')

username = config.get('user', 'username')
password = config.get('user', 'password')

print "Logging into Reddit..."
reddit.login(username, password)

print "We're in. Requesting comments from reddit..."
submissions=reddit.search('subreddit:learnprogramming', sort='top', limit='none')

print "Request complete. Parsing raw comments to CSV..."
commentCount = 0

#write comment to a csv file for counting
with open(commentsCSV, 'w') as csvFile:
	csvwriter= csv.writer(csvFile,delimiter='\t')
	
	for thread in submissions:
		flat_comments = praw.helpers.flatten_tree(thread.comments)
		
		for comment in flat_comments:
			#unescape the html and put in unicode
			try:
				pprint.pprint(comment)
				#commentFormatted = string.replace((redditParse.unescape(comment)).encode('utf-8'),'""', '"')
				#csvwriter.writerow([commentFormatted])
	
			except AttributeError:
				pass
		commentCount += 1

print "Complete. We parsed " + str(commentCount) + " comments."


# parse the document. We already removed the double quotes & replaced them with single quotes
with open(commentsFixedCSV,'r') as inputFile:
	#parse the input csv using beautiful soup
	soup = BeautifulSoup(inputFile)
	linkPile = [a.attrs.get('href') for a in soup.find_all('a')]
'''

def regExUrl(commentText):
	#thanks to  dperini (and adamrofer for the python port) https://gist.github.com/dperini/729294

# Regular Expression for URL validation
#
# Author: Diego Perini
# Updated: 2010/12/05
# License: MIT
#
# Copyright (c) 2010-2013 Diego Perini (http://www.iport.it)
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
	
	URL_REGEX = re.compile(
		u"^"
		# protocol identifier
		u"(?:(?:https?|ftp)://)"
		# user:pass authentication
		u"(?:\S+(?::\S*)?@)?"
		u"(?:"
		# IP address exclusion
		# private & local networks
		u"(?!(?:10|127)(?:\.\d{1,3}){3})"
		u"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
		u"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
		# IP address dotted notation octets
		# excludes loopback network 0.0.0.0
		# excludes reserved space >= 224.0.0.0
		# excludes network & broadcast addresses
		# (first & last IP address of each class)
		u"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
		u"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
		u"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
		u"|"
		# host name
		u"(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)"
		# domain name
		u"(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*"
		# TLD identifier
		u"(?:\.(?:[a-z\u00a1-\uffff]{2,}))"
		u")"
		# port number
		u"(?::\d{2,5})?"
		# resource path
		u"(?:/\S*)?"
		u"$"
		, re.UNICODE)
		
	urlsFound = URL_REGEX.findall(commentText)
	return urlsFound

# parse the document. We already removed the double quotes & replaced them with single quotes
with open(commentsFixedCSV,'r') as inputFile:
	#parse the document with regular expressions
	for commentText in commentsFixedCSV:
		pprint.pprint("todo: save the results in linkPile")
		pprint.pprint(regExUrl(""" some text http://www.nyt.com"""))



'''
#pretty print the output to see what we've got so far
#pp.pprint(linkPile)
print "We found " + str(len(linkPile)) + " total number of links"
	




#create a dictionary to keep the resource names in and count the number of appearences
print "Building dictionary...."
resources = {} 

#look at every link in the pile
for linkCandidate in linkPile:
	pp.pprint(linkCandidate)
	baseUrl = " "
	
	try:
		#we only want the hostname
		baseUrl = urlparse(linkCandidate).hostname 
		
	except: #if we get some non-url text somehow. 
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
	resources.update({'rubymonk':0, 'tryruby':0, 'hackety hack':0,'codecademy':0,'codeacademy':0,'eloquent javascript':0, 'caveofprogramming':0, 'udemy':0,'try python':0, 'learnpython':0, 'crunchy':0,  'coursera':0, 'udacity':0, 'edx':0 })

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
	
	#make sure we are in lower case for everything
	unicodeKey = unicodeKey.lower()
		
	totalCount = 0

	#we are counting by the row as each row is a comment
	with open(commentsCSV,'rb') as inputFile:
		reader = csv.reader(inputFile, delimiter='\t')
		for row in reader:
			#the second column has the body text. get it in lower case
			bodyText = row[0].lower()
			
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
	 
'''


