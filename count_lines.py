import requests
import subprocess
import os
import tempfile
from collections import defaultdict

GITHUB_USERNAME = os.getenv("GITHUB_ACTOR")  # автоматически подставится
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

EXT_TO_LANG = {
    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".jsx": "JavaScript", ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".go": "Go", ".c": "C", ".cpp": "C++", ".h": "C/C++ Header", ".hpp": "C++ Header",
    ".rs": "Rust", ".swift": "Swift", ".rb": "Ruby", ".php": "PHP", ".cs": "C#",
    ".scala": "Scala", ".sh": "Shell", ".pl": "Perl", ".lua": "Lua", ".R": "R",
    ".m": "MATLAB/Objective-C", ".hs": "Haskell"
}

headers = {"Authorization": f"token {GITHUB_TOKEN}"}
repos_url = f"https://api.github.com/users/{GITHUB_USERNAME}/repos?per_page=100"
repos = requests.get(repos_url, headers=headers).json()

total_lines = 0
lang_stats = defaultdict(int)

for repo in repos:
    repo_name = repo["name"]
    clone_url = repo["clone_url"]

    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = os.path.join(tmpdir, repo_name)
        subprocess.run(["git", "clone", "--depth", "1", clone_url, repo_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for root, dirs, files in os.walk(repo_path):
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in EXT_TO_LANG:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", errors="ignore") as f:
                            lines = sum(1 for _ in f)
                            total_lines += lines
                            lang_stats[EXT_TO_LANG[ext]] += lines
                    except Exception:
                        pass

with open("stats.md", "w", encoding="utf-8") as f:
    f.write(f"## 📊 Статистика по коду\n\n")
    f.write(f"**Всего строк кода:** {total_lines}\n\n")
    f.write("| Язык | Строки |\n")
    f.write("|------|--------|\n")
    for lang, lines in sorted(lang_stats.items(), key=lambda x: x[1], reverse=True):
        f.write(f"| {lang} | {lines} |\n")
