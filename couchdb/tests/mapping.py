# -*- coding: utf-8 -*-
#
# Copyright (C) 2007-2009 Christopher Lenz
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.

from decimal import Decimal
import doctest
import unittest
import datetime

from couchdb import design, mapping
from schematics.models import Model
from schematics.types import *
from schematics.types.compound import ListType, ModelType

from couchdb.tests import testutil

class DocumentTestCase(testutil.TempDatabaseMixin, unittest.TestCase):

    class Post(mapping.Document):
        title = StringType()

    def testDictType(self):
        class Test(mapping.Document):
            d = DictType()
        a = Test(id='a')
        b = Test()
        a.d['x'] = True
        b.id = 'b'
        self.assertTrue(a.d.get('x'))
        self.assertFalse(b.d.get('x'))
        a.store(self.db)
        b.store(self.db)
        a = Test.load(self.db,'b')
        b = Test.load(self.db,'a')
        self.assertTrue(b.d.get('x'))
        self.assertFalse(a.d.get('x'))

    def testAutomaticID(self):
        post = self.Post(title='foo bar')
        assert post.id is None
        post.store(self.db)
        assert post.id is not None
        self.assertEqual('foo bar', self.db[post.id]['title'])

    def testExplicitIDViaInit(self):
        post = self.Post(id='foo_bar',title='foo bar')
        self.assertEqual(post.id, 'foo_bar')
        post.store(self.db)
        self.assertEqual('foo bar', self.db['foo_bar']['title'])
        
    def testExplicitIDViaSetter(self):
        post = self.Post(title='foo bar')
        post.id = 'foo_bar'
        self.assertEqual(post.id, 'foo_bar')
        post.store(self.db)
        self.assertEqual('foo bar', self.db['foo_bar']['title'])
        
    def testChangeIDFailure(self):
        post = self.Post(title='foo bar')
        assert post.id is None
        post.store(self.db)
        assert post.id is not None
        try:
            post.id = 'new id'
            self.fail('Expected AttributeError')
        except AttributeError, e:
            self.assertEqual('id can only be set on new documents', e.args[0])
        
    def testBatchUpdate(self):
        post1 = self.Post(title='foo bar')
        post2 = self.Post(title='foo baz')
        results = self.db.update([post1, post2])
        self.assertEqual(2, len(results))
        assert results[0][0] is True
        assert results[1][0] is True

    def testStoreExisting(self):
        post = self.Post(title='Foo bar')
        post.store(self.db)
        post.store(self.db)
        self.assertEqual(len(list(self.db.view('_all_docs'))), 1)


class ModelTypeTestCase(testutil.TempDatabaseMixin, unittest.TestCase):

    class Post(mapping.Document):
        class Comment(Model):
            author = StringType()
            comment = StringType()
        title = StringType()
        comments = ListType(ModelType(Comment))


    class User(mapping.Document):
        class AuthToken(Model):
            token = UUIDType(auto_fill=True)
            created_on = DateTimeType(default=datetime.datetime.utcnow)
        email = EmailType()
        password = MD5Type()
        tokens = ListType(ModelType(AuthToken))
        
    def testPost(self):
        post = self.Post(id='foo_bar', title="Foo bar")
        assert isinstance(post.comments, ListType.Proxy)
        post.comments.append(self.Post.Comment(author="myself", comment="blah blah blah"))
        post.store(self.db)
        self.assertEqual(self.db['foo_bar']['comments'], [{u'author': u'myself', u'comment': u'blah blah blah'}])

    def testTokenCreation(self):
        authtoken = self.User.AuthToken()
        assert authtoken.token is not None
        assert authtoken.created_on is not None

    def testInvalidUser(self):
        user = self.User()
        user.email = 'invalid@email'
        self.assertRaises( Exception, user.store, self.db)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(mapping))
    suite.addTest(unittest.makeSuite(DocumentTestCase, 'test'))
    suite.addTest(unittest.makeSuite(ModelTypeTestCase, 'test'))
#   suite.addTest(unittest.makeSuite(ListFieldTestCase, 'test'))
#   suite.addTest(unittest.makeSuite(WrappingTestCase, 'test'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
