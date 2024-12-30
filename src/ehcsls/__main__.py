import logging
import os
import sys
from . import __version__, server


logger = logging.getLogger(__package__)

def main():
    logger.info("hello from EHCSLS", __version__)
    if "--version"in sys.argv[1::]:
        print(__version__)
        return os.EX_OK;

    server.start_io()


if __name__ == "__main__":
    sys.exit(main())
