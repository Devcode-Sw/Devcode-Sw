import requests
import os
import re

USERNAME = os.environ.get("GITHUB_USERNAME", "Devcode-Sw")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Cores e emojis por linguagem
LANG_STYLE = {
    "HTML":       {"emoji": "🟠", "color": "#E34F26"},
    "CSS":        {"emoji": "🔵", "color": "#1572B6"},
    "JavaScript": {"emoji": "🟡", "color": "#F7DF1E"},
    "TypeScript": {"emoji": "🔷", "color": "#3178C6"},
    "Java":       {"emoji": "🔴", "color": "#ED8B00"},
    "Python":     {"emoji": "🐍", "color": "#3776AB"},
    "Shell":      {"emoji": "⚫", "color": "#89E051"},
    "Dockerfile": {"emoji": "🐳", "color": "#2496ED"},
    "YAML":       {"emoji": "⚙️",  "color": "#CB171E"},
}

def get_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else []

def get_languages(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else {}

def make_bar(percent, length=20):
    filled = round((percent / 100) * length)
    return "█" * filled + "░" * (length - filled)

def build_section(repos):
    if not repos:
        return "_Nenhum repositório encontrado ainda. Crie seu primeiro projeto!_\n"

    lines = []
    for repo in repos:
        name = repo.get("name", "")
        desc = repo.get("description") or "_Sem descrição_"
        url  = repo.get("html_url", "")
        langs_raw = get_languages(name)

        if not langs_raw:
            continue

        total = sum(langs_raw.values())
        langs_pct = {k: round((v / total) * 100, 1) for k, v in langs_raw.items()}

        # Cabeçalho do repo
        lines.append(f"### 📁 [`{name}`]({url})")
        lines.append(f"> {desc}\n")
        lines.append("| Linguagem | % | Progresso |")
        lines.append("|:----------|:---:|:----------|")

        summary_parts = []
        for lang, pct in sorted(langs_pct.items(), key=lambda x: -x[1]):
            style = LANG_STYLE.get(lang, {"emoji": "⚪"})
            emoji = style["emoji"]
            bar = make_bar(pct)
            lines.append(f"| {emoji} {lang} | {pct}% | `{bar}` |")
            summary_parts.append(f"**{pct}% {lang}**")

        summary = " + ".join(summary_parts)
        lines.append(f"\n> 💡 *Wênio criou `{name}` usando: {summary}*\n")
        lines.append("---\n")

    return "\n".join(lines)

def update_readme(new_section):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Substitui o bloco entre os marcadores
    pattern = r"(<!-- TERMOMETRO:START -->).*?(<!-- TERMOMETRO:END -->)"
    replacement = f"<!-- TERMOMETRO:START -->\n{new_section}\n<!-- TERMOMETRO:END -->"
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

    print("✅ README.md atualizado com sucesso!")

if __name__ == "__main__":
    print(f"🔍 Buscando repositórios de {USERNAME}...")
    repos = get_repos()
    # Filtra repo de perfil e repos vazios/forks
    repos = [r for r in repos if not r.get("fork") and r["name"] != USERNAME]
    print(f"📦 {len(repos)} repositórios encontrados.")
    section = build_section(repos)
    update_readme(section)
