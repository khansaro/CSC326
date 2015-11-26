<html>

<head> 
	<link href='https://fonts.googleapis.com/css?family=Raleway:400,500,300,200,600,700' rel='stylesheet' type='text/css'>
	<link href='https://fonts.googleapis.com/css?family=Pacifico' rel='stylesheet' type='text/css'>
	<link href='https://fonts.googleapis.com/css?family=Lato:400,300' rel='stylesheet' type='text/css'>
	<link href="/static/style.css" rel='stylesheet' type='text/css'>
	<title>KKT Search</title>
</head>

<body>
	<div id="header">
		<a href="/"> <h1 class="logo"> KKT SEARCH </h1> </a>
	</div>

	<h2> RESULTS FROM YOUR QUERY </h2>

	<table id="WORDS" align="center" >
		<tr>
			<td> {{keyword}} </td>
		</tr>
		% if len(message):
			<tr>
				<td> {{message}} </td>
			</tr>
		% end	
		%for x in url_list:
		<tr>
			<td> <a href="{{x}}">{{x}}<a/> </td>
		</tr>
		%end
	</table>
	<div class="pagination">
	% for page_num in range(num_urls):
		% page_link = "/getSearchWords?" + original_query + "&offset=" + str(page_num * 5) 
		<a href="{{page_link}}"> {{page_num}} </a>
	% end
	</div>
</body>

</html>
