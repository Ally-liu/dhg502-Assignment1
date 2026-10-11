# segment.py
# Clean 明史.txt (traditional, Wikisource-derived) -> simplify (opencc) ->
# split into sentences -> segment with jieba (user dictionary).
#
# Outputs:
#   sentences.txt, sentence_index.csv      main set: sentences with >= 5 tokens
#   sentences_min3.txt                     sensitivity set: sentences with >= 3 tokens
#   output/segmentation_check.txt          human eye-check sample
#
# Target word for Assignment 1: 魏忠贤 (simplified).

import csv
import random
import re
from pathlib import Path

import jieba
import opencc

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "明史.txt"
USERDICT = BASE / "userdict.txt"
OUT_DIR = BASE / "output"
OUT_DIR.mkdir(exist_ok=True)
SENTENCES = BASE / "sentences.txt"
SENTENCES_MIN3 = BASE / "sentences_min3.txt"
INDEX = BASE / "sentence_index.csv"
CHECK = OUT_DIR / "segmentation_check.txt"

MIN_MAIN = 5          # main filter (Week 4 requirement)
MIN_SENS = 3          # sensitivity filter
TARGET = "魏忠贤"        # simplified target word
TARGET_TR = "魏忠賢"     # traditional form, for raw-text checks
BOILERPLATE = "本清朝作品在全世界都屬於公有領域，因為作者逝世已經超過100年。"
JUAN_RE = re.compile(r"^卷\S+$")          # juan heading line, e.g. 卷三百〇五
SEP_RE = re.compile(r"^[-=]+$")           # underlined heading / volume separators
RARE_MARK = re.compile(r"<[^<>]{1,8}>")   # Wikisource <A+B> rare-character markers
SENT_SPLIT = re.compile(r"[。！？；]")
SENT_PUNCT = re.compile(r"[。！？；]")
PUNCT_ONLY = re.compile(r"^\W+$", re.UNICODE)

CN_DIGIT = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,
            "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
CN_UNIT = {"十": 10, "百": 100, "千": 1000, "万": 10000}


def cn2int(s: str) -> int:
    total, num = 0, 0
    for ch in s:
        if ch in CN_DIGIT:
            num = CN_DIGIT[ch]
        elif ch in CN_UNIT:
            total += (num or 1) * CN_UNIT[ch]
            num = 0
    return total + num


def tokenize(sent: str):
    return [t for t in jieba.lcut(sent)
            if t.strip() and not PUNCT_ONLY.match(t)]


def main() -> None:
    raw = DATA.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    n_rare = len(RARE_MARK.findall(raw))
    raw = RARE_MARK.sub("", raw)

    cc = opencc.OpenCC("t2s")
    jieba.load_userdict(str(USERDICT))

    stats = dict(blank=0, sep=0, boiler=0, headings=0, catalog=0,
                 annotation=0, dropped_below3=0, dropped_3to4=0, kept_main=0)
    lost_catalog = lost_below3 = lost_3to4 = 0
    allrec = []  # (juan_heading, [tokens]) for every sentence with >= MIN_SENS tokens
    juan = "卷首"

    for line in raw.split("\n"):
        s = line.strip()
        if not s:
            stats["blank"] += 1
            continue
        if s == BOILERPLATE:
            stats["boiler"] += 1
            continue
        if SEP_RE.match(s):
            stats["sep"] += 1
            continue
        if JUAN_RE.match(s):
            juan = s
            stats["headings"] += 1
            continue
        if s.startswith("○"):
            # Narrative annotation keeps punctuation; bare name catalog has none.
            if SENT_PUNCT.search(s):
                stats["annotation"] += 1
                s = s.lstrip("○").strip()
            else:
                stats["catalog"] += 1
                lost_catalog += s.count(TARGET_TR)
                continue

        for sent in SENT_SPLIT.split(cc.convert(s)):
            sent = re.sub(r"○", "", sent).strip()
            if not sent:
                continue
            n_hit = sent.count(TARGET)
            toks = tokenize(sent)
            if len(toks) < MIN_SENS:
                stats["dropped_below3"] += 1
                lost_below3 += n_hit
                continue
            allrec.append((juan, toks))
            if len(toks) < MIN_MAIN:
                stats["dropped_3to4"] += 1
                lost_3to4 += n_hit

    main_records = [(j, t) for j, t in allrec if len(t) >= MIN_MAIN]
    stats["kept_main"] = len(main_records)

    with SENTENCES.open("w", encoding="utf-8") as f:
        for _, toks in main_records:
            f.write(" ".join(toks) + "\n")

    with SENTENCES_MIN3.open("w", encoding="utf-8") as f:
        for _, toks in allrec:
            f.write(" ".join(toks) + "\n")

    try:
        with INDEX.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["line", "juan_heading", "juan_num"])
            for i, (jh, _) in enumerate(main_records, 1):
                w.writerow([i, jh, cn2int(jh.replace("卷", ""))])
    except PermissionError as e:
        print("WARNING: could not write sentence_index.csv "
              "(file open elsewhere?).", e)

    main_tokens = sum(len(t) for _, t in main_records)
    min3_tokens = sum(len(t) for _, t in allrec)
    hit = [(jh, t) for jh, t in main_records if TARGET in t]
    n_raw_target = raw.count(TARGET_TR)
    n_main_target = sum(t.count(TARGET) for _, t in main_records)
    n_min3_target = sum(t.count(TARGET) for _, t in allrec)

    # ---- QA sample for the human eye check ----
    rng = random.Random(502)
    sample = rng.sample(hit, min(25, len(hit)))
    raw_ctx = []
    for m in list(re.finditer(TARGET_TR, raw))[:3]:
        raw_ctx.append(raw[m.start() - 45:m.start() + 45].replace("\n", "|"))
    catalog = [l.strip()[:120] for l in raw.split("\n")
               if l.strip().startswith("○") and not SENT_PUNCT.search(l)]

    with CHECK.open("w", encoding="utf-8") as f:
        f.write("SEGMENTATION CHECK — please read and judge by eye\n")
        f.write("=" * 60 + "\n\n")
        f.write("COUNTS\n")
        for k, v in stats.items():
            f.write(f"  {k:14s} {v}\n")
        f.write(f"  rare markers removed   {n_rare}\n")
        f.write(f"  sentences.txt (>=5)    {len(main_records)} lines / {main_tokens} tokens\n")
        f.write(f"  sentences_min3.txt     {len(allrec)} lines / {min3_tokens} tokens\n\n")

        f.write("TARGET RECOVERY (魏忠贤)\n")
        f.write(f"  in raw text                    {n_raw_target}\n")
        f.write(f"  lost in excluded ○ catalogs    {lost_catalog}\n")
        f.write(f"  lost in sentences <3 tokens    {lost_below3}\n")
        f.write(f"  in 3-4 token sentences (min3 only) {lost_3to4}\n")
        f.write(f"  kept in main (>=5)             {n_main_target}\n")
        f.write(f"  kept in min3 (>=3)             {n_min3_target}\n")
        f.write(f"  boilerplate left in sentences.txt  "
                f"{SENTENCES.read_text(encoding='utf-8').count('清朝作品')}\n\n")

        f.write("A. 25 RANDOM SEGMENTED SENTENCES CONTAINING 魏忠贤\n")
        f.write("   (read these and note any wrong splits)\n")
        f.write("-" * 60 + "\n")
        for jh, toks in sample:
            f.write(f"[{jh}] " + " / ".join(toks) + "\n\n")

        f.write("B. RAW SOURCE CONTEXT (traditional, before cleaning)\n")
        f.write("-" * 60 + "\n")
        for c in raw_ctx:
            f.write("..." + c + "...\n\n")

        f.write("C. EXAMPLES OF EXCLUDED ○ CATALOG LINES (name lists)\n")
        f.write("-" * 60 + "\n")
        for c in catalog[:6]:
            f.write("  " + c + "\n")

    print("done.")
    print({k: v for k, v in stats.items()})
    print("main:", len(main_records), "min3:", len(allrec), "main_tokens:", main_tokens)
    print("TARGET raw=%d lost_catalog=%d lost_below3=%d lost_3to4=%d main=%d min3=%d"
          % (n_raw_target, lost_catalog, lost_below3, lost_3to4,
             n_main_target, n_min3_target))


if __name__ == "__main__":
    main()
