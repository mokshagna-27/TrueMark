import argparse, json
from .pipeline import analyze
def main():
    parser=argparse.ArgumentParser(description="TrueMark independent analyzer")
    parser.add_argument("text", nargs="?")
    parser.add_argument("--file")
    parser.add_argument("--channel",default="unknown")
    args=parser.parse_args()
    if args.file:
        with open(args.file,encoding="utf-8") as f: draft=f.read()
    elif args.text is not None: draft=args.text
    else: parser.error("provide text or --file")
    print(json.dumps(analyze(draft,args.channel),indent=2,ensure_ascii=False))
if __name__=="__main__": main()
