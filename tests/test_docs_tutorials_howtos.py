"""Automated dataset manifest, NDJSON check, script.sh execution, and Diataxis verification suite."""

from __future__ import annotations

import json
import pathlib
import re
import shutil
import subprocess
import sys
import unittest

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^([ \t]*)(`{3,}|~{3,})(.*)$")
BOX_OR_ARROW_RE = re.compile(r"(?:[┌┐└┘╔╗╚╝├┤┬┴┼═─]{2,}|\+[-=]{2,}\+|(?<![<!])-->|<--)")
INDENTED_MERMAID_RE = re.compile(r"^[ \t]+(?:```|~~~)mermaid\b", re.MULTILINE)
UNFENCED_MERMAID_HEADER_RE = re.compile(r"^(?:flowchart|graph\s+(?:TD|TB|LR)|sequenceDiagram)\b")

WEAK_MODALS_RE = re.compile(r"\b(?:should|would|may|might|shall|ought)\b", re.IGNORECASE)
CONTRACTIONS_RE = re.compile(
    r"\b(?:don't|doesn't|didn't|won't|can't|isn't|aren't|wasn't|weren't|"
    r"haven't|hasn't|hadn't|you're|we're|they're|it's|that's)\b",
    re.IGNORECASE,
)
FRENCH_STOPWORD_RE = re.compile(
    r"[àâäçéèêëîïôöùûüÿœæ]|"
    r"\b(?:procédure|tutoriel|prérequis|étape|vérification|déploiement|référence)\b",
    re.IGNORECASE,
)


def _strip_code_blocks(text: str) -> str:
    """Return markdown prose with fenced code blocks removed."""
    kept: list[str] = []
    in_fence = False
    fence_char = ""
    fence_len = 0
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if not in_fence and match:
            in_fence = True
            fence_char = match.group(2)[0]
            fence_len = len(match.group(2))
            continue
        if in_fence:
            stripped = line.strip()
            if stripped and set(stripped) == {fence_char} and len(stripped) >= fence_len:
                in_fence = False
            continue
        kept.append(line)
    return "\n".join(kept)


class TestDocsTutorialsHowtos(unittest.TestCase):
    """Validate NDJSON datasets, script.sh execution, Compose config, Diataxis, STE, and Mermaid."""

    def test_dataset_files_exist_and_valid_json_records(self) -> None:
        dirs = sorted(p for p in REPO_ROOT.glob("sample_*") if p.is_dir())
        self.assertEqual(len(dirs), 7)
        json_files = sorted(REPO_ROOT.glob("sample_*/*.json"))
        self.assertEqual(len(json_files), 21)

        for json_path in json_files:
            with self.subTest(dataset=json_path.relative_to(REPO_ROOT).as_posix()):
                size = json_path.stat().st_size
                self.assertGreater(size, 0)
                if size < 500_000:
                    lines = [ln.strip() for ln in json_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
                    self.assertGreater(len(lines), 0)
                    for line in lines:
                        json.loads(line)
                else:
                    with json_path.open("rb") as fh:
                        first = fh.readline().decode("utf-8").strip()
                        fh.seek(0, 2)
                        fh.seek(max(0, fh.tell() - 65536))
                        tail_lines = [ln.strip() for ln in fh.read().decode("utf-8", errors="replace").splitlines() if ln.strip()]
                    json.loads(first)
                    json.loads(tail_lines[-1])

    def test_readme_compose_and_reference_match_all_collections(self) -> None:
        compose = yaml.safe_load((REPO_ROOT / "docker-compose.yaml").read_text(encoding="utf-8"))
        self.assertIn("mongodb", compose["services"])

        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        ref_doc = (DOCS_DIR / "03-reference/datasets-and-script-spec.md").read_text(encoding="utf-8")

        for legacy in ("neelabalan/mongodb-sample-dataset/blob", "need to installed", "seperate", "2717"):
            self.assertNotIn(legacy, readme)

        self.assertIn("sessions", readme)
        self.assertIn("inspections", readme)
        self.assertRegex(readme, r"\binspections\b")

        for json_path in sorted(REPO_ROOT.glob("sample_*/*.json")):
            db_name = json_path.parent.name
            coll_name = json_path.stem
            rel_path = json_path.relative_to(REPO_ROOT).as_posix()
            self.assertIn(db_name, readme)
            self.assertIn(coll_name, readme)
            self.assertIn(rel_path, ref_doc)

    def test_script_sh_syntax_and_mocked_mongoimport_execution(self) -> None:
        script_path = REPO_ROOT / "script.sh"
        raw_bytes = script_path.read_bytes()
        self.assertNotIn(b"\r\n", raw_bytes, "script.sh must use LF line endings")
        script_text = raw_bytes.decode("utf-8")
        self.assertIn("for directory in sample_*", script_text)

        bash_bin = shutil.which("bash")
        self.assertIsNotNone(bash_bin, "bash is required to execute script.sh checks")

        # Validate syntax via stdin and execute live CLI / mocked mongoimport paths under bash.
        syntax = subprocess.run([bash_bin, "-n"], input=raw_bytes, capture_output=True, check=False)
        self.assertEqual(syntax.returncode, 0, syntax.stderr.decode("utf-8", "replace"))

        help_run = subprocess.run(
            [bash_bin, "./script.sh", "--help"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(help_run.returncode, 0, help_run.stderr)
        self.assertIn("Usage: ./script.sh", help_run.stdout)

        mock_script = r"""set -euo pipefail
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/empty" "$tmp/bin"
ln -s "$(command -v basename)" "$tmp/empty/basename" 2>/dev/null || true
if PATH="$tmp/empty" ./script.sh 2>"$tmp/missing.err"; then
  echo "UNEXPECTED_SUCCESS_WITHOUT_MONGOIMPORT" >&2
  exit 1
fi
grep -q "mongoimport command not found" "$tmp/missing.err"

cat > "$tmp/bin/mongoimport" <<'SH'
#!/bin/bash
printf '%s\n' "$*" >> "${MOCK_LOG}"
SH
chmod +x "$tmp/bin/mongoimport"

export MOCK_LOG="$tmp/calls.log"
PATH="$tmp/bin:$PATH" ./script.sh 127.0.0.1 27018 admin 'secret123'
wc -l < "$MOCK_LOG"

if PATH="$tmp/bin:$PATH" ./script.sh localhost 27017 onlyuser 2>"$tmp/partial.err"; then
  echo "UNEXPECTED_SUCCESS_PARTIAL_AUTH" >&2
  exit 1
fi
grep -q "both username and password" "$tmp/partial.err"
cat "$MOCK_LOG"
"""
        # Pass LF script via stdin (-s) so Windows WSL bash.exe and Linux bash parse quotes identically.
        mocked = subprocess.run(
            [bash_bin, "-s"],
            input=mock_script.replace("\r\n", "\n").encode("utf-8"),
            cwd=str(REPO_ROOT),
            capture_output=True,
            check=False,
        )
        mocked_out = mocked.stdout.decode("utf-8", "replace")
        mocked_err = mocked.stderr.decode("utf-8", "replace")
        self.assertEqual(mocked.returncode, 0, mocked_out + mocked_err)
        call_lines = [ln for ln in mocked_out.splitlines() if "--db " in ln]
        self.assertEqual(len(call_lines), 21, f"Expected 21 dataset imports, got: {call_lines}")
        for line in call_lines:
            self.assertIn("--host 127.0.0.1 --port 27018 --db sample_", line)
            self.assertIn("--authenticationDatabase admin -u admin -p secret123", line)
            self.assertNotIn("--db docs", line)
            self.assertNotIn("--db tests", line)

    def test_diataxis_structure_links_and_ste_rules(self) -> None:
        for rel in (
            "index.md",
            "01-tutorials/index.md",
            "01-tutorials/01-import-datasets-into-local-mongo.md",
            "02-how-to-guides/index.md",
            "02-how-to-guides/import-and-verify-datasets.md",
            "03-reference/index.md",
            "03-reference/datasets-and-script-spec.md",
            "04-explanation/index.md",
            "04-explanation/ndjson-storage-and-loader-design.md",
        ):
            self.assertTrue((DOCS_DIR / rel).is_file(), f"Missing docs/{rel}")

        for page in [REPO_ROOT / "README.md", *sorted(DOCS_DIR.rglob("*.md"))]:
            prose = _strip_code_blocks(page.read_text(encoding="utf-8"))
            for target in LINK_RE.findall(prose):
                clean = target.split("#", 1)[0].strip()
                if not clean or clean.startswith(("http://", "https://", "mailto:")):
                    continue
                resolved = (page.parent / clean).resolve()
                self.assertTrue(
                    resolved.exists(),
                    f"Broken relative link '{target}' in {page.relative_to(REPO_ROOT)}",
                )

        for guide in sorted((DOCS_DIR / "02-how-to-guides").glob("*.md")):
            if guide.name == "index.md":
                continue
            prose = _strip_code_blocks(guide.read_text(encoding="utf-8"))
            self.assertIsNone(WEAK_MODALS_RE.search(prose), f"Weak modal in {guide}")
            self.assertIsNone(CONTRACTIONS_RE.search(prose), f"Contraction in {guide}")
            self.assertNotIn(";", prose, f"Semicolon in {guide}")
            self.assertFalse(re.search(r"^##\s+(?:Why|Architecture|Context)\b", prose, re.M))

    def test_optional_skill_validators_if_installed(self) -> None:
        skills_root = pathlib.Path.home() / ".gemini/config/skills"
        diataxis_script = skills_root / "diataxis-docs/scripts/diataxis_check.py"
        if diataxis_script.is_file():
            proc = subprocess.run(
                [sys.executable, str(diataxis_script), str(DOCS_DIR), "--strict", "--check-ste", "--lang", "en"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("0 error(s), 0 warning(s)", proc.stdout)

        ste_script = skills_root / "simplified-technical-english/scripts/ste_check.py"
        if ste_script.is_file():
            guides = sorted(
                str(p)
                for p in (DOCS_DIR / "02-how-to-guides").glob("*.md")
                if p.name != "index.md"
            )
            proc = subprocess.run(
                [sys.executable, str(ste_script), "--mode", "procedural", *guides],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("Result: 0 errors, 0 warnings.", proc.stdout)

    def test_diagrams_mermaid_no_ascii_and_english_only(self) -> None:
        md_files = sorted(
            p for p in REPO_ROOT.rglob("*.md") if ".git" not in p.parts and ".pytest_cache" not in p.parts
        )
        mermaid_count = 0
        for md_path in md_files:
            raw = md_path.read_text(encoding="utf-8")
            self.assertIsNone(INDENTED_MERMAID_RE.search(raw), f"Indented mermaid in {md_path}")
            in_fence = False
            fence_char = ""
            fence_len = 0
            fence_info = ""
            for idx, line in enumerate(raw.splitlines(), start=1):
                match = FENCE_RE.match(line)
                if not in_fence and match:
                    in_fence = True
                    fence_char = match.group(2)[0]
                    fence_len = len(match.group(2))
                    fence_info = match.group(3).strip().lower()
                    if fence_info == "mermaid":
                        mermaid_count += 1
                    continue
                if in_fence:
                    stripped = line.strip()
                    if stripped and set(stripped) == {fence_char} and len(stripped) >= fence_len:
                        in_fence = False
                        fence_info = ""
                        continue
                    if fence_info != "mermaid":
                        self.assertIsNone(
                            UNFENCED_MERMAID_HEADER_RE.match(line.strip()),
                            f"Untagged mermaid syntax at {md_path}:{idx}",
                        )
                        self.assertIsNone(
                            BOX_OR_ARROW_RE.search(line),
                            f"ASCII/box diagram at {md_path}:{idx}: {line}",
                        )
                    continue

                if "-->" not in line and "<--" not in line:
                    self.assertIsNone(BOX_OR_ARROW_RE.search(line), f"ASCII line at {md_path}:{idx}")
            self.assertIsNone(FRENCH_STOPWORD_RE.search(_strip_code_blocks(raw)), f"French text in {md_path}")
        self.assertGreaterEqual(mermaid_count, 2)


if __name__ == "__main__":
    unittest.main()
