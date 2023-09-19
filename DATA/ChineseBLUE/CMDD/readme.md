# ReadMe

### Structure of CMDD（Chinese Medical Dialogue Dataset）

**data-split:**	 Train/dev/test
**example-id:**	 Id of dialogue (unique)
**dialogue-content:** 	List of dict, each dict represents a sentence

### keys in dialogue-content

**speaker:** 	'医生'/'患者' (Doctor/Patient)
**sentence:** 	Content of the sentence
**label:** 	BIO label of sentence
**normalized:** 	Normalization of symptoms in the sentence
**type:** 	Type of symptoms 1: True 2: False 3: Uncertain

### Dataloader

We provide `dataloader.py` to read the data.

```bash
$ python dataloader.py
```

