# wuy 

It's like [python eel](https://github.com/ChrisKnott/Eel) BUT :

* it's not as polished
* it uses python3 ONLY
* it uses asyncio, and the marvellous [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
* it's server hosted friendly from scratch
* it uses pubsub mechanism to communicate from server to clients, or from client to clients
* it's not pyinstaller-friendly for now
* com errors are catch'able thru the promise

it's a proof of concept : WUY means **W**eb **U**ser **Y**nterface ...

## to test/run

Download a zip from here

    $ pip3 install aiohttp
    $ python3 -u server.py

## to use

    $ pip3 install wuy

    ...
