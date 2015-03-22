import os, sys, logging, praw, HTMLParser, ConfigParser
from bs4 import BeautifulSoup
from urlparse import urlparse
from tldextract import tldextract

'''
Grab the config file (we're gonna need it later on)
'''
try:
  config = ConfigParser.ConfigParser()
  config.read(os.path.dirname(os.path.realpath(__file__)) + '/settings.conf')
  assert(config.get('global', 'outputfile'))
  print "Settings parsed correctly."
except ConfigParser.NoSectionError:
  print "Your config file does not appear to be valid. Please verify that settings.conf exists."
  

# log events to redditScraper.log with debug level logging
LOG_FILENAME = config.get('global', 'logfile')
LOG_LEVEL = config.get('global', 'loglevel')
logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVEL)

# we need this to unescape the escaped characters
redditParse = HTMLParser.HTMLParser() 

# create a file for saving the reddit stuff to
scrapeOutput = open('prawScrape.html', 'r+')

#let's grab the stuff from reddit using praw
reddit = praw.Reddit(user_agent='linux:ResearchRedditScraper:v0.1 (by /u/plzHowDoIProgram)')

username = config.get('user', 'username')
password = config.get('user', 'password')

print "Logging into Reddit..."
reddit.login(username, password)

print "Requesting comments from reddit..."
commentPile = reddit.get_comments('learnprogramming', limit=None)
print type(commentPile)
#print "We got " + str(size(commentPile)) + " comments from reddit."

print "Request complete. Parsing raw comments..."
commentCount = 0
for comments in commentPile:
	scrapeOutput.write((redditParse.unescape(comments.body_html)).encode('utf-8')) #unescape the html and put in unicode
	commentCount += 1

print "Complete. We parsed " + str(commentCount) + " comments."
	
#or get input through a file on the command line, this is much faster
f = open(sys.argv[1]) #remember sys.argv[0] is the name of the script
					  #open defaults to read if no argument given

# create a dictionary to keep the resource names in and count the number of appearences
resources = {} 
#parse the document. we're using the praw version now
htmlParse = BeautifulSoup(scrapeOutput) 
# find all a href link tags
linkPile = htmlParse.find_all('a') 
# TODO: do we need to find markdown links also?

for linkCandidate in linkPile:
	print linkCandidate
	baseUrl = urlparse(linkCandidate['href']).hostname
	
	if baseUrl:
		resourceFound = tldextract.extract(baseUrl).domain # we only want top level domains
		if resources.has_key(resourceFound): #check each name against this list to see if it's new
			resources[resourceFound] = (resources[resourceFound]+1)  #if in list, increment count
		else:
			resources[resourceFound] = 1  #if not in list, add it 
print resources

#now go back through the file and find how many times in all text each resources shows up

with open(sys.argv[1],'r') as inputFile:
	allText = inputFile.read()
	for key in resources:
		totalCount = 0
		totalCount = allText.count(key)
		print key, totalCount 
	 



