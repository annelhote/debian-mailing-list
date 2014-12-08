// node debian.js

// Imports
var sandcrawler 	= require('sandcrawler'),
	logger 			= require('sandcrawler-logger'),
	fs 				= require('fs'),
	process 		= require('process'),
	MongoClient		= require('mongodb').MongoClient,
	format 			= require('util').format;

var iLimit	= 0;
var sUrl	= "https://lists.debian.org/debian-consultants/";

MongoClient.connect('mongodb://127.0.0.1:27017/debian', function(err, db) {
	if(err) throw err;
	var mailsCollection = db.collection('mails');

	// Create and config scraper
	var scraper = new sandcrawler.scraper('debian')
		.use(logger())
		.config({autoRetry : true, maxRetries : 5, timeout : 20 * 1000})
		.url(sUrl)
		.limit(iLimit)
		.beforeScraping(function(req, next) {
			setTimeout(next, 100);
		})
		.iterate(function(i, req, res) {
			var reg = new RegExp("\\?" + year + "\\+");
			if((res.data.nav.next.match(reg)) && ((res.data.nav.previous != res.data.nav.next) || (i == 1))) {
				return 'http://www.ccl.net' + res.data.nav.next;
			} else {
				return false;
			}
		})
		.script('./scraper.js')
		.afterScraping(function(req, res, next) {
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
				MongoClient.connect('mongodb://127.0.0.1:27017/ccl', function(err, db) {
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

