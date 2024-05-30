import numpy as np
import torch
import torch.nn.functional as F
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


def get_preds(layer, past_key_tensor, text, model, tokenizer,
              threshold=0.8, device='cpu'):
    toks = tokenizer(text,
                     padding=True,
                     max_length=512 - past_key_tensor[0].shape[3],
                     truncation=True,
                     return_tensors='pt').to(device)
    inp_ids = toks['input_ids']
    att_mask = torch.cat([torch.ones(1, past_key_tensor[0].shape[3]).to(device),
                          toks['attention_mask']
                          ], dim=1)
    with torch.no_grad():
        out = model(input_ids=inp_ids, attention_mask=att_mask, past_key_values=past_key_tensor)
        lin_out = layer(out['last_hidden_state'])
    mask = F.softmax(lin_out, dim=-1)[:, :, 1]
    mask = torch.where(mask >= threshold, 1, 0)
    pred = tokenizer.decode((inp_ids * mask)[0], skip_special_tokens=True).strip().split()

    return pred


def get_loanwords(text):
    device = 'cpu'
    model_path = 'sberbank-ai/ruRoberta-large'
    model = AutoModel.from_pretrained(model_path).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    train_past = torch.load(LOANWORDS_MODEL_WEIGHTS / "adapt_angls.pth")
    linear = torch.load(LOANWORDS_MODEL_WEIGHTS / "lin_angls.pth")
    return get_preds(layer=linear, past_key_tensor=train_past,
                     text=text, model=model, tokenizer=tokenizer,
                     threshold=0.8, device=device)


if __name__ == '__main__':
    dataset = load_data(DATA_PATH)
    for id, text in enumerate(dataset['wb_descriptions'][:25]):
        print(f"{id}-----------------------------------------------")
        get_loanwords(text)
