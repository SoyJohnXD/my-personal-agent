TAG_PREFIX = "#"


def format_tags(tags: list[str]) -> str:
    result = []

    for tag in tags:
        clean_tag = tag.lower().strip()
        format_tag = f"{TAG_PREFIX}{clean_tag}"
        result.append(format_tag)

    return "".join(result)


def merge_tags(comparison_tags: str, new_tags: list[str]) -> str:
    comparison_tags_array = []
    if comparison_tags:
        parts = comparison_tags.split(TAG_PREFIX)
        for part in parts:
            if part:
                comparison_tags_array.append(f"{TAG_PREFIX}{part}")

    for tag in new_tags:
        clean_tag = tag.lower().strip()
        formated_tag = f"{TAG_PREFIX}{clean_tag}"
        if formated_tag not in comparison_tags_array:
            comparison_tags_array.append(formated_tag)

    return "".join(comparison_tags_array)
