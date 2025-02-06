import os
import sys
import math
import torch
import wandb
import logging
import datasets
import argparse
import evaluate
import transformers

from typing import Optional
from itertools import chain
from dataclasses import dataclass, field

from datasets import load_dataset
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    HfArgumentParser,
    Trainer,
    TrainingArguments,
    default_data_collator
)
from transformers.trainer_utils import get_last_checkpoint

# ✅ W&B 설정
wandb.init(project='Hanghae99')
wandb.run.name = 'gpt-finetuning'

@dataclass
class Arguments:
    model_name_or_path: Optional[str] = field(default="gpt2")
    torch_dtype: Optional[str] = field(default="auto")
    dataset_name: Optional[str] = field(default="wikitext")
    dataset_config_name: Optional[str] = field(default="wikitext-2-raw-v1")
    block_size: int = field(default=1024)
    num_workers: Optional[int] = field(default=4)

# ✅ 파라미터 파싱
parser = HfArgumentParser((Arguments, TrainingArguments))
args, training_args = parser.parse_args_into_dataclasses()

logger = logging.getLogger()

# ✅ 로깅 설정
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%m/%d/%Y %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger.setLevel(training_args.get_process_log_level())

# ✅ 데이터셋 로드
raw_datasets = load_dataset(args.dataset_name, args.dataset_config_name)

# ✅ 모델 및 토크나이저 로드
config = AutoConfig.from_pretrained(args.model_name_or_path)
tokenizer = AutoTokenizer.from_pretrained(args.model_name_or_path)
model = AutoModelForCausalLM.from_pretrained(
    args.model_name_or_path,
    config=config,
    torch_dtype=args.torch_dtype
)

# ✅ 패딩 설정
tokenizer.pad_token_id = tokenizer.eos_token_id
tokenizer.chat_template = "{% for message in messages %}{{'<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n'}}{% endfor %}"

# ✅ 토크나이저 크기 조정
embedding_size = model.get_input_embeddings().weight.shape[0]
if len(tokenizer) > embedding_size:
    model.resize_token_embeddings(len(tokenizer))

column_names = list(raw_datasets["train"].features)
text_column_name = "text" if "text" in column_names else column_names[0]

# ✅ 데이터 전처리 함수
def tokenize_function(examples):
    return tokenizer(examples[text_column_name])

with training_args.main_process_first(desc="dataset map tokenization"):
    tokenized_datasets = raw_datasets.map(
        tokenize_function,
        batched=True,
        num_proc=args.num_workers,
        remove_columns=column_names
    )

max_pos_embeddings = config.max_position_embeddings if hasattr(config, "max_position_embeddings") else 1024
block_size = min(args.block_size, tokenizer.model_max_length)

def group_texts(examples):
    concatenated_examples = {k: list(chain(*examples[k])) for k in examples.keys()}
    total_length = len(concatenated_examples[list(examples.keys())[0]])
    total_length = (total_length // block_size) * block_size

    result = {
        k: [t[i : i + block_size] for i in range(0, total_length, block_size)]
        for k, t in concatenated_examples.items()
    }
    result["labels"] = result["input_ids"].copy()
    return result

with training_args.main_process_first(desc="grouping texts together"):
    lm_datasets = tokenized_datasets.map(
        group_texts,
        batched=True,
        num_proc=args.num_workers
    )

# ✅ Train & Validation 데이터셋 준비 (8:2 Split)
splits = lm_datasets["train"].train_test_split(test_size=0.2)
train_dataset = splits["train"]
eval_dataset = splits["test"]

# ✅ 평가 지표 설정
perplexity = evaluate.load("perplexity")

def compute_metrics(eval_pred):
    loss = eval_pred.metrics["eval_loss"]
    return {"perplexity": math.exp(loss)}

# ✅ Trainer 정의 (Validation 포함)
trainer = Trainer(
    model=model,
    args=TrainingArguments(  # 수정된 부분
        output_dir=training_args.output_dir,
        num_train_epochs=10,  # 에포크 10으로 설정
        per_device_train_batch_size=training_args.per_device_train_batch_size,
        per_device_eval_batch_size=training_args.per_device_eval_batch_size,
        logging_dir=training_args.logging_dir,
        evaluation_strategy=training_args.evaluation_strategy,
        save_strategy=training_args.save_strategy,
        logging_steps=training_args.logging_steps,
        learning_rate=training_args.learning_rate,
        weight_decay=training_args.weight_decay,
        warmup_steps=training_args.warmup_steps,
        fp16=training_args.fp16,
        push_to_hub=training_args.push_to_hub
    ),
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=default_data_collator,
    compute_metrics=compute_metrics
)

# ✅ Checkpoint 설정
checkpoint = None
last_checkpoint = get_last_checkpoint(training_args.output_dir)
if training_args.resume_from_checkpoint is not None:
    checkpoint = training_args.resume_from_checkpoint
else:
    checkpoint = last_checkpoint

# ✅ 학습 시작
train_result = trainer.train(resume_from_checkpoint=checkpoint)

# ✅ 모델 저장
trainer.save_model()

# ✅ 학습 결과 저장
metrics = train_result.metrics
trainer.log_metrics("train", metrics)
trainer.save_metrics("train", metrics)
trainer.save_state()

# ✅ W&B 종료
wandb.finish()
