import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from train_models import train_all_models

if __name__ == "__main__":
    print("Starting model training...")
    train_all_models()
    print("\n✓ Training complete!")
