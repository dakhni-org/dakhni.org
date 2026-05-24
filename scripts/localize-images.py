#!/usr/bin/env python3
"""Download hot-linked Wikimedia images into each page's local assets/ folder
and rewrite the page markup to point at the local copy.

Why: several pages reference images directly from commons.wikimedia.org. Those
hot-links can break, get rate-limited, or load slowly. This makes the site
self-contained.

Usage (run from the repo root):

    python3 scripts/localize-images.py            # download + rewrite
    python3 scripts/localize-images.py --plan     # just print the mapping (no network)

The script is idempotent: an image already present in assets/ is skipped, and a
src that already points at /…/assets/ is left alone. It needs outbound access to
commons.wikimedia.org / upload.wikimedia.org.
"""
import os, re, sys, time, glob, html, urllib.parse, urllib.request, urllib.error

# Wikimedia asks bots to send a descriptive UA and to keep request rates low,
# otherwise it returns HTTP 429. We throttle between requests and back off on 429.
UA = "dakhni.org-image-localizer/1.0 (+https://github.com/dakhni-org/dakhni.org)"
THROTTLE_SECONDS = 1.5  # polite delay between requests
SRC_RE = re.compile(r'src="(https://commons\.wikimedia\.org/wiki/Special:FilePath/[^"]+)"')


def slugify(name: str) -> str:
    name = urllib.parse.unquote(name)
    name = html.unescape(name)
    base, ext = os.path.splitext(name)
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()
    ext = (ext or ".jpg").lower()
    return f"{base}{ext}"


def plan():
    """Return list of (html_file, source_url, repo_path, web_path)."""
    out = []
    for f in sorted(glob.glob("**/index.html", recursive=True)):
        page_dir = os.path.dirname(f)
        s = open(f, encoding="utf-8").read()
        for url in SRC_RE.findall(s):
            fname = url.split("/Special:FilePath/")[1].split("?")[0]
            local = slugify(fname)
            rel = os.path.join(page_dir, "assets", local) if page_dir else os.path.join("assets", local)
            web = "/" + rel.replace(os.sep, "/")
            out.append((f, url, rel, web))
    return out


def download(url: str, dest: str) -> bool:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    backoff = 5
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if len(data) < 512:
                raise ValueError(f"suspiciously small ({len(data)} bytes)")
            with open(dest, "wb") as fh:
                fh.write(data)
            return True
        except urllib.error.HTTPError as e:
            print(f"    attempt {attempt+1} failed: HTTP {e.code}")
            wait = backoff
            if e.code == 429:  # rate limited — honour Retry-After if it's an int
                ra = e.headers.get("Retry-After") if e.headers else None
                try:
                    if ra is not None:
                        wait = int(ra)
                except (ValueError, TypeError):
                    wait = backoff
                print(f"    rate limited; waiting {wait}s")
            time.sleep(min(wait, 180))
            backoff = min(backoff * 2, 120)
        except Exception as e:  # noqa: BLE001
            print(f"    attempt {attempt+1} failed: {e}")
            time.sleep(backoff)
            backoff = min(backoff * 2, 120)
    return False


def main():
    items = plan()
    if "--plan" in sys.argv:
        for f, url, rel, web in items:
            print(f"{f}\t{url}\t{web}")
        print(f"\n# {len(items)} images across "
              f"{len({i[0] for i in items})} pages", file=sys.stderr)
        return

    ok = fail = skip = 0
    edits = {}  # html_file -> list of (old_src, web_path)
    for f, url, rel, web in items:
        if os.path.exists(rel):
            skip += 1
            edits.setdefault(f, []).append((url, web))
            continue
        print(f"GET {url}\n -> {rel}")
        if download(url, rel):
            ok += 1
            edits.setdefault(f, []).append((url, web))
        else:
            fail += 1
            print(f"  !! could not fetch; leaving markup unchanged for {rel}")
        time.sleep(THROTTLE_SECONDS)  # be polite to Wikimedia

    for f, pairs in edits.items():
        s = open(f, encoding="utf-8").read()
        orig = s
        for old, web in pairs:
            if os.path.exists(web.lstrip("/")):
                s = s.replace(f'src="{old}"', f'src="{web}"')
        if s != orig:
            open(f, "w", encoding="utf-8").write(s)
            print(f"rewrote {f}")

    print(f"\nDone. downloaded={ok} skipped(existing)={skip} failed={fail}")
    # Don't fail the job on stragglers: commit the progress made and let a
    # re-run pick up the rest (already-downloaded files are skipped). Only fail
    # hard if nothing at all could be fetched while work remained — that signals
    # a systemic problem (blocked host, auth) worth surfacing.
    if fail and ok == 0 and skip == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
