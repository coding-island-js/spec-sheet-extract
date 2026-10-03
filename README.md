# spec-sheet-extract

**Give it a manufacturer spec sheet and a part number, and it fills in the catalog fields for that one model. Every value comes with the exact words it was read from.**

Distributors have thousands of products waiting to go online, and the facts are stuck in PDFs. One sheet often covers five or seven models in one table, so the hard part isn't reading the PDF. It's reading the right column.

## What happened on 5 real sheets

I ran it on 5 public spec sheets from HVAC and plumbing manufacturers, one part number each. That came to 37 fields in total. Then I checked every value myself against the rendered page.

| Product | Part number | Right |
|---|---|---|
| Goodman split system AC | GSXN403610 | 9/9 |
| Goodman gas furnace | GR9S800804BU | 8/8 |
| Rheem tankless water heater | RTGH-95DVLN | 7/7 |
| Honeywell T6 Pro thermostat | TH6220WF2006 | 7/7 |
| Watts LF009 backflow preventer | 3/4 inch | 6/6 |

**37 of 37 right. The whole run cost about $0.91 in Claude API calls.**

## Why the quote check matters

Every answer has to include a quote. The script then looks for that quote in the PDF's text. If it isn't there, the value goes to a person instead of straight into the catalog.

8 of the 37 values were sent to a person this way, and all 8 turned out to be right. The reason is the interesting part. On the Goodman furnace sheet, the text inside the PDF is out of line with the table you see on the page. A tool that just copies that text would list this 80,000 BTU furnace at 64,000 BTU, and at 20 lb instead of 108 lb. Claude read the table the way a person sees it, got it right, and the check still made sure someone looked.

So the check doesn't prove a value is wrong. It finds the values that deserve a second look, and a shaky table is exactly where you want that.

## The notes matter too

The model adds a note when a value applies to a whole series rather than one exact part. For example, the AC's 14.3 SEER2 rating is printed for the whole series on the cover. Those notes are in `review.json`, and they are the kind of thing a catalog team would want to decide on, not have an AI decide quietly.

## Run it

```bash
pip install anthropic
export ANTHROPIC_API_KEY=...
python extract.py          # downloads the sheets from the manufacturers, writes results/
python extract.py score    # tallies the human review in review.json
```

To add a product, add an entry to `products.json` with the sheet's link, the part number, and the fields you want. You also need `pdftotext` (from Poppler) for the quote check.

## Limits, plainly

- Five sheets is a small sample, and I was the one checking the answers.
- The quote check uses the PDF's text. On a scanned sheet with no text, every value would go to a person.
- It uses Claude Opus 5 reading the whole PDF. A big multi-model sheet costs more than a one-pager. The Goodman AC sheet alone was about 100,000 input tokens.
