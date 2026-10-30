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

## Feedback mais recente — aplicar ao episódio 06

Após o episódio 05, o usuário informou **“algumas articulações ficaram toscas, a voz ficou ok”**. A voz Puck e seu tratamento estão aceitos; a animação não recebeu aprovação geral. Não copiar o rig do 05 sem revisar marcha, cotovelos, joelhos, alcance, apoio e transições em movimento. Leia [a revisão obrigatória de articulações e efeitos Python](references/joints-and-python-foley.md).

**Efeitos sonoros devem ser criados em Python e fazer parte da entrega.** Mapear passos, contatos de mão/objeto, madeira/ferramentas, água/vento, mecanismos e transições motivadas aos eventos da cena. Trilha musical e voz sozinhas não cumprem essa etapa. Salvar script reproduzível, stem de SFX e lista de eventos com instante/duração/ganho; conferir presença real na mix e inteligibilidade da voz. Não substituir todos os sons por bipes repetidos ou efeitos inaudíveis.

Preservar o perfil vocal aprovado. A aprovação já dada não precisa ser pedida de novo para a mesma voz/modelo/tratamento; novas variantes de voz ou mudanças de modelo exigem amostra antes do lote. Reaproveitar cache e limitar chamadas.

## Organização canônica

- `AiTrends/projetos/NN-slug/`: roteiro, configuração, `story/`, `scenes/`, `input/`, `audio/`, `exports/` e `qa/` daquele episódio.
- `AiTrends/youtube/NN - Título/`: `capa.jpg` e um único arquivo **`YOUTUBE`**, sem extensão, com seções TÍTULO, DESCRIÇÃO e TAGS (tags separadas por vírgulas). Esse é o formato solicitado a partir do episódio 06; preservar os pacotes antigos.
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

## Capas — padrão visual pedido pelo usuário

O usuário mandou refazer a capa do episódio 05 no estilo da imagem “QUEM ESTÁ MENTINDO?” e, após ver a nova versão neon, aprovou: **“ok, deixe esse estilo salvo”**. Esse é o padrão visual das próximas capas. Referência própria atual: `../youtube/05 - E se você fosse imortal/capa.jpg`. Leia [youtube-cover-style.md](references/youtube-cover-style.md).

Priorizar ilustração rica, iluminação cinematográfica neon, contornos fortes, rosto expressivo grande e texto curto em branco/amarelo com borda preta. Preservar identidade e cores de nossos personagens. Adaptar composição, fundo e elementos à premissa; não repetir os contadores de mentira ou a roupa amarela de outro canal. A capa simplificada procedural anterior do 05 fica como histórico, não como estilo a repetir.

## Canal e entrega

Canal: **Então**. CTAs visuais por código perto de 45 s, no meio e no encerramento, legíveis e sem cobrir rostos. Clique/sino discretos; CTA falado no encerramento se fizer sentido no roteiro. Nunca inclua o nome ou o CTA do canal de referência.

**Formato de metadados pedido pelo usuário:** reunir título, descrição e tags em um único arquivo chamado `YOUTUBE` (sem extensão), na subpasta YouTube do episódio. Não criar novos `titulo.txt`, `descricao.txt` e `tags.txt` separados. A capa fica ao lado.

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

Em 26/10/2026, o usuário reafirmou manter a voz Puck do início, reduzir oscilações e evitar vazios longos. Não interpretar como autorização para trocar o timbre ou como aprovação de uma amostra ainda não ouvida. No caminho `generateContent` do helper compartilhado, a orientação de estilo não era enviada: enviar direção de narração explícita no prompt nos próximos trechos. Isso é uma falha de implementação constatada, não diagnóstico completo da reprovação do episódio 04. Amostra 05: uma geração, variantes locais, sem acelerar nem cortar pausas; registro histórico anterior à aprovação posterior documentada abaixo.

## Episódio 05 — amostra aprovada e áudio natural

O usuário aprovou explicitamente `05-imortal/audio/03-voz-com-mix.mp3`: **“Aprovada com mix discreta”**. Esse arquivo passa a ser a referência curta aprovada para Puck e mix discreta. A aprovação cobre a amostra; não declarar aprovação editorial automática do filme ou voz completos. Registrar arquivo avaliado e resposta. Abertura reutilizada; oito blocos restantes no mesmo modelo, sem nova geração do trecho bom.

No episódio 05, a leitura natural ultrapassou o alvo inicial: 590,625 s. Não aceleramos a fala. Tratamento leve: filtro 65 Hz, compressão 1,6:1, −18 LUFS. Encurtamos somente vazios sustentados >1,2 s para ~0,65 s; as pausas curtas foram preservadas. Isso atende ao pedido de evitar longos vazios; não confundir com remoção agressiva de todas as respirações. Mistura com harmonia espaçada e Foley muito discreto, sem pulsação sonora insistente.

O helper `generate_voice.py` agora envia orientação de leitura também no caminho `generateContent`; caches antigos são preservados, sem regeneração automática. `new_project.py` passa a criar projetos com `fast3D: false` para manter MSAA. O exportador lê `config.ctaSeconds`, evitando relatar os tempos de outro episódio quando a duração muda.

Novo projeto de referência: `../projetos/05-imortal/`, com caixa articulada, fotografia por código, envelhecimento visual da amiga, cadeiras/rodas/plantas/mala, diagramas e cenas espaciais. Não copiar seu roteiro em outros episódios. Manter o procedimento de amostra de áudio e teste temporal do guia; não usar a reprovação do episódio 04 como padrão aprovado.

Perfil exato aprovado no episódio 05: Puck / `gemini-2.5-flash-preview-tts` / `generateContent`, direção explícita em português e mix discreta. Para duração de 8min30s com esse ritmo natural, estimar 1.150–1.230 palavras, depois validar a amostra; o episódio 05 mostrou que 1.391 palavras ultrapassam esse alvo. Não usar o alvo antigo de 165 palavras/min sem conferir o perfil real.

## Episódio 06 — mesma Puck, cota e Foley

O usuário escolheu “Aguardar a mesma voz/modelo” depois de o servidor confirmar HTTP 429 por cota diária gratuita (10 chamadas do modelo nessa conta). Não trocar de modelo nem gerar repetidamente antes da hora de liberação indicada pelo serviço. Dois blocos já existem em cache e devem ser reaproveitados. O estado do próximo episódio fica em `../projetos/06-recomecar-humanidade/README.md`.

O projeto 06 contém Foley Python em stem próprio `audio/sfx.mp3` e manifesto `audio/sfx-events.json`, além de música e mix separadas. Passos seguem distância de marcha; contatos incluem rádio, papel, água, caixas e madeira. Não voltar à mistura sem eventos de ação. O rig foi revisado, mas não chamar a nova animação de aprovada pelo usuário só porque passou em cálculos ou decode.

A retomada após cota pode usar `scripts/resume_after_quota.py` do próprio projeto: cache, fonte congelada, seis blocos faltantes, sem fallback/billing/retries contínuos, render e export nativos e publicação autorizada. É um processo no ambiente, não serviço externo durável; fonte alterada ou erro interrompe a fila. Não declarar vídeo completo antes de `qa/export-validation.json` e push confirmado.

## Episódio 07 — suspense e limites de voz

Nova referência: `../projetos/07-aranha-rotina/`, investigação original sobre aranha que aprende hábitos como hipótese fantástica. Declarar ficção, separar observação de interpretação e não apresentar regras de terror como biologia. Câmera de rodapé/macro precisa preservar legibilidade, escala dos objetos e continuidade. Aranha deve caber no copo. Conferir restauração de visibilidade de personagens após inserts e se móveis bloqueiam o assunto. Manter luz estável; apagar abajur uma vez não exige strobe.

Foley Python segue obrigatório, com sons de papel, vidro, tecido, madeira, interruptor, cabo e passos sincronizados. Não adicionar som exagerado a cada perna da aranha. Preservar Puck/modelo/mix aceitos. Cota é contada por chamadas ao modelo/projeto, não por número de vídeos; assinatura do aplicativo Gemini e faturamento da API são separados. O servidor reportou limite gratuito diário de10solicitações neste projeto; cinco blocos do07 foram preservados antes de429, sem troca de modelo ou ativação de cobrança. O usuário já escolheu aguardar o mesmo modelo. Os três blocos ainda não gerados foram condensados para orçamento de duração; não regenerar os cinco bons. Estado definitivo no README/QA de cada projeto, sem confundir prévia com filme completo.

No teste de uma segunda credencial fornecida pelo usuário para o07, um sexto bloco foi gerado; a chamada seguinte retornou429 diário novamente. Restam dois blocos. Não inferir que uma nova chave garante nova cota: limites de API podem ser compartilhados por projeto. Não imprimir credenciais de qualquer formato ao inspecionar anexos; extrair de forma privada e retornar somente estado redigido.

## Feedback do episódio 07 — finalizar sem novas tentativas

O usuário percebeu que a voz ficou diferente no final e supôs que a geração em momentos distintos contribuiu; a causa não foi confirmada. Pediu prosseguir com o vídeo porque não quer esperar múltiplas correções. **Finalizar o07 com a voz atual, sem novas chamadas ou amostras e sem reiniciar o render.** Essa decisão não aprova a consistência geral do áudio. Registro em `../projetos/07-aranha-rotina/qa/voice-consistency-feedback.json`.

Para os próximos episódios, planejar cota antes do lote e preferir gerar os blocos na mesma sessão, com modelo, voz e direção idênticos. Isso reduz uma variável, mas não garante timbre idêntico entre chamadas. Preservar os bons trechos e conferir transições localmente, comparando final/início de blocos; só ajustar ganho, pausas e mix quando necessário. Não disparar ciclos de regeneração para perseguir uma voz perfeita.

## Episódio08 — modo criativo, duração e continuidade

Referência original `../projetos/08-modo-criativo/`:169planos, câmera de voo/orbita, cidade miniatura, macros de criação e transferência, ilha/ponte e plataforma celeste, com nossos Nico/Lia. A referência de10min49s foi condensada para narração de509,083s; limite explícito do usuário:10min. Orçar palavras antes da API e verificar duração real antes do render, sem acelerar a voz para caber.

Após variação percebida no final do07, usamos a mesma Puck/modelo/direção em quatro blocos maiores na mesma sessão/credencial, em vez de oito blocos separados. Sem regenerações. Isso reduz transições, mas não comprova timbre idêntico nem substitui a avaliação do usuário. Registrar limites da revisão. Não criar nova rodada de voz só para ajustar mix.

Voo: compensar inclinação da cabeça, manter braços alcançáveis, não usar marcha no ar e projetar sombra no apoio correto. Ponte: interpolar altura de apoio, não saltar a raiz. Props: câmera mira no centro útil do objeto, não no pé do grupo; seguradas e entregas usam mãos após IK. Maquetes/construções devem alterar peças, não apenas trocar textos. Manter Foley Python e pacote YouTube único no padrão já aprovado.

## Episódio08 — feedback de aspereza/megafone e revisão de mix

Mesmo com Puck no mesmo modelo/sessão, o usuário percebeu no final som alto, áspero e sintético, lembrando megafone. Não tratar ausência de amostras saturadas como prova de boa sonoridade. A causa perceptiva exata não foi confirmada. Corrigimos localmente, sem novas chamadas: equalização suave de médios/agudos por bloco, ganho estático mais baixo e último bloco discretamente mais baixo, sem acrescentar compressão ou alterar tempo/tom. Referências em `../projetos/08-modo-criativo/scripts/remix_voice.py` e `audio/remix-quality.json`. Não declarar que todo caráter sintético foi eliminado ou que essa revisão foi aprovada pelo usuário sem avaliação.

Futuras revisões de mix devem reaproveitar a voz. Preservar a fonte anterior em área privada, verificar verdadeiros picos/níveis/aspereza entre blocos e manter folga para codecs. Trocar áudio na montagem final sem reiniciar render de imagens quando o tempo não mudou. Evitar compressão extra ou normalização dinâmica que façam a voz bombear para cima e para baixo.

## Shorts — episódio09, gravidade no elevador

Referência reutilizável: `../projetos/09-elevador-gravidade-zero/`. Short próprio vertical1080×1920,24fps, exatamente60s/1440quadros. Não usar o exportador horizontal sem adaptar as verificações. Um short de60s já serve como prévia de um minuto; não exigir duplicata idêntica. Orçar fala abaixo do minuto, preservar velocidade/tom e distribuir pequenos intervalos em pausas reais, com ações visuais; não deixar um grande vazio no fim. Perfil Puck/modelo mantido, uma única geração e mix com ganho estático/folga, sem compressor adicional.

Gramática adaptada das referências: corte de cabine para poço, mecanismo por dentro, escala geral/detalhe, objetos soltos e reações. Não copiar personagens ou roteiro. Ao agarrar o mesmo objeto, usar a mão correta de cada ator, calcular alvos em espaço local e verificar a distância entre as palmas após IK/rotação. Separar hipótese fantástica de gravidade nula e ausência de peso aparente em queda livre.

**Correção explícita do usuário para Shorts:** capa também vertical9:16/1080×1920. Não aplicar o padrão horizontal1280×720 dos vídeos longos a um short. Manter capa e export coerentes com o formato pedido.

## Short10 — pausa temporal

`../projetos/10-pausar-o-tempo/`:20planos, pausa fictícia de10segundos ampliada em câmera lenta para um short60s. Fixar tempo de animação da pessoa congelada (incluindo piscar/respiração do rig), objetos e gotas; a câmera e o protagonista continuam. Reinicializar também rotações de objetos em cada draw para garantir render determinístico ao voltar a um instante anterior. Retomar estado por tempo global, não reiniciar a queda em cada corte.

Foley Python específico (relógio, tênis, tecido, água, ambiente que cessa/retorna), mesma Puck em uma chamada, ganho estático e EQ suaves. Capa vertical9:16. Distinguir fantasia com regras próprias de explicação física real. Revisar enquadramento geral vertical para não cortar personagem lateral e esconder props não relacionados em inserts do relógio.

## Short11 — cenário vivo, sombra e CTA fornecido

`../projetos/11-sombra-vontade-propria/`: rua mais viva/colorida por pedido explícito do usuário. Preferir fachadas/toldos/plantas/objetos com paleta variada e alguns movimentos suaves de fundo; preservar áreas limpas em torno da ação principal. Silhueta derivada do rig por projeção no piso, com pose própria e contato visual legível. Não deixar props de janela flutuando em inserts quando a fachada está oculta. Garantir que a tentativa de pisar realmente alcance o local anterior da sombra, e que o personagem já tenha saído antes do impacto cartoon.

O usuário forneceu e pediu usar o CTA verde da pasta Drive. Asset reutilizável selecionado: `../projetos/11-sombra-vontade-propria/assets/cta-green.mp4`,7s; origem em cta-provenance.json. Aplicar chroma key/despill somente ao asset e compor pequeno na zona inferior; não remover verde da cena inteira. Exemplo vertical: janela650px, x60/y1490, desenho principal perto de metade da largura do frame. Conferir resultado no MP4 final, sem retângulo verde e sem cobrir rostos. Áudio do asset é dispensável; neste11 os cliques/sino vêm de Python para não disputar com a Puck. Adaptar duração/posições ao enquadramento de cada vídeo.

## Short12 — nuvem e novo tamanho/tempo do CTA

`../projetos/12-nuvem-particular/`: rua colorida, nuvem própria, chuva fina instanciada, guarda-chuva e jardim que muda gradualmente. Gotas cobertas pelo dossel devem ser bloqueadas; varetas e tecido fecham no mesmo grupo. Poças ficam ancoradas no cenário, sem seguir a raiz do personagem. Em mudanças de direção, relacionar fase da marcha à distância acumulada e suavizar o giro.

**Pedido mais recente do usuário para CTA:** maior e mais centralizado, aos15s e perto do final. Configuração atual de referência em vertical1080×1920: janela900px, x90/y1440,15–22s e53–60s, usando o mesmo asset verde com chroma key/despill. Esta preferência substitui a composição pequena à esquerda usada no11, salvo novo pedido. Conferir cenas reais do MP4 final para manter rostos e ação principal livres. Continuar com Puck/modelo aceitos, mix sem bombeamento e Foley Python.

### Correção de direção da chuva — feedback do usuário no12

A primeira entrega do12 tinha fase de partículas que aumentava a altura: chuva subindo. Inverter a fase vertical e orientar o traço conforme a trajetória de queda. Não confiar só em stills ou amostras espaçadas: verificar quadros consecutivos e o sinal do deslocamento vertical de cada gota, separando o salto de reposição do chão para o topo. Evidência corrigida: `../projetos/12-nuvem-particular/qa/rain-direction-validation.json` e `chuva-queda-consecutiva.jpg`. Reutilizar narração/mix/CTA, sem novas chamadas para corrigir uma animação.

No12, a checagem independente de pixels também distinguiu o erro: deslocamento dominante−62px/quadro na versão anterior e+60px/quadro no piloto corrigido (eixo vertical de imagem cresce para baixo). `scripts/audit_rain_pixels.py` mede máscara de chuva em tomada estacionária; ajustar ROI/tempo antes de aplicar a outro projeto ou câmera em movimento.


## Short13 — para-raios,90segundos e consistência de voz

Pedido explícito do usuário: permitir90segundos neste episódio, preservar CTA em vídeo e corrigir diferenças percebidas entre trechos da narração. Referência `../projetos/13-escolher-o-raio/`: preferir uma única geração de fala para uma duração curta, mesma Puck/modelo/direção aceitos. Isso elimina emendas de chamadas distintas, mas não garante timbre perfeitamente constante; não declarar aprovação sem retorno do usuário. Ganho estático/EQ suave, sem acelerar voz ou acrescentar compressão para perseguir volume. Reaproveitar fonte para revisões de mix.

Duração excepcional90s =2160quadros/24fps, vertical1080×1920; não retornar automaticamente ao alvo60s neste projeto. CTA fornecido900px centralizado emx90/y1440,15–22s e81–88s. Pacote YouTube com capa9:16 e arquivo únicoYOUTUBE. Foley Python continua obrigatório.

Diagramas subterrâneos: ocultar piso/terreno que encobre o assunto, mantendo um corte de solo atrás dos condutores. Rodas de partículas em anéis devem representar propagação ilustrativa, não escala física. Diferenciar poder fictício de segurança real. Não apresentar haste solta como sistema completo, não afirmar que puxa todos os raios e não sugerir árvores como abrigo. Conferir que o encerramento realmente mostre personagens dentro do abrigo, afastados da janela. Sem estrobos: descarga ilustrada estável, iluminação/exposição constantes.

No13, uma única chamada ainda apresentou subida gradual de volume: diferença6,28dB entre medianas RMS de janelas ativas. Corrigimos localmente com curva lenta de ganho pré-calculada, resultando0,70dB na mesma comparação. Evidência em `../projetos/13-escolher-o-raio/audio/consistency-check.json`. Portanto, uma única chamada reduz emendas, mas não substitui checagem de nível ao longo do áudio. Preservar dinâmica de sílabas/frases, evitar AGC rápido e não confundir uniformidade medida com naturalidade de timbre comprovada.


## Short14 — geladeira, ações e narração medida por episódio

`../projetos/14-geladeira-porta-aberta/`:90s verticais como continuação do13,27takes próprios numa cozinha colorida. Priorizar ações reais com props: maçaneta da porta articulada seguida pela mão; ventilador carregado/empurrado por personagens; vento orientado da cabeça do ventilador para a pessoa, não no sentido oposto. Preservar continuidade da posição dos objetos entre os cortes. Biela-manivela do compressor deve manter comprimento da biela, não esticá-la para alcançar o pistão.

Macros técnicos: remover oclusores do cenário/carcaça para ver o mecanismo. Escolher o lado da câmera que mostre pistão/biela, sem filmar através de uma placa opaca. Não usar só cenas gerais ou personagem parado explicando; alternar deslocamentos, contato, reação, interior do aparelho e câmera em movimento.

Puck em uma chamada, mesma direção/modelo. **Nunca copiar a curva de correção de ganho do episódio anterior:** medir a nova fonte. No14, variação de nível medida3,20dB→0,60dB com correção lenta pré-calculada, sem acelerar a fala ou adicionar compressor. Isso não comprova identidade perfeita de timbre; manter limites da revisão explícitos. Foley Python e CTA em vídeo continuam obrigatórios,900px centralizado aos15–22s e81–88s neste90s.

Revisão14: ao puxar a porta, Nico anda para trás; inverter a progressão da fase de marcha sem alterar o contato da mão. Não manter a passada para frente enquanto a raiz recua. Se for necessário corrigir só alguns takes após o render, substituir intervalos por quadros nativos e registrar a montagem/fonte final, preservando áudio. No termômetro, `.scale.y` substitui a altura anterior da malha: calcular comprimento/centro para a coluna vermelha crescer dentro da caixa, mantendo a base fixa. Não multiplicar visualmente a escala sem considerar dimensões existentes.


## Short15 — inércia, fatos e dois CTAs diferentes

`../projetos/15-enxergar-a-inercia/`:90s verticais,24takes, carro em corte e pista fechada. Usuário reafirmou cuidado com narração/ângulos/dinamismo e pediu conteúdo realmente informativo, sem informações inventadas. Conferir física em fonte rastreável: neste15, OpenStax oficial lido via git, arquivo/commit em `story/references.json`; registrar bloqueios de páginas sem fingir consulta. Não inventar velocidades, forças, percentuais ou detalhes universais de mecanismos. A silhueta é uma sobreposição explicativa, não um corpo que atravessa o cinto; rotular enquanto aparece. Inércia não é força extra empurrando a pessoa. Ocupantes reais afivelados antes de o carro andar. Cinto por ombro/peito e baixo no quadril, jamais encenar uso incorreto como solução.

Mãos alcançáveis no volante/fecho, rodas giram pela distância real do carro, direção do deslocamento da silhueta/mochila coerente com frenagem. Mover árvores para fora da linha da câmera e retirar travessas que escondam rostos nos cortes internos. Bagagem deve caber no trajeto, sem atravessar bancos/pessoas. Mecanismo de catraca é exemplo, com aviso de variações; evitar apresentação como projeto universal.

**Novo pedido: dois CTAs DIFERENTES do vídeo fornecido.** Variantes5/6 em `assets/cta-a.mp4` e `cta-b.mp4`, não repetir a variante1 dos episódios anteriores. Fonte57–64s e71,5–78,5s; composição15–22s e81–88s,900px centralizado. Usar duas entradas na montagem, chavear separadamente e inspecionar cada uma no MP4 final. Não incluir contagens/cartelas entre as variantes. Continuar voz Puck, curva de volume medida por episódio e Foley Python.

Ao terminar esta entrega, o usuário pediu sugestões de episódios sobre história/fatos históricos. Para esses temas, separar personagem/reconstituição fictícia de fatos documentados e pesquisar antes de fixar datas, ações ou perspectivas culturais específicas.


## Episódio16 — Jamestown,50segundos e nova reprovação de áudio

Usuário reduziu explicitamente este Jamestown para cerca50s e disse que a voz do último15 ficou meio ruim. **Não tratar a entrega15 como áudio aprovado só porque passou em métricas.** Causa perceptiva não identificada; feedback em `../projetos/15-enxergar-a-inercia/qa/user-audio-feedback.json`. Preservar Puck/modelo, leitura curta concreta, tratamento menos invasivo e cache; não prometer naturalidade perfeita nem disparar novas gerações para correções de mix. No16 a fonte já veio estável0,83dB entre janelas, então usamos ganho estático sem automação adicional, EQ mais suave e nenhum compressor.

Jamestown16 é short50s/1200quadros/24fps vertical1080×1920, não8min. CTA em vídeo duas variantes15–22s e42–49s; fullshort é sua própria prévia. Pedido de continuação nas entrelinhas: gancho de suprimentos/partida do navio, sem fala parte2 ou cartela continua.

História: NPS e OpenStax realmente consultados; matriz de fatos em `../projetos/16-jamestown-1607/story/fact-check.json`. Nico fictício identificado, épocaJunho1607, forte triangular; último plano avança explicitamente para22junho(partida deNewport). Não confundir com fome1609–1610/tabaco comercial posterior ou mostrar todos os navios indo embora juntos. Fortes/aldeias/roupas/navios são esquemáticos, sem afirmar planta/escala arqueológica. Roupas por código adaptadas(gibão,calções,meias,barrete), sem zíper/tênis/hoodie. POV inglês não apaga os povosPowhatan já presentes; sem diálogos históricos inventados, romance ou estereótipos de outras regiões.


## Episódio17 — Jamestown parte2,90segundos

Usuário elogiou16 e pediu parte2 com90s e dinamismo. Referência `../projetos/17-jamestown-parte-2/`:27takes com contato real tigela/mãos, remador sentado e duas mãos alinhadas ao remo, lâmina fora do casco, canoa deslocando sem reset entre cortes, cesto carregado e depois apoiado. Inspecionar sequências de quadros, além das amostras numéricas; não alegar movimento bom apenas por uma imagem. Novos enquadramentos próximos/baixos podem dividir takes longos sem regenerar voz.

Manter Puck/modelo/direção16 e EQ leve; medir cada fonte. No17, uma chamada71,851s foi distribuída por90s ampliando21pausas existentes em0,7904s, sem acelerar ou mudar tom. Medição da subida lenta4,04dB justificou correção ampla limitada a3dB, não AGC rápido; resultado de janelas0,51dB não equivale a aprovação perceptiva. Foley Python obrigatório, mix discreta, dois CTAs variantes5/6 em15–22 e81–88s.

Cronologia explícita: verão1607 após partida deNewport → meses depois/inverno1607–1608 com ajuda indígena → distinguir fome1609–1610. Personagens/canoa/rota/encontro/porção são dramatização, não documento. Povos indígenas com agência, comunidades e cultivo, sem converter ajuda coletiva em feito inventado de pessoa histórica nomeada. Não retratar doença curada instantaneamente pela comida. Capa deve manter todos os personagens na mesma família de cabeça preta estilizada, sem introduzir humano realista ao lado deNico. Pacote YouTube vertical e único arquivoYOUTUBE.


## Episódio18 — repetir o mesmo dia, análise da referência em90s

Novo pedido explícito: analisar profundamente o MP4 enviado e recriar seus movimentos/takes/câmeras com nossos personagens em90s. `../projetos/18-mesmo-dia-para-sempre/analysis/` guarda metadados/hash,128candidatos de segmento (a detecção inclui fades), análise visual e correspondência dos34takes com intervalos da referência634s. Não confundir quadros amostrados com inspeção integral de todos os quadros. Download ASR bloqueado403; não afirmar transcrição/escuta integral. Lentes/curvas/projeto original não são recuperáveis do MP4: a versão90s/vertical é uma reconstrução condensada e reenquadrada, não uma réplica pixel a pixel. Narração própria; não importar voz, frames ou elenco da referência.

Repetição visual precisa variar a ação: mesmo relógio/câmera, caminhada, café e reset; depois desvio por arco lateral. No café, desacelerar antes de cruzar corpos e fazer braços/copos encontrarem-se sem cabeças se atravessarem. Abrir o enquadramento para a aproximação e fechá-lo no contato. Mancha desaparece no reset. Contraplano traseiro do banco mostra os dois; close alternado destaca reação e isolamento.

**Gestos sentados devem usar altura relativa ao quadril:** alvos de mão de personagem em pé geram braço levantado acima da cabeça ao sentar. No teclado, comparar mãos com a área superior da tecla, não apenas o centro da caixa; pivô de frigideira no cabo real e panqueca fora da linha do rosto. Textura do telefone deve respeitar proporção do aparelho. Filmar refeição pelo lado que mostra rostos, tirando parede oclusora do caminho.

Mesma Puck/modelo/direção, uma geração bem-sucedida77,21s; primeira credencial inválida401, fornecida anteriormente funcionou. Fonte com variação2,32dBentre janelas, abaixo do limite3dB: apenas ganho estático/EQ leve, sem copiar curva do episódio17.32pausas naturais ampliadas0,3512s, sem speed/pitch/compressor. FoleyPython específico: café, passos, cama, teclado, frigideira, telefone e CTA. Duas variantesCTA15–22/81–88s, capa9:16neon e únicoYOUTUBE.

Revisão18: um take frontal do banco exibiu faixa listrada oclusora apenas na renderização nativa1080p; a folha em meia resolução parecia limpa. O problema repetiu em render isolado. Pequeno deslocamento lateral/vertical da câmera removeu a faixa no take nativo. Causa do rasterizador não confirmada: não chamá-la de erro de geometria ou aliasing comprovado. Substituídos21quadros do take com render nativo, áudio preservado, fonte/base/patch em qa/native-patch.json; não publicar antes de conferir MP4 final. Portanto, incluir ao menos um quadro nativo real de cada take nas verificações, não apenas folha reduzida ou testes numéricos.


## Série19–21 — três episódios de80segundos, produção sequencial

Pedido: salvar/carregar a vida → cada mentira vira realidade → roubar dez segundos do futuro. Cada episódio terá sua pasta/projeto/MP4/pacoteYouTube. Concluir, conferir e publicar um antes de iniciar o próximo; não declarar os três concluídos com um render pendente. Exceção de duração explícita:80s/1920quadros/24fps,1080×1920 nativo. Dois CTAs fornecidos15–22s e71–78s. Cores vivas, movimentos de raiz, ações com objetos e câmeras diferentes. Preservar Puck/modelo/direção, uma chamada por short/cache; tratamento medido por fonte e FoleyPython específico.

19: café desfeito, basquete com arco da bola, bicicleta/rodas e pedalada com pés em alvos de IK, banco e reencontro na porta. Quadril sentado do ciclista na altura do selim; mãos no guidão, roda gira pela distância. Porta pivota na dobradiça e mão toca frente do painel. Alternar macros do celular com reação/uso nas mãos para não sustentar uma tela estática em todas as ações. Final se resolve sem botões: pedir desculpas/ouvir a resposta, poder como ficção.

20:33takes, moedas instanciadas caindo para baixo a partir da cintura (reposições excluídas da interpretação), voo/órbita e seis cães geométricos próprios com deslocamento e pernas animadas. O buraco é efeito ficcional; cães ficam fora da linha entre câmera e resgate. Mão deLia e mão deNico preservam contato durante a subida; centro de palma não precisa coincidir exatamente quando volumes se sobrepõem (tolerância5cm, raio7,3cm). Registrar regra e distância, não mascarar falta de contato. Desaparecimento/reaparecimento com escala e partículas suaves, sem flash/estrobos. Roteiro assume explicitamente fantasia, sem transformar mentiras em alegação científica.

21:33takes, previsão possível+10s em silhuetas azuis com materiais clonados por malha para não alterar personagens reais. Instantes de previsão/presente rotulados; a intervenção muda a trajetória da bola, não apresentar previsão como certeza inevitável. Relógio acompanha pulso e aponta para câmera nos inserts; bandeja entre as duas mãos, livros sobre mãos deNico/amigo. Na parada antes da bicicleta, Lia eNico deslocam-se juntos, mantêm contato das mãos e passam a andar na direção do recuo; bicicleta só cruza depois de ambos saírem do trajeto.

Áudio21: fonte com subida gradual2,83dB, próxima do limiar anterior3dB. Para atender ao cuidado com aumento no final, aplicamos exceção medida2,5dB neste episódio: curva lenta precomputada reduziu diferença para0,59dB, sem compressor/speed/pitch ou nova geração. Não copiar esses ganhos para a próxima fonte. Medidas não provam naturalidade. Primeira folha21 já foi nativa1080p e piloto de8,5s conferiu articulações/parada/bicicleta antes do render completo.

Conferir também volume entre episódios: duplicar uma voz mono em dois canais altera a medida integrada estéreo. No21, mix inicial−17,1LUFS era mais alta que19(−19,0)e20(−19,9); recalibramos apenas ganho estático do mono para aproximar a saída estéreo de−19,5LUFS. Não presumir que um alvo mono idêntico garante mesmo volume do MP4. Sem compressor/API extra; medida final no QA.

Pastas desta série: [19 — Salvar/carregar](../projetos/19-salvar-e-carregar-a-vida/), [20 — Mentiras](../projetos/20-mentiras-viram-realidade/), [21 — Dez segundos](../projetos/21-dez-segundos-do-futuro/). Cada uma guarda MP4 de80s, prévia60s, stems, script de áudio, cenas e QA; pacoteYouTube próprio com capa vertical e únicoYOUTUBE. Medidas finais da série:19−19,0LUFS,20−19,9LUFS,21−19,1LUFS; nenhuma geração adicional para corrigir câmera/efeitos/mix. Não tratar medidas como aprovação perceptiva do usuário.


## Série22–24 — três episódios de65segundos

Novo pedido: sorte emprestada → apagar lembrança → dividir-se em dois. Produção sequencial com pasta própria para projeto/MP4/prévia/pacoteYouTube;65s/1560quadros/24fps nativo1080×1920, dois CTAs15–22 e56–63s. Preservar Puck/modelo, fonte única por short, FoleyPython e volume final comparado em estéreo. Primeiro arquivo só deve ser anunciado concluído após validação/push, depois seguir ao próximo.

22: Nico/verde-água eSol/laranja; ganhos e perdas em pares, seta e fluxo dourado deSolparaNico. A espessura/raio original de uma malha precisa entrar ao mudar sua escala: em contas de energia criadas com raio0,045, usar0,045×força, não substituir a escala por1. Folha nativa pegou a expansão indevida antes do filme completo. Deslocar pedestais para fora do corpo/pés; não deixar avatar atravessando caixa. Contato de resgate entre mãos verificado. Rig acrescenta inclinação de tronco para recolher chaves do chão, com cabeça/pescoço/ombros e zíper acompanhando o tronco, pernas e braços de dois segmentos fixos. Não simular alcance até o chão esticando braços.

23: ateliê próprio colorido, memória deontem/ação dehoje rotuladas. Apagar memória não limpa tinta nem desfaz objetos: o passado é mostrado como lembrança e a nova sujeira só desaparece durante limpeza física. Foto ilustrada gerada por canvas/código, não imagem externa. Bandeja precisa estar fora da passagem no final. O pano toca o piso e o rig inclina tronco sem esticar braços. Rolo tem haste0,70m; a mão escolhe altura/alcance para manter a cabeça do rolo na parede, revelando tinta por posição tocada. Remover contornos individuais dos pequenos retângulos de tinta para não parecer um mosaico. Folha de29takes nativa1080p, piloto10,8sde limpeza/transporte e piloto4sde pintura antes do render longo. Asserções de comprimento da haste/contato do pano com piso integram QA.

### Episódio 24 — Dividir em dois / 65 segundos
- Projeto `projetos/24-dividir-em-dois`; duas versões idênticas do Nico, mesmos trajes, sem usar aparência para provar qual é o original. A disputa é resolvida pela colaboração e divisão da pausa.
- Tábua carregada por duas mãos: centro calculado pelo ponto médio das palmas; auditar os dois contatos, membros de comprimento fixo e deslocamento real dos pés. A tábua termina encaixada nos montantes abertos da estante.
- A fusão é um efeito mágico explícito, após soltar o aperto de mãos; partículas suaves, sem flashes. Não transformar poses intermediárias em supostos erros de articulação.
- Mesma Puck/modelo, uma geração preservada. Medir cada arquivo, correção lenta e discreta apenas quando necessária, sem compressão agressiva nem mudança de velocidade. Efeitos obrigatórios sintetizados em Python: passos, bola, madeira, cadeira e contato das mãos. Não afirmar audição humana integral a partir de métricas.
- 65 s exatos / 1560 quadros / 24 fps, 1080×1920 nativo; dois CTAs distintos nos intervalos 15–22 e 56–63 s. Capa vertical e arquivo único `YOUTUBE`. Revisar quadros do MP4 final, mãos/objetos e CTA antes de publicar.

### Episódio 25 — Teletransporte voxel / 25 segundos
- Pedido específico: estilo inspirado em Minecraft, nossos personagens em blocos; não começar a narração com “E se”. Projeto `projetos/25-teletransporte-voxel`, pacote `youtube/25 - Quem saiu da cabine`. Não mudar automaticamente o estilo dos próximos episódios sem contexto.
- Geometria e expressões por código, sem skins/texturas/personagens do jogo. Membros mantêm IK de comprimento fixo; rosto acompanha a cabeça cúbica. Ao clonar materiais para clipping, preservar o material facial que a rotina de expressões atualiza.
- Leitura do corpo por plano de clipping progressivo e partículas pequenas; reconstrução inversa. Escalas animadas precisam multiplicar a escala-base dos cubos. Mapa vertical com destinos legíveis, sem flashes/cintilação.
- 25 s exatos / 600 quadros / 24 fps / 1080×1920 nativo. Um CTA variante 6 em 18–25 s para preservar a história. Prévia 10 s. Mesma Puck/modelo, fonte em uma chamada e cache; EQ/mix discreta, sem acelerar. Foley e stems em Python obrigatórios.
- O teletransporte de corpo em dados é ficção. Não apresentá-lo como ciência real nem confundir com teletransporte quântico. Análise visual da referência não equivale a transcrição integral do áudio.

### Episódio 26 — Inventário infinito / 25 segundos
- Continuidade autorizada do estilo voxel e duração 25 s. Sem abertura “E se” nem no título: “Nico colocou um carro no bolso. O problema foi tirar depois.” Projeto `projetos/26-inventario-infinito`; pacote `youtube/26 - Cade minha casa`.
- Carro, bicicleta, sofá e casa encolhem em direção à palma, que se recolhe ao bolso. A casa deixa base vazia; objetos errados aparecem em takes distintos. Interface e ícones por canvas, sem assets do jogo.
- Chuva obrigatoriamente para baixo: y = 4.5 - ((tempo * 3.2 + fase) % 4.5); conferir piloto/quadros sequenciais. Foley Python inclui cama de chuva contínua além de contatos e inventário. Não substituir toda a sonoplastia por bipes.
- Conferir personagem inteiro nos planos de objetos grandes; ampliar câmera antes do render final quando houver cortes nas bordas. Não corrigir somente miniaturas ou folhas antigas.
- Mesma Puck/modelo, uma geração, sem acelerar; apenas pequenas inserções em pausas detectadas. 25 s exatos, 600 quadros, 24 fps e 1080×1920 nativo; CTA variante 6 em 18–25 s, prévia 10 s, capa vertical e arquivo único YOUTUBE.

### Correção visual obrigatória — refação 25 e 26 em Minecraft clássico

O usuário reprovou o voxel genérico: queria aparência de animação de Minecraft com skins dos nossos personagens. Não interpretar “Minecraft” apenas como cabeça cúbica, corpo fino articulado e cores chapadas. Na refação dos episódios 25 e 26, usar modelo clássico de 32 pixels de altura: cabeça 8×8×8, tronco 8×12×4, braços e pernas 4×12×4, membros retos e inteiriços girando em ombros/quadris. Sem cotovelos, joelhos segmentados ou cabeças aumentadas. Skins próprias PNG 64×64 no padrão Java clássico de braços com 4 pixels; rostos e roupas pixelados, nearest sem interpolação.

Cenários com blocos de 1 unidade e texturas originais 16×16 de grama/terra, troncos, tábuas, pedra, folhas e vidro. Módulo `scenes/minecraft-world.js` em cada um. Não usar skins/texturas oficiais extraídas nem afirmar captura de gameplay: é animação por código no visual clássico, com skins utilizáveis fornecidas. Objetos seguem a extremidade real do braço reto. Gestos devem ficar abaixo do rosto. Entrada/saída das plataformas precisam conferir altura dos pés; não reaplicar a rampa do rig anterior sem revisão.

Preservar byte a byte os MP3s de narração/mix/stems nesta refação; nenhuma nova chamada TTS é necessária. Reexportar ambos em 25 s / 600 quadros / 1080×1920 nativo e revisar arquivos finais, CTA e capas. Congelar fonte incluindo módulos externos, PNGs de skins e texturas. Atualizar as instruções para não repetir a interpretação visual reprovada.
