import docx
import os
from collections import defaultdict
import re
from pathlib import Path
import numpy as np
from itertools import combinations
import hashlib
from sortedcontainers import SortedList
from zipfile import ZipFile, BadZipFile


def is_valid_docx(file_path):
    """Check if a file is a valid .docx (ZIP) file"""
    try:
        with ZipFile(file_path, 'r') as zipf:
            return True
    except BadZipFile:
        return False


def read_docx(file_path):
    """读取Word文档并返回文本和句子列表"""
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text.append(text)
        return ' '.join(full_text)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def get_ngrams(text, min_chars=5, n=5):
    """生成至少min_chars长度的n-grams"""
    words = text.split()
    ngrams = []
    for i in range(len(words) - n + 1):
        ngram = ' '.join(words[i:i + n])
        if len(ngram) >= min_chars:
            ngrams.append((ngram, i))
    return ngrams


def create_index(doc_texts):
    """创建倒排索引以加速匹配"""
    index = defaultdict(SortedList)
    for doc_name, text in doc_texts.items():
        ngrams = get_ngrams(text)
        for ngram, pos in ngrams:
            ngram_hash = hashlib.md5(ngram.encode()).hexdigest()
            index[ngram_hash].add((doc_name, ngram, pos))
    return index


def find_identical_ngrams(index):
    """找出所有文档中完全相同的n-grams"""
    identical_ngrams = {}
    for ngram_hash, locations in index.items():
        if len(set(loc[0] for loc in locations)) > 1:
            identical_ngrams[ngram_hash] = locations
    return identical_ngrams


def calculate_pairwise_overlap(doc_texts, identical_ngrams):
    """计算两两文档的重合占比"""
    doc_names = list(doc_texts.keys())
    n_docs = len(doc_names)
    overlap_matrix = np.zeros((n_docs, n_docs))

    # 计算每个文档的总n-grams
    doc_ngram_counts = {name: len(get_ngrams(text)) for name, text in doc_texts.items()}
    doc_positions = defaultdict(list)

    for ngram_hash, locations in identical_ngrams.items():
        for doc_name, ngram, pos in locations:
            doc_positions[doc_name].append((ngram, pos))

    for doc1, doc2 in combinations(doc_positions.keys(), 2):
        i = doc_names.index(doc1)
        j = doc_names.index(doc2)
        shared_ngrams = len(doc_positions[doc1])  # Number of shared n-grams
        # Use the average of the two documents' n-gram counts as denominator
        avg_ngrams = (doc_ngram_counts[doc1] + doc_ngram_counts[doc2]) / 2
        if avg_ngrams > 0:
            overlap = (shared_ngrams / avg_ngrams) * 100
            overlap_matrix[i][j] = overlap
            overlap_matrix[j][i] = overlap

    return overlap_matrix, doc_names


def print_overlap_matrix(overlap_matrix, doc_names):
    """打印两两重合占比矩阵"""
    print("\n两两文档重合占比矩阵 (%):")
    print(" " * 20, end="")
    for name in doc_names:
        print(f"{name[:15]:<15}", end=" ")
    print()

    for i, row in enumerate(overlap_matrix):
        print(f"{doc_names[i][:15]:<20}", end=" ")
        for val in row:
            print(f"{val:>6.2f}", end=" ")
        print()


def main(folder_path):
    """主函数"""
    # 获取所有文档的文本
    doc_texts = {}
    for file in Path(folder_path).glob('*.docx'):
        if not is_valid_docx(file):
            print(f"Skipping {file.name}: Not a valid .docx file")
            continue
        text = read_docx(file)
        if text:
            doc_texts[file.name] = text
        else:
            print(f"Skipping {file.name}: Failed to read content")

    if not doc_texts:
        print("No valid .docx files found in the specified folder.")
        return

    # 创建倒排索引
    index = create_index(doc_texts)

    # 找出完全相同的n-grams
    identical_ngrams = find_identical_ngrams(index)

    # 输出相同表述
    print("\n1. 完全相同的表述（至少5个字符）：")
    if identical_ngrams:
        for ngram_hash, locations in identical_ngrams.items():
            ngram = locations[0][1]
            print(f"\n表述: {ngram}")
            for doc_name, _, pos in locations:
                print(f"  - {doc_name} (起始单词位置: {pos})")
    else:
        print("未找到完全相同的表述。")

    # 计算并输出两两重合占比
    overlap_matrix, doc_names = calculate_pairwise_overlap(doc_texts, identical_ngrams)
    print_overlap_matrix(overlap_matrix, doc_names)

    # 计算总重合占比
    total_words = sum(len(text) for text in doc_texts.values())
    # Calculate unique shared words
    identical_length = 0
    for locations in identical_ngrams.values():
        ngram = locations[0][1]  # Get the n-gram text
        identical_length += len(ngram)
    identical_word_count = identical_length
    proportion = (identical_word_count / total_words * 100) if total_words > 0 else 0
    print(f"\n2. 完全相同表述的总体占比: {proportion:.2f}%")


if __name__ == "__main__":
    folder_path = r"/home/woody/aid/woodpecker/sample_doc/docx"  # 替换为实际路径
    main(folder_path)