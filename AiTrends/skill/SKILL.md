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
