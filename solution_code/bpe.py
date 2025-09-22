"""
Byte Pair Encoding
Broad logic: Iteratively replace the most frequent pairs of bytes with a single unused index

Steps:
1. Vocabulary initialization: In this case - set of all bytes = 256 initially
2. Pretokenization: Coarse grained tokenization over the corpus
(Why do we need to do this?): 1) Computationally expensive to just count over the corpus; 2) Similar tokens will get a different id because of minor differences like punctuations
Logic: split by regex patterns (simplest is split by whitespace). Count pairs of bytes within pre-tokenized words and aggregate
3. Compute BPE merges: 
    3a. Iteratively count every pair of bytes
    3b. Identify highest frequency pair
    3c. Merge it and map it to new token in the vocab (256 + 1 + 1...max_vocab_size)

Additional considerations:
I) For efficiency don't consider pairs that cross pre-token boundaries
II) To break ties prefer lexicographically greater pair
III) Add special tokens to vocab ids - <|endoftext|> token, etc.

Algorithmic Steps
1. Vocabulary Initialization: Set initial vocabulary as a mapping of bytestring token to integer_id
2. Pretokenize and Count: Split by regex and special tokens
"""
import regex as re
from collections import Counter
import time

# Step 1: vocab initialization
vocab = {bytes([i]): i for i in range(256)}
vocab['<|endoftext|>'] = 256

# Step 2: Pretokenize and Count

def remove_special_token(input_text, special_token='<|endoftext|>'):
    combined_text = " ".join(input_text.split(special_token))
    return combined_text

def pretokenize_regex(input_text, PAT=r"'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"):
    freq_map = Counter(re.findall(PAT, input_text))
    return freq_map

def split_to_bytes(input_word):
    encoded_input = input_word.encode('utf-8')
    return tuple(bytes([b]) for b in encoded_input)


# Step 3: Combine most common pairs

def merge_most_common(tuple_dict):
    byte_pair_count = Counter()

    for byte_pair, freq in tuple_dict.items():
        if len(byte_pair) == 1:
            continue
        for a, b in zip(byte_pair, byte_pair[1:]):
            byte_pair_count[(a,b)] += freq

    # No pairs to merge
    if not byte_pair_count:
        return tuple_dict, None, None
    
    max_freq = max(byte_pair_count.values())
    candidates = [pair for pair, count in byte_pair_count.items() if count == max_freq]
    a, b = max(candidates)  # Lexicographically largest
    merged_byte_pair = a + b

    merged_tuple_dict = {}
    for byte_pair, freq in tuple_dict.items():
        if len(byte_pair) == 1:
            merged_tuple_dict[byte_pair] = merged_tuple_dict.get(byte_pair, 0) + freq
            continue

        out = []
        i = 0
        for j in range(len(byte_pair)):
            if i != j:
                continue
            if j < len(byte_pair) - 1 and byte_pair[j] == a and byte_pair[j+1] == b:
                out.append(merged_byte_pair)
                i = j + 2
            else:
                out.append(byte_pair[j])
                i = j + 1
        
        merged_tuple_dict[tuple(out)] = merged_tuple_dict.get(tuple(out), 0) + freq
        
    return merged_tuple_dict, (a, b), merged_byte_pair

# Clean up functions

def extract_vocab(tuple_dict): 
    vocab = set()
    for token_tuple in tuple_dict.keys():
        for token in token_tuple:
            vocab.add(token)
    return vocab

if __name__ == "__main__":


    # example_text = """low low low low low lower lower widest widest widest <|endoftext|> newest newest newest newest newest newest"""
    with open("data/TinyStoriesV2-GPT4-train.txt", "r", encoding="utf-8") as f:
        example_text = f.read()

    # cleaned_text = remove_special_token(example_text)
    text_chunks = example_text.split('<|endoftext|>')

    total_word_count = Counter()
    for text_chunk in text_chunks:
        total_word_count.update(pretokenize_regex(text_chunk))
        
    tuple_dict = {}
    for word, freq in total_word_count.items():
        tuple_dict[split_to_bytes(word)] = freq

    # print("Original Tuple Dict: ", tuple_dict)
    print("Original vocab: ", extract_vocab(tuple_dict), "\n")
    iterations = 0
    merged_tuple_dict = tuple_dict

    start = time.time()
    print("Starting merges...")
    while iterations < 10000:
        merged_tuple_dict, best_pair, merged_bytes = merge_most_common(merged_tuple_dict)
        iterations += 1

    print("Updated vocab: ", extract_vocab(merged_tuple_dict))

    end = time.time()
    print(f"Time taken for 10,000 merges: {end - start} seconds")


