import torch
import numpy as np
import librosa
import os
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

class ArabicAudioProcessor:
    """
    Système de reconnaissance vocale arabe sans diacritisation.
    Version simplifiée qui fonctionne avec les modèles disponibles publiquement.
    """
    
    def __init__(self):
        print("Chargement du modèle de reconnaissance vocale...")
        
        # Modèle de reconnaissance vocale arabe (ASR)
        self.asr_processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
        self.asr_model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-arabic")
        
        print("Modèle chargé avec succès")
    
    def process_audio(self, audio_path):
        """
        Traite un fichier audio pour produire un texte arabe.
        """
        transcription = self.transcribe_audio(audio_path)
        print(f"Transcription: {transcription}")
        return transcription
    
    def transcribe_audio(self, audio_path, sample_rate=16000):
        """
        Transcrit un fichier audio en texte arabe.
        """
        print(f"Transcription de l'audio: {audio_path}")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Le fichier audio {audio_path} n'existe pas")
        
        # Charger l'audio avec librosa (fonctionne avec différents formats)
        print("Chargement de l'audio...")
        speech_array, _ = librosa.load(audio_path, sr=sample_rate)
        print(f"Audio chargé, longueur: {len(speech_array)} échantillons")
        
        print("Traitement par le modèle ASR...")
        inputs = self.asr_processor(speech_array, sampling_rate=sample_rate, return_tensors="pt")
        
        with torch.no_grad():
            logits = self.asr_model(inputs.input_values).logits
            predicted_ids = torch.argmax(logits, dim=-1)
            transcription = self.asr_processor.batch_decode(predicted_ids)[0]
        
        return transcription


def test_with_sample():
    """
    Test de démonstration avec un exemple statique.
    """
    sample_text = "محمود والد زيد وهو يعمل في شركة في العاصمة"
    print("\n--- Exemple de texte arabe (sans traitement) ---")
    print(f"Texte: {sample_text}")
    print("\nPour un test réel avec un fichier audio, utilisez un chemin valide vers un fichier .wav ou .ogg")


if __name__ == "__main__":
    # Spécifiez ici le chemin vers votre fichier audio
    audio_path = "C:/Users/ayaas/Arabictest/Audios/Mahmoud.ogg"
    
    try:
        # Vérifier si le fichier existe
        if os.path.exists(audio_path):
            print(f"✅ Fichier audio trouvé : {audio_path}")
            processor = ArabicAudioProcessor()
            transcription = processor.process_audio(audio_path)
            
            # Sauvegarde du résultat dans un fichier texte
            output_path = os.path.join(os.path.dirname(audio_path), "resultat_transcription.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(transcription)
            print(f"\nRésultat sauvegardé dans : {output_path}")
            
            print("\nNote: Cette version n'inclut pas la diacritisation car les modèles disponibles ne sont pas accessibles.")
            print("Vous pouvez utiliser des services en ligne comme https://tashkeel.net/ pour ajouter manuellement les diacritiques.")
        else:
            print(f"\n⚠️ Fichier audio non trouvé à : {audio_path}")
            print("Exécution du test simulé à la place...\n")
            test_with_sample()
    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        print("Vérifiez que toutes les dépendances sont installées.")
        # Pour mieux déboguer
        import traceback
        traceback.print_exc()