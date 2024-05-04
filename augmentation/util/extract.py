def extract_ad_spans(edits):
    ad_spans = []
    seen_a = [0 for i in range(len(edits))]
    for i in range(len(edits) - 1):
        if seen_a[i] != 1:
            if edits[i] != 'KEEP' and edits[i] != 'DEL':
                start = i
                j = i + 1
                flag = False
                while j < len(edits):
                    if edits[j] == 'DEL':
                        j += 1
                        flag = True
                    elif edits[j] != 'KEEP' and edits[j] != 'DEL':
                        if flag == False:
                            seen_a[j] = 1
                            j += 1
                        else:
                            break
                    else:
                        break
                if flag == True:
                    end = j - 1
                    if end - start > 0:
                        ad_spans.append((start, end))
    return ad_spans

def extract_d_spans(edits):
    d_spans = []
    flag = False
    seen = [0 for i in range(len(edits))]
    for i in range(len(edits)):
        if seen[i] != 1:
            seen[i] = 1
            if edits[i] != 'KEEP' and edits[i] != 'DEL':
                flag = True
            elif edits[i] == 'KEEP':
                flag = False
            else:
                if flag == True:
                    continue
                else:
                    start = i
                    j = i + 1
                    while j < len(edits):
                        if edits[j] == 'DEL':
                            seen[j] = 1
                            j += 1
                        elif edits[j] == 'KEEP':
                            break
                        else:
                            flag = True
                            break
                    end = j - 1
                    if end - start >= 0:
                        d_spans.append((start, end))
    return d_spans 

def extract_a_spans(edits):
    a_spans = []
    seen_a = [0 for i in range(len(edits))]
    for i in range(len(edits)):
        if seen_a[i] != 1:
            seen_a[i] = 1
            if edits[i] != 'KEEP' and edits[i] != 'DEL':
                start = i
                j = i + 1
                flag = False
                while j < len(edits):
                    if edits[j] != 'KEEP' and edits[j] != 'DEL':
                        seen_a[j] = 1
                        j += 1
                    elif edits[j] == 'DEL':
                        flag = True
                        break
                    else:
                        break
                end = j - 1
                if (flag == False) and (end - start >= 0):
                    a_spans.append((start, end))
    return a_spans

def extract_ad_ids(ad_spans):
    ad_ids = []
    for ad_span_idx in range(len(ad_spans)):
        ad_ids.append(['ad_span', ad_span_idx])
    return ad_ids

def extract_d_ids(d_spans):
    d_ids = []
    for d_span_idx in range(len(d_spans)):
        d_ids.append(['d_span', d_span_idx])
    return d_ids

def extract_a_ids(a_spans):
    a_ids = []
    for a_span_idx in range(len(a_spans)):
        a_ids.append(['a_span', a_span_idx])
    return a_ids