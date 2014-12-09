module.exports = function($) {
	var mail = {
		// url : document.URL,
		title : $('h1').text(),
		content : $('pre').html(),
		metas : $('ul').first().scrapeOne({
			to : {sel : 'li:has(em:contains(\'To\'))', method: 'html'},
			subject: {sel: 'li:has(em:contains(\'Subject\'))', method: 'html'},
			from: {sel: 'li:has(em:contains(\'From\'))', method: 'html'},
			date: {sel: 'li:has(em:contains(\'Date\'))', method: 'html'},
			messageid: {sel: 'li:has(em:contains(\'Message-id\'))', method: 'html'},
			inreplyto: {sel: 'li:has(em:contains(\'In-reply-to\'))', method: 'html'},
			references: {sel: 'li:has(em:contains(\'References\'))', method: 'html'}
		}),
		nextbydate : $('ul > li:contains(\'Next by Date\')').html(),
		nextbythread : $('ul > li:contains(\'Next by thread\')').html()
	};

	var nextbydate = $('ul > li:contains(\'Next by Date\') a').attr('href');

	return {mail: mail, nextbydate : nextbydate};
}