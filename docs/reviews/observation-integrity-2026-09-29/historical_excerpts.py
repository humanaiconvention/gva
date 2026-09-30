"""Historical GVA audit excerpts, bundled only for classification review.

Do not import this file: the reproduction harness compiles selected AST function
definitions with explicitly supplied dependencies. See SOURCE-PROVENANCE.json.
No historical function body is changed.
"""

# Original: development/observation_integrity/serialization.py:11-17
def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result

# Original: development/observation_integrity/serialization.py:20-21
def _constant(value):
    raise ValueError(f"Nonstandard JSON constant: {value}")

# Original: development/observation_integrity/serialization.py:24-28
def _exact_float(token):
    try:
        return Decimal(token)
    except InvalidOperation as exc:
        raise ValueError("Invalid decimal JSON number") from exc

# Original: development/observation_integrity/serialization.py:31-35
def strict_loads(text, *, exact_numbers=False):
    # Validate transport numbers before binary floating-point rounding can erase
    # a fractional part or underflow a nonzero value to zero.
    return json.loads(text, object_pairs_hook=_object, parse_constant=_constant,
                      parse_float=_exact_float if exact_numbers else float)

# Original: development/observation_integrity/serialization.py:70-71
def read_json(path):
    return strict_loads(Path(path).read_text(encoding="utf-8"))

# Original: development/observation_campaign/statistics.py:41-49
def root_campaign_status(attempt_records, expected_attempts):
    """OR endpoint: a known witness settles event=true even if other attempts fail."""
    by_attempt = {r["attempt"]:r for r in attempt_records}
    if len(by_attempt) != len(attempt_records) or set(by_attempt)-set(expected_attempts):
        raise ValueError("Duplicate or unexpected root attempts")
    known = any(r.get("status") == "complete" and r["analysis"]["attack_associated_excess"] for r in by_attempt.values())
    unresolved = any(a not in by_attempt or by_attempt[a].get("status") != "complete" for a in expected_attempts)
    return {"attack_associated_campaign_event":True if known else (None if unresolved else False),
            "has_unresolved_attempts":unresolved,"known_witness":known}

# Original: development/observation_campaign/runner.py:104-122
def collect_root(out, fixture, worker):
    records, failures = [], []
    for attempt in ATTEMPTS:
        for label, system in (("r1",R1Receiver.name),("control",CONTROL_FOR[attempt].name)):
            path = out/f"{attempt}-{label}.json"
            try:
                record = read_json(path)
            except (OSError,ValueError) as exc:
                record = {"status":"unresolved","attempt":attempt,"system":system,"family":FAMILIES[attempt],
                          "fixture_id":fixture["fixture_id"],"parent_root_id":fixture["parent_root_id"],
                          "failure_category":worker.get("failure_category","invalid_runs"),"message":"Missing/incomplete result: "+str(exc)}
            records.append(record)
            if record["status"] != "complete":
                failures.append(record)
    r1 = [r for r in records if r["system"] == R1Receiver.name]
    result = root_campaign_status(r1,ATTEMPTS)
    result["families"] = {family:root_campaign_status([r for r in r1 if r["family"] == family],
                            [a for a in ATTEMPTS if FAMILIES[a] == family]) for family in sorted(set(FAMILIES.values()))}
    return records, failures, result
