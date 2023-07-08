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

    exit_code = 0
    if numeric_score < fail_below:
        exit_code = 1

    os.system("echo exit_code=" + exit_code + " >> $GITHUB_OUTPUT")
    return numeric_score

def update_badge(readme_file_path, fail_below):

    color_dict = create_color_dict(fail_below)
    score = get_score(fail_below)
    badge_color = get_badge_color(score, color_dict)

    if not os.path.isfile(readme_file_path):
        raise FileNotFoundError(f"README.md path is wrong, no file can be located at {readme_file_path}")

    with open(readme_file_path, "r", encoding="utf8") as f:
        content = f.read()

    query = f"pylint-{score:0.02f}-{badge_color}?logo=python&logoColor=white"
    badge_url = f"https://img.shields.io/badge/{query}"
    badge_pattern = r"(?<=!\[pylint]\()(.*?)(?=\))"

    if re.search(badge_pattern, content) is None:
        content_split = content.split("\n")
        # add badge in 2nd line
        content_split[1] = "![pylint]() " + content_split[1] 
        content = "\n".join(content_split)

    result = re.sub(badge_pattern, badge_url, content)
    with open(readme_file_path, "w", encoding="utf8") as f:
        f.write(result)

if __name__ == "__main__":
    input_args = sys.argv[1:]
    if len(input_args) < 1:
        raise AttributeError("readme file path is required.")
    file_path = input_args[0]
    if len(input_args)>1:
        fail_below = input_args[2]
    update_badge(file_path, fail_below)
