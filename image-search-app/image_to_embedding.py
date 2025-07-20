from PIL import Image
import chromadb
from chromadb.utils.embedding_functions import OpenCLIPEmbeddingFunction
from transformers import BlipProcessor, BlipForConditionalGeneration
from chromadb.utils.data_loaders import ImageLoader
import torch
import numpy as np
from tqdm import tqdm
import os
import glob


db_path=r"image_caption_vdb" #add your db path here
# Initialize Chroma DB client, embedding function, and data loader

client = chromadb.PersistentClient(path=db_path)
embedding_function = OpenCLIPEmbeddingFunction()
data_loader = ImageLoader()

# 3. Load BLIP for image captioning
blip_path = "blip-captioning"
blip_processor = BlipProcessor.from_pretrained(blip_path)
blip_model = BlipForConditionalGeneration.from_pretrained(blip_path)


# 6. Get image caption using BLIP
def get_caption_blip(image_path):
    raw_image = Image.open(image_path).convert('RGB')
    inputs = blip_processor(images=raw_image, return_tensors="pt")
    with torch.no_grad():
        output = blip_model.generate(**inputs)
    caption = blip_processor.decode(output[0], skip_special_tokens=True)
    return caption

collection = client.get_or_create_collection(
    name='embed_caption_collection',
    embedding_function=embedding_function,
    data_loader=data_loader
)

def add_images_to_collection(folder_path):
    image_files = glob.glob(os.path.join(folder_path, '*.*'))

    for image_path in tqdm(image_files, desc="Creating Image Embeddings and Adding to DB"):
        try:
            image = np.array(Image.open(image_path))
            caption = get_caption_blip(image_path)
            collection.add(
                metadatas=[{"image_path": image_path, "caption": caption}],
                ids=[os.path.basename(image_path)],
                images=[image]
            )
        except Exception as e:
            print(f"Error processing {image_path}: {str(e)}")

image_folder_path=r"images"

add_images_to_collection(image_folder_path)
