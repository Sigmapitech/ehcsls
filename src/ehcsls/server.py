import tempfile
from typing import List

from .version import __version__
from .lambdananas import get_lambdananas_output, Report, ReportType

from pygls.server import LanguageServer
from pygls.workspace import Document
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    Diagnostic,
    DiagnosticSeverity,
    DidOpenTextDocumentParams,
    Position,
    Range,
)

server = LanguageServer("ehcsls", __version__)

class LineRange(Range):

    def __init__(self, line: int, last_line: int = 0):
        super().__init__(
            start=Position(line - 1, 1),
            end=Position(last_line, 80)
        )

SEVERITIES = {
    ReportType.FATAL: DiagnosticSeverity.Error,
    ReportType.MAJOR: DiagnosticSeverity.Warning,
    ReportType.MINOR: DiagnosticSeverity.Information,
    ReportType.INFO: DiagnosticSeverity.Hint
}

def merge_reports(reports: List[Report]) -> List[Report]:
    out_reports = []

    for rule in set(report.rule for report in reports):
        m = {}

        for report in sorted(reports, key=lambda r: r.line):
            if report.rule != rule:
                continue

            for k in m.values():
                if k.is_mergeable(report.line):
                    k.merge(report)
                    break
            else:
                m[report.line] = report

        out_reports.extend(m.values())
    return out_reports


def get_diagnostics(ls: LanguageServer, text_doc: Document):
    content = text_doc.source
    filename = ".mk" if text_doc.filename == "Makefile" else text_doc.filename

    with tempfile.NamedTemporaryFile(suffix=filename) as tf:
        tf.write(content.encode())
        tf.flush()

        reports = get_lambdananas_output(ls, tf.name)

    return [
        Diagnostic(
            range=LineRange(
                report.line,
                report.last_line
            ),
            message=report.message,
            source="Json Server",
            severity=SEVERITIES[report.type]
        ) for report in merge_reports(reports)
    ]


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams):
    text_doc = ls.workspace.get_document(params.text_document.uri)
    ls.publish_diagnostics(text_doc.uri, get_diagnostics(ls, text_doc))

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
async def did_changement(ls: LanguageServer, params: DidOpenTextDocumentParams):
    """Text document did open notification."""
    text_doc = ls.workspace.get_document(params.text_document.uri)
    ls.publish_diagnostics(text_doc.uri, get_diagnostics(ls, text_doc))

