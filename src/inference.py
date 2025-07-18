import torchio as tio
import pandas as pd
from data.dataset import CustomDataset,CustomDatasetPrediction
from torch.utils.data import DataLoader
from model.adaptformer import AdaptFormer
from model.bifit import BiFit
from model.dvpt import DynamicVisualPromptTuning
from model.evp import ExplicitVisualPrompting
from model.ssf import ScalingShiftingFeatures
from model.melo import MedicalLoRA
from model.vpt import PromptedVisionTransformer
from model.gaviko import Gaviko
import torch
import logging
import os
from tqdm import tqdm
import numpy as np


def inference(config):
    os.makedirs(config['utils']['log_dir'], exist_ok=True)
    time_stamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    logging.basicConfig(filename=os.path.join(config['utils']['log_dir'], f'log_{time_stamp}.txt'), level=logging.INFO, format='%(asctime)s - %(message)s')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f"Using device: {device}")

    test_transforms = tio.Compose([
        tio.RescaleIntensity(out_min_max=(0,1)),
    ])

    test_df = generate_csv(config['data']['image_folder'])

    test_ds = CustomDatasetPrediction(test_df, transforms=test_transforms)
    test_loader = DataLoader(test_ds, batch_size=config['data']['batch_size'], shuffle=False, num_workers=config['data']['num_workers'], pin_memory=True)

    if config['model']['model_type'] == 'gaviko':
        model = Gaviko(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads=config['model']['heads'],
            dim=config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            attn_drop=config['model']['attn_drop'],
            proj_drop=config['model']['proj_drop'],
            channels=config['model']['channels'],
            num_classes=config['model']['num_classes'],
            freeze_vit = config['model']['freeze_vit'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
            num_prompts=config['model']['num_prompts'],
            prompt_latent_dim=config['model']['prompt_latent_dim'],
            local_dim=config['model']['local_dim'],
            local_k= tuple(config['model']['local_k']),
            DHW=tuple(config['model']['DHW']),
            share_factor=config['model']['share_factor']
        )

    elif config['model']['model_type'] == 'adaptformer':
        model = AdaptFormer(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads=config['model']['heads'],
            dim=config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            freeze_vit = config['model']['freeze_vit'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
        )# .to(device)

    elif config['model']['model_type'] == 'bifit':
        model = BiFit(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads=config['model']['heads'],
            dim=config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
        )
        for key, value in model.named_parameters():
            if "bias" in key:
                value.requires_grad = True
            elif "head" in key:
                value.requires_grad = True
            else:
                value.requires_grad = False
    elif config['model']['model_type'] == 'dvpt':
        model = DynamicVisualPromptTuning(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads= config['model']['heads'],
            dim= config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            freeze_vit = config['model']['freeze_vit'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
            num_prompts = config['model']['num_prompts'],
        )# .to(device)

    elif config['model']['model_type'] == 'evp':
        model = ExplicitVisualPrompting(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads=config['model']['heads'],
            dim=config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            pool = config['model']['pool'],
            pretrain_path=config['model']['pretrain_path'],
            freeze_vit=config['model']['freeze_vit'],
            scale_factor=config['model']['scale_factor'],
            input_type=config['model']['input_type'],
            freq_nums=config['model']['freq_nums'],
            handcrafted_tune=config['model']['handcrafted_tune'],
            embedding_tune=config['model']['embedding_tune'],
        )# .to(device)

    elif config['model']['model_type'] == 'ssf':
        model = ScalingShiftingFeatures(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads=config['model']['heads'],
            dim=config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            freeze_vit = config['model']['freeze_vit'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
        )
    elif config['model']['model_type'] == 'melo':
        model = MedicalLoRA(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames=config['model']['frames'],
            frame_patch_size=config['model']['frame_patch_size'],
            depth=config['model']['depth'],
            heads=config['model']['heads'],
            dim=config['model']['dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
        )
    elif config['model']['model_type'] == 'deep_vpt' or config['model']['model_type'] == 'shallow_vpt':
        model = PromptedVisionTransformer(
            image_size=config['model']['image_size'],
            image_patch_size=config['model']['image_patch_size'],
            frames = config['model']['frames'],
            frame_patch_size = config['model']['frame_patch_size'],
            num_layers=config['model']['num_layers'],
            num_heads=config['model']['num_heads'],
            hidden_dim=config['model']['hidden_dim'],
            mlp_dim=config['model']['mlp_dim'],
            dropout=config['model']['dropout'],
            emb_dropout=config['model']['emb_dropout'],
            channels = config['model']['channels'],
            num_classes = config['model']['num_classes'],
            freeze_vit = config['model']['freeze_vit'],
            pool = config['model']['pool'],
            pretrain_path = config['model']['pretrain_path'],
            num_prompts = config['model']['num_prompts'],
            prompt_dropout = config['model']['prompt_dropout'],
            prompt_dim = config['model']['prompt_dim'],
            deep_prompt=config['model']['deep_prompt']
        )
    model.to(device)
    #load trained weights
    model_path = config['utils']['model_path']
    if os.path.exists(model_path):
        logging.info(f"Loading model weights from {model_path}")
        model.load_state_dict(torch.load(model_path, map_location=device))
    else:
        logging.error(f"Model weights not found at {model_path}. Please check the path.")
        return
    model.eval()
    all_outputs = []

    with torch.no_grad():
        for inputs in tqdm(test_loader, desc="Running Inference"):
            inputs = inputs.to(device)  


            outputs = model(inputs)  

            predicted_classes = torch.argmax(outputs, dim=1).cpu().numpy() 

            all_outputs.append(predicted_classes)
    print(all_outputs)
    all_outputs = np.concatenate(all_outputs, axis=0)  
    print(f"Final outputs shape: {all_outputs.shape}")

    test_df['outputs'] = all_outputs.tolist()

    test_df['mri_path'] = test_df['mri_path'].apply(lambda x: os.path.basename(x))

    output_df = test_df[['mri_path', 'outputs']]

    output_df['outputs'] = output_df['outputs'].apply(lambda x: x.tolist() if isinstance(x, np.ndarray) else x)

    results_dir = config['utils']['results_dir']
    os.makedirs(results_dir, exist_ok=True)
    logging.info(f"Saving inference outputs to {results_dir}")
    model_type = config['model']['model_type']
    output_csv_path = os.path.join(results_dir, f'{model_type}_inference_results_details.csv')

    output_df.to_csv(output_csv_path, index=False)
    print(f"Results saved to {output_csv_path}")
def generate_csv(image_folder):
    """
    Generates a CSV file with image paths and labels.
    :param image_folder: Path to the folder containing images.
    :param output_csv_path: Path where the output CSV will be saved.
    """
    image_paths = []
    # labels = []
    
    for filename in os.listdir(image_folder):
        if filename.endswith('.npz'):
            image_paths.append(os.path.join(image_folder, filename))
            # label = filename.split('_')[-1].split('.')[0]  # Extracting label from filename
            # labels.append(label)
    
    df = pd.DataFrame({'mri_path': image_paths})
    # df.to_csv(output_csv_path, index=False)
    return df
if __name__ == "__main__":
    from omegaconf import OmegaConf
    import argparse
    parser = argparse.ArgumentParser(description="Inference script for Gaviko model")
    parser.add_argument('--config', type=str, default='/workspace/train_deep_prompt/configs/original_gaviko.yaml',
                        help='Path to the configuration file')
    parser.add_argument('--image_folder', type=str, required=True,
                        help='Path to the folder containing MRI images')
    parser.add_argument('--results_dir', type=str, default='./',
                        help='Directory to save inference results')
    parser.add_argument('--model_path', type=str, required=True,
                        help='Path to the trained model weights')
    parser.add_argument('--model_type', type=str, default='gaviko',
                        help='Type of model to use (default: gaviko)')
    args = parser.parse_args()

    config = OmegaConf.load(args.config)
    config['data']['image_folder'] = args.image_folder
    config['utils']['results_dir'] = args.results_dir
    config['utils']['model_path'] = args.model_path
    config['model']['model_type'] = args.model_type
    os.makedirs(config['utils']['results_dir'], exist_ok=True)
    logging.info(f"Config: {config}")
    inference(config)

