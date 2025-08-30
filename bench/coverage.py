import glob
import traceback

from gfl.parser import GFLParseError, GFLParser


def main():
    parser = GFLParser()
    files = sorted(glob.glob("bench/corpus/*.gfl"))
    total = len(files)
    success = 0
    failed = []
    for f in files:
        # Leer con utf-8-sig para que Python quite el BOM si existe
        text = open(f, encoding="utf-8-sig").read()
        try:
            parser.parse(text)
            success += 1
        except GFLParseError as e:
            failed.append((f, str(e)))
        except Exception:
            failed.append((f, "Unexpected: " + traceback.format_exc().splitlines()[-1]))
    print(f"Parsed successfully: {success}/{total} ({success/total*100:.1f}% coverage)")
    if failed:
        print("\n-- Failures --")
        for fn, err in failed:
            print(f"{fn}: {err}")


if __name__ == "__main__":
    main()
