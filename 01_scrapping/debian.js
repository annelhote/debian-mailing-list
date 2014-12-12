// node debian.js 1996

// Imports
var sandcrawler 	= require('sandcrawler'),
	logger 			= require('sandcrawler-logger'),
	fs 				= require('fs'),
	process 		= require('process'),
	MongoClient		= require('mongodb').MongoClient,
	format 			= require('util').format
	debianScraper	= require('./scraper.js');


// Get command line args
var iYear = process.argv[2];


// Parameters
var iLimit			= 0;
var sRoottUrl		= "https://lists.debian.org/debian-user/";
var iMonth			= 1;
var sStartMessage	= "msg00000.html";
var sStartUrl		= sRoottUrl + iYear + '/' + (iMonth < 10 ? '0' + iMonth : iMonth) + '/' + sStartMessage;


MongoClient.connect('mongodb://127.0.0.1:27017/debian', function(err, db) {
	if(err) throw err;
	var mailsCollection = db.collection('mails');

	// Create and config scraper
	var scraper = new sandcrawler.staticScraper('debian')
		.use(logger())
		.config({autoRetry : true, maxRetries : 5, timeout : 20 * 1000})
		.url(sStartUrl)
		.limit(iLimit)
		.iterate(function(i, req, res) {
			if(res.data.nextbydate) {
				// If the next url is full
				if(res.data.nextbydate.indexOf('http://') != -1) {
					sUrl = res.data.nextbydate;
				// Else build it
				} else {
					sUrl = sRoottUrl + iYear + '/' + (iMonth < 10 ? '0' + iMonth : iMonth) + '/' + res.data.nextbydate;	
				}
				return sUrl;
			} else {
				if(iMonth == 12) {
					return false;
				} else {
					iMonth 		+= 1;
					sUrl 		= sRoottUrl + iYear + '/' + (iMonth < 10 ? '0' + iMonth : iMonth) + '/' + sStartMessage;
					return sUrl;
				}
			}
			
		})
		.parse(debianScraper)
		.afterScraping(function(req, res, next) {
			// Add scraped url
			res.data.mail.url = req.url;
			mailsCollection.insert(res.data.mail, function(err, docs) {
				if(err) {
					return next(new Error('mongo-error'));
				} else {
					next();
				}
			});
		})
		.on('job:done', function(job) {
			if(job.state.failing) {
				MongoClient.connect('mongodb://127.0.0.1:27017/debian', function(err, db) {
					if(err) throw err;
					var urlsCollection = db.collection('urls');
					urlsCollection.insert({'url' : job.req.url, 'state' : 'fail'}, function(err, docs) {
						if(err) {
							console.log(err);
						}
					});
					db.close();
				});
			}
		})
		.result(function(err, req, res) {
		});

	sandcrawler.run(scraper, function(err, remains) {
		setTimeout(function() { db.close(); }, 1 * 1000);
		console.log(remains.map(function(item) {
			return item.error;
		}));
	});
});