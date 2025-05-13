let mediaRecorder;
let audioChunks = [];

const recordBtn = document.getElementById("record-btn");
const stopBtn = document.getElementById("stop-btn");

recordBtn.addEventListener("click", async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  audioChunks = [];

  mediaRecorder.ondataavailable = event => {
    audioChunks.push(event.data);
  };

  mediaRecorder.onstop = async () => {
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');

    const targetText = document.getElementById('target-text').textContent;
    formData.append('target_text', targetText);

    try {
      const res = await fetch('http://localhost:5000/evaluate', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();

      document.getElementById("transcription").textContent = data.transcription || '❌';
      document.getElementById("similarity").textContent = data.similarite ? data.similarite + "%" : '❌';
      document.getElementById("feedback").textContent = data.feedback || '❌';

    } catch (err) {
      console.error("Erreur:", err);
      alert("Échec de l'envoi de l'audio.");
    }
  };

  mediaRecorder.start();
  recordBtn.disabled = true;
  stopBtn.disabled = false;
});

stopBtn.addEventListener("click", () => {
  mediaRecorder.stop();
  recordBtn.disabled = false;
  stopBtn.disabled = true;
});
