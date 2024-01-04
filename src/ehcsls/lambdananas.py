from __future__ import annotations

import re
import subprocess

from dataclasses import dataclass
from enum import Enum

import re
import subprocess
from typing import Final, List, Optional

from pygls.server import LanguageServer


class ReportType(str, Enum):
    FATAL = "FATAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"
    INFO = "INFO"


_levels = '|'.join(m for m in ReportType.__members__)

REPORT_FORMAT: Final[re.Pattern] = re.compile(
    rf"^[^:]+:(?P<line>\d+):\s?(?P<type>{_levels})"
    rf":(?P<rule>H-\w\d+)\s[#](?P<file>.*hs\s)?\s(?P<desc>.*)$"
)

@dataclass
class Report:
    line: int
    type: ReportType
    rule: str
    desc: str

    last_line: int = 0
    count: int = 1

    def __post_init__(self):
        self.last_line = self.line

    def is_mergeable(self, line):
        return line in range(self.line - 1, self.last_line + 2)

    def merge(self, report: Report):
        self.line = min(self.line, report.line)
        self.last_line = max(self.last_line, report.line)
        self.count += report.count

    @classmethod
    def from_string(cls, line: str) -> Optional[Report]:
        match = re.match(REPORT_FORMAT, line)

        if match is None:
            return None

        line, typ, rule, file, desc = match.groups()
        return cls(
            line=int(line), type=ReportType(typ),
            rule=rule, desc=desc if file is None else f"(file) {desc}"
        )

    @property
    def message(self) -> str:
        return f"{self.rule}: {self.desc}"

def parse_lambdananas_output(raw_report: str) -> List[Report]:
    reports = raw_report.split("\n")

    out = []
    for reported_line in reports:
        report = Report.from_string(reported_line)

        if report is None:
            continue

        out.append(report)

    return out


def get_lambdananas_output(ls: LanguageServer, filename: str) -> List[Report]:
    if not filename:
        return []
    out = subprocess.run(
        ("lambdananas-exe", filename),
        capture_output=True,
        timeout=5
    )

    if out.stderr:
        ls.show_message(out.stderr.decode())

    out = out.stdout
    return parse_lambdananas_output(out.decode())
