# 21 - Dez segundos do futuro

Pedido do usuário: um dos três novos episódios, cada um com80segundos, cenas por código e pasta própria. Vertical1080×1920 nativo,24fps/1920quadros,33takes. Projeto aiTrends/Three.js, elenco próprio Nico/verde-água,Lia/lavanda e amigos. Ficção/experimento imaginário, sem afirmar que o poder é ciência real.

Nico enxerga uma possibilidade dez segundos adiante: uma bandeja, uma bola e livros ao vento. Ao tentar corrigir tudo, muda as trajetórias e se distrai do presente. Lia o faz parar antes de uma bicicleta passar. Ele então usa a previsão para uma ajuda concreta, em vez de controlar a rua inteira. Visões azuis com silhuetas translúcidas, relógio preso ao pulso, objetos em contato e câmeras próprias; precognição e regras são ficção, não ciência comprovada.

## Voz, efeitos e CTA

Mesma Puck/gemini-2.5-flash-preview-tts/generateContent e direção aceita. Uma geração bem-sucedida em cache privado, fonte68.291s. Sem acelerar ou mudar tom. Pausas adicionadas somente em silêncios detectados; tratamento suave55Hz/10500Hz,8%redução ampla de médios, ganho estático e correção lenta neste21 se diferença de janelas exceder2,5dB, para reduzir a subida medida no final. Nova fonte medida: 2.83dBantes/0.59dBdepois; não reutilizar curva de outro vídeo. Métricas não comprovam naturalidade; não alegamos escuta humana integral nem ASR independente.

Foley sintetizado em Python, stems separados e eventos em audio/sfx-events.json; cenas/eventos específicos em story/foley.json. Dois CTAs diferentes fornecidos pelo usuário, variantes5/6,15–22s e71–78s,900px centralizados(x90/y1440), chroma key/despill somente nos assets. Áudio original dos CTAs omitido.

## Reprodução e entrega

`python3 AiTrends/studio.py doctor`; setup só se faltar dependência. Render: `node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/21-dez-segundos-do-futuro" --scale 1 --workers 2 --format jpeg --out /tmp/episodio/full-silent.mp4`, guardando log em /tmp/episodio/full-render.log. Finalizar com `AiTrends/.venv/bin/python AiTrends/projetos/21-dez-segundos-do-futuro/scripts/finish.py --work /tmp/episodio`. Fonte congelada em qa/frozen-source.json; mix.wav privado necessário, ou decodificar mix.mp3 publicado com recodificação adicional. Não regenerar voz para ajustes de cena/mix. Licenças do kit preservadas. Capa ilustrada separada das cenas por código.

MP4/prévia e validações reais em exports/ e qa/. Pacote YouTube em ../../youtube/21 - Dez segundos do futuro/, capa9:16 e único arquivoYOUTUBE. Não é upload ao YouTube.

Calibração21: a primeira mix estéreo estava em−17,1LUFS, acima dos outros dois. Reduzimos o alvo mono estático em2,4dB para aproximar a saída estéreo de−19,5LUFS; mesma fonte, sem compressor ou nova API. Medida final em qa/final-audio-validation.json.

Estado final:80,000s/1920quadros,1080×1920/24fps nativo, decodificação integral e prévia60s aprovadas. Mix final-19.1LUFS/-5.4dBTP. Imagens reais dos33takes, doisCTAs e sequências de ação conferidas; não alegamos escuta humana integral.
