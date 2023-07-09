import os.path
import re
import sys

COLORS = [
    "darkred",
    "red",
    "orange",
    "yellow",
    "lightgreen",
    "green"
]

def create_color_dict(fail_below=5):
    if fail_below > 10:
        raise ValueError("Fail threshold should be below 10")
    step = (10 - fail_below)/(len(COLORS) - 1)
    color_dict = {color:fail_below + itr * step for itr,color in enumerate(COLORS)}
    return color_dict

def get_badge_color(score, color_dict):
    for color, limit in color_dict.items():
        if score <= float(limit):
            return color
    return "darkred"

def get_score(fail_below):
    with open("pylint_score.txt", "r") as f:
        pylint_result = f.read()
    numeric_score = re.search(r"(?<=\s)(\d+\.\d+)\/\d+(?=\s)", pylint_result).group().split("/")[0]

    score = float(numeric_score)
    exit_code = 0
    if score < fail_below:
        exit_code = 1

    os.system(f"echo exit_code={exit_code} >> $GITHUB_OUTPUT")
    return score

def update_badge(readme_file_path, score, badge_color):

    with open(readme_file_path, "r", encoding="utf8") as f:
        content = f.read()

    query = f"pylint-{score:0.02f}-{badge_color}?logo=python&logoColor=white"
    badge_url = f"https://img.shields.io/badge/{query}"
    badge_pattern = r"(?<=!\[pylint]\()(.*?)(?=\))"

    if re.search(badge_pattern, content) is None:
        if content.strip()[0] == "#":
            content = "![pylint]() \n\n" + content
        else:
            content = "![pylint]() " + content

    result = re.sub(badge_pattern, badge_url, content)
    with open(readme_file_path, "w", encoding="utf8") as f:
        f.write(result)

def main(readme_file_path, fail_below):

    fail_below = float(fail_below)
    color_dict = create_color_dict(fail_below)
    score = get_score(fail_below)
    badge_color = get_badge_color(score, color_dict)

    if readme_file_path:
        if not os.path.isfile(readme_file_path):
            raise FileNotFoundError(f"No file can be located at {readme_file_path}")
        
        update_badge(readme_file_path, score, badge_color)

        
if __name__ == "__main__":
    fail_below = sys.argv[1]
    file_path = sys.argv[2]

    if file_path.strip().lower() in ("na", "null", "none"):
        file_path=None

    main(file_path, fail_below)
