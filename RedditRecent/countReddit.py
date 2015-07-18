import os, logging, praw, HTMLParser, ConfigParser, pprint, csv,re
from bs4 import BeautifulSoup
from urlparse import urlparse
from tldextract import tldextract
from collections import Counter

print "Reddit Research Scraper TOP v0.1"
print "============================"

'''
Grab the config file (we're gonna need it later on)
'''

try:
  config = ConfigParser.ConfigParser()
  config.read(os.path.dirname(os.path.realpath(__file__)) + '/settingsR.conf')
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
linkPile = config.get('global', 'linkPile')
linksAndTLD = config.get('global', 'linksAndTLD')

# put together a dictionary for building the CSV file
# resource, number of links, number of mentions
fieldnames = ['resource', 'number of links', 'number of mentions']


'''#let's grab the stuff from reddit using praw

reddit = praw.Reddit(user_agent='linux:ResearchRedditScraper:v0.1 (by /u/plzHowDoIProgram)')

username = config.get('user', 'username')
password = config.get('user', 'password')

print "Logging into Reddit..."
reddit.login(username, password)

print "We're in. Requesting comments from reddit..."
submissions=reddit.search('subreddit:learnprogramming', sort='new', limit='none')


print "Request complete. Parsing raw comments to CSV..."
commentCount = 0

#write thread comments to a csv file for counting
with open(commentsCSV, 'w') as csvFile:
	csvwriter= csv.writer(csvFile,delimiter='\t')
	
	for thread in submissions:
		flat_comments = praw.helpers.flatten_tree(thread.comments)
		
		for comment in flat_comments:
			#unescape the html and put in unicode
			try:
				
				commentFormatted = (redditParse.unescape(comment.body)).encode('utf-8')
				#pprint.pprint(comment)
				
				csvwriter.writerow([commentFormatted])
	
			except AttributeError:
				pass
		commentCount += 1

print "Complete. We parsed " + str(commentCount) + " comments."


'''
#pause here. Run a grep on the output to find the urls, save it in a textfile with same name as determined in the config file
#here is the grep:
#cat redditCommentsFixed.csv | egrep -o "http://([A-Za-z0-9-]+\.)+[A-Za-z]+(/)*([[:alnum:]/._])*" | sort > whateveryouwanttocallthis.txt
#new lines fixed thus: opened the .csv file in LibreCalc and did a 'find a replace' for \n, checking the 'regular expression' box
#also, you probably want to make sure all simple links (www.google.com) end with a back slash or they might be counted as tld of 'com' or 'org', etc
with open(linkPile, 'r') as inputFile:
	
	#create a dictionary to keep the resource names in and count the number of appearences
	print "Building dictionary...."
	resources = {} 
	candidateAndBaseURL = [] #this is for debugging purposes, it is helpful to see the orignial link and the derived tld

	#look at every link in the pile
	for linkCandidate in inputFile:
		
		resourceFound = tldextract.extract(linkCandidate).domain 
		pp.pprint(resourceFound)
	
		#store these values for debugging purposes
		#you will want to look through this for any anomolies, such as http://learnpythonthehardway.com being parsed as 'com'
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

#save the results in closer detail for debugging
with open(linksAndTLD, 'w+') as csvfile:
	csvwrite = csv.writer(csvfile)
	for row in candidateAndBaseURL:
		csvwrite.writerow(row)

print "Links and the derived TLD printed to file"

#create an empty list for collecting results
csvOutput = []
csvOutput.append(fieldnames)

#now go back through the file and find how many times in all text each resources shows up. Count by comments, not total appearences.
#i.e., if someone talks about 'stackoverflow' three times in a single comment, it is only counted once.
#this will run slow!


#count the number of appearences per resource key
keyCounts = Counter()
	
#count progress through all the comments
lineCounter = 0
	
with open(commentsFixedCSV,'rb') as inputFile:
	
	#for every line of text in file
	for textComment in inputFile:
		#for every resource URL previously found
		for key in resources:
			
			#\b is for word boundary - we don't want to match to parts of words or 
			#python and learnpythonthehardway will get mixed up
			searchString = "\\b" + key + "\\b" 
			
			#if they key is found, increment the counter
			if re.search(searchString, textComment , flags=re.I):
				keyCounts[key] += 1
		
		#track progress
		lineCounter += 1
		if (lineCounter % 1000) == 0:
			print "\rlines: " + str(lineCounter)
		
				
#now that we've gone through each row, add it to the output.
for key in resources:
	csvOutput.append([key,resources[key], keyCounts[key]])
	
#finally, save the CSV file
print "Writing results to CSV file...."

with open(outputCSV, 'w+') as csvfile:
	csvwrite = csv.writer(csvfile)
	for row in csvOutput:
		csvwrite.writerow(row)
print "Complete. Results can be found in " + outputCSV
	 



