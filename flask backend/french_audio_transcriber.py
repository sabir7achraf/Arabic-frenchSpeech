import torch
import librosa
import os
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

class FrenchAudioProcessor:
    def __init__(self):
        print("🔤 Chargement du modèle français...")
        self.processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-french")
        self.model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-french")
        print("✅ Modèle chargé.")

    def transcribe(self, audio_path, sample_rate=16000):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Fichier non trouvé : {audio_path}")

        audio, _ = librosa.load(audio_path, sr=sample_rate)
        inputs = self.processor(audio, sampling_rate=sample_rate, return_tensors="pt")

        with torch.no_grad():
            logits = self.model(inputs.input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0]
        return transcription.strip()
