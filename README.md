# DHG 502 — Assignment 1: Collocations of 魏忠贤 in the *Mingshi*

**Course:** DHG 502, Term 1, 2026–2027

## Research question

How does the *Mingshi* 明史 (History of the Ming) frame 魏忠贤 (Wei Zhongxian)?
Using collocation analysis, which words does the Qing-compiled official history
attach to him, and what does the company he keeps tell us about how an official
history constructs a person?

## Source and rights

- **File:** `data/明史.txt` — the full *Mingshi*, classical Chinese, traditional
  characters, UTF-8.
- **Provenance:** taken from the course template repository
  (`https://github.com/mcjkurz/qh-starter`, the "course template" named in the
  assignment). The transcription corresponds to the **Wikisource 明史** edition
  (zh.wikisource.org); the file carries Wikisource's public-domain notice
  template ("本清朝作品在全世界都屬於公有領域…") 312 times.
- **Rights:** public domain. The *Mingshi* was compiled at the Qing court and
  completed in 1739; the authors' rights have long expired, and the Wikisource
  transcription is released as public domain.
- **Size:** ~3.28 million characters; 332 juan (the script detects 328 juan
  headings).

## Repository contents

```
data/明史.txt                     source (UTF-8)
userdict.txt                      jieba user dictionary
segment.py                        clean → opencc t2s → sentence split → jieba
collocates.py                     find_collocates runs A–E
make_report.py                    builds output/results.html
concordance.py                    builds output/kwic.html
sentences.txt / sentences_min3.txt   segmented corpora (≥5 and ≥3 tokens)
sentence_index.csv                line ↔ juan index
output/collocates_*.csv           one CSV per run
output/results.html               all collocation tables, switchable + sortable
output/kwic.html                  concordance for the discussed collocates
report.md / report.pdf            the report (800–1,200 words, English)
AI-USE.md                         AI-use disclosure
requirements.txt                  dependencies
```

## How to run

```
python -m venv .venv
. .venv/Scripts/activate          # Windows;  source .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

python segment.py                 # -> sentences.txt, sentences_min3.txt, sentence_index.csv
python collocates.py              # -> output/collocates_*.csv, output/collocates_top20.txt
python make_report.py             # -> output/results.html
python concordance.py             # -> output/kwic.html
```

## Method summary

Collocates of 魏忠贤 are scored against a 2×2 contingency table and tested with
Fisher's exact test; multiple testing is corrected with the Benjamini–Hochberg
procedure (`correction="fdr_bh"`, `max_adjusted_p=0.05`). Both a significance
measure (`log_likelihood`) and a strength measure (`logDice`) are reported and
compared. Runs: window with `horizon=5` and `10`, `method="sentence"`, a pooled
run (魏忠贤 + the short form 忠贤), and a ≥3-token sensitivity corpus. Stopwords use
`load_stopwords("zh_cl_sim")` plus a small classical-function-word list.
