# Notes about proxified request

Since 0.6 release, **wuy** (server side) provides `async wuy.request(url,data=None,headers={})`, to simplify doing http request. This method simplify access to http or https urls (no ssl verification), and handle cookies for you. (It's similar to _urllib.Request_, so only GET/POST http verbs for now.)

Since that, **wuy** (javascript side) provides `wuy.fetch() -> promise` (same signature as `window.fetch()`) : so it does exatcly what _fetch_ does, except :
* the call pass thru the server side (server side act as a proxy, on path `/_/<url>`) : and server side use `wuy.request()`.
* it's limited to GET/POST http verbs (for now)
* it forces the browser to use "no-cache" : always access to a fresh content of the proxifed url.
* it handles credentials as same-origin.

With this new mechansim : you can access any url (on client-side (html/js)) without [CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS) troubles ;-) (it's not the browser which do the fetch : it's the server ; avoiding cors issues)

On clientside : if you have CORS issues on this kind of fetch :

```javascript
fetch("https://example.com/myapi/retrieve",{method:"post"}).then( ... )
 ```
You'll should have no CORS issues like that:

```javascript
wuy.fetch("https://example.com/myapi/retrieve",{method:"post"}).then( ... )
 ```
Juste added `wuy.` before `fetch` ;-)
