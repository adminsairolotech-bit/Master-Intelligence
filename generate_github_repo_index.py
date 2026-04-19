import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ACCOUNT = "adminsairolotech-bit"


REPO_ALIASES = {
    "sai-rolotech-cloud-code-extension": "sai-rolotech-cloud-code-extension-20260419",
}


CATEGORY_TITLES = {
    "ai-agents": "AI Agents & Automation",
    "ai-tools": "AI Tools & Extensions",
    "dev-tools": "Developer Tools & Repo Intelligence",
    "engineering": "CAD, Roll Forming & Engineering",
    "automation": "Automation & Infrastructure",
    "business": "Business, CRM & Portfolios",
    "web-design": "Web, UI & Design",
    "research-security": "Research & Security",
    "archive-profile": "Archive, Profile & Misc",
}


def ascii_text(value):
    if value is None:
        return ""
    text = str(value)
    replacements = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u00a0": " ",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("ascii", "ignore").decode("ascii").strip()


def canonical_name(name, url=""):
    clean_name = ascii_text(name)
    clean_url = str(url or "").strip()
    if clean_url.startswith(f"https://github.com/{ACCOUNT}/"):
        url_tail = clean_url.rstrip("/").split("/")[-1]
        if url_tail:
            clean_name = url_tail
    return REPO_ALIASES.get(clean_name, clean_name)


def canonical_repo_url(name, url=""):
    clean_url = str(url or "").strip()
    clean_name = canonical_name(name, clean_url)
    if clean_url.startswith(f"https://github.com/{ACCOUNT}/") or not clean_url:
        return f"https://github.com/{ACCOUNT}/{clean_name}"
    return clean_url


NAME_CATEGORY_OVERRIDES = {
    "adminsairolotech-bit": "archive-profile",
    "adminsairolotech-bit-ultimate-archive": "archive-profile",
    "Master-Intelligence": "ai-agents",
    "GitNexus": "dev-tools",
    "Code-Fixer": "dev-tools",
    "reposcope-app": "dev-tools",
    "cc-cache-fix": "dev-tools",
    "test-token-check": "dev-tools",
    "plugin-samples": "dev-tools",
    "byte-buddy": "dev-tools",
    "crm-2": "business",
    "developer-portfolios": "business",
    "sai-rolotech-autocad": "engineering",
    "sai-rolotech-smart-engines": "engineering",
    "HowickMaker-for-Dynamo": "engineering",
    "sai-rolotech-n8n": "automation",
    "sai-rolotech-laptop-control-app": "automation",
    "computer-agent": "automation",
    "cirrus": "automation",
    "openclaw.ai": "web-design",
    "openclaw.ai-NEW-": "web-design",
    "ui-ux-pro-max-skill": "web-design",
    "multi-ai-system_prompts_leaks": "research-security",
    "HowToHunt": "research-security",
    "kagglehub": "research-security",
    "sora2API": "ai-tools",
    "elevenlabs-python": "ai-tools",
    "sai-rolotech-prompts": "ai-tools",
    "sai-rolotech-cloud-code-extension-20260419": "ai-tools",
    "claude-mem": "ai-tools",
    "claude-opus-4.6-offline": "ai-tools",
    "everything-claude-code": "ai-tools",
    "awesome-claude-code": "ai-tools",
    "second-brain-skills": "ai-tools",
    "oh-my-codex": "ai-tools",
    "sai-rolotech-openclaw": "ai-agents",
    "sai-rolotech-pro-ai": "ai-agents",
    "BUDDY-AUTO-MODE": "ai-agents",
    "buddy-automation-suite": "ai-agents",
    "agents": "ai-agents",
    "awesome-claude-code-subagents": "ai-agents",
    "open-multi-agent": "ai-agents",
    "cloude-ai-agiant-superpowers": "ai-agents",
    "super-pro": "ai-agents",
}


def load_json(path: str, default):
    file_path = ROOT / path
    if not file_path.exists():
        return default
    try:
        return json.loads(file_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return default


def normalize_date(value):
    if not value:
        return ""
    text = str(value)
    if "T" in text:
        return text.split("T", 1)[0]
    return text[:10]


def normalize_visibility(value):
    if not value:
        return "unknown"
    return str(value).lower()


def infer_category(name, description="", language="", fallback="archive-profile"):
    if name in NAME_CATEGORY_OVERRIDES:
        return NAME_CATEGORY_OVERRIDES[name]

    text = f"{name} {description or ''} {language or ''}".lower()
    if any(key in text for key in ["autocad", "cad", "cnc", "roll", "dynamo"]):
        return "engineering"
    if any(key in text for key in ["crm", "portfolio", "business"]):
        return "business"
    if any(key in text for key in ["security", "hunt", "prompt_leaks", "research", "kaggle"]):
        return "research-security"
    if any(key in text for key in ["figma", "ui", "ux", "website", "web", "design"]):
        return "web-design"
    if any(key in text for key in ["n8n", "automation", "laptop", "cloudflare", "worker"]):
        return "automation"
    if any(key in text for key in ["repo", "git", "code-fixer", "plugin", "token", "cache"]):
        return "dev-tools"
    if any(key in text for key in ["agent", "openclaw", "buddy", "multi-agent", "superpowers"]):
        return "ai-agents"
    if any(key in text for key in ["claude", "codex", "skill", "prompt", "sora", "elevenlabs", "ai"]):
        return "ai-tools"
    return fallback


def parse_markdown_tables():
    md_path = ROOT / "REPOS_BY_CATEGORY.md"
    rows = {}
    if not md_path.exists():
        return rows

    pattern = re.compile(
        r"^\|\s*(?P<stars>\d+)\s*\|\s*(?P<created>[^|]+)\|\s*(?P<updated>[^|]+)\|"
        r"\s*\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\s*\|\s*(?P<description>[^|]*)\|"
        r"\s*(?P<language>[^|]*)\|\s*(?P<status>[^|]+)\|"
    )
    for line in md_path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        match = pattern.match(line.strip())
        if not match:
            continue
        data = {key: value.strip() for key, value in match.groupdict().items()}
        name = canonical_name(data["name"], data["url"])
        rows[name] = {
            "name": name,
            "url": canonical_repo_url(name, data["url"]),
            "description": "" if data["description"] == "-" else ascii_text(data["description"]),
            "language": "" if data["language"] == "-" else ascii_text(data["language"]),
            "visibility": normalize_visibility(data["status"]),
            "created_at": data["created"],
            "updated_at": data["updated"],
            "stars": int(data["stars"]),
            "source": "local-markdown",
        }
    return rows


def merge_repos():
    public_repos = load_json("github_public_repos_enriched.json", [])
    local_snapshot = load_json("repos_by_category.json", {}).get("repos", [])
    markdown_rows = parse_markdown_tables()

    merged = {}

    def ensure(name, url=""):
        name = canonical_name(name, url)
        if name not in merged:
            merged[name] = {
                "name": name,
                "url": canonical_repo_url(name, url),
                "description": "",
                "language": "",
                "visibility": "unknown",
                "created_at": "",
                "updated_at": "",
                "pushed_at": "",
                "your_stars": 0,
                "forks": 0,
                "is_fork": False,
                "parent_full_name": "",
                "parent_url": "",
                "parent_stars": 0,
                "category": "archive-profile",
                "source": "local",
            }
        return merged[name]

    for row in markdown_rows.values():
        repo = ensure(row["name"], row.get("url"))
        repo.update(
            {
                "url": canonical_repo_url(row["name"], row["url"]),
                "description": row["description"],
                "language": row["language"],
                "visibility": row["visibility"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "your_stars": row["stars"],
                "source": row["source"],
            }
        )

    for item in local_snapshot:
        name = canonical_name(item.get("name"), item.get("url"))
        if not name:
            continue
        repo = ensure(name, item.get("url"))
        repo["description"] = item.get("description") or repo["description"]
        repo["description"] = ascii_text(repo["description"])
        repo["language"] = ascii_text(item.get("language") or repo["language"])
        repo["visibility"] = normalize_visibility(item.get("status") or repo["visibility"])
        repo["created_at"] = item.get("created") or repo["created_at"]
        repo["updated_at"] = item.get("updated") or repo["updated_at"]
        repo["your_stars"] = int(item.get("stars") or repo["your_stars"] or 0)
        repo["is_fork"] = bool(item.get("is_fork", repo["is_fork"]))
        repo["category"] = item.get("category") or repo["category"]
        repo["source"] = "local-json"

    for item in public_repos:
        name = canonical_name(item.get("name"), item.get("html_url"))
        if not name:
            continue
        repo = ensure(name, item.get("html_url"))
        repo.update(
            {
                "url": item.get("html_url") or repo["url"],
                "description": ascii_text(item.get("description") or repo["description"]),
                "language": ascii_text(item.get("language") or ""),
                "visibility": normalize_visibility(item.get("visibility") or repo["visibility"]),
                "created_at": normalize_date(item.get("created_at")) or repo["created_at"],
                "updated_at": normalize_date(item.get("updated_at")) or repo["updated_at"],
                "pushed_at": normalize_date(item.get("pushed_at")) or repo["pushed_at"],
                "your_stars": int(item.get("stargazers_count") or 0),
                "forks": int(item.get("forks_count") or 0),
                "is_fork": bool(item.get("fork")),
                "parent_full_name": item.get("parent_full_name") or "",
                "parent_url": item.get("parent_url") or "",
                "parent_stars": int(item.get("parent_stars") or 0),
                "source": "github-public-api",
            }
        )

    for repo in merged.values():
        repo["category"] = infer_category(
            repo["name"],
            repo.get("description", ""),
            repo.get("language", ""),
            repo.get("category") or "archive-profile",
        )
        repo["created_at"] = normalize_date(repo.get("created_at"))
        repo["updated_at"] = normalize_date(repo.get("updated_at"))
        repo["visibility"] = normalize_visibility(repo.get("visibility"))

    return list(merged.values())


def sort_original(repo):
    return (
        -repo["your_stars"],
        -int((repo.get("updated_at") or "0000-00-00").replace("-", "") or 0),
        repo["name"].lower(),
    )


def sort_fork(repo):
    return (
        -repo["parent_stars"],
        -repo["your_stars"],
        -int((repo.get("updated_at") or "0000-00-00").replace("-", "") or 0),
        repo["name"].lower(),
    )


def group_by_category(repos):
    grouped = defaultdict(list)
    for repo in repos:
        grouped[repo["category"]].append(repo)
    return grouped


def md_link(label, url):
    return f"[{label}]({url})" if url else label


def table_for_originals(rows):
    lines = [
        "| Stars | Updated | Repo | Description | Lang | Visibility | Source |",
        "|---:|---|---|---|---|---|---|",
    ]
    for repo in sorted(rows, key=sort_original, reverse=False):
        lines.append(
            "| {stars} | {updated} | {repo} | {desc} | {lang} | {visibility} | {source} |".format(
                stars=repo["your_stars"],
                updated=repo.get("updated_at") or "-",
                repo=md_link(repo["name"], repo["url"]),
                desc=(ascii_text(repo.get("description")) or "-").replace("|", "/"),
                lang=repo.get("language") or "-",
                visibility=repo.get("visibility") or "-",
                source=repo.get("source") or "-",
            )
        )
    return lines


def table_for_forks(rows):
    lines = [
        "| Upstream Stars | Your Stars | Updated | Fork Repo | Upstream | Description | Lang | Visibility | Source |",
        "|---:|---:|---|---|---|---|---|---|---|",
    ]
    for repo in sorted(rows, key=sort_fork, reverse=False):
        upstream = (
            md_link(repo["parent_full_name"], repo["parent_url"])
            if repo.get("parent_full_name")
            else "-"
        )
        lines.append(
            "| {parent_stars} | {stars} | {updated} | {repo} | {upstream} | {desc} | {lang} | {visibility} | {source} |".format(
                parent_stars=repo["parent_stars"],
                stars=repo["your_stars"],
                updated=repo.get("updated_at") or "-",
                repo=md_link(repo["name"], repo["url"]),
                upstream=upstream,
                desc=(ascii_text(repo.get("description")) or "-").replace("|", "/"),
                lang=repo.get("language") or "-",
                visibility=repo.get("visibility") or "-",
                source=repo.get("source") or "-",
            )
        )
    return lines


def render_markdown(repos):
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    originals = [repo for repo in repos if not repo["is_fork"]]
    forks = [repo for repo in repos if repo["is_fork"]]
    live_public = [repo for repo in repos if repo["source"] == "github-public-api"]
    local_only = [repo for repo in repos if repo["source"] != "github-public-api"]

    lines = [
        "# SAI Rolotech GitHub Repos - Organized",
        "",
        f"> Generated: {generated_at}",
        f"> Account: @{ACCOUNT}",
        f"> Named repos in index: {len(repos)}",
        f"> Live public repos fetched from GitHub API: {len(live_public)}",
        f"> Local snapshot-only repos: {len(local_only)}",
        "",
        "Note: GitHub CLI auth is currently invalid on this PC, so private repositories cannot be refreshed live. Local snapshot-only rows are preserved from the existing local files.",
        "",
        "## Summary",
        "",
        "| Group | Count | Stars Used For Sorting |",
        "|---|---:|---|",
        f"| Sai Rolotech Originals (non-fork) | {len(originals)} | Your repo stars |",
        f"| Forked Repos | {len(forks)} | Upstream stars first, then your fork stars |",
        f"| Live Public API Rows | {len(live_public)} | Current GitHub public data |",
        f"| Local Snapshot Only Rows | {len(local_only)} | Existing local data; may be private, renamed, or deleted |",
        "",
        "## Sai Rolotech Originals",
        "",
    ]

    grouped_originals = group_by_category(originals)
    for category in CATEGORY_TITLES:
        rows = grouped_originals.get(category, [])
        if not rows:
            continue
        lines.extend([f"### {CATEGORY_TITLES[category]}", ""])
        lines.extend(table_for_originals(rows))
        lines.append("")

    lines.extend(["## Forked Repos", ""])
    grouped_forks = group_by_category(forks)
    for category in CATEGORY_TITLES:
        rows = grouped_forks.get(category, [])
        if not rows:
            continue
        lines.extend([f"### {CATEGORY_TITLES[category]}", ""])
        lines.extend(table_for_forks(rows))
        lines.append("")

    lines.extend(
        [
            "## Local Snapshot Only",
            "",
            "These names were present in local files but were not visible in the unauthenticated public GitHub API fetch.",
            "",
            "| Repo | Category | Visibility | Last Known Updated | Source |",
            "|---|---|---|---|---|",
        ]
    )
    for repo in sorted(local_only, key=lambda item: (item["category"], item["name"].lower())):
        lines.append(
            f"| {md_link(repo['name'], repo['url'])} | {CATEGORY_TITLES.get(repo['category'], repo['category'])} | {repo.get('visibility') or '-'} | {repo.get('updated_at') or '-'} | {repo.get('source') or '-'} |"
        )

    lines.append("")
    return "\n".join(lines)


def write_outputs(repos):
    originals = [repo for repo in repos if not repo["is_fork"]]
    forks = [repo for repo in repos if repo["is_fork"]]
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "account": ACCOUNT,
        "counts": {
            "total_named": len(repos),
            "originals": len(originals),
            "forks": len(forks),
            "live_public_api": sum(1 for repo in repos if repo["source"] == "github-public-api"),
            "local_snapshot_only": sum(1 for repo in repos if repo["source"] != "github-public-api"),
        },
        "categories": CATEGORY_TITLES,
        "repos": sorted(repos, key=lambda repo: (repo["is_fork"], repo["category"], repo["name"].lower())),
    }
    (ROOT / "repos_by_category.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    markdown = render_markdown(repos)
    (ROOT / "REPOS_BY_CATEGORY.md").write_text(markdown, encoding="utf-8")
    (ROOT / "GITHUB_REPOS_ORGANIZED.md").write_text(markdown, encoding="utf-8")


def main():
    repos = merge_repos()
    write_outputs(repos)
    originals = sum(1 for repo in repos if not repo["is_fork"])
    forks = sum(1 for repo in repos if repo["is_fork"])
    live = sum(1 for repo in repos if repo["source"] == "github-public-api")
    local = len(repos) - live
    print(
        f"Generated repo index: total={len(repos)} originals={originals} forks={forks} live_public={live} local_snapshot_only={local}"
    )


if __name__ == "__main__":
    main()
