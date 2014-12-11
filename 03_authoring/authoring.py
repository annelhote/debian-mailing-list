#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python authoring.py


# Imports
import io, datetime
from pprint import pprint
from pymongo import MongoClient


# Log the message level and the message into a log file
# file				: file object	: the file into which write
# level				: string 		: the log level of the message (info, warning, alert ...)
# message 			: string 		: the message content to be logged
# return 			: void
def log(file, level, message):
	message = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' | ' + level + ' | ' + message + '\n'
	file.write(unicode(message))


# Main
if __name__ == "__main__":
	# MongoDB connection
	client 				= MongoClient('localhost', 27017)
	db 					= client.debian
	mailsCollection 	= db.mails201409
	authorsCollection 	= db.authors201409

	# Clear all authors
	authorsCollection.remove({})

	# Open a log file
	f = io.open('error.log', 'w', encoding='utf-8')
	log(f, 'info', 'Start authoring')

	# Iterate over mails
	for mail in mailsCollection.find():
		# If mail['fromemail'] is not already an author, add it
		if authorsCollection.find({'emails':mail['fromemail'],'deleted':{'$exists':False}}).count() == 0:
			authorsCollection.insert({'emails':[mail['fromemail']],'mails':[mail['_id']],'count':1,'startdate':mail['timestamp'],'enddate':mail['timestamp']})
		# Else increment the count and update the startdate and enddate fields if needed
		else:
			author = authorsCollection.find({'emails':mail['fromemail'],'deleted':{'$exists':False}})[0]
			startdate = mail['timestamp'] if mail['timestamp'] < author['startdate'] else author['startdate']
			enddate = mail['timestamp'] if mail['timestamp'] > author['enddate'] else author['enddate']
			authorsCollection.update({'_id':author['_id']},{'$set':{'startdate':startdate,'enddate':enddate},'$push':{'mails':mail['_id']}, '$inc':{'count':1}})


	# Close the log file
	log(f, 'info', 'End authoring')
	f.close()