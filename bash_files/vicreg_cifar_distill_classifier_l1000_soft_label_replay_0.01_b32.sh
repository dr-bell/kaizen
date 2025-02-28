python3 main_continual.py \
    --dataset cifar100 \
    --encoder resnet18 \
    --data_dir $DATA_DIR \
    --split_strategy class \
    --max_epochs 500 \
    --num_tasks 5 \
    --task_idx 4 \
    --gpus 0 \
    --precision 16 \
    --optimizer sgd \
    --lars \
    --grad_clip_lars \
    --eta_lars 0.02 \
    --exclude_bias_n_norm \
    --scheduler warmup_cosine \
    --lr 0.3 \
    --classifier_lr 0.05 \
    --weight_decay 1e-4 \
    --batch_size 256 \
    --num_workers 2 \
    --min_scale 0.2 \
    --brightness 0.4 \
    --contrast 0.4 \
    --saturation 0.2 \
    --hue 0.1 \
    --solarization_prob 0.1 \
    --gaussian_prob 0.0 0.0 \
    --name cifar100-vicreg-predictive_mse-distill-classifier-l1000-soft-label-replay-0.01-b32 \
    --project ever-learn-2 \
    --entity your_entity \
    --offline \
    --wandb \
    --save_checkpoint \
    --proj_hidden_dim 2048 \
    --output_dim 2048 \
    --sim_loss_weight 25.0 \
    --var_loss_weight 25.0 \
    --cov_loss_weight 1.0 \
    --disable_knn_eval \
    --online_eval_classifier_lr 0.1 \
    --classifier_training True \
    --classifier_stop_gradient True \
    --classifier_layers 1000 \
    --distiller_library factory \
    --method vicreg \
    --distiller predictive_mse \
    --classifier_distill_lamb 2.0 \
    --distiller_classifier soft_label \
    --classifier_distill_no_predictior True \
    --replay True \
    --replay_proportion 0.01 \
    --replay_batch_size 32 \
    --online_evaluation True \
    --online_evaluation_training_data_source seen_tasks \
    --pretrained_model experiments/2023_03_05_04_19_14-cifar100-vicreg-predictive_mse-distill-classifier-l1000-lamb2-soft-label-replay-0.01-b32/task3-6348uzl8/cifar100-vicreg-predictive_mse-distill-classifier-l1000-lamb2-soft-label-replay-0.01-b32-task3-ep=499-6348uzl8.ckpt
