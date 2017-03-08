##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Tests for z.c._api
"""
import unittest

class Test_getGlobalSiteManager(unittest.TestCase):

    def _callFUT(self):
        from guillotina.component.globalregistry import getGlobalSiteManager
        return getGlobalSiteManager()

    def test_gsm_is_IComponentLookup(self):
        from guillotina.component.globalregistry import base
        from guillotina.component.interfaces import IComponentLookup
        gsm = self._callFUT()
        self.assertTrue(gsm is base)
        self.assertTrue(IComponentLookup.providedBy(gsm))

    def test_gsm_is_singleton(self):
        gsm = self._callFUT()
        self.assertTrue(self._callFUT() is gsm)

    def test_gsm_pickling(self):
        from guillotina.component._compat import _pickle
        gsm = self._callFUT()
        dumped = _pickle.dumps(gsm)
        loaded = _pickle.loads(dumped)
        self.assertTrue(loaded is gsm)

        dumped_utilities = _pickle.dumps(gsm.utilities)
        loaded_utilities = _pickle.loads(dumped_utilities)
        self.assertTrue(loaded_utilities is gsm.utilities)

        dumped_adapters = _pickle.dumps(gsm.adapters)
        loaded_adapters = _pickle.loads(dumped_adapters)
        self.assertTrue(loaded_adapters is gsm.adapters)


class Test_provideUtility(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.globalregistry import provideUtility
        return provideUtility(*args, **kw)

    def test_anonymous_no_provides(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from guillotina.component.globalregistry import getGlobalSiteManager
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        foo = Foo()
        self._callFUT(foo)
        gsm = getGlobalSiteManager()
        self.assertTrue(gsm.getUtility(IFoo, '') is foo)

    def test_named_w_provides(self):
        from zope.interface import Interface
        from guillotina.component.globalregistry import getGlobalSiteManager
        class IFoo(Interface):
            pass
        class Foo(object):
            pass
        foo = Foo()
        self._callFUT(foo, IFoo, 'named')
        gsm = getGlobalSiteManager()
        self.assertTrue(gsm.getUtility(IFoo, 'named') is foo)


class Test_provideAdapter(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.globalregistry import provideAdapter
        return provideAdapter(*args, **kw)

    def test_anonymous_no_provides_no_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from guillotina.component.globalregistry import getGlobalSiteManager
        from guillotina.component._declaration import adapter
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        @adapter(IFoo)
        @implementer(IBar)
        class Bar(object):
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar)
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.getAdapter(foo, IBar)
        self.assertTrue(isinstance(adapted, Bar))
        self.assertTrue(adapted.context is foo)

    def test_named_w_provides_w_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from guillotina.component.globalregistry import getGlobalSiteManager
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        class Bar(object):
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar, (IFoo,), IBar, 'test')
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.getAdapter(foo, IBar, name='test')
        self.assertTrue(isinstance(adapted, Bar))
        self.assertTrue(adapted.context is foo)


class Test_provideSubscriptionAdapter(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.globalregistry import provideSubscriptionAdapter
        return provideSubscriptionAdapter(*args, **kw)

    def test_no_provides_no_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from guillotina.component.globalregistry import getGlobalSiteManager
        from guillotina.component._declaration import adapter
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        @adapter(IFoo)
        @implementer(IBar)
        class Bar(object):
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar)
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.subscribers((foo,), IBar)
        self.assertEqual(len(adapted), 1)
        self.assertTrue(isinstance(adapted[0], Bar))
        self.assertTrue(adapted[0].context is foo)

    def test_w_provides_w_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from guillotina.component.globalregistry import getGlobalSiteManager
        class IFoo(Interface):
            pass
        class IBar(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        class Bar(object):
            def __init__(self, context):
                self.context = context
        self._callFUT(Bar, (IFoo,), IBar)
        gsm = getGlobalSiteManager()
        foo = Foo()
        adapted = gsm.subscribers((foo,), IBar)
        self.assertEqual(len(adapted), 1)
        self.assertTrue(isinstance(adapted[0], Bar))
        self.assertTrue(adapted[0].context is foo)


class Test_provideHandler(unittest.TestCase):

    from guillotina.component.testing import setUp, tearDown

    def _callFUT(self, *args, **kw):
        from guillotina.component.globalregistry import provideHandler
        return provideHandler(*args, **kw)

    def test_no_adapts(self):
        from zope.interface import Interface
        from zope.interface import implementer
        from zope.interface import providedBy
        from guillotina.component.globalregistry import getGlobalSiteManager
        from guillotina.component._declaration import adapter
        class IFoo(Interface):
            pass
        @implementer(IFoo)
        class Foo(object):
            pass
        @adapter(IFoo)
        def _handler(context):
            assert 0, "DON'T GO HERE"
        self._callFUT(_handler)
        gsm = getGlobalSiteManager()
        regs = list(gsm.registeredHandlers())
        self.assertEqual(len(regs), 1)
        hr = regs[0]
        self.assertEqual(list(hr.required), list(providedBy(Foo())))
        self.assertEqual(hr.name, '')
        self.assertTrue(hr.factory is _handler)

    def test_w_adapts(self):
        from zope.interface import Interface
        from guillotina.component.globalregistry import getGlobalSiteManager
        class IFoo(Interface):
            pass
        def _handler(context):
            assert 0, "DON'T GO HERE"
        self._callFUT(_handler, (IFoo,))
        gsm = getGlobalSiteManager()
        regs = list(gsm.registeredHandlers())
        self.assertEqual(len(regs), 1)
        hr = regs[0]
        self.assertEqual(list(hr.required), [IFoo])
        self.assertEqual(hr.name, '')
        self.assertTrue(hr.factory is _handler)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_getGlobalSiteManager),
        unittest.makeSuite(Test_provideUtility),
        unittest.makeSuite(Test_provideAdapter),
        unittest.makeSuite(Test_provideSubscriptionAdapter),
        unittest.makeSuite(Test_provideHandler),
    ))