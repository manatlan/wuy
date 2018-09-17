# -*- coding: utf-8 -*-
import wuy,sys,asyncio,os
from datetime import date,datetime
import unittest

# Officiel unit tests (more than coverage 80% of code (cef works too), windows-mode only)
#TODO: may block under windows (but each test works independantly) ... should find a solution ! It works as expected unde linux only (mac ?)

ONLYs=[]
def only(f): # decorator to place on tests, to limit usage to only theses ones
    ONLYs.append(f.__name__)
    return f

JSTEST=27 # there are 'JSTEST' js tests in class vv, to test with app-mode and cefpython3 !
class UnitTests(wuy.Window):
    """
    <meta charset="utf-8" />

    I am 
    <script>
    document.write(wuy.iam);

    document.addEventListener("init", async function() {

        await wuy.report("declared var", wuy.val=="mémé" ,"")

        await testRequestPath("/unknown", r=>r.status==404 )
        await testRequestPath("/1", r=>r.status==200 && r.headers["content-type"].includes("text/html") )
        await testRequestPath("/2", r=>r.status==200 && r.headers["content-type"].includes("application/octet-stream") )
        await testRequestPath("/11", r=>r.status==201 && r.headers["content-type"].includes("text/html") )
        await testRequestPath("/12", r=>r.status==201 && r.headers["content-type"].includes("application/octet-stream") )
        await testRequestPath("/20", r=>r.status==202 && r.headers["content-type"].includes("text/plain") )
        await testRequestPath("/30", r=>r.status==203 && r.headers["content-type"].includes("text/plain") )

        await testBadCall("Test unknown proc",()=>wuy.unknown() );
        await testBadCall("Test call proc with bad number of params",()=>wuy.call(1) );
        await testBadCall("Test async call proc with bad number of params",()=>wuy.acall(1) );

        await wuy.report("Test good sync call", "abc" == await wuy.call('a','b','c') ,"")
        await wuy.report("Test good async call", "abc" == await wuy.acall('a','b','c') ,"")
        await wuy.report("Test good sync call", "abc" == await wuy.call('a','b') ,"")
        await wuy.report("Test good async call", "abc" == await wuy.acall('a','b') ,"")

        //---------------------------------------------------------
        // test a method which send a event

        r=await wuy.testEmit()
        wuy.on("pyEvent",async function(a,b,c) {
            await wuy.report("Test py/emit event recepted",a=="a" && b=="b" && c=="c","")
        })
        await wuy.report("Test py/emit return",r=="ok","")

        //---------------------------------------------------------
        // test wuy.emit() (not usefull in windows mode !)

        wuy.on("jsEvent",async function(a,b,c) { // not called in windows mode
            await wuy.report("jsEvent not received (normal)",False,"")  // it's bad !
        })
        var p=await wuy.emit("jsEvent",1,2,3)
        await wuy.report("Test js/emit return good things", p.length==3 && p[0]==1 && p[1]==2 && p[2]==3 ,"")

        //---------------------------------------------------------

        var content=await wuy.testWuyRequest()
        await wuy.report("Test wuy.request GET", content.includes("wuy.js") ,"")

        var content=await wuy.testWuyRequestPost()
        await wuy.report("Test wuy.request POST", content.includes("'wuy'") ,"")

        await testBadCall("Test wuy.request Error",()=>wuy.testWuyRequestError() )

        var content=await fetch("UnitTests.html").then( x=>x.text())
        await wuy.report("Test classic fetch", content.includes("wuy.js") ,"")

        //TODO: the givent port is arbitary ... change to self._port !
        var content=await wuy.fetch("http://localhost:8080/UnitTests.html").then( x=>x.text())  // need to have FULL URL !
        await wuy.report("Test wuy.fetch", content.includes("wuy.js") ,"")

        await testDivError("Test error",()=>wuy.testError() );
        await testDivError("Test async error",()=>wuy.atestError() );

        var d=new Date()
        var dd=await wuy.checkDate(d)
        await wuy.report("Test json date", ""+d == ""+dd ,"")

        await wuy.set("a",d,"test_config.json")
        var r=await wuy.get("a","test_config.json")
        await wuy.report("Test config (json date)", ""+d == ""+r ,"")

        window.close()
    });

    async function testRequestPath(p,cbt) {
        var r=await fetch(p)
        var h={};
        for(var i of r.headers) h[ i[0] ] = i[1]
        var rep={status:r.status, headers:h, content: await r.text()}

        wuy.report(`Test path "${p}"`, cbt(rep), "Tests:"+cbt+" with:"+JSON.stringify(rep))
    }

    async function testBadCall(p,cbt) {
        try {
            await cbt()                 // raise an exception !
            await wuy.report(p,false,"")
        }
        catch(e) {wuy.report(p,true,e)}
    }

    async function testDivError(p,cbt) {
        try {
            await cbt()
            await wuy.report(p, False ,"")
        }
        catch(e) {
            await wuy.report(p, (""+e).includes("division by zero") ,"")
        }
    }


    </script>

    """
    size=(100,100)

    def init(self):
        self.tests=[]

    def report(self,libl,val,info):
        self.tests.append( (val,libl,info) )

    #===========================================================================
    def request(self,req):    # async or not
        if req.path=="/1":
            return "text body"   # 200, text/html
        elif req.path=="/2":
            return b"text body"  # 200, application/octect-stream
        elif req.path=="/11":
            return wuy.Response(201,"text body")    # text/html
        elif req.path=="/12":
            return wuy.Response(201,b"text body")   # application/octect-stream
        elif req.path=="/20":
            return wuy.Response(202,"text body","text/plain")    # text/plain
        elif req.path=="/30":
            return wuy.Response(203,"text body",{"content-type":"text/plain"})
        if req.path=="/post" and req.method=="POST":
            return "say hello to '%s'"%req.body   # 200, text/html

    def call(self,a,b,c="c"):
        return "%s%s%s" % (a,b,c)

    async def acall(self,a,b,c="c"):
        return "%s%s%s" % (a,b,c)

    def testEmit(self):
        self.emit("pyEvent","a","b","c")
        return "ok"

    async def atestError(self):
        a=12/0
        return "ok" 

    def testError(self):
        a=12/0
        return "ok" 

    async def testWuyRequest(self):
        return (await wuy.request("http://localhost:%s/UnitTests.html" % self._port)).content

    async def testWuyRequestPost(self):
        return (await wuy.request("http://localhost:%s/post" % self._port,"wuy")).content

    async def testWuyRequestError(self):
        return await wuy.request("hvfgdfdsgfdsgdf")

    def checkDate(self,dat):
        assert type(dat)==datetime
        return dat

def reportJS(ll,txt):
    print("#"*79,txt)
    for test,libl,info in ll:
        print( test and "ok:" or "KO:",libl, "" if test is True else info)
    print("#"*79)


class TestWuy(unittest.TestCase):

    def setUp(self):
        if os.path.isfile("test_config.json"): os.unlink("test_config.json")
    def tearDown(self):
        self.setUp()

    def test_isFreePort(self):
        ll=[wuy.isFree("localhost",p) for p in [22,23,445]]
        self.assertTrue( False in ll)

    def test_path(self):
        self.assertFalse(hasattr(sys,"_MEIPASS"))
        self.assertEqual(wuy.path("jo"),os.path.join(os.getcwd(),"jo"))

    def test_pathFrozen(self):
        sys._MEIPASS="kiki"
        self.assertEqual(wuy.path("jo").replace("\\","/"),"kiki/jo")
        delattr(sys,"_MEIPASS")
        self.assertFalse(hasattr(sys,"_MEIPASS"))

    def test_getname(self):
        self.assertEqual( wuy.getname("jo"),"jo" )
        self.assertEqual( wuy.getname("jo.html"),"jo" )
        self.assertEqual( wuy.getname("jim/jo"),"jim.jo" )
        self.assertEqual( wuy.getname("jim/jo.html"),"jim.jo" )

    def test_json(self):
        def test(j, testType=None):
            def testSUS(obj,testType=None):
                s=wuy.jDumps(obj)
                nobj=wuy.jLoads(s)
                self.assertEqual( type(nobj), testType )

            testSUS( dict(v=j) ,dict )
            testSUS( [ j, dict(a=[j]) ] ,list )
            testSUS( j ,testType)

        class Ob:
            def __init__(self):
                self.name="koko"

        test( datetime.now(), datetime)
        test( date(1983,5,20), datetime )
        test( b"kkk", str)
        test( "kkk", str)
        test( 42, int)
        test( 4.2, float)
        test( None, type(None))
        test( Ob(), dict )
        test( datetime.now()-datetime.now(), str)

    def test_a_window_render_html(self):
        class aeff(wuy.Window):
            size=(100,100)
            def init(self):
                asyncio.get_event_loop().call_later(2, self.exit)

        if os.path.isfile("web/aeff.html"): os.unlink("web/aeff.html")
        aeff()
        self.assertTrue( os.path.isfile("web/aeff.html") )
        os.unlink("web/aeff.html")

    def test_a_double_window(self):
        class aeff(wuy.Window):
            "test double open"
            size=(100,100)
            def init(self):
                asyncio.get_event_loop().call_later(2, self.exit)

        aeff()
        aeff()

    def test_a_server(self):
        class saeff(wuy.Server):
            "I'm a server"
            def init(self):
                asyncio.get_event_loop().call_later(2, self.exit)
        saeff()
        self.assertEqual( len(wuy.currents),1)  # there was one instance

    def test_2_server(self):
        class saeff1(wuy.Server):
            "I'm a server, and the quitter"
            def init(self):
                asyncio.get_event_loop().call_later(2, self.exit)
        class saeff2(wuy.Server):
            "I'm a server, and I will killed by saeff1"
            pass
        wuy.Server.run()
        self.assertEqual( len(wuy.currents),2) # there were 2 instances

    # @only
    def test_a_window(self):                # <--- main tests here
        ut=UnitTests(log=True,val="mémé",iam="local chrome")

        reportJS(ut.tests,"main tests on local chrome app-mode")

        self.assertEqual( len([ok for ok,*_ in ut.tests if ok]),JSTEST)        # 23 tests ok

    def test_cef_if_present(self):
        import pkgutil 
        if pkgutil.find_loader("cefpython3"):
            try:
                old=wuy.ChromeApp
                wuy.ChromeApp=wuy.ChromeAppCef

                ut=UnitTests(log=True,val="mémé",iam="cef")
                reportJS(ut.tests,"main tests with cefpython3")
                self.assertEqual( len([ok for ok,*_ in ut.tests if ok]),JSTEST)        # 23 tests ok

            finally:
                wuy.ChromeApp=old
        else:
            print("***WARNING*** : cefpython3 not present, no tests !")

    # def test_a_windows(self):
    #     s = 'hello world'
    #     self.assertEqual(s.split(), ['hello', 'world'])
    #     # check that s.split fails when the separator is not a string
    #     with self.assertRaises(TypeError):
    #         s.split(2)


if __name__=="__main__":
    if ONLYs:
        print("*** WARNING *** skip some tests !")
        def load_tests(loader, tests, pattern):
            suite = unittest.TestSuite()
            for c in tests._tests:
                suite.addTests( [t for t in c._tests if t._testMethodName in ONLYs] )
            return suite

    unittest.main( )
