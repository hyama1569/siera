from util.apply import *
import spacy
import pickle
import pandas as pd
import nltk

if __name__ == '__main__':
    with open('./data/newsela_woaug.pickle', 'rb') as f:
        data = pickle.load(f)

    # data = pd.read_csv("./data/simplicity_DA.csv")

    random_seed = 1

    sources = data["orig_sent"].tolist()
    targets = data["simp_sent"].tolist()
        
    nltk.download('punkt')
    sent1_toks = preprocess_texts(sources)
    sent2_toks = preprocess_texts(targets)
    nlp = spacy.load('en_core_web_sm')

    edit_sequences, edits_ls, spans_ls = get_edit_sequences(sent1_toks, sent2_toks)
    data["edit_sequences"] = edit_sequences
    data["edits"] = edits_ls
    data["spans"] = spans_ls
    # with open('./src/simplicityDA_edit_sequences.pickle', 'wb') as f:
    #     pickle.dump(data, f)

    max_cnt = 1000
    applied_sentences_all, applied_edit_sequences_all = apply_edit_sequences(edit_sequences, sent1_toks, sent2_toks, nlp, max_cnt)
    with open('./src/newsela_silver.pickle', 'wb') as f:
        pickle.dump(applied_sentences_all, f)
    # with open('./src/augmented_simplicityDA_applied_sequence.pickle', 'wb') as f:
    #     pickle.dump(applied_edit_sequences_all, f)
