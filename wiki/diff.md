## Here are the main differences between the _wuy.Window_ and the _wuy.Server_ modes

Depending of your class inheritance

| | wuy.Window | wuy.Server |
|:-:|:-:|:-:|
| aka mode | App/Window | Server |
| act as | Real GUI (your clients won't see any difference) | Regular Web Server, it's up to you to connect to it with browser of your choice |
| At open | Open GUI in a managed chrome app | no |
| At end | Close the window/gui | no end (except ctrl-c on server-side, like a regular server) |
| If socket brokes | Close the window/app | clients retry to reconnect (like a regular server) |
| Websocket | Only one (think one client) | as many as clients |
| Browser | Chrome, in **chrome app mode**. | Any browsers from world wild. But you'll better Need to use the wonderful [polyfill](https://polyfill.io/v2/docs/) to be able to serve old browsers (IE11, etc ...). Because wuy.js use Promise (*)|
| Host listening | only localhost | wide (0.0.0.0) |
| Port listening | Will use the defined/default port, or the next free port available | Will use the defined/default port. If the port is not available ; it will not start ! (like a regular server) |
| using wuy.emit(event) on client side | do nothing | Will send the event to all others connected clients (except self) |

(*) : in a future release : **wuy** will embbed its promise polyfill.
