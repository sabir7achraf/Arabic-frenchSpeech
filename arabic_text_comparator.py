import os
import re
import difflib

class TextComparator:
    """
    Classe pour comparer le texte original avec la transcription.
    """
    
    @staticmethod
    def clean_arabic_text(text):
        """
        Nettoie le texte arabe en supprimant les guillemets et les espaces multiples,
        mais conserve les diacritiques et la ponctuation.
        """
        # Supprimer les guillemets
        text = text.replace('"', '')
        
        # Normaliser les sauts de ligne
        text = text.replace('\\n', ' ')
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def compare_texts(original_text, transcribed_text):
        """
        Compare le texte original avec la transcription et génère un rapport de différences.
        Conserve les diacritiques et la ponctuation pour une comparaison précise.
        """
        # Nettoyer les textes sans supprimer les diacritiques
        clean_original = TextComparator.clean_arabic_text(original_text)
        clean_transcribed = TextComparator.clean_arabic_text(transcribed_text)
        
        # Calculer la similarité entre les textes complets
        similarity_ratio = difflib.SequenceMatcher(None, clean_original, clean_transcribed).ratio()
        similarity_percentage = similarity_ratio * 100
        
        # Générer un diff pour visualisation au niveau des mots
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
    
    @staticmethod
    def print_report(report):
        """
        Affiche le rapport de comparaison de manière lisible.
        """
        print("\n" + "="*50)
        print("RAPPORT DE COMPARAISON DE TEXTE")
        print("="*50)
        
        print("\nTEXTE ORIGINAL:")
        print(report["texte_original"])
        
        print("\nTEXTE ORIGINAL (NETTOYÉ):")
        print(report["texte_original_nettoye"])
        
        print("\nTRANSCRIPTION:")
        print(report["transcription"])
        
        print("\nTRANSCRIPTION (NETTOYÉE):")
        print(report["transcription_nettoyee"])
        
        print("\nSTATISTIQUES:")
        print(f"- Similarité: {report['similarite_pourcentage']:.2f}%")
        print(f"- Mots communs: {report['mots_communs']}")
        print(f"- Mots manquants dans la transcription: {report['mots_manquants']}")
        print(f"- Mots supplémentaires dans la transcription: {report['mots_supplementaires']}")
        
        print("\nDÉTAILS DES DIFFÉRENCES:")
        print("  Légende: '- ' = mot manquant, '+ ' = mot ajouté, '  ' = mot commun")
        for d in report["diff_details"]:
            print(f"  {d}")
        
        print("="*50)
    
    @staticmethod
    def save_report_to_file(report, output_path):
        """
        Sauvegarde le rapport dans un fichier texte.
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("RAPPORT DE COMPARAISON DE TEXTE\n")
            f.write("="*50 + "\n\n")
            
            f.write("TEXTE ORIGINAL:\n")
            f.write(report["texte_original"] + "\n\n")
            
            f.write("TEXTE ORIGINAL (NETTOYÉ):\n")
            f.write(report["texte_original_nettoye"] + "\n\n")
            
            f.write("TRANSCRIPTION:\n")
            f.write(report["transcription"] + "\n\n")
            
            f.write("TRANSCRIPTION (NETTOYÉE):\n")
            f.write(report["transcription_nettoyee"] + "\n\n")
            
            f.write("STATISTIQUES:\n")
            f.write(f"- Similarité: {report['similarite_pourcentage']:.2f}%\n")
            f.write(f"- Mots communs: {report['mots_communs']}\n")
            f.write(f"- Mots manquants dans la transcription: {report['mots_manquants']}\n")
            f.write(f"- Mots supplémentaires dans la transcription: {report['mots_supplementaires']}\n\n")
            
            f.write("DÉTAILS DES DIFFÉRENCES:\n")
            f.write("  Légende: '- ' = mot manquant, '+ ' = mot ajouté, '  ' = mot commun\n")
            for d in report["diff_details"]:
                f.write(f"  {d}\n")
        
        print(f"Rapport sauvegardé dans: {output_path}")


def main():
    # Chemins des fichiers
    transcription_path = "C:/Users/ayaas/Arabictest/Audios/resultat_transcription.txt"
    original_text_path = "C:/Users/ayaas/Arabictest/textes/Mahmoudfaux.txt"
    report_output_path = "C:/Users/ayaas/Arabictest/rapports/rapport_comparaison.txt"
    
    # Vérifier l'existence des répertoires et les créer si nécessaire
    os.makedirs(os.path.dirname(report_output_path), exist_ok=True)
    
    # Texte original
    original_text = ""
    transcribed_text = ""
    
    # Lire le texte original s'il existe
    if os.path.exists(original_text_path):
        with open(original_text_path, 'r', encoding='utf-8') as f:
            original_text = f.read().strip()
        print(f"✅ Texte original chargé depuis: {original_text_path}")
    else:
        # Texte d'exemple si le fichier n'existe pas
        original_text = "محمود والد زيد وهو يعمل في شركة في العاصمة"
        print(f"⚠️ Fichier texte original non trouvé. Utilisation du texte d'exemple.")
        
        # Créer le répertoire pour le fichier texte s'il n'existe pas
        os.makedirs(os.path.dirname(original_text_path), exist_ok=True)
        
        # Sauvegarder le texte d'exemple pour référence future
        with open(original_text_path, 'w', encoding='utf-8') as f:
            f.write(original_text)
        print(f"Texte d'exemple sauvegardé dans: {original_text_path}")
    
    # Lire la transcription si elle existe
    if os.path.exists(transcription_path):
        with open(transcription_path, 'r', encoding='utf-8') as f:
            transcribed_text = f.read().strip()
        print(f"✅ Transcription chargée depuis: {transcription_path}")
    else:
        print(f"⚠️ Fichier de transcription non trouvé à: {transcription_path}")
        print("Veuillez d'abord exécuter le script de transcription audio.")
        return
    
    try:
        # Comparer les textes
        comparator = TextComparator()
        report = comparator.compare_texts(original_text, transcribed_text)
        
        # Afficher et sauvegarder le rapport
        comparator.print_report(report)
        comparator.save_report_to_file(report, report_output_path)
        
    except Exception as e:
        print(f"Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()