# AI-USE.md

*Assignment 1 — DHG 502. This disclosure follows the course-wide submission rules.*

## 1. Tools and models used

- **OpenCode** (VS Code AI coding agent), model **`opencode-go/deepseek-v4.1-flash`**.

## 2. What the AI was used for

- **Coding and troubleshooting only.** The AI helped write and debug the Python
  scripts (`segment.py`, `collocates.py`, `make_report.py`, `concordance.py`) and
  looked up the `qhchina` API (`find_collocates`, `kwic`, `load_stopwords`).
- The AI also suggested standard method scaffolding (contingency table, Fisher's
  exact test, FDR correction, log-likelihood vs logDice) based on the Week 4 notes.
- **The analytical prose in `report.md` is my own work.** No AI-generated text was
  submitted as my analysis. The AI did **not** write the research question, the
  interpretation, or the arguments.

## 3. Representative prompts / session excerpts

- "Write `segment.py` that loads `明史.txt`, converts it to simplified with
  `opencc`, splits it into sentences, segments with `jieba` using `userdict.txt`,
  and saves `sentences.txt` and `sentence_index.csv`."
- "Using `sentences.txt`, write `collocates.py` that calls `find_collocates` for
  魏忠贤 with `correction='fdr_bh'`, `max_adjusted_p=0.05`, `min_word_length=2`,
  `min_obs_local=3`, measures `log_likelihood` and `logDice`; run window h=5,
  window h=10, and sentence."
- "Build `results.html` / `kwic.html` from the CSVs / from `kwic`."

## 4. Important changes I made

- Chose the target word (魏忠贤) and the user-dictionary entries, and decided the
  cleaning rules (remove the Wikisource notice lines, drop the `○` name-catalog
  lines, keep narrative annotations).
- Checked the segmentation by eye and corrected names/compounds that jieba split
  or merged (e.g. 王体干, 门克新, 子壮, 孙本高, 张讷, 搘柱, 谒选), which required the
  user dictionary to use the same opencc normalisation as the corpus (乾→干).
- Chose the parameters for all runs and the ≥3-token sensitivity corpus.
- Wrote the report prose, the central argument, and the close readings myself.

## 5. How I checked the AI's output

- Ran every script myself and read the printed output.
- Inspected a sample of ~25 segmented sentences containing the target by eye and
  recorded the residual segmentation problems.
- Verified character and occurrence counts against the raw text (e.g. 魏忠贤:
  245 occurrences = 1 lost in excluded catalogs + 18 in 3–4-token sentences +
  226 kept).
- Read the KWIC passages against the source text and checked the cited 卷 numbers.
- Compared the logDice and log-likelihood rankings and confirmed the divergences
  against the CSV files.
