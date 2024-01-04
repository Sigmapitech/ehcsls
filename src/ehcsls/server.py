from .version import __version__

from pygls.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    DidOpenTextDocumentParams,
)

server = LanguageServer("ehcsls", __version__)

@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    ls.show_message(f"Hello, ehcsls")
