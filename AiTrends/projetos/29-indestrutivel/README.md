# 29 - Indestrutível não significa invencível

História original inspirada na premissa do print, com nossos personagens e skins Minecraft. Oito atos com câmeras distintas, movimento corporal e efeitos Python. Não é reprodução exata de um vídeo nem captura de gameplay. Ficção especulativa.

Entrega: **30 segundos / 720 quadros / 24 fps / 1080×1920 nativo**, áudio presente e decodificação integral aprovada. Prévia de 10 s em exports/.

Voz Puck / gemini-2.5-flash-preview-tts, uma geração preservada, sem acelerar ou mudar o tom. Pausas excessivas limitadas a 0,45 s; EQ leve, ganho estático medido. Transcrição automática conferida em qa/narration-check.json. Temporização aproximada das frases em qa/timing-method.json. Não se afirma audição humana integral. Mix final: -20.7 LUFS e pico verdadeiro -3.5 dBFS. Foley sintetizado em scripts/audio.py, stem e eventos publicados.

CTAs em vídeo fornecidos pelo usuário, duas variantes, 10–17 e 23–30 s, sem o áudio original. Capa vertical do próprio episódio e arquivo único YOUTUBE em ../../youtube/29 - Indestrutível não significa invencível/. A capa usa a mesma cena e skin, com câmera e iluminação próprias para o pôster; render e tipografia por código. Sem publicação no YouTube.

Render: node AiTrends/skill/scripts/render-short-series.mjs --project CAMINHO_ABSOLUTO --scale 1 --workers 2 --format jpeg --ff-grade --preset fast --crf 20 --out PRIVADO/full-silent.mp4. Preserva MSAA e aplica cor/vinheta por FFmpeg na resolução nativa. Salvar full-render.log no mesmo diretório. Áudio: AiTrends/.venv/bin/python scripts/audio.py --work PRIVADO, reutilizando voice/block-01.wav. Finalização: scripts/finish.py --work PRIVADO --youtube PASTA --cover TEXTO. Chaves e fontes privadas não são publicadas. Skins e texturas próprias; licenças do kit preservadas.

SHA-256: `b91a0d39cb8ddb64180bcdcf82e87355686d30722fe279b1f653c4d04bd26d3c`. QA visual em qa/filme-completo.jpg; auditoria numérica amostrada não é simulação física completa nem aprovação estética automática.

Capa final: retrato próprio com contorno, luz ciano/magenta e tipografia branca/amarela, sem API de imagem. Reproduzir com `AiTrends/.venv/bin/python AiTrends/projetos/29-indestrutivel/scripts/make_cover.py`; receita em story/cover.json e prova em qa/cover-validation.json.

Para revisar somente imagens sem o cache WAV privado, reutilize `audio/mix.mp3`: decodifique-o para `audio/mix.wav` local quando necessário. Não gerar voz novamente por causa de câmera, cenário ou capa.
