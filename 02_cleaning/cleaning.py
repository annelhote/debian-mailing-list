#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python cleaning.py


# Imports
import datetime, io, re, string, time
from pprint import pprint
from dateutil import parser
from pymongo import MongoClient


# Log the message level and the message into a log file
# file				: file object	: the file into which write
# level				: string 		: the log level of the message (info, warning, alert ...)
# message 			: string 		: the message content to be logged
# return 			: void
def log(file, level, message):
	message = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ' | ' + level + ' | ' + message + '\n'
	file.write(unicode(message))


# Normalize a string ie. transform it into lowercase, remove prepend 're:' and 'ccl:' and filter non alphanumeric character
# Recursive function
# title				: string 		: the string to normalize
# return 			: string 		: the normalized title
def normalize(title):
	title	= string.lower(title)
	search	= re.search('^ *(re|ccl) *: *(.*)', title, flags=re.IGNORECASE)
	if search:
		return normalize(search.group(2))
	else:
		return re.sub(r'[^\w\d]', '', title)


# Main
if __name__ == "__main__":
	# MongoDB connection
	client 	= MongoClient('localhost', 27017)
	db 		= client.debian
	mails 	= db.mails201409

	# Open a log file
	f = io.open('error.log', 'w', encoding='utf-8')
	log(f, 'info', 'Start cleaning')

	# Iterate over each email stored into mails collection
	for mail in mails.find():
		if mail['title']:
			titleclean = normalize(mail['title'])
		else:
			log(f, 'warning', 'Error in cleaning the field "title" of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['to'] and re.search('href=\"mailto:(.*?)\"', mail['metas']['to']):
			toemails = []
			tmps = re.findall('href=\"mailto:(.*?)\"', mail['metas']['to'])
			for tmp in tmps:
				tmp = re.sub(r'%40', r'@', tmp)
				toemails.append(tmp)
		else:
			log(f, 'warning', 'Error in cleaning the email address from the to field "to" of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['subject']:
			subjectclean = re.sub(r'<em>Subject</em>: ', r'', mail['metas']['subject'])
		else:
			log(f, 'warning', 'Error in cleaning the field "subject" of metas of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['from'] and re.search('href=\"mailto:(.*?)\"', mail['metas']['from']):
			fromemail = re.search('href=\"mailto:(.*?)\"', mail['metas']['from']).group(1)
			fromemail = re.sub(r'%40', r'@', fromemail)
		else:
			log(f, 'warning', 'Error in cleaning the email address from the field "from" of metas of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['date']:
			dateclean = re.sub(r'<em>Date</em>: ', r'', mail['metas']['date'])
		else:
			log(f, 'warning', 'Error in cleaning the field "date" of metas of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['messageid'] and re.search(r'html\">(.*?)</a>', mail['metas']['messageid']):
			messageidclean = re.search(r'html\">(.*?)</a>', mail['metas']['messageid']).group(1)
		else:
			log(f, 'warning', 'Error in searching the id from the field "messageid" of metas of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['inreplyto'] and re.search(r'html\">(.*?)</a>', mail['metas']['inreplyto']):
			inreplytoclean = re.search(r'html\">(.*?)</a>', mail['metas']['inreplyto']).group(1)
		else:
			log(f, 'warning', 'Error in searching the email address from the field "inreplyto" of metas of mail : ' + str(mail['_id']))
		if mail['metas'] and mail['metas']['references'] and re.search(r'html\">(.*?)</a>', mail['metas']['references']):
			referencesclean = re.sub(r'<em>References</em>: ', r'', mail['metas']['references'])
		else:
			log(f, 'warning', 'Error in searching the email address from the field "references" of metas of mail : ' + str(mail['_id']))
		if mail['url'] and re.search(r'/(\d{4})/(\d{2})/', mail['url']):
			datemonth = re.search(r'/(\d{4})/(\d{2})/', mail['url']).group(2)
			dateyear = re.search(r'/(\d{4})/(\d{2})/', mail['url']).group(1)
		else:
			log(f, 'warning', 'Error in searching field "url" of mail : ' + str(mail['_id']))
		if datemonth and dateyear:
			timestamp = int(time.mktime(parser.parse(datemonth + '/01/' + dateyear).timetuple()))
		else:
			log(f, 'warning', 'Error in calculating "datemonth" and "dateyear" of mail : ' + str(mail['_id']))
		mails.update(
			{'_id': mail['_id']},
			{
				'$set': {
					'titleclean': titleclean,
					'toemails': toemails,
					'subjectclean': subjectclean,
					'fromemail': fromemail,
					'dateclean': dateclean,
					'messageidclean': messageidclean,
					'inreplytoclean': inreplytoclean,
					'referencesclean': referencesclean,
					'datemonth': datemonth,
					'dateyear': dateyear,
					'timestamp': timestamp
				}
			}
		)

	# Close the log file
	log(f, 'info', 'End cleaning')
	f.close()