var mail = $('[name=message]').contents().scrapeOne({
	title : {sel : 'h1', method : 'text'},
	from : {sel : 'ul li:contains(\'From\')', method : 'html'},
	subject : {sel : 'ul li:contains(\'Subject\')', method : 'text'},
	content : {sel : 'pre', method : 'text'},
	comments : {method : function() {
		data = [];
		nodes = $('[name=message]')[0].contentWindow.document.childNodes;
		for(var i = 0; i < nodes.length; i++) {
			t = nodes[i].nodeValue;
			if(t) {
				data.push(t);
			}
		};
		return data;
	}}
});

mail.url = document.URL;

var nav = $('[name=top_nav]').contents().scrapeOne({
	previous : {sel : 'nobr a:eq(0)', attr : 'href'},
	next : {sel : 'nobr a:eq(2)', attr : 'href'},
	date : {sel : 'nobr'}
});

mail.date = nav.date;

done({mail: mail, nav : nav})