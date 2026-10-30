# 20 - Cada mentira vira realidade

Pedido do usuário: um dos três novos episódios, cada um com80segundos, cenas por código e pasta própria. Vertical1080×1920 nativo,24fps/1920quadros,33takes. Projeto aiTrends/Three.js, elenco próprio Nico/verde-água,Lia/lavanda e amigos. Ficção/experimento imaginário, sem afirmar que o poder é ciência real.

Cada mentira de Nico muda o mundo: moedas caem dos bolsos, ele flutua e seis cachorros passam a segui-lo. Uma reclamação abre um buraco no chão e uma mentira sobre não precisar de ninguém faz Lia desaparecer. O caminho de volta começa quando ele admite o medo e pede ajuda. Cenas próprias com voo, perseguição, resgate de mãos em contato e partículas de transformação; regras e acontecimentos inteiramente ficcionais.

## Voz, efeitos e CTA

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção aceita. Uma geração bem-sucedida em cache privado, fonte63.331s. Sem acelerar ou mudar tom. Pausas adicionadas somente em silêncios detectados; tratamento suave55Hz/10500Hz,8%redução ampla de médios, ganho estático e correção lenta somente se diferença de janelas exceder3dB. Nova fonte medida: 0.56dBantes/0.56dBdepois; não reutilizar curva de outro vídeo. Métricas não comprovam naturalidade; não alegamos escuta humana integral nem ASR independente.

Foley sintetizado em Python, stems separados e eventos em audio/sfx-events.json; cenas/eventos específicos em story/foley.json. Dois CTAs diferentes fornecidos pelo usuário, variantes5/6,15–22s e71–78s,900px centralizados(x90/y1440), chroma key/despill somente nos assets. Áudio original dos CTAs omitido.

## Reprodução e entrega

`python3 AiTrends/studio.py doctor`; setup só se faltar dependência. Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/20-mentiras-viram-realidade" --scale 1 --workers 2 --format jpeg --out /tmp/episodio/full-silent.mp4`, guardando log em /tmp/episodio/full-render.log. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/20-mentiras-viram-realidade/scripts/finish.py --work /tmp/episodio`. Fonte congelada em qa/frozen-source.json; mix.wav privado necessário, ou decodificar mix.mp3 publicado com recodificação adicional. Não regenerar voz para ajustes de cena/mix. Licenças do kit preservadas. Capa ilustrada separada das cenas por código.

MP4/prévia e validações reais em exports/ e qa/. Pacote YouTube em ../../youtube/20 - Cada mentira vira realidade/, capa9:16 e único arquivoYOUTUBE. Não é upload ao YouTube.

Estado final:80,000s/1920quadros,1080×1920/24fps nativo. Decodificação integral e prévia60s aprovadas; mix-19.9LUFS/-2.9dBTP.33takes/CTAs/ações conferidos em imagens reais do MP4. O takecalm foi reenquadrado para mostrar os cachorros se acalmando,33quadros nativos substituídos, sem regenerar fala; rastreio em qa/native-patch.json.
