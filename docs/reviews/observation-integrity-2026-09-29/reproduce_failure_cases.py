"""Derived three-case GVA classifier review; standard library only.

See SOURCE-PROVENANCE.json for the original harness hash and documented changes.
Historical classification/parsing bodies are compiled verbatim, not imported.
"""
import argparse
import ast
import contextlib
import copy
import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import SimpleNamespace

sys.dont_write_bytecode = True


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_historical_functions(package, provenance, baseline):
    data = (package / "historical_excerpts.py").read_bytes()
    require(hashlib.sha256(data).hexdigest() == provenance["excerpt_file_sha256"],
            "Historical excerpt file hash mismatch")
    source = data.decode("utf-8")
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    require(all(isinstance(node, ast.FunctionDef) or
                (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
                 and isinstance(node.value.value, str)) for node in tree.body),
            "Unexpected top-level excerpt content")
    entries = provenance["historical_functions"]
    require([node.name for node in functions] == [e["function"] for e in entries],
            "Historical function membership/order mismatch")
    names = {
        "json": json, "Path": Path, "Decimal": Decimal,
        "InvalidOperation": InvalidOperation,
        "ATTEMPTS": tuple(baseline["attempts"]), "FAMILIES": baseline["families"],
        "R1Receiver": SimpleNamespace(name=baseline["r1_system"]),
        "CONTROL_FOR": {key: SimpleNamespace(name=value)
                        for key, value in baseline["control_systems"].items()},
    }
    for node, entry in zip(functions, entries):
        body = ast.get_source_segment(source, node)
        require(hashlib.sha256(body.encode("utf-8")).hexdigest() == entry["verbatim_body_sha256"],
                "Historical function body hash mismatch")
        # Restore original source-line locations; the function body is unchanged.
        ast.increment_lineno(node, entry["start_line"] - node.lineno)
        code = compile(ast.Module(body=[node], type_ignores=[]), entry["archived_file"], "exec")
        exec(code, names)
    return names


def baseline_records(baseline):
    records = {}
    for attempt in baseline["attempts"]:
        for label, system in (("r1", baseline["r1_system"]),
                              ("control", baseline["control_systems"][attempt])):
            records[f"{attempt}-{label}.json"] = {
                **baseline["fixture"], "status": "complete", "attempt": attempt,
                "family": baseline["families"][attempt], "system": system,
                "analysis": {"attack_associated_excess": False},
            }
    return records


def run(package, output):
    evidence = read_json(package / "FAILURE-PATH-EVIDENCE.json")
    provenance = read_json(package / "SOURCE-PROVENANCE.json")
    baseline = evidence["baseline"]
    names = load_historical_functions(package, provenance, baseline)
    require([case["id"] for case in evidence["cases"]] ==
            ["G-string-flag", "G-short-circuit", "I-fixture-mismatch"],
            "Expected exactly the three reviewed examples")
    template = baseline_records(baseline)
    results = []
    for case in evidence["cases"]:
        records = copy.deepcopy(template)
        for change in case["changes_from_baseline"]:
            value = records[change["file"]]
            for key in change["path"][:-1]:
                value = value[key]
            if change["operation"] == "set":
                value[change["path"][-1]] = change["value"]
            elif change["operation"] == "delete":
                del value[change["path"][-1]]
            else:
                raise ValueError("Unknown synthetic edit operation")
        case_output = output / case["id"]
        case_output.mkdir()
        for name, record in records.items():
            require(Path(name).name == name, "Synthetic filename must be a basename")
            write_json(case_output / name, record)
        returned, failures, root = names["collect_root"](
            case_output, baseline["fixture"], case["worker"])
        actual = {
            "case_statuses": [{"attempt": r["attempt"], "system": r["system"],
                               "status": r["status"]} for r in returned],
            "case_status_counts": dict(Counter(r["status"] for r in returned)),
            "returned_failure_records": failures, "root": root,
        }
        expected = case["original_expected"]
        historical_assertion = (
            expected["exception"] is None
            and root["attack_associated_campaign_event"] is expected["event"]
            and root["has_unresolved_attempts"] is expected["has_unresolved_attempts"]
            and root["known_witness"] is expected["known_witness"]
            and len(failures) == expected["failure_count"])
        # Also compare the full recorded family and case results, beyond the old assertion.
        exact_result_match = json.dumps(actual, sort_keys=True) == json.dumps(case["recorded_result"], sort_keys=True)
        results.append({"id": case["id"], "worker": case["worker"], "actual": actual,
                        "historical_scalar_assertion_matched": historical_assertion,
                        "full_recorded_result_matched": exact_result_match})
        require(historical_assertion and exact_result_match, "Unexpected classifier result")
        print(f"{case['id']}: event={root['attack_associated_campaign_event']}, "
              f"unresolved={root['has_unresolved_attempts']}, "
              f"known={root['known_witness']}; recorded result matched")
    result = {
        "format": "gva-three-case-classifier-review-v1",
        "scope": "Synthetic archived-function classification only; no receiver, worker or simulator execution",
        "cases": results, "all_matched": True,
    }
    write_json(output / "RESULTS.json", result)
    print("Three recorded classifier behaviors reproduced; no claim of adequate policy or valid scored witnesses.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True, type=Path,
                        help="Read-only directory containing this public review package")
    parser.add_argument("--output", required=True, type=Path,
                        help="New, nonexistent output directory; its parent must already exist")
    args = parser.parse_args()
    package, output = args.package.resolve(), args.output.absolute()
    try:
        # Claim the directory before opening any log. No shell redirection is needed.
        # Existing files, directories, and broken symlinks are refused by mkdir.
        output.mkdir(exist_ok=False)
    except OSError:
        print("Output directory was not created; choose a fresh path with an existing parent. No logs were opened.", file=sys.stderr)
        return 2
    with (output / "stdout.txt").open("x", encoding="utf-8", newline="\n") as stdout:
        with (output / "stderr.txt").open("x", encoding="utf-8", newline="\n") as stderr:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                try:
                    run(package, output)
                except Exception as error:
                    # Paths, tracebacks, session metadata and environment details are omitted.
                    print(f"Reproduction failed ({type(error).__name__}); inspect the package and synthetic inputs.", file=sys.stderr)
                    return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
