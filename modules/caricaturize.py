#Run Once at startup
import torch
from diffusers import BitsAndBytesConfig, SD3Transformer2DModel
from diffusers import StableDiffusion3Img2ImgPipeline
from PIL import Image
from diffusers import (
    StableDiffusionControlNetPipeline,
    ControlNetModel,
    UniPCMultistepScheduler
)
from controlnet_aux import LineartDetector
from PIL import Image



def create_pipeline(model_id: str = "stabilityai/stable-diffusion-3.5-large"):
    """Create and return a configured Stable Diffusion img2img pipeline.

    Returns a `StableDiffusion3Img2ImgPipeline` ready for use. This function
    encapsulates the heavy model loading so it can be called on demand.
    """
    nf4_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )

    model_nf4 = SD3Transformer2DModel.from_pretrained(
        model_id,
        subfolder="transformer",
        quantization_config=nf4_config,
        torch_dtype=torch.bfloat16,
    )

    local_pipe = StableDiffusion3Img2ImgPipeline.from_pretrained(
        model_id,
        transformer=model_nf4,
        torch_dtype=torch.bfloat16,
    )
    local_pipe.enable_model_cpu_offload()
    return local_pipe


# -------------------------
def generate_caricature(source_image_path,
                        gender=None,
                        output_path=None,
                        pipe_instance=None):
    """Create a cleaned lineart from a source image and run the final stylization pass.

    Args:
        source_image_path (str): path to input photo.
        gender (str|None): 'm' or 'f' to guide stylization; if None, prompts the user.
        output_path (str|None): where to save final image.
        pipe_instance: the pre-initialized StableDiffusion3Img2ImgPipeline instance.

    Returns:
        str: path to saved output image.
    """
    from PIL import ImageOps

    # Load source image
    src_img = Image.open(source_image_path).convert("RGB")

    # Create lineart
    detector = LineartDetector.from_pretrained("lllyasviel/Annotators", local_files_only=True)
    control_image = detector(src_img, detect_resolution=512, image_resolution=512)
    control_image.save("lineart15.png")

    # Clean and threshold
    lineart_img = Image.open("lineart15.png").convert("L")
    lineart_img = ImageOps.invert(lineart_img)
    lineart_img = lineart_img.point(lambda x: 0 if x < 160 else 255)
    lineart_img = lineart_img.convert("RGB")
    lineart_img.save("lineart_bw_fixe15.png")

    first_pass = Image.open("lineart_bw_fixe15.png").convert("L")
    first_pass = ImageOps.autocontrast(first_pass)
    first_pass = first_pass.point(lambda x: 0 if x < 200 else 255)
    first_pass = first_pass.convert("RGB")
    first_pass.save("lineart10.png")
    print("Lineart cleaned")

    # Ask for gender if not provided
    if gender is None:
        gender = input("Gender: Male(m) or Female(f) or caner(c): ").strip().lower()

    if gender not in ("m", "f"):
        raise ValueError("gender must be 'm' or 'f'")

    if gender == "c":
        quit()

    if output_path is None:
        output_path = f"caricature_final_{'male' if gender=='m' else 'female'}.png"

    # Prepare prompts
    if gender == "m":
        prompt = (
            "Make it look like a hand drawn cartoon caricature, please keep the male gender characteristics,if glasses are present keep them, exaggerate facial features, "
        )
    else:
        prompt = (
            "Make it look like a hand drawn cartoon caricature, please keep the female gender characteristics,if glasses are present keep them, exaggerate the facial features, "
        )

    negative_prompt = (
        "realistic, realism, portrait, "
        "shading, shadows, gradients, gray tones, "
        "dark background, black background, "
        "lighting, depth, volume, contrast, "
        "engraving, etching, crosshatching, "
        "digital art, clean vector, polished illustration"
    )

    # Ensure pipeline is available (create on demand)
    if pipe_instance is None:
        global pipe
        if pipe is None:
            pipe = create_pipeline()
        pipe_instance = pipe

    # Final stylization pass using the cleaned lineart
    result = pipe_instance(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=Image.open("lineart10.png"),
        strength=0.7,
        guidance_scale=8,
        num_inference_steps=35,
    ).images[0]

    result.save(output_path)
    print(f"Final Pass complete for {gender}. Saved to {output_path}")
    return output_path
