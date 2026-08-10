"""Command-line interface for packets, counsel, Council, and journal review."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Sequence, TextIO

from .alignment import audit_repository
from .benchmark import BenchmarkSuite
from .council import Council
from .doctrines import get_doctrine, list_doctrines
from .journal import DecisionJournal
from .models import DecisionPacket, ValidationError
from .paths import asset_path
from .reasoning import HeuristicReasoner
from .sources import SourceCorpus


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phronesis", description="Pluralistic, source-grounded decision advisory")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="validate and normalize a Decision Packet")
    validate.add_argument("packet")

    examine = sub.add_parser("examine", help="challenge a packet's framing without recommending")
    examine.add_argument("packet")
    examine.add_argument("--corpus-dir", default="sources/corpus", help="ingested primary-source corpus")

    ask = sub.add_parser("ask", help="ask one school for counsel")
    ask.add_argument("school")
    ask.add_argument("packet")
    ask.add_argument("--corpus-dir", default="sources/corpus", help="ingested primary-source corpus")

    council = sub.add_parser("council", help="run independent counsel, contest, red team, and arbiter")
    council.add_argument("packet")
    council.add_argument("--schools", nargs="+", help="school ids; defaults to the initial five")
    council.add_argument("--corpus-dir", default="sources/corpus", help="ingested primary-source corpus")
    council.add_argument("--record", action="store_true", help="record the result in a decision journal")
    council.add_argument("--journal-dir", default="decisions")
    council.add_argument("--user-decision")
    council.add_argument("--user-confidence", type=float)
    council.add_argument("--review-date")
    council.add_argument("--predicted-outcome", action="append", default=[])

    doctrines = sub.add_parser("doctrines", help="list doctrines or show one")
    doctrines.add_argument("school", nargs="?")

    benchmark = sub.add_parser("benchmark", help="run a cross-domain Council benchmark suite")
    benchmark.add_argument("suite", nargs="?", help="suite path; defaults to the bundled five-domain suite")
    benchmark.add_argument("--corpus-dir", help="verified primary-source corpus used to measure grounded coverage")

    audit = sub.add_parser("audit", help="verify doctrine, skill, source, schema, and package alignment")
    audit.add_argument("--root", default=".", help="repository root to audit")

    sources = sub.add_parser("sources", help="ingest and search rights-verified primary texts")
    sources.add_argument("--corpus-dir", default="sources/corpus")
    source_sub = sources.add_subparsers(dest="source_command", required=True)
    source_sub.add_parser("list")
    search = source_sub.add_parser("search")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--source-id", action="append")
    ingest = source_sub.add_parser("ingest")
    ingest.add_argument("text")
    ingest.add_argument("metadata", help="JSON metadata conforming to source-record.schema.json")

    journal = sub.add_parser("journal", help="inspect and review recorded decisions")
    journal.add_argument("--journal-dir", default="decisions")
    journal_sub = journal.add_subparsers(dest="journal_command", required=True)
    journal_sub.add_parser("list")
    show = journal_sub.add_parser("show")
    show.add_argument("entry_id")
    review = journal_sub.add_parser("review")
    review.add_argument("entry_id")
    review.add_argument("--actual-outcome", required=True)
    review.add_argument("--lesson", action="append", required=True)
    review.add_argument("--prediction-result", choices=("true", "false"), action="append", default=[])
    journal_sub.add_parser("insights")
    return parser


def _load_packet(path: str) -> DecisionPacket:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValidationError(f"cannot read packet: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"packet is not valid JSON: {exc.msg} at line {exc.lineno}") from exc
    return DecisionPacket.from_dict(data)


def _emit(payload: Any, stream: TextIO) -> None:
    json.dump(payload, stream, indent=2, ensure_ascii=False)
    stream.write("\n")


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    try:
        args = _parser().parse_args(argv)
        corpus_dir = getattr(args, "corpus_dir", None)
        corpus = SourceCorpus(corpus_dir) if corpus_dir else None
        council = Council(reasoner=HeuristicReasoner(corpus)) if corpus else Council()

        if args.command == "validate":
            _emit(_load_packet(args.packet).to_dict(), stdout)
        elif args.command == "examine":
            _emit(council.examine(_load_packet(args.packet)).to_dict(), stdout)
        elif args.command == "ask":
            _emit(council.ask(args.school, _load_packet(args.packet)).to_dict(), stdout)
        elif args.command == "council":
            packet = _load_packet(args.packet)
            result = council.convene(packet, args.schools)
            payload: dict[str, Any] = result.to_dict()
            if args.record:
                user_decision = args.user_decision or result.synthesis.recommendation
                user_confidence = args.user_confidence if args.user_confidence is not None else result.synthesis.confidence
                entry = DecisionJournal(args.journal_dir).record(
                    packet,
                    result,
                    user_decision=user_decision,
                    user_confidence=user_confidence,
                    predicted_outcomes=args.predicted_outcome,
                    review_date=args.review_date,
                )
                payload["journal_entry"] = entry.to_dict()
            _emit(payload, stdout)
        elif args.command == "doctrines":
            payload = get_doctrine(args.school).to_dict() if args.school else [d.to_dict() for d in list_doctrines()]
            _emit(payload, stdout)
        elif args.command == "benchmark":
            suite_path = args.suite or asset_path("benchmarks/cases.json")
            _emit(BenchmarkSuite.from_file(suite_path, council=council, corpus=corpus).run(), stdout)
        elif args.command == "audit":
            report = audit_repository(args.root)
            _emit(report, stdout)
            return 1 if report["errors"] else 0
        elif args.command == "sources":
            corpus = SourceCorpus(args.corpus_dir)
            if args.source_command == "list":
                _emit([record.__dict__ for record in corpus.list_records()], stdout)
            elif args.source_command == "search":
                _emit(
                    [passage.to_dict() for passage in corpus.search(args.query, top_k=args.top_k, source_ids=args.source_id)],
                    stdout,
                )
            else:
                try:
                    metadata = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    raise ValidationError(f"cannot load source metadata: {exc}") from exc
                _emit(corpus.ingest_file(args.text, metadata).__dict__, stdout)
        elif args.command == "journal":
            journal = DecisionJournal(args.journal_dir)
            if args.journal_command == "list":
                _emit([entry.to_dict() for entry in journal.list_entries()], stdout)
            elif args.journal_command == "show":
                _emit(journal.get(args.entry_id).to_dict(), stdout)
            elif args.journal_command == "review":
                results = [value == "true" for value in args.prediction_result]
                entry = journal.review(
                    args.entry_id,
                    actual_outcome=args.actual_outcome,
                    lessons=args.lesson,
                    prediction_results=results,
                )
                _emit(entry.to_dict(), stdout)
            else:
                _emit(journal.insights(), stdout)
        return 0
    except (ValidationError, KeyError, ValueError) as exc:
        stderr.write(f"error: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
