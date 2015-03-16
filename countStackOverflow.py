
from bs4 import BeautifulSoup
import sys
from urlparse import urlparse
from tldextract import tldextract
import logging
import praw
import HTMLParser


LOG_FILENAME = 'countStackOverflow.log'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
h = HTMLParser.HTMLParser() #we need this to unescape the escaped characters

#for c in lp:
#		f.write((h.unescape(c.body_html)).encode('utf-8')) #unescape the html and put in unicode
		

#get input through a file on the command line, 
f = open(sys.argv[1]) #remember sys.argv[0] is the name of the script
					  #open defaults to read if no argument given


resources = {} #create a dictionary to keep the resource names in and count the number of appearences
soup = BeautifulSoup(f) #parse the document. we're using the praw version now
links = soup.find_all('a')#find all a href link tags

# we need to find markdown links also?

for x in links:
	#print x
	try:
		anchorText = x.findNext('a').text #get the anchor text
		print anchorText
		burl = urlparse(anchorText).hostname # we only want the hostname
	except: #we get some non-url text somehow
		print 'Skip this:' 
		print x

	if burl:
		resourceFound = tldextract.extract(burl).domain # we only want top level domains
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
		totalCount = allText.count(key.encode('utf-8'))
		print key, totalCount 
	 



