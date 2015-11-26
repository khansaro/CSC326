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
		% if len(name)==0:
		<div class="login">
			<a href="/auth"> login </a>
		</div>
		% end
		<a href="/"> <h1 class="logo"> KKT SEARCH </h1> </a>
	</div>
	
	<h2> Enter your query </h2>
	<form action="/getSearchWords" method="GET">
		<input type="text" name="keywords" autofocus>
		<input type="submit" value="SUBMIT">
	</form>

	%if len(history):
	<h2> MOST SEARCHED WORDS </h2>
	<table id="WORDS" align="center" >
		<tr>
			<th><b>WORD</b></th>
			<th><b>COUNT</b></th>
		</tr>
		%for x in history:
		<tr>
			<td> {{x[0]}} </td>
			<td> {{x[1]}} </td>
		</tr>
		%end
	</table>
	%end
</body>

</html>
