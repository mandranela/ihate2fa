import argparse

from src.io import datasets


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--datasets",       nargs="+", type=str, default=[])
    parser.add_argument("--serialization",  nargs="+", type=str, default=[])
    parser.add_argument("--compression",    nargs="+", type=str, default=[])
    parser.add_argument("--packaging",      nargs="+", type=str, default=[])
    
    args = parser.parse_args()
    print(args)
    dfs = datasets.get_dfs(args.datasets)
    print(dfs)
    


if __name__ == "__main__":
    main()
    # df = datasets.get_BWSAS()
    # serialize
    # compress
    # package
    # evaluate
    # other things