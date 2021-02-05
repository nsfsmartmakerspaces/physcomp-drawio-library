#!/usr/bin/env python3

import asyncio

from physcomp_drawio_generate import main

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
