import csv
import os
import sys

import qscript

_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(_DIR, "input.csv")


def main() -> int:
    qscript.PATH_TO_VIDEO_FOLDER = os.path.join(_DIR, "video")
    os.makedirs(qscript.PATH_TO_VIDEO_FOLDER, exist_ok=True)

    if not os.path.isfile(INPUT_CSV):
        print(f"Missing CSV: {INPUT_CSV}", file=sys.stderr)
        return 1

    with open(INPUT_CSV, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f, delimiter=";", quotechar='"')
        for row in reader:
            path = qscript.CaptureVideo_Magento(
                row["URL"].strip(),
                row["Company Name"].strip(),
                row["Language"].strip(),
                row["Country"].strip(),
                row["Postcode"].strip(),
                row["City"].strip(),
                row["Street"].strip(),
                row["HouseNo"].strip(),
            )
            if path:
                print(path)
            else:
                print(f"Failed: {row['Company Name']}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
