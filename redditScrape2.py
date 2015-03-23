import os, logging, praw, HTMLParser, ConfigParser, pprint
from bs4 import BeautifulSoup
from urlparse import urlparse
from tldextract import tldextract

print "Reddit Research Scraper v0.1"
print "============================"

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

# gimme a pretty printer in case I need it later
pp = pprint.PrettyPrinter(indent=4)  

# log events to redditScraper.log with debug level logging
LOG_FILENAME = config.get('global', 'logfile')
LOG_LEVEL = config.get('global', 'loglevel')
logging.basicConfig(filename=LOG_FILENAME, level=LOG_LEVEL)

# we need this to unescape the escaped characters
redditParse = HTMLParser.HTMLParser() 

# create a file for saving the reddit stuff to
outputFile = config.get('global', 'outputFile')

#let's grab the stuff from reddit using praw
reddit = praw.Reddit(user_agent='linux:ResearchRedditScraper:v0.1 (by /u/plzHowDoIProgram)')

username = config.get('user', 'username')
password = config.get('user', 'password')

print "Logging into Reddit..."
reddit.login(username, password)

print "We're in. Requesting comments from reddit..."
commentPile = reddit.get_comments('learnprogramming', limit=None)

print "Request complete. Parsing raw comments to HTML..."
commentCount = 0
with open(outputFile, 'w+') as scrapeOutput:
	for comments in commentPile:
		scrapeOutput.write((redditParse.unescape(comments.body_html)).encode('utf-8')) #unescape the html and put in unicode
		commentCount += 1

print "Complete. We parsed " + str(commentCount) + " comments."
	
# parse the document. we're using the praw version now
with open(outputFile, 'r') as scrapeOutput:
	soup = BeautifulSoup(scrapeOutput) 
	# find all a href link tags
	linkPile = soup.find_all('a') 
	# pretty print the output to see what we've got so far
	#pp.pprint(linkPile)
	print "We found " + str(len(linkPile)) + " total links in this pull."

	print "Building dictionary..."
	# create a dictionary to keep the resource names in and count the number of appearences
	resources = {} 
	

	# look at every link in the pile
	for linkCandidate in linkPile:
		# obtain the baseUrl
		baseUrl = urlparse(linkCandidate['href']).hostname
		
		# if it's not empty
		if baseUrl:
			# extract the TLD
			resourceFound = tldextract.extract(baseUrl).domain # we only want top level domains
			if resources.has_key(resourceFound): #check each name against this list to see if it's new
				resources[resourceFound] = (resources[resourceFound]+1)  #if in list, increment count
			else:
				resources[resourceFound] = 1  #if not in list, add it 
	
	print "Dictionary complete. \n Here's what I've found so far: "
	pp.pprint(resources)



# now go back through the file and find how many times in all text each resources shows up
with open(outputFile, 'r') as scrapeOutput:
	allText = scrapeOutput.read()
	for key in resources:
		totalCount = 0
		totalCount = allText.count(key)
		print key + " was referenced " + str(totalCount) + " times."



