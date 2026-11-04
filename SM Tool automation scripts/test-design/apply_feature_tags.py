"""Apply functional tags from opsdesk_test_data.py to the Cucumber feature files.

- Feature line: the first tag becomes the feature's functional tag (FEATURE_TAGS).
- Scenario / Examples tag lines: the functional tag for the line's @TC id is put first (FUNCTION_TAGS).
- A Scenario Outline whose TC ids sit on its Examples blocks gets OUTLINE_TAGS (or the feature tag).
Re-running is safe: existing functional tags are replaced, not duplicated.

usage: python apply_feature_tags.py [features_dir]
"""
import re
import sys
from pathlib import Path

import opsdesk_test_data as d

ROOT = Path(__file__).resolve().parent.parent
FEATURES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "automation" / "features"
OLD_FEATURE_TAGS = {"@admin", "@assignment", "@audit", "@auth", "@change", "@customer-portal", "@dashboard",
                    "@knowledge-base", "@lifecycle", "@major-incident", "@nfr", "@priority", "@rbac", "@reports",
                    "@service-request", "@sla", "@tickets"}
# Scenario Outlines whose TC ids sit on their Examples blocks
OUTLINE_TAGS = {"reports.feature": "@export_report_csv_pdf"}
ALL_FUNCTIONAL = set(d.FUNCTION_TAGS.values()) | set(d.FEATURE_TAGS.values()) | set(OUTLINE_TAGS.values()) | OLD_FEATURE_TAGS
TC_RE = re.compile(r"@(TC-[A-Z]+-\d{3})\b")

missing = []
for f in sorted(FEATURES.glob("*.feature")):
    lines = f.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("@"):
            continue
        indent = line[: len(line) - len(line.lstrip())]
        tags = [t for t in line.split() if t not in ALL_FUNCTIONAL]
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        tc = TC_RE.search(line)
        if nxt.startswith("Feature:"):
            lead = d.FEATURE_TAGS[f.name]
        elif tc:
            lead = d.FUNCTION_TAGS.get(tc.group(1))
            if not lead:
                missing.append(f"{f.name}: {tc.group(1)}")
                continue
        elif nxt.startswith("Scenario Outline:"):
            lead = OUTLINE_TAGS.get(f.name, d.FEATURE_TAGS[f.name])  # TC ids live on the Examples blocks
        else:
            continue
        lines[i] = indent + " ".join([lead] + tags)
    f.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"tagged {f.name}")
if missing:
    print("NO FUNCTIONAL TAG DEFINED FOR: " + ", ".join(missing))
    sys.exit(1)
