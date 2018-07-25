## Here are the main differences between the _wuy.Window_ and the _wuy.Server_ modes

Depending of your class inheritance

| | wuy.Window | wuy.Server |
|:-:|:-:|:-:|
[ mode | App/Window | Server |
| At open | Open GUI in a managed chrome app | no |
| At end | Close the window/gui | no end (except ctrl-c on server-side, like a regular server) |
| Can exit on its own ?| Using self.exit() | no (except ctrl-c on server-side, like a regular server) |
| If socket brokes | Close the window/app | clients retry to reconnect (like a regular server) |
| Websocket | Only one (think one client) | as many as clients |
| Browser | Chrome, in **chrome app mode**. If chrome is not present : will fallback to server mode (listening localhost only, and the next free port) | any browsers from worldwild|
| Host listening | only localhost | wide (0.0.0.0) |
| Port listening | Will use the defined/default port, or the next free port available | Will use the defined/default port. If the port is not available ; it will not start ! (like a regular server) |
| using wuy.emit(event) on client side | do nothing | Will send the event to all others connected clients (except self) |


