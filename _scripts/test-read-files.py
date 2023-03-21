import os
import re
import numpy as np
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_random_exponential
from tabulate import tabulate

#################################
# MOLECULAR NOTES PREPROCESSING #
#################################

def extract_sections(file_path: str) -> dict[str, str]:
    # For a given markdown note, make a dict mapping headers to content.
    sections = {}
    with open(file_path, "r") as file:
        content = file.read().split("\n")
        section = ""
        sections[section] = ""
        for line in content:
            if line.startswith("##"):
                if sections[section]:
                    section = line.lstrip("#").strip()
                    sections[section] = ""
            else:
                sections[section] += line + "\n"
    return sections


def clean_section(txt: str) -> str:
    # Clean a text block, removing frontmatter, formatting, empty lines.
    # if "#atom" in txt or "#molecule" in txt:
    #     txt = txt.split("---")[0]
    # elif "#source" in txt:
    #     txt = txt.split("---")[1]
    excludes = ["*see", "mocs:", "tags:"]
    for exclude in excludes:
      if exclude in txt:
        return ""

    txt = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", txt)

    repl = ["[[", "]]", "*", "---"]
    for r in repl:
        txt = txt.replace(r, "")
    repl_space = ["\n", "\t", "\xa0", "  "]
    for r in repl_space:
        txt = txt.replace(r, " ")
    txt = txt.replace("\\\\", "\\")

    txt = txt.lstrip().rstrip()
    print(txt)
    return txt


def read_markdown_notes(folder_path: str) -> dict[str, dict[str, str]]:
    # Iterate through vault, making a dictionary of {(filename, chapter): text}
    notes = {}
    for root, dirs, files in os.walk(folder_path):
        # if dirs in [
        #     "_templates",
        #     #"_scripts",
        #     ".obsidian",
        #     ".trash",
        #     "__Canvases",
        #     ".git",
        #     "_attachments",
        #     "media",
        # ]:
        #     continue
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)

                # Filter out topic files
                with open(file_path, "r") as f:
                    md = f.read()
                #if any(x in md for x in ["#topic", "#author"]):
                if any(x in md for x in ["- moc"]):
                    continue

                # Clean files
                sections = extract_sections(file_path)
                for section_id, section_contents in sections.items():
                    cleaned_txt = clean_section(section_contents)
                    if cleaned_txt == "":
                        continue
                    notes[(file_path.lstrip("./"), section_id)] = cleaned_txt
    return notes

read_markdown_notes("./_scripts/test-files/")
