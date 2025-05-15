from flask import Flask, request, jsonify, render_template
from arabic_audio_diacritizer_fixed import ArabicAudioProcessor
from arabic_text_comparator import TextComparator
from french_audio_transcriber import FrenchAudioProcessor
import tempfile
import os
import shutil
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# 🔤 Initialisation des modèles
print("Chargement des modèles...")
arabic_processor = ArabicAudioProcessor()
french_processor = FrenchAudioProcessor()
print("✅ Modèles chargés.")

# 🧠 Génération de feedback multilingue
def generer_feedback(similarite, langue="ar"):
    if langue == "fr":
        if similarite >= 90:
            return f"🌟 Excellente lecture ! 👏 ({similarite:.2f}%)"
        elif similarite >= 70:
            return f"👍 Bonne lecture, attention à quelques erreurs. ({similarite:.2f}%)"
        elif similarite >= 50:
            return f"🙂 Lecture passable, tu peux mieux faire. ({similarite:.2f}%)"
        else:
            return f"🛠️ Lecture difficile, un peu de pratique aidera ! ({similarite:.2f}%)"
    else:
        if similarite >= 90:
            return f"🌟 قراءة ممتازة! 👏 ({similarite:.2f}%)"
        elif similarite >= 70:
            return f"👍 قراءة جيدة، لكن بها بعض الأخطاء. ({similarite:.2f}%)"
        elif similarite >= 50:
            return f"🙂 قراءة مقبولة، لكن تحتاج إلى تحسين. ({similarite:.2f}%)"
        else:
            return f"🛠️ قراءة صعبة. تدرب أكثر لتحسن مستواك! ({similarite:.2f}%)"

# Connexion DB

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Ajoute le mot de passe si nécessaire
        database="AgentiAi"
    )

# 🌐 Pages Web
@app.route('/')
def index_arabe():
    return render_template("index.html")

@app.route('/fr')
def index_francais():
    return render_template("french.html")

# 🇦🇪 Évaluation arabe
@app.route('/evaluate', methods=['POST'])
def evaluate_arabe():
    if 'audio' not in request.files or 'target_text' not in request.form:
        return jsonify({'error': 'Fichier audio ou texte manquant'}), 400

    audio_file = request.files['audio']
    target_text = request.form['target_text']

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_path = temp_audio.name
        audio_file.save(audio_path)

    try:
        transcription = arabic_processor.process_audio(audio_path, remove_diacritics=True)
        comparator = TextComparator()
        report = comparator.compare_texts(target_text, transcription, remove_diacritics=True)
        similarity_score = round(report["similarite_pourcentage"], 2)
        feedback = generer_feedback(similarity_score, langue="ar")

        # Sauvegarde de l'audio
        audio_filename = f"ar_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        audio_save_path = os.path.join("audios", audio_filename)
        shutil.move(audio_path, audio_save_path)

        # Enregistrement dans la BDD
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO record (language, audio_path, similarity, feedback)
            VALUES (%s, %s, %s, %s)
        """, ("ar", audio_save_path, similarity_score, feedback))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "transcription": transcription,
            "similarite": similarity_score,
            "feedback": feedback,
            "mots_corrects": report["mots_communs"],
            "mots_manquants": report["mots_manquants"],
            "mots_supplementaires": report["mots_supplementaires"]
        })

    except Exception as e:
        return jsonify({'error': f"Erreur de traitement (arabe) : {str(e)}"}), 500

# 🇫🇷 Évaluation français
@app.route('/evaluate-fr', methods=['POST'])
def evaluate_francais():
    if 'audio' not in request.files or 'target_text' not in request.form:
        return jsonify({'error': 'Audio ou texte manquant'}), 400

    audio_file = request.files['audio']
    target_text = request.form['target_text']

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        audio_path = temp_audio.name
        audio_file.save(audio_path)

    try:
        transcription = french_processor.transcribe(audio_path)
        comparator = TextComparator()
        report = comparator.compare_texts(target_text, transcription)
        similarity_score = round(report["similarite_pourcentage"], 2)
        feedback = generer_feedback(similarity_score, langue="fr")

        # Sauvegarde de l'audio
        audio_filename = f"fr_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        audio_save_path = os.path.join("audios", audio_filename)
        shutil.move(audio_path, audio_save_path)

        # Enregistrement dans la BDD
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO recorder (langue, audio_path, similarity, feedback)
            VALUES (%s, %s, %s, %s)
        """, ("fr", audio_save_path, similarity_score, feedback))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "transcription": transcription,
            "similarite": similarity_score,
            "feedback": feedback,
            "mots_corrects": report["mots_communs"],
            "mots_manquants": report["mots_manquants"],
            "mots_supplementaires": report["mots_supplementaires"]
        })

    except Exception as e:
        return jsonify({'error': f"Erreur de traitement (français) : {str(e)}"}), 500

# 🚀 Lancement du serveur
if __name__ == '__main__':
    if not os.path.exists("audios"):
        os.makedirs("audios")
    app.run(host='0.0.0.0', port=5000, debug=True)
