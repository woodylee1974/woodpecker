import os.path
import json
from collections import defaultdict
from itertools import combinations
from utils.file_man import collect_pdf_files
from utils.find_position import find_index_by_value


def find_exact_same_segments(paragraphs, min_len=4):
    """
    Finds all maximal exact-same segments (at least min_len Chinese characters)
    across multiple Chinese paragraphs. A segment is maximal if it's not a
    substring of another identified exact-same segment.

    Args:
        paragraphs: A list of strings, where each string is a Chinese paragraph.
        min_len: The minimum length of the exact-same segment to consider.

    Returns:
        A dictionary where keys are the maximal exact-same segments (strings) and
        values are lists of tuples. Each tuple represents an occurrence of the segment
        in a paragraph and contains:
            - paragraph_index: The index of the paragraph (0-based).
            - start_index: The starting index of the segment within the paragraph.
            - ratio: The length of the segment divided by the total length of the paragraph.
    """
    n = len(paragraphs)
    if n < 2:
        return {}

    combined_text = ""
    paragraph_indices = []
    paragraph_lengths = [len(p) for p in paragraphs]
    for i, para in enumerate(paragraphs):
        combined_text += para + chr(1)  # Use a unique separator not in Chinese
        paragraph_indices.extend([i] * (len(para) + 1))

    suffix_array = sorted(range(len(combined_text)), key=combined_text.__getitem__)

    lcp_array = [0] * len(combined_text)
    for i in range(1, len(combined_text)):
        lcp_array[i] = longest_common_prefix_length(
            combined_text, suffix_array[i - 1], suffix_array[i]
        )

    potential_segments = []
    for i in range(1, len(lcp_array)):
        if lcp_array[i] >= min_len:
            segment = combined_text[
                suffix_array[i] : suffix_array[i] + lcp_array[i]
            ]
            para_index1 = paragraph_indices[suffix_array[i - 1]]
            start_index1 = suffix_array[i - 1] - sum(paragraph_lengths[k] + 1 for k in range(para_index1))
            ratio1 = len(segment) / paragraph_lengths[para_index1]

            para_index2 = paragraph_indices[suffix_array[i]]
            start_index2 = suffix_array[i] - sum(paragraph_lengths[k] + 1 for k in range(para_index2))
            ratio2 = len(segment) / paragraph_lengths[para_index2]

            if para_index1 != para_index2:
                potential_segments.append(
                    (segment, (para_index1, start_index1, ratio1), (para_index2, start_index2, ratio2))
                )

    maximal_segments = {}
    processed_segments = set()

    # Sort potential segments by length in descending order
    potential_segments.sort(key=lambda x: len(x[0]), reverse=True)

    for segment, occurrence1, occurrence2 in potential_segments:
        if segment in processed_segments:
            continue

        if segment not in maximal_segments:
            maximal_segments[segment] = []

        maximal_segments[segment].append(occurrence1)
        maximal_segments[segment].append(occurrence2)
        processed_segments.add(segment)

        # Mark all substrings of the current segment as processed
        for i in range(1, len(segment)):
            for j in range(len(segment) - i + 1):
                processed_segments.add(segment[j : j + i])

    # Remove duplicate occurrences
    for segment in maximal_segments:
        unique_occurrences = []
        seen = set()
        for occurrence in maximal_segments[segment]:
            if (occurrence[0], occurrence[1]) not in seen:
                unique_occurrences.append(occurrence)
                seen.add((occurrence[0], occurrence[1]))
        maximal_segments[segment] = unique_occurrences

    return {k: v for k, v in maximal_segments.items() if len(v) > 1}


def longest_common_prefix_length(text, i, j):
    """Calculates the length of the longest common prefix of text[i:] and text[j:]"""
    length = 0
    while i < len(text) and j < len(text) and text[i] == text[j]:
        length += 1
        i += 1
        j += 1
    return length


def find_exact_same_substrings():
    pdf_files = collect_pdf_files()
    text_infos = []
    for pdf_file, scaned_file in pdf_files:
        if os.path.exists(scaned_file):
            metadata = {}
            with open(scaned_file, 'r', encoding='utf-8') as json_file:
                json_repr = json.load(json_file)
                text = ''
                start = 0
                for text_block in json_repr['metadata']['text_block']:
                    if text_block['type'] == 'text':
                        text += text_block['text']
                        metadata[start] = text_block
                        start += len(text_block['text'])
                text_infos.append({
                    "text": text,
                    "filename": pdf_file,
                    "metadata": metadata.copy()
                })

    paragraphs = [t['text'] for t in text_infos]
    exact_same_segments = find_exact_same_segments(paragraphs)
    results = defaultdict(list)
    matrix = {}
    relations = {}
    for pdf_file, _ in pdf_files:
        matrix[pdf_file] = {
            filename: 0.0 for filename, _ in pdf_files
        }
        relations[pdf_file] = {
            filename: [] for filename, _ in pdf_files
        }

    for segment, occurrences in exact_same_segments.items():
        print(f"Maximal exact-same segment: '{segment}'")
        for para_index, start_index, ratio in occurrences:
            print(f"  - Paragraph {para_index}, Start: {start_index}, Ratio: {ratio:.4f}")
            metadata = text_infos[para_index]['metadata']
            position = find_index_by_value(metadata.keys(), start_index)
            pdf_file = text_infos[para_index]['filename']
            results[segment].append((pdf_file, metadata[position], start_index - position, ratio))

        for occurrent1, occurrent2 in combinations(results[segment], 2):
            matrix[occurrent1[0]][occurrent2[0]] += occurrent1[3]
            matrix[occurrent2[0]][occurrent1[0]] += occurrent2[3]
            relations[occurrent1[0]][occurrent2[0]].append((segment, occurrent1[1], occurrent2[1], occurrent1[3]))
            relations[occurrent2[0]][occurrent1[0]].append((segment, occurrent2[1], occurrent1[1], occurrent2[3]))

    return {
        "same_segments": results,
        "ratio_matrix": matrix,
        "relation_matrix": relations
    }


if __name__ == '__main__':
    # Example Usage:
    # paragraphs = [
    #     "这是一个包含相同片段的第一个中文段落，相同的片段是世界你好。",
    #     "这是第二个中文段落，也包含相同的片段世界你好，你好世界。",
    #     "第三个段落内容不同，没有任何相同的。",
    #     "第四个段落又出现了相同的片段世界你好，你好吗？"
    # ]
    #
    # result = find_exact_same_segments(paragraphs)
    # for segment, occurrences in result.items():
    #     print(f"Maximal exact-same segment: '{segment}'")
    #     for para_index, start_index, ratio in occurrences:
    #         print(f"  - Paragraph {para_index}, Start: {start_index}, Ratio: {ratio:.4f}")
    #     print("-" * 30)



    result = find_exact_same_substrings()
    # for segment, _ in result['same_segments'].items():
    #     print(segment)

    # print(result['relation_matrix'])