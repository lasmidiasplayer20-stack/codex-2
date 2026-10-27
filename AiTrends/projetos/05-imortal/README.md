# 05 — E se você fosse imortal?

**Entregue no GitHub.** História própria em português, horizontal, 1920×1080/24 fps. Duração natural: **9min50,625s**, 1.391 palavras, 32 sequências e 160 planos. O alvo inicial de 8min30s cedeu ao ritmo natural da voz aprovada; não aceleramos a narração para caber.

## Vídeos

- [Episódio completo — 9min50s / 1080p](exports/05%20-%20E%20se%20voc%C3%AA%20fosse%20imortal.mp4)
- [Prévia de um minuto — 1080p](exports/05%20-%20E%20se%20voc%C3%AA%20fosse%20imortal%20-%20Preview%201min.mp4)
- [Piloto inicial de 20 segundos](exports/05-imortal-piloto-20s.mp4)

MP4 H.264/AAC estéreo; resolução nativa, 24 fps. Decodificação integral passou no filme (14.175 quadros) e na prévia (1.440 quadros). O tamanho do filme está abaixo do limite individual do GitHub; `qa/export-validation.json` registra hash, bitrate e evidências. Aprovação editorial do filme completo ainda não foi solicitada nem presumida.

## Áudio aprovado antes da geração completa

O usuário avaliou [a amostra com mix discreta](audio/03-voz-com-mix.mp3) e respondeu “Aprovada com mix discreta”. Puck e `gemini-2.5-flash-preview-tts` foram mantidos em todos os trechos. A abertura aprovada foi reutilizada. Nove chamadas ao todo: uma amostra e oito blocos restantes, sem regenerações, tentativas automáticas ou troca de modelo.

A [voz reutilizável](audio/narracao.mp3), [mix](audio/mix.mp3) e [trilha própria](audio/trilha.mp3) ficam em `audio/`. Tratamento leve igual ao da amostra: filtro de 65 Hz, compressão 1,6:1 e volume alvo −18 LUFS. Apenas pausas sustentadas acima de 1,2 s foram encurtadas para aproximadamente 0,65 s. Não há alteração de velocidade ou tom. Voz final: −18 LUFS, LRA 3,1 LU, pico verdadeiro −2,6 dBTP; nenhum vazio abaixo de −40 dB por mais de 1,2 s foi detectado no MP3. Essas medições não substituem escuta. O usuário aprovou a amostra, não avaliou ainda a narração inteira. Não houve ASR independente completo nem alegação de escuta humana completa.

## Direção e projeto

[ROTEIRO.md](ROTEIRO.md), [bible de direção](story/bible.md) e [análise da referência](story/reference-analysis.md). Oficina, praça, diagramas, estação e espaço. Nico mantém jaqueta verde-menta; Lia usa violeta. O envelhecimento dela aparece no cabelo. A caixa, fotografia, cadeira, caderno, carrinho, roda, muda e mala são geometria/texturas desenhadas por código.

Ações usam tempo global da sequência, inclusive entre cortes. Dois segmentos por membro e alcance limitado; pés em apoio; fotografia e ferramentas ligadas às mãos mundiais. Câmeras de acompanhamento, pés, detalhe, vista superior, reação, contraplanos e órbita. CTAs do Então perto de 45 s, no meio e no encerramento. Sem lip sync do narrador.

Antialiasing habilitado (`fast3D: false`), luz fixa, sem opacidade pulsante, flashes repetidos, grão ou partículas aleatórias. Planos em folhas e amostras nativas de movimento foram inspecionados; isso não equivale a garantia subjetiva de ausência de todo artefato. QA e cobertura real em `qa/`.

## Reproduzir sem novas APIs

Da raiz do repositório:

```bash
python3 AiTrends/studio.py doctor
node AiTrends/skill/scripts/render.mjs --project "$PWD/AiTrends/projetos/05-imortal" --from 0 --to 6 --scale 1 --workers 1 --format jpeg --out /tmp/imortal-teste.mp4
```

O render é silencioso. Usar `audio/mix.mp3` existente para montar o MP4. O exportador compartilhado exige log completo de render, usa resolução nativa e valida os arquivos. Não executar `scripts/build_story.py` após a temporização final: ele recria o rascunho proporcional inicial. `generate_remaining.py` só é necessário para recuperar voz com cache privado de originais; não roda durante render/mix. Credencial exclusivamente no ambiente.

O [pacote YouTube](../../youtube/05%20-%20E%20se%20voc%C3%AA%20fosse%20imortal/) reúne capa, título, descrição/capítulos e tags. Não houve upload no YouTube.

Assets: roteiro, personagens, geometria, fotografia e sons próprios. Rig derivado do código próprio do episódio 04, com postura estendida, cabeça mais arredondada e transições de apoio. Motor/fontes aiTrends mantêm suas licenças originais. Referência externa foi guardada em área privada, sem redistribuição de frames, fala ou música. Verificação externa das páginas científicas foi bloqueada por 403 e está registrada em `qa/research-status.md`; não se declara pesquisa consultada com sucesso.

## Feedback posterior à entrega

O usuário informou “a voz ficou ok” e relatou algumas articulações toscas. Voz aceita; animação não aprovada integralmente. Esse feedback e a exigência de efeitos Python estão em [qa/FEEDBACK-USUARIO.md](qa/FEEDBACK-USUARIO.md) e na skill. Os arquivos entregues foram preservados.
