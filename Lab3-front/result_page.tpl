<html>

<head> 
	<link href='https://fonts.googleapis.com/css?family=Raleway:400,500,300,200,600,700' rel='stylesheet' type='text/css'>
	<link href='https://fonts.googleapis.com/css?family=Pacifico' rel='stylesheet' type='text/css'>
	<link href='https://fonts.googleapis.com/css?family=Lato:400,300' rel='stylesheet' type='text/css'>
	<link href="/static/style.css" rel='stylesheet' type='text/css'>
	<title>KKT Search</title>

</head>

<body>
	% if len(name):
		<div class="wrapper">
			<img src="{{picture}}"></img>
			<h4> Hello, {{name}} </h4>
			<a href="/logout" class="logout"> log out </a>
		</div>
	% end
	<div id="header">
		<a href="/"> <h1 class="logo"> KKT SEARCH </h1> </a>
	</div>

	<h2> RESULTS FROM YOUR QUERY </h2>

	<h3>Search for "{{keywords}}"</h3>

	<table id="WORDS" align="center" >
		<tr>
			<th><b>WORD</b></th>
			<th><b>COUNT</b></th>
		</tr>
		%for x in count_list:
		<tr>
			<td> {{x}} </td>
			<td> {{count_list[x]}} </td>
		</tr>
		%end
	</table>
</body>

</html>
