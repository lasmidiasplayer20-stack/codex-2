# UM PIXEL — curta original

Animação de 2 minutos, 1280 × 720, 24 fps, sem diálogos. Dois personagens encontram um pixel dourado e enfrentam uma ferramenta de limpeza que está apagando o ambiente. Seleção vira plataforma, duplicação vira armadilha, rigidez vira uma mola. A solução final é desfazer a ordem destrutiva e salvar também quem a executava.

## Assistir

Abra `UM-PIXEL.mp4` ou `index.html` junto ao vídeo. O HTML funciona localmente; a página de arquivo do GitHub permite baixar o MP4.

## Arquivos

- `UM-PIXEL.mp4`: filme com áudio estéreo.
- `src/render.py`: roteiro temporal, desenhos vetoriais, rig articulado e renderização determinística.
- `src/mix_audio.py`: trilha eletrônica original por síntese e mixagem dos efeitos.
- `audio/*.mp3`: seis efeitos gerados com a API ElevenLabs Sound Effects.
- `audio/cue-sheet.json`: posições dos efeitos na montagem.
- `previews/`: quadros de revisão.
- `validation.json`: informações técnicas e resultado da decodificação.

## Reproduzir a renderização

Requer Python 3, Pillow, NumPy e FFmpeg, além da fonte DejaVu Sans (caminho configurável em `src/render.py`).

```sh
python src/render.py
python src/mix_audio.py
ffmpeg -y -i silent.mp4 -i audio/mix.wav -c:v copy -c:a aac -b:a 192k -t 120 -movflags +faststart UM-PIXEL.mp4
```

O código desenha cada quadro; não usa vídeo, contornos ou imagens de Alan Becker. Os anexos fornecidos foram consultados como referência de organização, rigs e revisão. A história, personagens, cenário e movimento foram criados para este curta. A animação é dirigida por código, sem simulação física autônoma. A estética de bonecos e interação com ferramentas atende ao pedido, com identidade visual e história próprias.

Nenhuma credencial integra o projeto. Os efeitos já estão incluídos; a reprodução não chama APIs nem gera custos.
