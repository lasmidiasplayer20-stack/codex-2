---
name: entao-animation-studio
description: Produzir episódios próprios do canal Então com o aiTrends local, voz Puck, cenas por código e exportação nativa 1080p.
---

# Estúdio do Então — leia primeiro em outro chat

Repositório: `lasmidiasplayer20-stack/codex-2`. Raiz deste pacote: `AiTrends/`. Esta é uma skill local versionada, não um plugin automaticamente instalado na interface. Um novo chat deve acessar o GitHub/clonar o repositório e ler este arquivo explicitamente. O código do projeto anterior é referência de implementação, não roteiro para copiar.

## Prioridade de qualidade — feedback do usuário

O episódio **04 — Quanto Tempo Resta foi reprovado pelo usuário no áudio e apresentou cintilação em parte da animação**. Seus resultados técnicos não representam aprovação editorial. Antes da próxima produção, leia obrigatoriamente [áudio, estabilidade temporal e controle de créditos](references/audio-and-temporal-quality.md).

Para o próximo vídeo: uma amostra de voz de 20–30 s, comparação local de voz original/tratada/mix e avaliação do usuário **antes de gerar a narração completa**. Renderizar também uma amostra em movimento para avaliar cintilação antes do render longo. Reaproveitar cache; corrigir trechos isolados; não repetir gerações completas nem presumir que a cadeia do episódio 04 foi aprovada. O usuário enviará outra referência; este feedback não autoriza regenerar o vídeo atual.

Amostra aprovada posteriormente: `../projetos/05-imortal/audio/03-voz-com-mix.mp3`, Puck / `gemini-2.5-flash-preview-tts`, resposta do usuário “Aprovada com mix discreta”. Preservar esse perfil; aprovação da amostra não é aprovação editorial automática do episódio completo.

## Organização canônica

- `AiTrends/projetos/NN-slug/`: roteiro, configuração, `story/`, `scenes/`, `input/`, `audio/`, `exports/` e `qa/` daquele episódio.
- `AiTrends/youtube/NN - Título/`: `capa.jpg`, `titulo.txt`, `descricao.txt`, `tags.txt` com vírgulas e `metadata.json`.
- `AiTrends/skill/`: este guia, scripts compartilhados e cópias atribuídas das referências do kit.
- Referência atual: `../projetos/05-imortal/`, com amostra Puck + mix discreta aprovada. Anteriores: `../projetos/04-quanto-tempo-resta/` (áudio reprovado/cintilação relatada), `../projetos/03-10x-mais-rapido/` e `../projetos/02-quantas-mentiras/`.
- Os antigos pacotes em `Animação/youtube/` continuam preservados. Novos pacotes ficam em `AiTrends/youtube/`.

Use o próximo número livre. Preserve projetos existentes. Nunca publique intermediários, arquivos de chaves, `.env`, tokens ou configurações de conta. Use `GEMINI_API_KEY` do ambiente; não peça para colar uma chave em uma mensagem.

## Ambiente e referências

Da raiz do repositório, rode `python3 AiTrends/studio.py doctor`. Só rode `setup` quando faltarem dependências. Python para scripts de áudio: `AiTrends/.venv/bin/python`. Node, FFmpeg/FFprobe e Chromium são usados localmente. Sem After Effects, ferramentas exclusivas do Claude ou Blender nesta produção.

Leia `../README-CODEX.md`, `../codex-skills/animation-studio/SKILL.md` e `references/{engine-api,style-bible,story-breakdown,sound-design,render-qc}.md`. Essas referências vêm do pacote aiTrends fornecido pelo usuário; as condições originais continuam válidas. Este guia não amplia direitos sobre o kit ou assets. Fontes do kit preservam OFL; ícones fornecidos, se usados, preservam MIT.

## Direção que o usuário espera

Personagens próprios com identidade e cores constantes. Construir imagens por código: geometria, rig, câmera, faces, props, iluminação e efeitos. Não importar personagens ou frames dos vídeos de referência. O episódio 03 mostra um caminho com 3D real, materiais estilizados, cenários claros e diagramas curtos. Manter o feeling de aventura/curiosidade e escrever cenas novas.

Movimento não é apenas zoom: personagens precisam deslocar-se no cenário, manipular objetos e reagir. Use acompanhamento lateral, câmera baixa nos pés, aproximações, órbitas, vista superior com trajetórias e detalhes físicos. Objetos em contato devem usar a posição real da mão/pé. Não reinicie o estado de uma ação em cada corte; use tempo global da sequência. A narração não deve sair da boca dos personagens como se fosse diálogo.

Articulações: dois segmentos de comprimento fixo, cotovelos/joelhos com lado de dobra estável; limite alcance. Combine deslocamento com apoio do pé. Em assentos, altura do quadril e do assento devem coincidir, mantendo pés no chão. Confira enquadramento de cabeça em planos sentados e objetos em primeiro plano para não bloquear rostos. Não finalize um filme com os personagens correndo parados no mesmo lugar.

Ritmo: 15–25 planos por minuto; ação e detalhes podem ser mais curtos. Diagramas devem mostrar processos, trajetórias e valores animados. Não sustentar o mesmo quadro de cartões durante longos trechos. Efeitos precisam ter função: rastros, poeira, onda de impacto, objeto em suspensão e câmera lenta nos momentos certos. Evite blocos opacos de partículas e explosões de texto.

## Roteiro, voz e sincronização

Crie `ROTEIRO.md`, `input/narracao.txt`, `story/bible.md`, `story/beats.json` e `story/shots.json`. `input/narracao.txt` contém somente o que deve ser falado — sem instruções, nomes de arquivos, notas de programação ou direção. Explicite hipóteses e limites em assuntos científicos; não copie estatísticas sem verificar. Não transcreva/reutilize integralmente a narração de outro canal.

Voz de preferência histórica: **Gemini Puck**, português brasileiro, curiosa/alegre e com volume estável. O áudio do episódio 04 foi reprovado; validar a nova amostra e o tratamento conforme a seção de prioridade antes de usar o mesmo pipeline em outro episódio. Só gere se houver autorização para usar a API e a chave estiver disponível no ambiente; reutilizar o áudio pronto não chama a API. Nunca habilite cobrança para superar uma cota. Cota diária: pare, registre e tente apenas modelo gratuito compatível quando autorizado pelo contexto; não fique repetindo a chamada com cota diária esgotada. Para preservar timbre, use o mesmo modelo em todos os trechos do episódio.

Exemplos (caminhos absolutos em `--project` e diretório privado em `--work`):

```bash
python3 AiTrends/skill/scripts/generate_voice.py --project /CAMINHO/DO/PROJETO --work /tmp/voz-episodio --model gemini-3.1-flash-tts-preview --api generateContent
AiTrends/.venv/bin/python AiTrends/skill/scripts/treat_voice.py --project /CAMINHO/DO/PROJETO --work /tmp/voz-episodio --target 510
```

O gerador usa blocos de até quatro sequências, cache por texto/modelo e não registra credenciais. O tratamento reduz pausas excessivas, nivela volume, comprime moderadamente e recalibra a duração sem mudar o tom. Os limites dos trechos são reais; divisão entre parágrafos usa proporção do texto e mínimos de energia próximos. Isso é temporização aproximada, não alinhamento exato por palavra. Não repita o gerador de storyboard inicial depois dessa etapa sem intenção de refazer a temporização.

## Render e qualidade

`scripts/render.mjs` é uma adaptação do renderizador aiTrends: usa o mesmo player, registro de cenas, fontes, rig e Three.js. Resolve o kit em `aitrends-2d-studio/skills/make-2d-video/kit/`. O estilo opcional `runtime-style.json` pertence ao projeto; `fast3D` desativa MSAA em software, mantendo a resolução real. Após a queixa de cintilação, essa opção exige comparação em movimento com antialiasing habilitado; velocidade de render não substitui qualidade temporal. Um estágio 3D pode usar render direto e sombras de contato por geometria para reduzir custo de CPU. Não simule 1080p ampliando um render menor.

```bash
node AiTrends/skill/scripts/render.mjs --project /CAMINHO/DO/PROJETO --sheet --scale 0.3 --format jpeg
node AiTrends/skill/scripts/render.mjs --project /CAMINHO/DO/PROJETO --from 0 --to 6 --scale 1 --workers 1 --format jpeg --out /tmp/teste-nativo.mp4
node AiTrends/skill/scripts/render.mjs --project /CAMINHO/DO/PROJETO --scale 1 --workers 2 --format jpeg --preset fast --crf 20 --out /tmp/filme-silencioso.mp4
```

Inspecione as imagens reais, incluindo poses de contato, antes do render longo. Abra folhas completas e uma amostra de movimento; corrija erros e cenas ausentes. O render é determinístico por quadro e os diretórios de partes são separados por intervalo. Não execute dois renders do mesmo intervalo no mesmo projeto simultaneamente. Em CPU, use no máximo dois workers; publique uma estimativa baseada no log, sem prometer prazo antes do teste nativo.

O render produz vídeo silencioso. Música e SFX são sintetizados em Python; misture com a Puck tratada, mantendo clareza e sem saturação. Faça MP4 completo e prévia de cerca de um minuto **a partir do arquivo final**, ambos em 1920×1080/24 fps. Verifique codecs, duração, contagem de quadros e decodificação completa com FFmpeg `-xerror`. Confirme imagens do próprio MP4 final, não somente do player. Registre cobertura real da análise de áudio; não afirme escuta humana ou ASR completo se não ocorreu.

## Canal e entrega

Canal: **Então**. CTAs visuais por código perto de 45 s, no meio e no encerramento, legíveis e sem cobrir rostos. Clique/sino discretos; CTA falado no encerramento se fizer sentido no roteiro. Nunca inclua o nome ou o CTA do canal de referência.

Prepare capa própria 16:9 (1280×720, JPEG abaixo de 2 MB), título complementar, descrição com capítulos e tags separadas por vírgulas em `AiTrends/youtube/`. Capa não precisa ser frame do vídeo, mas deve representar a premissa. Preserve originalidade de composição e não copie marcas.

Quando o pedido autorizar publicação no GitHub, publique projeto, áudio tratado reutilizável, MP4 completo, prévia e evidências de QA. Não publique no YouTube sem solicitação explícita. Faça alterações apenas no escopo do pedido. Verifique o push e a revisão remota antes de declarar a entrega publicada. Termine com links diretos para vídeo, prévia, projeto e pacote YouTube.

## Comandos de áudio e entrega compartilhados

```bash
AiTrends/.venv/bin/python AiTrends/skill/scripts/sound.py --project /CAMINHO/DO/PROJETO
AiTrends/.venv/bin/python AiTrends/skill/scripts/export.py --project /CAMINHO/DO/PROJETO --silent /tmp/filme-silencioso.mp4 --work /tmp/entrega-episodio
```

Guarde o log de render em `--work/full-render.log`. O exportador exige marcador de sucesso, verifica o MP4 completo, limita tamanho para GitHub, faz preview e extrai imagens do arquivo final. `sound.py` é exemplo sonoro do episódio 03; adapte eventos e temas para cada história, sem reutilizar cegamente a mesma trilha. Veja também `references/rig-and-action.md`.

Para abrir pastas do próximo episódio sem sobrescrever os anteriores: `python3 AiTrends/skill/scripts/new_project.py "Título" --seconds 510 --copy-cast`. Isso cria uma estrutura vazia e, opcionalmente, copia o rig/cenário próprios. Não cria roteiro, narração ou cenas prontas. Reescreva a ação e confira o próximo número antes de renderizar.

Preferir um modelo de voz por episódio. O episódio 03 documenta uma exceção: cota diária após sete trechos exigiu o mesmo timbre Puck em outro modelo no trecho final. Não afirmar identidade perfeita entre modelos; tratar e revisar a transição. `scripts/audit_voice.py` permite transcrição local independente se o modelo Whisper puder ser baixado; falha do download deve ser registrada, não apresentada como auditoria aprovada.

## Evolução do episódio 04

Consulte `../projetos/04-quanto-tempo-resta/scenes/` para braços com IK tridimensional, cenários com objetos instanciados, parede oposta habilitada nos contraplanos e visores que evitam rostos. `config.json` pode definir `qaTimes` e `qaStills` para imagens de QA específicas do tema. Evite herdar rótulos e instantes do episódio anterior sem conferir o conteúdo.

## Voz reafirmada — episódio 05

Em 26/10/2026, o usuário reafirmou manter a voz Puck do início, reduzir oscilações e evitar vazios longos. Não interpretar como autorização para trocar o timbre ou como aprovação de uma amostra ainda não ouvida. No caminho `generateContent` do helper compartilhado, a orientação de estilo não era enviada: enviar direção de narração explícita no prompt nos próximos trechos. Isso é uma falha de implementação constatada, não diagnóstico completo da reprovação do episódio 04. Amostra 05: uma geração, variantes locais, sem acelerar nem cortar pausas; avaliação ainda pendente.

## Episódio 05 — amostra aprovada e áudio natural

O usuário aprovou explicitamente `05-imortal/audio/03-voz-com-mix.mp3`: **“Aprovada com mix discreta”**. Esse arquivo passa a ser a referência curta aprovada para Puck e mix discreta. A aprovação cobre a amostra; não declarar aprovação editorial automática do filme ou voz completos. Registrar arquivo avaliado e resposta. Abertura reutilizada; oito blocos restantes no mesmo modelo, sem nova geração do trecho bom.

No episódio 05, a leitura natural ultrapassou o alvo inicial: 590,625 s. Não aceleramos a fala. Tratamento leve: filtro 65 Hz, compressão 1,6:1, −18 LUFS. Encurtamos somente vazios sustentados >1,2 s para ~0,65 s; as pausas curtas foram preservadas. Isso atende ao pedido de evitar longos vazios; não confundir com remoção agressiva de todas as respirações. Mistura com harmonia espaçada e Foley muito discreto, sem pulsação sonora insistente.

O helper `generate_voice.py` agora envia orientação de leitura também no caminho `generateContent`; caches antigos são preservados, sem regeneração automática. `new_project.py` passa a criar projetos com `fast3D: false` para manter MSAA. O exportador lê `config.ctaSeconds`, evitando relatar os tempos de outro episódio quando a duração muda.

Novo projeto de referência: `../projetos/05-imortal/`, com caixa articulada, fotografia por código, envelhecimento visual da amiga, cadeiras/rodas/plantas/mala, diagramas e cenas espaciais. Não copiar seu roteiro em outros episódios. Manter o procedimento de amostra de áudio e teste temporal do guia; não usar a reprovação do episódio 04 como padrão aprovado.

Perfil exato aprovado no episódio 05: Puck / `gemini-2.5-flash-preview-tts` / `generateContent`, direção explícita em português e mix discreta. Para duração de 8min30s com esse ritmo natural, estimar 1.150–1.230 palavras, depois validar a amostra; o episódio 05 mostrou que 1.391 palavras ultrapassam esse alvo. Não usar o alvo antigo de 165 palavras/min sem conferir o perfil real.
