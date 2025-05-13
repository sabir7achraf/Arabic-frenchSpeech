import re
import difflib
from arabic_audio_diacritizer_fixed import ArabicAudioProcessor

class TextComparator:
    """
    Classe pour comparer le texte original avec la transcription.
    Optimisée pour intégration avec une API Flask.
    """
    
    @staticmethod
    def clean_arabic_text(text):
        """
        Nettoie le texte arabe en supprimant les guillemets et les espaces multiples,
        mais conserve les diacritiques et la ponctuation.
        """
        text = text.replace('"', '')
        text = text.replace('\\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def compare_texts(original_text, transcribed_text, remove_diacritics=False):
        """
        Compare le texte original avec la transcription et génère un rapport de différences.
        Option pour supprimer les diacritiques avant la comparaison.
        """
        # Nettoyer les textes
        clean_original = TextComparator.clean_arabic_text(original_text)
        clean_transcribed = TextComparator.clean_arabic_text(transcribed_text)
        
        # Supprimer les diacritiques si demandé
        if remove_diacritics:
            clean_original = ArabicAudioProcessor.remove_diacritics(clean_original)
            clean_transcribed = ArabicAudioProcessor.remove_diacritics(clean_transcribed)
        
        # Calculer la similarité
        similarity_ratio = difflib.SequenceMatcher(None, clean_original, clean_transcribed).ratio()
        similarity_percentage = similarity_ratio * 100
        
        # Générer un diff au niveau des mots
        d = difflib.Differ()
        diff = list(d.compare(clean_original.split(), clean_transcribed.split()))
        
        # Compter les erreurs
        additions = len([d for d in diff if d.startswith('+ ')])
        deletions = len([d for d in diff if d.startswith('- ')])
        common = len([d for d in diff if d.startswith('  ')])
        
        # Préparer le rapport
        report = {
            "texte_original": original_text,
            "texte_original_nettoye": clean_original,
            "transcription": transcribed_text,
            "transcription_nettoyee": clean_transcribed,
            "similarite_pourcentage": similarity_percentage,
            "mots_communs": common,
            "mots_manquants": deletions,
            "mots_supplementaires": additions,
            "diff_details": diff
        }
        
        return report