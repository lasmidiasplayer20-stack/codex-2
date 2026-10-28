# Fontes e reprodução

- `generate_voice.py`: perfil Puck existente, cache privado; requer chave via ambiente, não salva chave. Não repetir chamadas para remixar.
- `audio.py --work PASTA_PRIVADA`: lê `voice/block-01.wav`, detecta pausas, distribui curtos intervalos, EQ/ganho estático e Foley/trilha NumPy/SciPy; exporta WAV/MP3 de60s.
- `align_plan.py`: temporização aproximada por pausas medidas, não alinhamento ASR por palavra. Só executar ao refazer plano, não depois de congelar/renderizar.
- Render: `node AiTrends/skill/scripts/render.mjs --project CAMINHO_ABSOLUTO --scale 1 --workers 2 --format jpeg --out PASTA_PRIVADA/full-silent.mp4`; redirecionar log para full-render.log.
- `finish.py --work PASTA_PRIVADA`: exige marcador de render concluído e hash visual congelado; monta voz+imagem, exige1440quadros/60s nativos1080×1920, testa decode/picos e extrai QA do MP4 final. Não faz push automático.

Arquivos intermediários WAV e build não entram no Git; MP3s reutilizáveis ficam em audio/. Dependências no ambiente AiTrends/.venv e kit Three.js original com suas licenças preservadas.
