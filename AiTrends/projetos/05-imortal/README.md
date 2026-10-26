# 05 — E se você fosse imortal?

**Em produção. Não é o episódio final.** Roteiro original em português, alvo de 8min30s, horizontal, 1920×1080/24 fps. Voz Puck preservada conforme pedido do usuário. Sem nova geração completa até avaliação da amostra.

## Avaliar o áudio primeiro

Uma única chamada Gemini gerou 20,13 segundos. As três versões abaixo usam exatamente essa geração:

- [01 — voz original](audio/01-voz-original.mp3)
- [02 — tratamento leve](audio/02-voz-tratamento-leve.mp3)
- [03 — com mix discreta](audio/03-voz-com-mix.mp3)

Nenhuma alteração de velocidade, tom ou remoção de pausas. Tratamento: filtro baixo de 65 Hz, compressão leve 1,6:1, normalização a −18 LUFS. A versão mix acrescenta harmonia discreta e um clique de madeira isolado, sintetizados em Python. A escolha do usuário continua pendente; medições não aprovam timbre nem naturalidade. Não reutilizar automaticamente o tratamento reprovado no episódio 04.

## Projeto e limites desta etapa

[ROTEIRO.md](ROTEIRO.md): 1.391 palavras; 32 sequências e 160 planos **provisórios**. Cenas implementadas: somente os cinco planos da abertura; os outros 155 ainda precisam de implementação e revisão. A narração completa, sincronização fina, CTAs no filme final, demais cenários, capa definitiva e export de um minuto não estão concluídos. Não executar render completo neste estado.

[Plano de direção](story/bible.md) e [análise da referência](story/reference-analysis.md). Referência externa guardada em área privada, sem redistribuição de vídeo/frames/fala. Sem transcrição independente completa do áudio original.

Abertura: geometria Three.js por código, personagem próprio, janela, mesa, caixa com tampa articulada, fotografia desenhada por código, aproximação/close/orbita. Tempo global contínuo entre cortes; mão e fotografia compartilham transformação mundial. Antialiasing habilitado (`fast3D: false`), iluminação fixa, sem opacidade pulsante, grão ou partículas aleatórias. Ainda é um piloto para avaliação, não aprovação do filme completo.

## Próxima etapa

Aguardar avaliação da voz conforme [regra da skill](../../skill/references/audio-and-temporal-quality.md), seção “Próxima produção”. Depois reutilizar o áudio aprovado, gerar somente trechos faltantes, ajustar texto e pausas em vez de acelerar, implementar e revisar o restante das cenas. Export final e preview de um minuto em 1080p somente após essas etapas.

Assets: geometria, fotografia, roteiro, sons e personagens próprios por código; rig derivado do código próprio do episódio 04 com ajuste de extensão das pernas e tesselação do crânio. Motor aiTrends e fontes mantêm as licenças fornecidas no kit. Não há fotos ou personagens importados da referência.
