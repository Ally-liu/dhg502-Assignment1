# collocates.py
# Run the collocation analysis for target 魏忠贤 over the segmented Mingshi.
#
# Runs (all: fdr_bh, max_adjusted_p=0.05, min_word_length=2, min_obs_local=3,
#        measures = log_likelihood + logDice, alternative="greater"):
#   A window5   window h=5   target 魏忠贤         (>=5-token corpus)
#   B window10  window h=10  target 魏忠贤         (>=5-token corpus)
#   C sentence  sentence     target 魏忠贤         (>=5-token corpus)
#   D pooled    window h=5   target 魏忠贤+忠贤     (>=5-token corpus, pooled)
#   E min3      window h=5   target 魏忠贤         (>=3-token corpus, sensitivity)
#
# Outputs: output/collocates_<name>.csv  and  output/collocates_top20.txt

from pathlib import Path

from qhchina import load_stopwords
from qhchina.analytics.collocations import find_collocates

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"
OUT.mkdir(exist_ok=True)

CUSTOM_STOPWORDS = ["于", "为", "有", "则", "且", "由", "自", "从", "得",
                    "因", "当", "悉", "俱", "并", "尽"]
STOPWORDS = set(load_stopwords("zh_cl_sim")) | set(CUSTOM_STOPWORDS)

MEASURES = ["log_likelihood", "logDice"]
FILTERS = {"stopwords": STOPWORDS, "max_adjusted_p": 0.05,
           "min_word_length": 2, "min_obs_local": 3}


def read_sentences(path: Path):
    return [line.split(" ") for line in path.read_text(encoding="utf-8").splitlines()]


def run(corpus, name, target_words, method="window", horizon=5, pooled=False):
    df = find_collocates(
        corpus,
        target_words=target_words,
        method=method,
        horizon=(horizon if method == "window" else None),
        pooled=pooled,
        measures=MEASURES,
        correction="fdr_bh",
        alternative="greater",
        filters=FILTERS,
        sort_by="log_dice",
    )
    df.to_csv(OUT / f"collocates_{name}.csv", index=False, encoding="utf-8-sig")
    print(f"  {name}: {len(df)} collocates")
    return df


def main() -> None:
    sents5 = read_sentences(BASE / "sentences.txt")
    sents3 = read_sentences(BASE / "sentences_min3.txt")
    print(f"corpora: >=5 -> {len(sents5)} sentences; >=3 -> {len(sents3)} sentences")

    specs = [
        ("window5",  sents5, dict(target_words="魏忠贤", method="window", horizon=5)),
        ("window10", sents5, dict(target_words="魏忠贤", method="window", horizon=10)),
        ("sentence", sents5, dict(target_words="魏忠贤", method="sentence")),
        ("pooled",   sents5, dict(target_words=["魏忠贤", "忠贤"], method="window",
                                  horizon=5, pooled=True)),
        ("min3",     sents3, dict(target_words="魏忠贤", method="window", horizon=5)),
    ]

    results = {}
    for name, corpus, kw in specs:
        results[name] = run(corpus, name, **kw)

    cols_d = ["collocate", "obs_local", "exp_local", "ratio_local",
              "log_dice", "log_likelihood", "adjusted_p_value"]
    parts = []
    for name, df in results.items():
        by_dice = df.sort_values("log_dice", ascending=False)
        by_ll = df.sort_values("log_likelihood", ascending=False)
        parts.append(f"### {name}  (rows={len(df)})")
        parts.append("-- top 20 by logDice (strength) --")
        parts.append(by_dice.head(20)[cols_d].to_string(index=False))
        parts.append("")
        parts.append("-- top 20 by log_likelihood (significance) --")
        parts.append(by_ll.head(20)[cols_d].to_string(index=False))
        top_d10 = list(by_dice.head(10)["collocate"])
        top_l10 = list(by_ll.head(10)["collocate"])
        shared = [w for w in top_d10 if w in top_l10]
        parts.append("")
        parts.append(f"top-10 overlap (dice vs LL): {len(shared)}/10  "
                     f"| only-in-dice: {[w for w in top_d10 if w not in top_l10]}"
                     f" | only-in-LL: {[w for w in top_l10 if w not in top_d10]}")
        parts.append("")

    txt = "\n".join(parts)
    (OUT / "collocates_top20.txt").write_text(txt, encoding="utf-8")
    print("wrote output/collocates_top20.txt")


if __name__ == "__main__":
    main()
