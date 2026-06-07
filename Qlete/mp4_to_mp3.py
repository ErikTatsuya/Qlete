from moviepy import VideoFileClip

# 1. Carrega o arquivo de vídeo MP4
video = VideoFileClip("pronuncia.mkv")

# 2. Extrai apenas a parte do áudio
audio = video.audio

# 3. Salva o áudio no formato MP3
audio.write_audiofile("apenas_audio.mp3")

# 4. Fecha os arquivos para liberar a memória do PC
audio.close()
video.close()

print("Áudio extraído com sucesso!")