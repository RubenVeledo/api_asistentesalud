from fastapi import FastAPI
from transformers import pipeline
import torch

print("FastAPI y transformers están instalados correctamente")
print("PyTorch está instalado:", torch.__version__)
print("¿CUDA está disponible?:", torch.cuda.is_available())
