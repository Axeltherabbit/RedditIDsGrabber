import argparse


def tryb36(w):
    # just need it because some words are not base36
    try:
        val = int(w, 36)
        if val > int("italia", 36):
            return val
    except:
        return None


def main(ifile: str, ofile: str):
    with open(ifile, "r") as f:
        l = f.read().strip().split("\n")
        d = {tryb36(w): w for w in l}
        if None in d:
            del d[None]
        l = [d[k] for k in sorted(d.keys())]
    with open(ofile, "w") as f:
        f.write("\n".join(l))
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="convert wordlist in a reddit ID list")
    parser.add_argument("--ifile", type=str, help="inputfile")
    parser.add_argument("--ofile", type=str, help="output file")
    args = parser.parse_args()
    main(**vars(args))
