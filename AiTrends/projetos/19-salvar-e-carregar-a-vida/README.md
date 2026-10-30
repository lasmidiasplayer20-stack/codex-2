# 19 - Salvar e carregar a vida

Pedido do usuário: um dos três novos episódios, cada um com80segundos, cenas por código e pasta própria. Vertical1080×1920 nativo,24fps/1920quadros,31takes. Projeto aiTrends/Three.js, elenco próprio Nico/verde-água,Lia/lavanda e amigos. Ficção/experimento imaginário, sem afirmar que o poder é ciência real.

Nico pode salvar um momento e voltar para ele. Café, cesta, conversa e um encontro de bicicleta mostram vantagens e limites. Depois de uma briga, ele substitui o ponto antigo e precisa aprender a continuar sem ensaiar a resposta. Cenários coloridos próprios: rua, quadra, banco, sala e entrada com porta articulada.

## Voz, efeitos e CTA

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção aceita. Uma geração bem-sucedida em cache privado, fonte68.411s. Sem acelerar ou mudar tom. Pausas adicionadas somente em silêncios detectados; tratamento suave55Hz/10500Hz,8%redução ampla de médios, ganho estático e correção lenta somente se diferença de janelas exceder3dB. Nova fonte medida: 0.82dBantes/0.82dBdepois; não reutilizar curva de outro vídeo. Métricas não comprovam naturalidade; não alegamos escuta humana integral nem ASR independente.

Foley sintetizado em Python, stems separados e eventos em audio/sfx-events.json; cenas/eventos específicos em story/foley.json. Dois CTAs diferentes fornecidos pelo usuário, variantes5/6,15–22s e71–78s,900px centralizados(x90/y1440), chroma key/despill somente nos assets. Áudio original dos CTAs omitido.

## Reprodução e entrega

`python3 AiTrends/studio.py doctor`; setup só se faltar dependência. Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/19-salvar-e-carregar-a-vida" --scale 1 --workers 2 --format jpeg --out /tmp/episodio/full-silent.mp4`, guardando log em /tmp/episodio/full-render.log. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/19-salvar-e-carregar-a-vida/scripts/finish.py --work /tmp/episodio`. Fonte congelada em qa/frozen-source.json; mix.wav privado necessário, ou decodificar mix.mp3 publicado com recodificação adicional. Não regenerar voz para ajustes de cena/mix. Licenças do kit preservadas. Capa ilustrada separada das cenas por código.

MP4/prévia e validações reais em exports/ e qa/. Pacote YouTube em ../../youtube/19 - Salvar e carregar a vida/, capa9:16 e único arquivoYOUTUBE. Não é upload ao YouTube.

Estado final:80,000s/1920quadros,1080×1920/24fps nativo. Decodificação completa e prévia60s aprovadas. Áudio final-19.0LUFS/-2.8dBTP; sem alegação de escuta humana integral. Todos os31takes e os doisCTAs conferidos em imagens reais do MP4.
