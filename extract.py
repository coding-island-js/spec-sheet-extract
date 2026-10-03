"""Pull catalog fields for one part number out of a manufacturer spec sheet.

Every value comes back with the exact words it was read from. The script then
checks that those words really are in the PDF, so a made-up value shows up as
"not found" instead of slipping into the catalog.

    python extract.py              # extract every product in products.json
    python extract.py score        # tally the human review in review.json
"""

import base64
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import anthropic

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).parent
SHEETS = ROOT / "sheets"
RESULTS = ROOT / "results"
MODEL = "claude-opus-5"

INSTRUCTIONS = """You are filling in catalog fields for ONE product from a manufacturer spec sheet.
Product: {sku} ({category}).
The sheet may cover many models in one table. Use only the row or column for {sku}.

For each field return:
- value: the value for {sku}, with units, exactly as the sheet states it. null if the sheet does not give it for this model.
- quote: the shortest exact text from the sheet that shows the value (copy it character for character). Empty if value is null.
- page: the page number where the quote appears. 0 if value is null.
- note: one short sentence if anything is uncertain (for example the value is for a model family, not this exact model). Otherwise empty.

Never guess or calculate a value the sheet does not state.

Fields:
{fields}"""


def schema(fields):
    item = {
        "type": "object",
        "properties": {
            "value": {"type": ["string", "null"]},
            "quote": {"type": "string"},
            "page": {"type": "integer"},
            "note": {"type": "string"},
        },
        "required": ["value", "quote", "page", "note"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {name: item for name in fields},
        "required": list(fields),
        "additionalProperties": False,
    }


def squash(text):
    """Lowercase and drop everything but letters and digits, so spacing and PDF layout don't matter."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def sheet_text(pdf):
    out = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return squash(out.stdout)


def fetch(product):
    """The sheets are the manufacturers' files, so they are downloaded from the source instead of kept in this repo."""
    pdf = SHEETS / product["sheet"]
    if not pdf.exists():
        SHEETS.mkdir(exist_ok=True)
        request = urllib.request.Request(product["source"], headers={"User-Agent": "Mozilla/5.0"})
        pdf.write_bytes(urllib.request.urlopen(request, timeout=60).read())
    return pdf


def extract(product, client):
    pdf = fetch(product)
    data = base64.standard_b64encode(pdf.read_bytes()).decode("utf-8")
    fields = "\n".join(f"- {k}: {v}" for k, v in product["fields"].items())
    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"format": {"type": "json_schema", "schema": schema(product["fields"])}},
        messages=[{"role": "user", "content": [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": data}},
            {"type": "text", "text": INSTRUCTIONS.format(sku=product["sku"], category=product["category"], fields=fields)},
        ]}],
    ) as stream:
        message = stream.get_final_message()
    if message.stop_reason == "refusal":
        sys.exit(f"{product['sku']}: refused")
    answer = json.loads(next(b.text for b in message.content if b.type == "text"))

    text = sheet_text(pdf)
    for field in answer.values():
        field["quote_found_in_pdf"] = bool(field["quote"]) and squash(field["quote"]) in text
    usage = message.usage
    return {"sku": product["sku"], "sheet": product["sheet"], "source": product["source"],
            "input_tokens": usage.input_tokens, "output_tokens": usage.output_tokens, "fields": answer}


def run():
    client = anthropic.Anthropic()
    RESULTS.mkdir(exist_ok=True)
    for product in json.loads((ROOT / "products.json").read_text(encoding="utf-8")):
        result = extract(product, client)
        name = re.sub(r"[^A-Za-z0-9]+", "-", product["sku"]).strip("-")
        (RESULTS / f"{name}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
        found = sum(f["quote_found_in_pdf"] for f in result["fields"].values() if f["value"] is not None)
        filled = sum(1 for f in result["fields"].values() if f["value"] is not None)
        print(f"{product['sku']:<16} {filled}/{len(result['fields'])} filled, {found}/{filled} quotes found in the PDF, "
              f"{result['input_tokens']:,} in / {result['output_tokens']:,} out tokens")


def score():
    """review.json holds a person's verdict for every field, checked against the page itself."""
    review = json.loads((ROOT / "review.json").read_text(encoding="utf-8"))
    total = right = flagged = flagged_right = 0
    for sku, fields in review.items():
        name = re.sub(r"[^A-Za-z0-9]+", "-", sku).strip("-")
        got = json.loads((RESULTS / f"{name}.json").read_text(encoding="utf-8"))["fields"]
        ok = sum(v["verdict"] == "right" for v in fields.values())
        for field, v in fields.items():
            if not got[field]["quote_found_in_pdf"]:
                flagged += 1
                flagged_right += v["verdict"] == "right"
        total += len(fields)
        right += ok
        print(f"{sku:<16} {ok}/{len(fields)} right")
    print(f"\nAll fields: {right}/{total} right")
    print(f"Quote not found in the PDF text, so sent to a person: {flagged}. Of those, right: {flagged_right}.")


if __name__ == "__main__":
    score() if sys.argv[1:] == ["score"] else run()
