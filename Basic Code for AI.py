#Run Once at startup
model_id = "stabilityai/stable-diffusion-3.5-large"
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
import numpy as np

nf4_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)
model_nf4 = SD3Transformer2DModel.from_pretrained(
    model_id,
    subfolder="transformer",
    quantization_config=nf4_config,
    torch_dtype=torch.bfloat16
)

pipe = StableDiffusion3Img2ImgPipeline.from_pretrained(
    model_id, 
    transformer=model_nf4,
    torch_dtype=torch.bfloat16
)
pipe.enable_model_cpu_offload()


# -------------------------
#RUN EVERY TIME
image = Image.open("Child2.png").convert("RGB")                   #Starting image here

# Create lineart
lineart = LineartDetector.from_pretrained("lllyasviel/Annotators")
control_image = lineart(image, detect_resolution=512, image_resolution=512)

control_image.save("lineart13.png")                          #Change to avoid overwrite
# content_img = control_image.resize((512, 512))

from PIL import Image, ImageOps

# Load lineart output
lineart = Image.open("lineart13.png").convert("L")              #Change to avoid overwrite
lineart = ImageOps.invert(lineart)
lineart = lineart.point(lambda x: 0 if x < 160 else 255)
lineart = lineart.convert("RGB")

lineart.save("lineart_bw_fixe13.png")                     #Change to avoid overwrite(Make sure it matches below)

#cleanup Crew

first_pass = Image.open("lineart_bw_fixe13.png").convert("L")          #Change to avoid overwrite (Make sure it matches above)
first_pass = ImageOps.autocontrast(first_pass)
first_pass = first_pass.point(lambda x: 0 if x < 200 else 255)
first_pass = first_pass.convert("RGB")

first_pass.save("lineart_clean9.png")                           #Change to avoid overwrite
print ("Lineart cleaned")




# -------------------------
# PASS 1 — Caricature from clean lineart                        This pass is a bit iffy Im not sure if its needed 


prompt = (
    "simple black ink caricature drawing, "
    "hand-drawn editorial cartoon, "
    "exaggerated facial proportions, "
    "loose uneven pen lines, "
    "flat white background, "
    "no shading, no lighting"
)

negative_prompt = (
    "shading, shadows, dark background, gray background, "
    "realistic, portrait, lighting, depth, engraving"
)

result_pass1 = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=lineart,          # assumes lineart is already fixed BW
    strength=0.45,
    guidance_scale=5.0,
    num_inference_steps=22,
).images[0]

result_pass1.save("pass13_fixed.png")                    #Change name each time to avoid overwrite
print ("Pass 1 complete")

# -------------------------
# Pass 2 — Final stylization to cartoon caricature

input = input("Gender: Male(m) or Female(f)")
if input.lower() == "m":
    prompt = (
    "Make it look like a hand drawn cartoon caricature, please keep the male gender characteristics, keep the glasses, exaggerate the facial features, "
    )

    negative_prompt = (
        "realistic, realism, portrait, "
        "shading, shadows, gradients, gray tones, "
        "dark background, black background, "
        "lighting, depth, volume, contrast, "
        "engraving, etching, crosshatching, "
        "digital art, clean vector, polished illustration"
    )

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=Image.open("lineart_clean5.png"),   # <- CLEAN BLACK ON WHITE LINEART
        strength=0.7,        # THIS IS THE SECRET 0.8 is the basis
        guidance_scale=8,  # lower = less realism correction   BEST = 9.0
        num_inference_steps=35,   #40 is original
    ).images[0]

    result.save("caricature_final_Greentest15.png")                #Change name each time to avoid overwrite
    print ("Final Pass complete of Male. Done.")

if input.lower() == "f":
    prompt = (
        "Make it look like a hand drawn cartoon caricature, please keep the female gender characteristics, keep the glasses, exaggerate the facial features, "
    )

    negative_prompt = (
        "realistic, realism, portrait, "
        "shading, shadows, gradients, gray tones, "
        "dark background, black background, "
        "lighting, depth, volume, contrast, "
        "engraving, etching, crosshatching, "
        "digital art, clean vector, polished illustration"
    )

    result = pipe(
        prompt=prompt,
        negative_prompt=negative_prompt,
        image=Image.open("lineart_clean7.png"),   # <- CLEAN BLACK ON WHITE LINEART
        strength=0.7,        # THIS IS THE SECRET 0.8 is the basis
        guidance_scale=8,  # lower = less realism correction   BEST = 9.0
        num_inference_steps=35,   #40 is original
    ).images[0]

    result.save("caricature_final_Greentest15.png")                #Change name each time to avoid overwrite
    print ("Final Pass complete of Female. Done.")




###AI Version for testing######
gender = input(print("Gender: Male(m) or Female(f): ")).strip().lower()

if gender == "m":
    prompt = (
        "Make it look like a hand drawn cartoon caricature, please keep the male gender characteristics, keep the glasses, exaggerate the facial features, "
    )
    image_path = "lineart_clean5.png"
    output_path = "caricature_final_male.png"
    print("Processing Male...")

elif gender == "f":
    prompt = (
        "Make it look like a hand drawn cartoon caricature, please keep the female gender characteristics, keep the glasses, exaggerate the facial features, "
    )
    image_path = "lineart_clean7.png"
    output_path = "caricature_final_female.png"
    print("Processing Female...")

else:
    print("Invalid input. Please enter 'm' or 'f'.")
    exit()

negative_prompt = (
    "realistic, realism, portrait, "
    "shading, shadows, gradients, gray tones, "
    "dark background, black background, "
    "lighting, depth, volume, contrast, "
    "engraving, etching, crosshatching, "
    "digital art, clean vector, polished illustration"
)

result = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=Image.open(image_path),
    strength=0.7,
    guidance_scale=8,
    num_inference_steps=35,
).images[0]

result.save(output_path)
print(f"Final Pass complete for {gender}. Done.")
###############################

















##### Just to keep testing
prompt = (
    "Make it look like a simple hand drawn cartoon caricature, please keep the male gender characteristics, if there are glasses present keep them;"
    "Keep the approximated age the same, keep as a simple linedrawing, ")
negative_prompt = (
    "realistic, realism, portrait, "
    "shading, shadows, gradients, gray tones, "
    "dark background, black background, "
    "lighting, depth, volume, contrast, "
    "engraving, etching, crosshatching, "
    "digital art, clean vector, polished illustration, color, text, writing, signature, watermark"
)

result = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    image=Image.open("lineart_bw_fixe11.png"),   # <- CLEAN BLACK ON WHITE LINEART
    strength=0.7,        # THIS IS THE SECRET 0.8 is the basis 0.7 is best 
    guidance_scale=8,  # lower = less realism correction   BEST = 8.0
    num_inference_steps=35,   #40 is original-- 35 is best
).images[0]

result.save("caricature_final_Greentest-21.png")                #Change name each time to avoid overwrite
print ("Final Pass complete of Male. Done.")