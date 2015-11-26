"""        
Unit Test for crawler.py. Tests whether the inverted_index works by checking the output of the resolved inverted index.
"""
from crawler import crawler
import unittest
import sqlite3 as lite
from collections import defaultdict 
import pickle as pk

class TestResolvedInvertedIndex(unittest.TestCase):
	
    def test_resolved_inverted_index_(self):
        #Create object crawler with an empty text file
        con = lite.connect("dbFile.db")
        
        c = crawler(None, "urls_test.txt")
		 
        c.crawl()
        #Check inverted index
        self.assertEqual(c._inverted_index_str[u'languages'], set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']))
        self.assertEqual(c._inverted_index_str[u'csc326'], set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']))
        self.assertEqual(c._inverted_index_str[u'programming'], set(['http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html']))
        
    def test_sql_db(self) :
        # test db
        con = lite.connect("dbFile.db")
        cur = con.cursor()
        
        cur.execute('SELECT docid, value from docIndex_Table')
        data= cur.fetchone()
        while (data) :
            self.assertEqual(pk.loads(data[1])[0], 'http://www.eecg.toronto.edu/~jzhu/csc326/csc326.html')
            data = cur.fetchone()
            

     
if __name__ == '__main__':
    unittest.main()


