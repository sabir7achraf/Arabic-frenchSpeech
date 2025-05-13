from flask import Flask, request, jsonify,render_template
from arabic_audio_diacritizer_fixed import ArabicAudioProcessor
from arabic_text_comparator import TextComparator
import os
import tempfile

app = Flask(__name__)

# Initialisation unique du processeur audio
print("Initialisation du processeur audio...")
processor = ArabicAudioProcessor()

def generer_feedback(similarite):
    similarite_str = f" ({similarite:.2f}%)"  # Formatage du pourcentage
    if similarite >= 90:
        return f"🌟 قراءة ممتازة! إنه جيد 👏{similarite_str}"
    elif similarite >= 70:
        return f"👍 قراءة جيدة، ولكن كن حذرا مع بضع كلمات.{similarite_str}"
    elif similarite >= 50:
        return f"🙂 القراءة مقبولة، ولكن يمكنك القيام بعمل أفضل{similarite_str}"
    else:
        return f"🛠️ قراءة صعبة. القليل من الممارسة سوف يساعدك !{similarite_str}"

        
@app.route('/')
def serve_index():
    return render_template('index.html')


@app.route('/evaluate', methods=['POST'])
def evaluate_reading():
    # Vérifier la présence de l’audio et du texte cible
    if 'audio' not in request.files or 'target_text' not in request.form:
        return jsonify({'error': 'Fichier audio ou texte cible manquant'}), 400

    audio_file = request.files['audio']
    target_text = request.form['target_text']

    # Sauvegarde temporaire de l'audio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_path = temp_audio.name
        audio_file.save(audio_path)

    try:
        # Étape 1 : Transcription
        transcription = processor.process_audio(audio_path, remove_diacritics=True)

        # Étape 2 : Évaluation
        comparator = TextComparator()
        report = comparator.compare_texts(target_text, transcription, remove_diacritics=True)
        feedback = generer_feedback(report["similarite_pourcentage"])

        # Supprimer le fichier temporaire
        os.remove(audio_path)

        # Réponse JSON
        return jsonify({
            "transcription": transcription,
            "similarite": round(report["similarite_pourcentage"], 2),
            "feedback": feedback,
            "mots_corrects": report["mots_communs"],
            "mots_manquants": report["mots_manquants"],
            "mots_supplementaires": report["mots_supplementaires"]
        })

    except FileNotFoundError as e:
        return jsonify({"error": f"Fichier audio introuvable: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Erreur lors du traitement: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)