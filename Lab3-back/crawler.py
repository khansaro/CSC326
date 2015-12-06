# Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files 
# (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES 
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE 
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR 
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import urllib2 
import urlparse 
from BeautifulSoup import * 
from collections import defaultdict 
import re 
import sqlite3 as lite 
import pickle as pk 
import pagerank as pr
import pdb

def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return "" 
        
WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]') 

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.
    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""
    
    def __init__(self, db_conn, url_file):
        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        
        self._url_queue = [ ]
        self._doc_id_cache = { }
        self._word_id_cache = { }
        
        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)
        
        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a
        
        # record the currently indexed document's title an increase the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)
            
        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title
        
        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)
        
        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame',
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset',
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])
        
        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])
        
        self._next_doc_id = 0
        self._next_word_id = 0
        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None
	
    	# dicts to store Document IDs, Lexicon, Inverted_index
    	self._doc_dict = defaultdict(list)
    	self._word_dict = defaultdict(list)
    	self._inverted_index = defaultdict(set)
    	self._inverted_index_str = defaultdict(set)
        self._link_db = []
        
		# populate the above data structure with values in db_conn
        if db_conn :
            self._db_conn = db_conn
        else :
            self._db_conn = lite.connect("dbFile.db")
            
        cur = self._db_conn.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS docIndex_Table(id INTEGER PRIMARY KEY, docid INT, value TEXT);')
        cur.execute('CREATE TABLE IF NOT EXISTS lexicon_Table(id INTEGER PRIMARY KEY, wordid INT, value TEXT);')
        cur.execute('CREATE TABLE IF NOT EXISTS invertedindex_Table(id INTEGER PRIMARY KEY, invertedid INT, value TEXT);')
        cur.execute('CREATE TABLE IF NOT EXISTS pagerank_Table(id INTEGER PRIMARY KEY, pageid INT, value TEXT);')
        
        cur.execute('SELECT docid, value from docIndex_Table')
        data= cur.fetchone()
        while (data) :
            self._doc_dict[data[0]] = pk.loads(data[1])
            data = cur.fetchone()
            
        cur.execute('SELECT wordid, value from lexicon_Table')
        data= cur.fetchone()
        while (data) :
            self._word_dict[data[0]] = pk.loads(data[1])
            data = cur.fetchone()
            
        cur.execute('SELECT invertedid, value from invertedindex_Table')
        data= cur.fetchone()
        while (data) :
            self._inverted_index[data[0]] = pk.loads(data[1])
            data = cur.fetchone()
            		
        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
    def _insert_document(self, url):
        """A function that searches for the url in the
    	document database and returns document's id if
    	it exists. Otherwise it inserts the url into the
    	document db table and then returns that newly
    	inserted document's id."""
    	
    	for docID in self._doc_dict :
    	    if url in self._doc_dict[docID] :
    	    	return docID
    	
    	self._doc_dict[self._next_doc_id].append(url)
    	ret_id = self._next_doc_id
        self._next_doc_id += 1
        return ret_id
	
    def _insert_inverted_index(self, word, wordID) :
        """Inserts word and word id into inverted database
    	which maps word and word id with a set of doc id and
    	urls if needed"""
        if self._curr_doc_id not in self._inverted_index[wordID] :
            self._inverted_index[wordID].add(self._curr_doc_id)
            self._inverted_index_str[word].add(self._curr_url)
	
    def _insert_word(self, word):
        """A function that searches for the word in the lexicon
    	and returns word id if it exists. Otherwise it inserts
    	the word into the lexicon db table and then returns that
    	newly inserted word's id."""
    	
    	for wordID in self._word_dict :
    	    if word in self._word_dict[wordID] :
    	        # enter the word into the inverted database
    	    	self._insert_inverted_index(word, wordID)
    	    	return wordID
    		
    	self._word_dict[self._next_word_id].append(word)
    	self._insert_inverted_index(word, self._next_word_id)
        ret_id = self._next_word_id
        self._next_word_id += 1
        return ret_id
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            # make sure to add docID to inverted database
            self._insert_inverted_index(word, self._word_id_cache[word])
            return self._word_id_cache[word]
	
        word_id = self._insert_word(word)
        self._word_id_cache[word] = word_id
        return word_id

    def get_word(self, word_id):
        """Get the word given a word id"""
        for id in self._word_dict.keys():
            if (id == word_id):
                return self._word_dict[id][0]
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        doc_id = self._insert_document(url)
        self._doc_id_cache[url] = doc_id
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""
        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)
        
    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        tuple = (from_doc_id, to_doc_id)
        self._link_db.append(tuple)
        
    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        # add info to the document ID database
        self._doc_dict[self._curr_doc_id].append(title_text)
    
    def _visit_a(self, elem):
        """Called when visiting <a> tags."""
        
        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))
        
        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \ 
        #       "alt="+repr(attr(elem,"alt")), \ 
        #       "text="+repr(self._text_of(elem)) add the 
        #       just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))
        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the database for this document
        self._doc_dict[self._curr_doc_id].append(len(self._curr_words))
        temp = ""
        num_words = 0
        for i,j in self._curr_words:
            if num_words > 20:
                break
            temp = temp + " " + self.get_word(i)
            num_words += 1
        self._doc_dict[self._curr_doc_id].append(temp)
 
    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass
        
    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string
	
    def update_db(self, rank):
        """Update the sql database on disk. Only add if the data is unique"""
        if not self._db_conn :
            return 
            
        cur = self._db_conn.cursor()
		
        try :
            for id in self._word_dict :
                str = self._word_dict[id]
                cur.execute('INSERT INTO lexicon_Table(wordid, value) VALUES(?, ?);', (id, str[0]))
                
            for id in self._doc_dict :
                str = pk.dumps(self._doc_dict[id])
                cur.execute('INSERT INTO docIndex_Table(docid, value) VALUES(%d, "%s");'% (id, str))

            for id in self._inverted_index :
                str = pk.dumps(self._inverted_index[id])
                cur.execute('INSERT INTO invertedindex_Table(invertedid, value) VALUES(?, ?);', (id, str))

            if rank :
                for id in rank :
                    str = pk.dumps(rank[id])
                    cur.execute('INSERT INTO pagerank_Table(pageid, value) VALUES(?, ?);', (id, str))
        except Exception as e:
            print e
            
        self._db_conn.commit()
	    
    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]
        
        while tag and tag.next:
            tag = tag.next
            
            # html tag
            if isinstance(tag, Tag):
                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()
            
                tag_name = tag.name.lower()
    
                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:

                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)

                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        
        seen = set()

        while len(self._url_queue):
            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > depth:
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                continue
           
            seen.add(doc_id) # mark this document as haven't been visited
            
            socket = None
            
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())
                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                
                self._index_document(soup)
                self._add_words_to_document()
                
            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()
                    
        rank = None
        if (self._link_db) :
            rank = pr.page_rank(self._link_db)
        self.update_db(rank)
    
    def get_inverted_index(self):
        """Get the inverted index database."""
	    # crawl the list of urls to generate database first
    	self.crawl()
    	return self._inverted_index
        
    def get_resolved_inverted_index(self):
        """Get the resolved inverted index database."""
	    # crawl the list of urls to generate database first
    	self.crawl()
        return self._inverted_index_str
        
    def get_doc_dict(self):
        """Get the doc dictionary database."""
        # crawl the list of urls to generate database first
        self.crawl()
        return self._doc_dict
        
    def get_word_dict(self):
        """Get the word dictionary database."""
        # crawl the list of urls to generate database first
        self.crawl()
        return self._word_dict
		
		
if __name__ == "__main__":
    #con = lite.connect("dbFile.db")
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)
    print bot.get_doc_dict()
    #con.close()
