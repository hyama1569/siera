import re
import nltk
import tqdm
import random
from util.extract import *
from util.editnts import *

def preprocess_texts(texts):
    tokenized_texts = []
    for text in texts:
        text = re.sub(r'[\(\)\`\'\"\:\;\,]', '', text)
        text = re.sub(r'-RRB-', '', text)
        text = re.sub(r'-LRB-', '', text)
        text = re.sub(r'DEL', 'del', text)
        text = re.sub(r'KEEP', 'keep', text)
        text = re.sub(r'ADD', 'add', text)
        tokenized_texts.append(nltk.word_tokenize(text))
    return tokenized_texts

def get_edit_sequences(sent1_toks, sent2_toks):
    edit_sequences = []
    edits_ls = []
    spans_ls = []
    for i in tqdm.tqdm(range(len(sent1_toks))):
        sent1_tok = sent1_toks[i]
        sent2_tok = sent2_toks[i]
        edits = sent2edit(sent1_tok, sent2_tok)
        ad_spans = extract_ad_spans(edits)
        d_spans = extract_d_spans(edits)
        a_spans = extract_a_spans(edits)

        ad_ids = extract_ad_ids(ad_spans)
        d_ids = extract_d_ids(d_spans)
        a_ids = extract_a_ids(a_spans)

        edit_sequence = ad_ids + d_ids + a_ids
        edit_sequences.append(edit_sequence)
        edits_ls.append(edits)
        spans_ls.append((('ad_spans', ad_spans), ('d_spans', d_spans), ('a_spans', a_spans)))
    return edit_sequences, edits_ls, spans_ls

def assign_ids_to_edits(edits, sent2_tok):
    edits_ids = []
    sent1_pointer = 0
    sent2_pointer = 0
    for i in range(len(edits)):
        if edits[i] == 'KEEP':
            edits_ids.append(sent1_pointer)
            sent1_pointer += 1
        elif edits[i] == 'DEL':
            edits_ids.append(sent1_pointer)
            sent1_pointer += 1
        else:
            while sent2_pointer < len(sent2_tok):
                if sent2_tok[sent2_pointer] == edits[i]:
                    edits_ids.append(sent2_pointer)
                    sent2_pointer += 1
                    break
                else:
                    sent2_pointer += 1
    return edits_ids

def create_text_to_edit(edits, sent1_tok, sent2_tok, nlp):
    text_to_edit = []
    edits_ids = assign_ids_to_edits(edits, sent2_tok)

    doc_sent1 = nlp(" ".join(sent1_tok))
    sent1_tok_pos_lemma = []
    for i, token in enumerate(doc_sent1):
        sent1_tok_pos_lemma.append([token.text, token.pos_, token.lemma_])

    doc_sent2 = nlp(" ".join(sent2_tok))
    sent2_tok_pos_lemma = []
    for i, token in enumerate(doc_sent2):
        sent2_tok_pos_lemma.append([token.text, token.pos_, token.lemma_])
 
    for i in range(len(edits)):
        if edits[i] == 'DEL' or edits[i] == 'KEEP':
            text_to_edit.append([sent1_tok_pos_lemma[edits_ids[i]][0], sent1_tok_pos_lemma[edits_ids[i]][1], sent1_tok_pos_lemma[edits_ids[i]][2]])
        else:
            word_in_sent2 = sent2_tok_pos_lemma[edits_ids[i]][0]
            word_in_sent2 = 'ADD_' + word_in_sent2
            text_to_edit.append([word_in_sent2, sent2_tok_pos_lemma[edits_ids[i]][1], sent2_tok_pos_lemma[edits_ids[i]][2]])
    return text_to_edit

def apply_edit_sequences(edit_sequences, sent1_toks, sent2_toks, nlp, max_cnt):
    random.seed(111)
    applied_sentences_all = []
    applied_edit_sequences_all = []

    for i in tqdm.tqdm(range(len(edit_sequences))):
        edit_sequence = edit_sequences[i]
        sent1_tok = sent1_toks[i]
        sent2_tok = sent2_toks[i]
        edits = sent2edit(sent1_tok, sent2_tok)
        text_to_edit = create_text_to_edit(edits, sent1_tok, sent2_tok, nlp)
        ad_spans = extract_ad_spans(edits)
        d_spans = extract_d_spans(edits)
        a_spans = extract_a_spans(edits)

        if len(edit_sequence) > 1:
            applied_sentences = []
            apply_sequences = []
            limit = max_cnt
            now_cnt = 0
            while limit != 0:
                if now_cnt == 2**(len(edit_sequence)) - 2:
                    break
                rn = random.randint(1, len(edit_sequence)-1)
                apply_sequence = random.sample(edit_sequence, rn)
                apply_sequence = [tuple(val) for val in apply_sequence]
                if set(apply_sequence) not in apply_sequences:
                    apply_sequences.append(set(apply_sequence))
                    now_cnt += 1
                    limit -= 1

                    apply_ad_spans = []
                    apply_d_spans = []
                    apply_a_spans = []
                    for apply_span in apply_sequence:
                        if apply_span[0] == 'ad_span':
                            ad_span_idx = apply_span[1]
                            ad_span = list(range(ad_spans[ad_span_idx][0], ad_spans[ad_span_idx][1]+1))
                            apply_ad_spans += ad_span
                        if apply_span[0] == 'd_span':
                            d_span_idx = apply_span[1]
                            d_span = list(range(d_spans[d_span_idx][0], d_spans[d_span_idx][1]+1))
                            apply_d_spans += d_span
                        if apply_span[0] == 'a_span':
                            a_span_idx = apply_span[1]
                            a_span = list(range(a_spans[a_span_idx][0], a_spans[a_span_idx][1]+1))
                            apply_a_spans += a_span

                    applied_sentence_tok = []
                    for i in range(len(text_to_edit)):
                        if i in apply_ad_spans:
                            if edits[i] == 'DEL':
                                continue
                            else:
                                applied_sentence_tok.append(text_to_edit[i][0][4:])

                        elif i in apply_d_spans:
                            continue
                        elif i in apply_a_spans:
                            applied_sentence_tok.append(text_to_edit[i][0][4:])
                        else:
                            if edits[i] == 'DEL' or edits[i] == 'KEEP':
                                applied_sentence_tok.append(text_to_edit[i][0])
                            else:
                                continue 
                    applied_sentences.append(" ".join(applied_sentence_tok))
                    #applied_edit_sequences_all.append(apply_sequence)
            applied_sentences_all.append(applied_sentences)
            applied_edit_sequences_all.append(apply_sequences)
        else:
            applied_edit_sequences_all.append([])
            applied_sentences_all.append([])
    return applied_sentences_all, applied_edit_sequences_all
