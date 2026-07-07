import re


def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.readlines()


def write_txt(file_path, lines):
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


# Remove duplicate lines
def remove_duplicates(lines):
    seen = set()
    result = []

    for line in lines:
        if line not in seen:
            seen.add(line)
            result.append(line)

    return result


# Replace text or link
def replace_text(lines, old, new):
    return [line.replace(old, new) for line in lines]


# Remove lines containing a word/link
def filter_text(lines, keyword):
    return [line for line in lines if keyword not in line]


# Compress (remove empty lines)
def compress_txt(lines):
    return [line.strip() + "\n" for line in lines if line.strip()]


# Sort lines
def sort_lines(lines):
    return sorted(lines)


# Reverse lines
def reverse_lines(lines):
    return list(reversed(lines))


# Add prefix
def add_prefix(lines, prefix):
    return [prefix + line for line in lines]


# Add suffix
def add_suffix(lines, suffix):
    output = []

    for line in lines:
        line = line.rstrip("\n")
        output.append(line + suffix + "\n")

    return output


# Find lines containing keyword
def find_lines(lines, keyword):
    return [line for line in lines if keyword in line]


# Count lines
def line_count(lines):
    return len(lines)


# Remove blank lines
def remove_blank(lines):
    return [line for line in lines if line.strip()]


# Remove URLs
def remove_urls(lines):
    regex = r"https?://\S+|www\.\S+"

    output = []

    for line in lines:
        newline = re.sub(regex, "", line)
        if newline.strip():
            output.append(newline)

    return output


# Keep only URLs
def extract_urls(lines):
    regex = r"https?://\S+|www\.\S+"

    output = []

    for line in lines:
        urls = re.findall(regex, line)
        output.extend(url + "\n" for url in urls)

    return output