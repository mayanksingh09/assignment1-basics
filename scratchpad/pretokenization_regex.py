import regex as re

def pretokenize_regex(input_text, PAT=r"""'(?:[sdmt]|ll|ve|re)| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""):
    tokenized_text = re.findall(PAT, input_text)
    # tokenized_text = re.finditer(PAT, input_text)
    return tokenized_text


if __name__ == "__main__":
    sentences_to_tokenize = ["some text that I'll pre-tokenize", "hello there, how are you?", "˙˚˙ßå∂œ∑ˆ∑´œçß∑ßß"]

    for text in sentences_to_tokenize:
        print("Original Text: ", text)
        print("Pretokenized Text: ", pretokenize_regex(text), "\n")