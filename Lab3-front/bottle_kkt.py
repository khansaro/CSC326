from bottle import route, request, run, template, static_file, error
import bottle, httplib2
from beaker.middleware import SessionMiddleware
import sqlite3 as lite 
import pickle as pk 


conn = lite.connect("dbFile.db")
cur = conn.cursor()
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 300,
    'session.data_dir': './data',
    'session.auto': True
}
app = SessionMiddleware(bottle.app(), session_opts)

history_list = {}
some_list = {}

@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='.')

@route('/')
def serve_homepage():
	s = bottle.request.environ.get('beaker.session')
	random_name = ''
	sorted_history = []
	picture = ''
	if 'user_email' in s:
		if s['user_email'] in history_list:
			sorted_history = sorted(history_list[s['user_email']].items(), reverse=True, key=lambda x: x[1])
		else:
			history_list[s['user_email']] = {}
		random_name = s['name']
		picture = s['picture']
	return template('query_page.tpl', history=sorted_history, name=random_name, picture=picture)


def get_word_id(word):
	result = cur.execute("SELECT * FROM lexicon_Table where value = '%s'" % word).fetchone()
	if result is not None:
		return result[1]
	return None

def get_doc_ids(word_id):
	result = cur.execute("SELECT * FROM invertedindex_Table where invertedid = '%s'" % word_id).fetchone()
	return list(pk.loads(result[2]))

def resolve_doc_ids(sorted_doc_ids):
	resolved_list = []
	for doc_id in sorted_doc_ids:
		result = cur.execute("SELECT * FROM docIndex_Table where docid = '%s'" % doc_id).fetchone()
		resolved_list.append(pk.loads(result[2]))
	return resolved_list

def get_page_ranks(doc_ids):
	ranks = {}
	for doc_id in doc_ids:
		result = cur.execute("SELECT * FROM pagerank_Table where pageid = '%s'" % doc_id).fetchone()
		ranks[result[1]] = pk.loads(result[2])
	return ranks

@route('/getSearchWords', method="GET")
def input_handle():
	s = bottle.request.environ.get('beaker.session')
	
	sorted_history = []
	count_list = {}
	keywords = request.query['keywords']
	l_keywords = keywords.lower()
	list_all_words = l_keywords.split()
	
	offset = 0 if 'offset' not in request.query else int(request.query['offset'])
	if len(list_all_words) == 0: list_all_words.append('')
	word_id = get_word_id(list_all_words[0])
	if word_id is not None:
		doc_ids = get_doc_ids(word_id)
		ranks = get_page_ranks(doc_ids)
		sorted_doc_ids = sorted(doc_ids, reverse=True, key=lambda doc_id: ranks[doc_id])
		url_list = [doc[0] for doc in resolve_doc_ids(sorted_doc_ids)]
	else:
		url_list = []

	if len(url_list):			
		num_urls = len(url_list)/5
		if (num_urls % 5 != 0):num_urls += 1
		message=""
		if list_all_words[0] != '':
			original_query = "keywords=" + "+".join(list_all_words)
			return template('new_result_page.tpl', original_query=original_query, keyword=list_all_words[0], num_urls=num_urls, url_list=url_list[offset:offset+5], message=message)
		else:
			return serve_homepage()
	else:
		original_query = "keywords=" + "+".join(list_all_words)
		num_urls = 0
		message = "NO LINKS FOUND"
		url_list.append('')
		if list_all_words[0] != '':
			return template('new_result_page.tpl', original_query=original_query, keyword=list_all_words[0], num_urls=num_urls, url_list=url_list, message=message)
		else:
			return serve_homepage()				

@route('/auth')
def auth():
	return serve_homepage()				

@route('/logout')
def logout():
	s = bottle.request.environ.get('beaker.session')
	s.delete()
	bottle.redirect('/')

@error(404)
def error404(error):
	return """
		<h1>Page does not exist, click <a href="/">here</a> to go back to the home page</h1>
	"""

run(app=app, host='0.0.0.0', port=8080, debug=True)


