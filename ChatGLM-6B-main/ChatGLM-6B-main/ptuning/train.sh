PRE_SEQ_LEN=8
LR=1e-2

CUDA_VISIBLE_DEVICES=3 python3 main.py \
    --do_train \
    --train_file train-1/train.json \
    --validation_file train-1/dev.json \
    --prompt_column question \
    --response_column answer \
    --overwrite_cache \
    --model_name_or_path THUDM/chatglm-6b \
    --output_dir output/train1-chatglm-6b-pt-$PRE_SEQ_LEN-$LR \
    --overwrite_output_dir \
    --max_source_length 64 \
    --max_target_length 64 \
    --per_device_train_batch_size 1 \
    --per_device_eval_batch_size 1 \
    --gradient_accumulation_steps 16 \
    --predict_with_generate \
    --max_steps 3000 \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate $LR \
    --pre_seq_len $PRE_SEQ_LEN \
    --quantization_bit 4

N \
    --quantization_bit 4

