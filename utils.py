import os

def read_txt(file_path):
    """
    Read txt file and return clean non-empty lines.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


def compare_txt(old_file, new_file, output_file):
    """
    Compare old and new txt files.
    Save only new unique lines in output_file.
    """

    old_lines = set(read_txt(old_file))
    new_lines = read_txt(new_file)

    unique = []
    seen = set()

    for line in new_lines:
        if line not in old_lines and line not in seen:
            unique.append(line)
            seen.add(line)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(unique))

    return {
        "old": len(old_lines),
        "new": len(new_lines),
        "unique": len(unique),
        "output": output_file
    }