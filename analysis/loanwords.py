import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score, precision_score, recall_score
from tqdm.auto import tqdm
from transformers import AutoModel, AutoTokenizer

from config.common import load_data
from config.constants import DATA_PATH, LOANWORDS_MODEL_WEIGHTS


def create_mask(full_txts, phrases, tokenizer, max_length=512):
    if isinstance(full_txts, str):
        full_txts = [full_txts]
        phrases = [phrases]
    toks = tokenizer(full_txts, return_offsets_mapping=True, truncation=True, max_length=max_length, padding=True,
                     return_tensors='pt')
    all_maps = []
    phrases = [x.split(', ') for x in phrases]
    for phrase, full_txt, off_map, att_mask in zip(phrases, full_txts, toks['offset_mapping'], toks['attention_mask']):
        local_maps = []
        for k, phr in enumerate(phrase):
            first_end = False
            ner_map = []
            start_point = full_txt.find(phr)
            end_point = start_point + len(phr)
            for s0, e0 in off_map.detach().cpu().numpy():
                if first_end:
                    ner_map.append(-100)
                elif s0 != e0 and s0 >= start_point and e0 <= end_point:
                    ner_map.append(1)
                elif s0 != e0 and e0 >= start_point and e0 <= end_point:
                    ner_map.append(1)
                elif s0 == e0:
                    ner_map.append(-100)
                elif e0 > len(full_txt):
                    ner_map.append(-100)
                    first_end = True
                else:
                    ner_map.append(0)
            if (len(phrase) > 1) and (k + 1 == len(phrase)):
                ner_map = (np.array(ner_map) + np.array(local_maps[-1])).tolist()
                ner_map = [-100 if x == -200 else x for x in ner_map]
                ner_map = [1 if x == 2 else x for x in ner_map]
            if k + 1 == len(phrase):
                all_maps.append(ner_map)
            else:
                local_maps.append(ner_map)
    return all_maps


def get_preds(layer, past_key_tensor, df, model, tokenizer,
              threshold=0.8, dx=1, device='cpu'):
    f1_scores = []
    precision_scores = []
    recall_scores = []
    preds = []
    for pos in tqdm(range(0, len(df), dx)):
        txt = df['sentence'].values[pos:pos + dx].tolist()
        word = df['form'].values[pos:pos + dx].tolist()
        use_past = [x.repeat_interleave(len(txt), dim=1) for x in past_key_tensor]
        toks = tokenizer(txt, truncation=True,
                         max_length=512-past_key_tensor[0].shape[3], padding=True,
                         return_tensors='pt').to(device)
        att_mask = torch.cat([torch.ones(len(txt),
                                         past_key_tensor[0].shape[3]).to(device),
                              toks['attention_mask']], dim=1)
        out = model(toks['input_ids'], attention_mask=att_mask,
                    past_key_values=use_past)['last_hidden_state']
        target = torch.tensor(create_mask(txt, word, tokenizer,
                                          max_length=512-past_key_tensor[0].shape[3])).to(device)
        out = layer(out)
        mask = F.softmax(out, dim=-1)[:, :, 1]
        mask = torch.where(mask >= threshold, 1, 0)
        target[target == -100] = 0
        precision_ner = precision_score(target.cpu().numpy().tolist()[0],
                                        mask.cpu().numpy().tolist()[0], labels=[1],
                                        average='binary', zero_division=0)
        recall_ner = recall_score(target.cpu().numpy().tolist()[0],
                                  mask.cpu().numpy().tolist()[0], labels=[1],
                                  average='binary', zero_division=0)
        f1_ner = f1_score(target.cpu().numpy().tolist()[0],
                          mask.cpu().numpy().tolist()[0], labels=[1],
                          average='binary', zero_division=0)
        precision_scores.append(precision_ner)
        recall_scores.append(recall_ner)
        f1_scores.append(f1_ner)
        pr = [tokenizer.decode(x, skip_special_tokens=True).strip()
              for x in toks['input_ids'] * mask]
        preds.extend(pr)
    return f1_scores, precision_scores, recall_scores, preds


if __name__ == '__main__':
    dataset = load_data(DATA_PATH)
    device = 'cpu'
    model_path = 'sberbank-ai/ruRoberta-large'
    model = AutoModel.from_pretrained(LOANWORDS_MODEL_WEIGHTS).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    train_past = torch.load(LOANWORDS_MODEL_WEIGHTS / "adapt_angls.pth")
    linear = torch.load(LOANWORDS_MODEL_WEIGHTS / "lin_angls.pth")
    f1_val, precision_val, recall_val, preds = get_preds(layer=linear, past_key_tensor=train_past,
                                                         df=dataset, model=model, tokenizer=tokenizer,
                                                         threshold=0.8, dx=1, device=device)
