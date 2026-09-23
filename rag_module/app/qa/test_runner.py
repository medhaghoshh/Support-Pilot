"""
SupportPilot AI

QA Test Runner

Executes all QA validation checks and
prints a formatted QA report.
"""
from __future__ import annotations

from app.database import SessionLocal
from app.qa.qa_report import QAReport
from app.qa.qa_service import QAService

def run_tests():
    """
    Execute all QA tests.
    """

    db = SessionLocal()

    try:

        results = QAService.run_all_tests(db)

        report = QAReport.generate(results)

        QAReport.print_report(report)

        return report

    finally:

        db.close()


if __name__ == "__main__":
    run_tests()