# 13 — E se você escolhesse onde o raio cai?

Short original do Então, vertical nativo1080×1920/24fps, alvo exato90segundos. Nico e Lia em cidade procedural colorida; hipótese fantástica abre uma explicação conceitual de proteção contra raios. Não reproduz um vídeo de referência: o usuário forneceu capturas com temas e escolheu o para-raios.

## Produção

- Cenas e personagens Three.js por código no aiTrends adaptado; contornos, IK de dois segmentos, deslocamento relacionado à marcha, câmera geral/detalhe, acompanhamento da descida e corte subterrâneo.
- Uma única geração de narração Puck / gemini-2.5-flash-preview-tts / generateContent, mesma direção aceita, aproximadamente79,691s de fonte. Sem troca de voz/modelo, aceleração ou mudança de tom.
- EQ suave, compensação lenta pré-calculada da subida de nível e ganho final estático com folga; pausas curtas acrescentadas em silêncios existentes. Sem compressor extra ou controle rápido de ganho. A variação entre medianas de janelas ativas caiu de6,28dB para0,70dB; isso mede nível, não identidade perfeita de timbre. Fonte bruta e credenciais ficam fora do Git.
- Efeitos sintetizados em Python: chuva baixa, trovão distante discreto, passos, porta, corrente ilustrada e cliques/sino do CTA. Stems reutilizáveis em áudio MP3.
- CTA em vídeo fornecido pelo usuário, reutilizado com recorte/chroma key/despill aplicados apenas ao asset; janela900px emx90/y1440,15–22s e81–88s. Áudio original do CTA omitido.
- Capa ilustrada própria vertical, separada das cenas por código, no pacote YouTube. Título/descrição/tags no arquivo único `YOUTUBE`.

## Reproduzir

Na raiz do repositório, execute `python3 AiTrends/studio.py doctor`. Use o ambiente `.venv` configurado por `studio.py setup` se as dependências estiverem ausentes. O código depende do motor aiTrends e da licença do pacote fornecido pelo usuário; esta pasta não redistribui o motor sob outra licença.

```bash
node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/13-escolher-o-raio" --scale 1 --workers 2 --format jpeg --out /tmp/raio/full-silent.mp4
AiTrends/.venv/bin/python AiTrends/projetos/13-escolher-o-raio/scripts/finish.py --work /tmp/raio
```

Guarde a saída do render em `/tmp/raio/full-render.log`. O finalizador valida a fonte congelada em `qa/frozen-source.json`. Ele espera `audio/mix.wav`: decodifique `audio/mix.mp3` localmente se o WAV privado não estiver mais disponível. Isso reproduz a montagem com uma recodificação de áudio, sem prometer identidade binária. `scripts/audio.py` documenta a síntese e o tratamento a partir da fonte Puck privada; não faz novas chamadas. `generate_voice.py` exige credencial em variável de ambiente e tem cache; não execute para uma simples revisão visual ou de mix.

## Escopo científico e revisão

O poder de escolher raios é explicitamente inventado. Um SPDA completo envolve captação, descidas, aterramento e outras medidas coordenadas. A representação é simplificada e não serve para dimensionamento/instalação. Árvores não são abrigo seguro. Procurar abrigo adequado ao ouvir trovões e aguardar30minutos após o último antes de retomar atividades externas.

Fontes indicadas e limites de acesso estão em `story/references.json`. A consulta ao site NOAA foi bloqueada pelo proxy nesta produção; não alegamos pesquisa ao vivo concluída ou análise de vídeo não assistido.

Evidências: `qa/export-validation.json`, decodificação integral, níveis do áudio final, amostragem das cenas e quadros consecutivos da chuva/marcha. Limite: não houve escuta humana integral nem transcrição independente. Métricas de nível não garantem naturalidade perfeita ou aprovação editorial.

Estado de entrega: MP4 final exportado e validado —90,000s,2160quadros,1080×1920/24fps, decodificação integral aprovada, áudio−18,9LUFS/−4,6dBTP. Prévia de60s e pacote YouTube incluídos. Consulte os relatórios em `qa/`.
