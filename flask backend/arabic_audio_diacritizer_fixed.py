import torch
import numpy as np
import librosa
import os 
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

class ArabicAudioProcessor:
    """
    Système de reconnaissance vocale arabe sans diacritisation.
    Optimisé pour intégration avec une API Flask.
    """
    
    def __init__(self):
        print("Chargement du modèle de reconnaissance vocale...")
        self.asr_processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
        self.asr_model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
        print("Modèle chargé avec succès")
    
    @staticmethod
    def remove_diacritics(text):
        """
        Supprime les diacritiques d'un texte arabe.
        """
        diacritics = [
            '\u0610', '\u0611', '\u0612', '\u0613', '\u0614', '\u0615', '\u0616', '\u0617', '\u0618', '\u0619', '\u061A',
            '\u064B', '\u064C', '\u064D', '\u064E', '\u064F', '\u0650', '\u0651', '\u0652', '\u0653', '\u0654', '\u0655',
            '\u0656', '\u0657', '\u0658', '\u0659', '\u065A', '\u065B', '\u065C', '\u065D', '\u065E', '\u065F'
        ]
        for diac in diacritics:
            text = text.replace(diac, '')
        return text

    def process_audio(self, audio_path, sample_rate=16000, remove_diacritics=False):
        """
        Traite un fichier audio pour produire un texte arabe.
        Option pour supprimer les diacritiques du texte transcrit.
        """
        print(f"Transcription de l'audio: {audio_path}")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Le fichier audio {audio_path} n'existe pas")
        
        print("Chargement de l'audio...")
        try:
            speech_array, _ = librosa.load(audio_path, sr=sample_rate)
        except Exception as e:
            raise Exception(f"Erreur lors du chargement de l'audio: {str(e)}")
        
        print(f"Audio chargé, longueur: {len(speech_array)} échantillons")
        
        print("Traitement par le modèle ASR...")
        try:
            inputs = self.asr_processor(speech_array, sampling_rate=sample_rate, return_tensors="pt")
            with torch.no_grad():
                logits = self.asr_model(inputs.input_values).logits
                predicted_ids = torch.argmax(logits, dim=-1)
                transcription = self.asr_processor.batch_decode(predicted_ids)[0]
        except Exception as e:
            raise Exception(f"Erreur lors de la transcription: {str(e)}")
        
        if remove_diacritics:
            transcription = self.remove_diacritics(transcription)
        
        print(f"Transcription: {transcription}")
        return transcription