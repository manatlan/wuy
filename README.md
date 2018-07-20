# huy

It's like [python eel](https://github.com/ChrisKnott/Eel) BUT :

* it's not as polished
* it uses python3 ONLY
* it uses asyncio, and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
* it's server hosted friendly from scratch
* it uses pubsub mechanism to communicate from server to clients, or from client to clients
* it's not pyinstaller-friendly for now
* it doesn't exit when no sockets anymore
* com errors are catch'able thru the promise
* it doesn't auto-run a browser

it's a proof of concept : HUY means **H**tml **U**ser **Y**nterface ...

## to run

    $ pip3 install aiohttp
    $ python3 server.py