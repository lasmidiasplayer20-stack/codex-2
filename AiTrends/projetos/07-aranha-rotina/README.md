# 07 — E se uma aranha aprendesse sua rotina? / Então

<!-- CURRENT_STATUS_START -->
**Em produção. Seis blocos da Puck gerados; dois aguardam a cota gratuita do mesmo modelo.** Não existe ainda um filme completo com narração. Roteiro/cenas próprios completos e prévia inicial disponível abaixo. Retomada prevista para 28/10/2026 às 04h03 de Brasília, condicionada a este ambiente permanecer ativo. O horário não é promessa de conclusão.
<!-- CURRENT_STATUS_END -->

Ficção original de suspense com humor. Nico e Lia investigam uma aranha que parece antecipar os caminhos deles. A hipótese fantástica é declarada; o filme não é uma explicação científica de comportamento animal. Uma causa comum explica o apagão e o último plano preserva a ambiguidade.

## Conteúdo e visual

32 sequências e189 planos com geometria/rig/câmeras em JavaScript/Three.js no aiTrends. Apartamento contínuo: quarto, corredor, cozinha, sofá e mesa, janela/vaso, abajur/interruptor/cabo. Câmera humana, rodapé, macro da aranha, pés, vista superior, contracampo e revelações. Sem Blender ou bitmaps nos cenários. Aranha de oito pernas construída por código. Rig Nico/Lia revisado do06; não implica aprovação do usuário para todas as articulações.

A referência do Drive informa enquadramentos de suspense, mudança de escala e uso de objetos cotidianos. Roteiro, personagens, cenário, sons e montagem são próprios; não há reaproveitamento de fala, frames, trilha ou marca. Veja `input/reference-analysis.md`.

## Voz, duração e custo

Puck / `gemini-2.5-flash-preview-tts`, direção em português e tratamento/mix discretos já aceitos pelo usuário. Cinco blocos vieram da primeira credencial; a tentativa seguinte retornou429 diário. Uma segunda credencial enviada pelo usuário gerou o sexto bloco; a chamada seguinte também retornou429 diário. Todos os seis estão preservados, sem troca de voz/modelo ou ativação de cobrança. O texto dos blocos ainda não gerados foi condensado; os blocos anteriores ficam intactos, sem desperdício. Roteiro final: 1.270 palavras. Alvo: 8–9 min; duração exata depende da leitura natural, sem acelerar a voz.

`audio/partial-voice.json` registra áudio já existente, sem afirmar narração completa. Tempos dentro de cada bloco são aproximados por parágrafos/energia, não alinhamento exato por palavra. Nenhuma escuta humana integral ou ASR completo é declarado. Segredos e áudio bruto ficam fora do Git; scripts usam a variável de ambiente já configurada.

Foley original obrigatório em `scripts/sound.py`: passos, papel, vidro, tecido, cadeira, interruptor, trinco, cabo, celular e chaleira. Stems separados, 174 eventos iniciais, mix reproduzível. Nada de ruído alto de aranha em toda passada ou whoosh em todo corte. Trilha harmônica discreta; clímax sem aumento brusco de volume. CTAs por código aos43–51s, no meio e no fim.

## Arquivos

- `ROTEIRO.md`, `input/narracao.txt`: somente história em português; sem instruções no texto falado.
- `story/bible.md`, `beats.json`, `shots.json`: direção, continuidade e temporização.
- `scenes/`: cenário, cast/IK, animação e câmeras.
- `scripts/`: geração com cache, tratamento, Foley, metadados e retomada com guarda de fonte.
- `qa/`: inspeções, alcance real da revisão e validações técnicas.
- [Pacote YouTube](../../youtube/07%20-%20E%20se%20uma%20aranha%20aprendesse%20sua%20rotina/): capa neon no estilo aprovado e único arquivo `YOUTUBE`.

## Reprodução

Leia `../../skill/SKILL.md`. Dependências já verificadas com `python3 AiTrends/studio.py doctor`. Para renderizar, use o renderizador compartilhado com `--project` absoluto. O render sai silencioso; a exportação exige o áudio final e usa `../../skill/scripts/export.py`. Não execute `build_story` ou refaça tempos por cima da voz existente. `treat_available.py` serve apenas à prévia parcial; depois da voz completa, usar `treat_natural.py`. Chamadas de voz requerem a autorização já dada, chave de ambiente e cota disponível. Não repetir chamadas por429.

Fontes/licenças: motor aiTrends fornecido pelo usuário, Three.js e fontes do kit com suas licenças originais. Personagens/props/geometria/SFX próprios do projeto; capa gerada por ferramenta de imagem conforme estilo aprovado. Nenhuma licença nova sobre o kit é concedida.

## Prévia inicial disponível

[Assistir à prévia inicial de1min em1080p](exports/07%20-%20Previa%20inicial%201min.mp4). Usa os blocos reais da Puck e Foley Python. É uma prévia parcial; o filme completo ainda depende dos dois blocos de voz restantes. `qa/preview-validation.json` contém decode, dimensões, quadros e hash.
