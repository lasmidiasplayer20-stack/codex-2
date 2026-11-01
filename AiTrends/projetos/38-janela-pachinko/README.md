# 38 — A janela do pachinko

Versão autoral da explicação enviada pelo usuário: **69 segundos, vertical 1080×1920 nativo, 24 fps, 1.656 quadros**. Elenco arredondado original do Então, sem Minecraft. Roteiro novo: acompanhar o prêmio e revelar o circuito entre salão, comprador e atacadista. A referência orientou escala dos planos, inserts, travelling, contracampo e a descoberta da janela; seus frames, fala, personagens e música não entram no filme.

- [MP4 completo](exports/38%20-%20A%20janela%20do%20pachinko.mp4)
- [Prévia de 15 s](exports/preview-15s.mp4), intervalo 23–38 s do filme
- [Capa e arquivo único YOUTUBE](../../youtube/38%20-%20A%20janela%20do%20pachinko/)
- [Roteiro](input/narracao.txt), [plano de 22 takes](story/shots.json), [análise de referência e limites factuais](research/REFERENCIA-E-FATOS.md)
- [Quadros do filme final](qa/filme-completo.jpg), [validação de exportação](qa/export-validation.json)

## Direção e áudio

Cenários próprios de salão, balcão, rua, janela com vão físico e diagrama dos três estabelecimentos. Marcha por distância, articulações em dois segmentos, cotovelos com polos estáveis, prêmios vinculados à palma, contato com balcão e passagem de dinheiro. Piloto nativo de 16 s conferido em quadros consecutivos antes do render integral; não é uma simulação física nem se afirma revisão humana de cada frame.

Mesma **Puck / gemini-2.5-flash-preview-tts**, uma geração contínua, sem mudança de velocidade ou tom. Filtro/EQ leves, ganho estático medido, apenas pausas excessivas encurtadas. Transcrição automática independente: `qa/narration-check.json`; métricas não substituem avaliação humana de timbre. Stems tratados de voz, música e Foley em `audio/`. Sons de aço, passos, apoio do prêmio, papel e tecido sintetizados em Python, com eventos em `audio/sfx-events.json`.

Dois CTAs em vídeo fornecidos pelo usuário, variantes diferentes, aos 15–22 e 60–67 s, 740 px de largura, sem o áudio desses clipes. Chroma key aplicado somente ao asset CTA.

A explicação jurídica é geral: não declara que qualquer aposta seja legal ou que toda loja seja societariamente independente. As consultas externas nesta execução foram bloqueadas/limitadas; esse limite e os links para conferência independente estão no documento de pesquisa. Objetos e estabelecimentos fictícios, sem taxa de conversão ou ganhos prometidos.

## Reprodução

Na raiz do repositório, executar `python3 AiTrends/studio.py doctor`. O render completo deste episódio usa **aiTrends/Three.js**. A integração Remotion foi instalada em paralelo em `../../remotion/`; este MP4 não deve ser atribuído a ela.

```bash
node AiTrends/skill/scripts/render-short-series.mjs --project CAMINHO_ABSOLUTO_DO_PROJETO --scale 1 --workers 2 --format jpeg --ff-grade --preset fast --crf 20 --out PRIVADO/full-silent.mp4
# Guardar a saída do comando em PRIVADO/full-render.log.
AiTrends/.venv/bin/python CAMINHO_DO_PROJETO/scripts/finish.py --work PRIVADO
AiTrends/.venv/bin/python CAMINHO_DO_PROJETO/scripts/make_cover.py --work PRIVADO
```

Para revisão visual a partir do Git, decodificar o stem `audio/mix.mp3` em `audio/mix.wav` local antes da finalização; **não regenerar a voz**. `scripts/audio.py` reproduz a mix a partir do cache privado `voice/block-01.wav`, quando disponível. `generate_voice.py` existe para produção autorizada, não é etapa necessária para rever cenas/capa. Chaves nunca são publicadas.

Código de cenário/rig, roteiro, timeline, mix, eventos e QA permanecem no projeto. Licenças do kit e fonte Anton preservadas. Pacote YouTube preparado, sem upload para o YouTube.
