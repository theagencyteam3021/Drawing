import os
from turtle import width
from unittest import result
from PIL import Image
import torch
from diffusers import QwenImageEditPlusPipeline
from diffusers.utils import load_image

# Functions

def create_pipeline(model_id: str = "ovedrive/Qwen-Image-Edit-2509-4bit"):
    """Create and return a configured Stable Diffusion img2img pipeline.

    Returns a `StableDiffusion3Img2ImgPipeline` ready for use. This function
    encapsulates the heavy model loading so it can be called on demand.
    """
    pipe = QwenImageEditPlusPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
    print("pipeline loaded") # not true but whatever. do not move to cuda

    pipe.set_progress_bar_config(disable=None)

    # optionally load LoRA weights to speed up inference
    # pipe.load_lora_weights("lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Lightning-8steps-V1.1.safetensors")
    #pipe.load_lora_weights("lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Lightning-4steps-V2.0-bf16.safetensors")
    pipe.load_lora_weights("lightx2v/Qwen-Image-Lightning", weight_name="Qwen-Image-Lightning-8steps-V2.0-bf16.safetensors")

    pipe.load_lora_weights("caricature_v1.1_000002500.safetensors")

    #pipe.load_lora_weights("peteromallet/Qwen-Image-Edit-InStyle", weight_name="InStyle-0.5.safetensors")

    pipe.enable_model_cpu_offload()

    #generator = torch.Generator(device="cuda").manual_seed(42)
    return pipe


def generate_caricature(pipe, source_image_path,out_image_path ="Caricature_finished.png",caricaturize = False,):
    """Create a cleaned lineart from a source image and run the final stylization pass.

    Args:
        source_image_path (str): path to input photo.
        gender (str|None): 'm' or 'f' to guide stylization; if None, prompts the user.
        output_path (str|None): where to save final image.
        pipe_instance: the pre-initialized StableDiffusion3Img2ImgPipeline instance.

    Returns:
        str: path to saved output image."""

    # Load source image
    image = load_image(source_image_path).convert("RGB")
    # resize image but maintain aspect ratio
    max_size = 512
    width, height = image.size
    if max(width, height) > max_size:
        if width > height:
            new_width = max_size
            new_height = int(max_size * height / width)
        else:
            new_height = max_size
            new_width = int(max_size * width / height)
        image = image.resize((new_width, new_height), resample=Image.BICUBIC)

    if caricaturize:
        prompt = "Turn the person into a minimalistic black and white headshot coloring book page with a plain white background and simple bolded lines in a caricature style."
        negative_prompt = "shading, color, greyscale, beard, colored background, big eyes, full body, cartoon eyes, hyperextended neck, big cheeks"
        inputs = {
            "image": image,
            "prompt": prompt,
            "generator": None,
            "true_cfg_scale": 8.2,
            "negative_prompt": negative_prompt,
            "num_inference_steps": 12,
        }
    else:
        prompt = "Turn the person into a black and white coloring book page with a plain white background and simple bolded lines. Please keep the person the same age."
        negative_prompt = "shading, color, greyscale, colored background, complex"
        inputs = {
            "image": image,
            "prompt": prompt,
            "generator": None,
            "true_cfg_scale": 2,
            "negative_prompt": negative_prompt,
            "num_inference_steps": 8,
        }

    image_out = pipe(**inputs).images[0]

    image_out.save(out_image_path)
    return out_image_path
