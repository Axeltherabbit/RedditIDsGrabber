import argparse
from os import listdir
from os.path import isfile, join


def tryb36(w):
    # just need it because some words are not base36
    try:
        return int(w, 36)
    except:
        return None


def main(idir: str, ofile: str):
    dirfiles = [f for f in listdir(idir) if isfile(join(idir, f))]
    s = set()
    for f in dirfiles:
        with open(f"./{idir}/{f}", "r") as f:
            l = f.read().strip().split("\n")
            s.update(l)

    # sort the list
    d = {tryb36(w): w for w in s}
    if None in d:
        del d[None]
    l = [d[k] for k in sorted(d.keys())]

    with open(ofile, "w") as f:
        f.write("\n".join(l))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "convert each file in an input directory into a wordlist of reddit possible"
            " IDs, the file format is a word for line"
        )
    )
    parser.add_argument("--idir", type=str, help="input directory")
    parser.add_argument("--ofile", type=str, help="output file")
    args = parser.parse_args()
    main(**vars(args))
