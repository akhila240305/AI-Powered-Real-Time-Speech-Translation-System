async function translate() {
  // This is a demo integration
  // Replace API URL with your backend endpoint

  document.getElementById("translatedText").value =
    "Hello! This is a translated output.";

  // Example TTS audio
  const audioUrl = "http://localhost:8000/output.mp3";

  const audio = document.getElementById("audioPlayer");
  audio.src = audioUrl;

  document.getElementById("downloadAudio").href = audioUrl;
}

function copyText() {
  const text = document.getElementById("translatedText");
  text.select();
  document.execCommand("copy");
  alert("Text copied!");
}

function downloadText() {
  const text = document.getElementById("translatedText").value;
  const blob = new Blob([text], { type: "text/plain" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "translated.txt";
  link.click();
}
