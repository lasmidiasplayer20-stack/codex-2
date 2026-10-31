# Estúdios 2D adaptados para Codex

Os `.plugin` enviados são ZIPs com fontes, documentação e assets. Foram extraídos e adaptados; não houve descompilação de binários. As versões originais dos anexos permanecem preservadas.

Este pacote funciona por comandos locais e uma skill legível pelo agente. Não registra automaticamente ferramentas MCP nem instala botões ou comandos `/` na interface. Aqui, peça para usar o aiTrends ou o Stick Animator de `/workspace/codex-2/AiTrends`.

## Comandos

```bash
cd /workspace/codex-2/AiTrends
python3 studio.py setup      # reinstala dependências fixadas; requer rede
python3 studio.py doctor
python3 studio.py aitrends --project examples/reaction-time --sheet --scale 0.3
python3 studio.py stick new_project "Meu vídeo"
python3 studio.py stick ra_preview /CAMINHO/ABSOLUTO/PROJETO --scale 0.5 --fps 15 -o /CAMINHO/ABSOLUTO/video.mp4
```

Pré-requisitos: Python 3.12, Node 18+, FFmpeg/FFprobe, Chromium e bibliotecas de sistema do Skia. Já disponíveis nesta instância. O instalador usa Chromium do sistema ou `CHROMIUM_EXECUTABLE_PATH`; se ausente, tenta a instalação padrão do Playwright. Não desativa verificações TLS. Em outras máquinas, instalação de bibliotecas do sistema pode exigir o gerenciador de pacotes apropriado.

`studio.py aitrends` repassa opções ao renderizador JavaScript; `ai-tool NOME` executa os utilitários Python aiTrends; `stick NOME` executa os utilitários Stick. Caminhos relativos passados ao aiTrends são resolvidos na pasta do kit; os do Stick, na raiz `2d-stick-animator`. Prefira caminhos absolutos para projetos próprios.

## O que foi adaptado

- aiTrends aceita Chromium do sistema/variável de caminho; diagnóstico reconhece esse navegador.
- Stick propaga falhas do FFmpeg pelo código de saída do processo Python.
- Adaptador comum `studio.py`, lock Python, lock npm e skill `codex-skills/animation-studio/SKILL.md` descrevem o uso sem ferramentas exclusivas do Claude.
- O download de Chromium do Playwright retornou HTTP 403; o Chromium do sistema foi usado com sucesso.

## Origem exata das demonstrações

Nenhum dos dois arquivos `.plugin` originais continha MP4s. Os vídeos deste repositório foram exportados pelo Codex nesta máquina usando conteúdo de teste incluído nos plugins. Não houve criação de roteiro, direção de cenas ou personagens novos para essas demos.

| Arquivo | Conteúdo original usado | Trabalho executado aqui |
|---|---|---|
| `aitrends-demo.mp4` | Projeto `aitrends-2d-studio/skills/make-2d-video/kit/examples/reaction-time/`, incluindo `config.json`, `story/shots.json` e JavaScript em `scenes/` | Render dos primeiros 3 segundos a 50% da resolução: 640×360, 24 fps, 72 quadros, sem áudio |
| `aitrends-sheet.png` | As 14 cenas do mesmo exemplo | Render de um quadro de cada cena e montagem da folha de contato |
| `stick-demo.mp4` | `2d-stick-animator/kit/py/selftest.py`, que já contém a história da maleta de dinheiro, o elenco e quatro cenas | Execução do gerador de teste, compilação do plano, síntese/mixagem de música e efeitos e render Python: 540×960, 15 fps, 114 quadros, 7,6 segundos |
| `stick-frame.png` | Cena do teste Stick no instante 3,4 s | Exportação de um quadro para inspeção |

As legendas em inglês do Stick vêm do texto do teste. A trilha é procedural com efeitos; não foi gerada fala nem usada uma API de voz. Os PNGs, ícones e figurinos fornecidos nos plugins não foram desenhados pelo Codex. O simulador de After Effects usado no teste de rig é código de teste do pacote, não o aplicativo Adobe em execução.

## Reproduzir exatamente o tipo de teste feito

Execute a partir da raiz desta pasta. Os comandos escrevem arquivos de teste e podem substituir exports anteriores dos próprios exemplos. Não os use em projetos que queira preservar sem uma cópia.

```bash
cd /workspace/codex-2/AiTrends
python3 studio.py setup
python3 studio.py doctor

# aiTrends: folha com as 14 cenas e vídeo dos primeiros 3 segundos.
python3 studio.py aitrends --project examples/reaction-time --sheet --scale 0.3
python3 studio.py aitrends --project examples/reaction-time --from 0 --to 3 --scale 0.5 --workers 1 --out "$PWD/aitrends-demo.mp4"

# Stick: gera o projeto _selftest, incluindo assets, plano, áudio e stills.
python3 studio.py stick selftest
python3 studio.py stick ra_preview "$PWD/2d-stick-animator/projects/_selftest" --scale 0.5 --fps 15 -o "$PWD/stick-demo.mp4"

# Confere o rig Python contra as expressões JSX no simulador Node.
.venv/bin/python 2d-stick-animator/kit/dev/rig_parity.py "$PWD/2d-stick-animator/projects/_selftest"

# Confere os arquivos finais; ausência de erro e saída zero são obrigatórias.
ffprobe -v error -count_frames -show_streams -show_format -of json aitrends-demo.mp4
ffprobe -v error -count_frames -show_streams -show_format -of json stick-demo.mp4
ffmpeg -v error -xerror -i aitrends-demo.mp4 -f null -
ffmpeg -v error -xerror -i stick-demo.mp4 -f null -
```

`--sheet` salva a folha em `aitrends-2d-studio/skills/make-2d-video/kit/examples/reaction-time/build/sheets/sheet_01.png`. O still Stick original está em `2d-stick-animator/projects/_selftest/qc/stills/preview_003400.png`. As cópias na raiz são os previews publicados. O teste de rig executado conferiu 318 casos e 5.724 articulações sem divergências; ele não substitui um teste no Adobe After Effects real. Reexecuções podem produzir hashes diferentes conforme navegador, codec e ambiente.

## Criar um vídeo novo aqui no chat

Peça, por exemplo: “Use o aiTrends de `AiTrends/` para criar um vídeo novo de 30 segundos, horizontal, sobre [tema], com roteiro em português e sem APIs pagas”. Para o outro motor: “Use o Stick Animator de `AiTrends/` para criar uma animação vertical de 20 segundos sobre [tema], usando os assets gratuitos”. Envie uma narração se quiser uma voz específica; sem narração, pode-se produzir uma animação com textos, música e efeitos, sem inventar que há fala.

Esses pedidos exigem escrever um roteiro e cenas próprios. Não basta trocar o título do exemplo. Informe tema, duração, formato, idioma e áudio desejado; os detalhes restantes podem ser definidos pelo agente e registrados no projeto. Uma nova produção deve ter sua própria pasta e origem dos assets documentada.

### Projeto novo no aiTrends

1. Leia `aitrends-2d-studio/skills/make-2d-video/references/engine-api.md` e `story-breakdown.md` para a API de cenas e o plano.
2. Com uma narração local existente, crie a estrutura com `python3 studio.py ai-tool new_project --name meu-video --voice /CAMINHO/ABSOLUTO/narracao.wav --aspect 16:9 --resolution 720p --fps 24 --style dusk`. O script copia o áudio, mas não inventa nem desenha as cenas. Sem narração, crie uma estrutura própria a partir do exemplo e ajuste a configuração; isso requer autoria manual das cenas.
3. No projeto criado em `aitrends-2d-studio/skills/make-2d-video/kit/projects/meu-video/`, escreva o roteiro, `story/shots.json` e os módulos em `scenes/shots/`, com elenco/cenários quando necessários. Ajuste duração e caminhos no `config.json`. Não reutilize silenciosamente a história do café.
4. Gere a folha com `python3 studio.py aitrends --project projects/meu-video --sheet --scale 0.3`. Abra as imagens e confira logs, cenas ausentes, texto, poses e enquadramento.
5. Exporte com `python3 studio.py aitrends --project projects/meu-video --scale 1 --workers 1 --out /CAMINHO/ABSOLUTO/video-sem-audio.mp4`. O renderizador produz vídeo silencioso. Para uma narração que já esteja alinhada à mesma linha do tempo, monte com `ffmpeg -n -i /CAMINHO/ABSOLUTO/video-sem-audio.mp4 -i /CAMINHO/ABSOLUTO/narracao.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -shortest -movflags +faststart /CAMINHO/ABSOLUTO/video-final.mp4`. Música/SFX precisam de mixagem adicional; verifique a duração para não cortar a animação por engano com `-shortest`.

### Projeto novo no Stick Animator

1. Execute `python3 studio.py stick new_project "Meu vídeo" --slug meu-video`. Isso cria `2d-stick-animator/projects/meu-video/`; não gera automaticamente roteiro, planos ou vídeo.
2. Escreva o roteiro em `script/`, forneça áudio quando houver e prepare a temporização em `timing/`. Planeje `plan/spec.json` conforme `2d-stick-animator/skills/plan-shots/references/spec-schema.md`; consulte também `kit/templates/spec.example.json`. Defina `meta`, `cast`, `shots`, legendas e referências a assets/áudio existentes.
3. Use os assets gratuitos em `kit/assets/`, ou assets próprios, copiando-os ao projeto e preservando os créditos. Não habilite geração paga sem autorização. O plano precisa de posições, poses, ações e câmera para cada cena.
4. Defina o caminho absoluto do projeto: `projeto="$PWD/2d-stick-animator/projects/meu-video"`. Compile com `python3 studio.py stick compile_spec "$projeto"` e valide com `python3 studio.py stick validate_spec "$projeto"`. Corrija erros antes de renderizar.
5. Gere previews com `python3 studio.py stick ra_preview "$projeto" --sheet --scale 0.3`. Para vídeo, execute `python3 studio.py stick ra_preview "$projeto" --full -o "$projeto/exports/final-python.mp4"`. O modo `--full` é mais lento e usa resolução completa; teste primeiro um intervalo curto. Confira áudio, texto e cobertura das ações, além do ffprobe e da decodificação completa.

Os checklists originais mencionam AE e ElevenLabs; neste ambiente, registre render Python e áudio local quando forem as alternativas utilizadas. Não marque como realizadas as etapas de After Effects ou serviços que não foram executados.

## Limites

After Effects não roda neste Linux: use o renderizador Python. JSX e servidor desktop originais estão incluídos, mas não ativados nem validados no After Effects real. O MP4 de exemplo aiTrends é um teste visual de 3 segundos sem áudio; o Stick usa mixagem procedural com SFX, sem narração humana. Transcrição está instalada, mas nenhum modelo Whisper foi baixado ou testado. Serviços ElevenLabs/Kie e outras APIs pagas não foram acionados. O renderizador aiTrends pode apenas avisar sobre cenas ausentes: inspecione a folha de quadros/logs antes de afirmar que um vídeo está completo.

As fontes originais continuam com suas licenças: Stick declara uso pelo proprietário do plugin, ícones Fluent são MIT e Anton é OFL. A adaptação não amplia direitos de redistribuição. Referências visuais originais foram preservadas como material do pacote fornecido pelo usuário.

Veja `VALIDATION.json` para evidências dos testes desta instância. O ZIP portátil contém fontes/locks/instruções e demonstrações; dependências binárias, caches e ambientes virtuais são reinstalados por `setup`.

## Produção nova — canal Então

[02 — Quantas mentiras](projetos/02-quantas-mentiras/README.md): roteiro próprio em português, direção com 128 planos, voz Puck e CTAs vetoriais do Então. Exportado em 8min20s, 1920×1080/24 fps, com prévia de um minuto na mesma resolução. O estado e os arquivos entregues ficam no README e na pasta `exports/` do projeto; esta produção não é uma das demos originais descritas acima.

## Produção do canal Então e próximos projetos

Leia a [skill local reutilizável](skill/SKILL.md) para voz Puck, animação por código, tratamento de áudio, CTAs e exportação 1080p. Ela complementa a skill adaptada original; não instala uma extensão na interface.

O [episódio 03 — 10x Mais Rápido](projetos/03-10x-mais-rapido/) inclui cenas 3D próprias, rig com IK, câmera e diagramas. [Pacotes YouTube novos](youtube/) ficam dentro de AiTrends. Projetos e capas anteriores permanecem nos seus caminhos originais.

[04 — Quanto Tempo Resta](projetos/04-quanto-tempo-resta/) traz história própria sobre contadores de vida, cenários 3D mais detalhados, ações com objetos e voz Puck consistente nos oito trechos. Consulte o estado de render/entrega no README do projeto.

### Feedback de qualidade a aplicar ao próximo episódio

O usuário reprovou o áudio do episódio 04 e relatou cintilação em parte da animação. Antes de reutilizar esse pipeline, leia [o procedimento obrigatório de áudio e estabilidade temporal](skill/references/audio-and-temporal-quality.md). Fazer uma amostra curta e aguardar a avaliação do áudio antes de gerar o lote completo, reaproveitando cache para evitar gasto repetido. O episódio 04 permanece como referência técnica, com a reprovação registrada.


[05 — E se você fosse imortal?](projetos/05-imortal/) preserva a Puck e inclui amostra de voz/mix aprovada pelo usuário, tratamento leve sem aceleração, antialiasing ativo e pacote YouTube próprio. Consulte o estado de render/entrega no README do projeto.


[06 — Duas pessoas podem recomeçar a humanidade?](projetos/06-recomecar-humanidade/) tem prévia inicial nativa 1080p, rig revisado, Foley Python em stem separado e capa neon com arquivo único YOUTUBE. O usuário escolheu aguardar a mesma Puck após cota diária. Consulte o estado real no README/QA do projeto; prévia inicial não é o filme completo.

[07 — E se uma aranha aprendesse sua rotina?](projetos/07-aranha-rotina/) adapta uma referência de suspense para história original com Nico/Lia, apartamento procedural, câmera de rodapé/macro, Foley Python e capa neon. Consulte o README/QA para o estado real de voz, prévia e exportação.

[08 — E se você tivesse Modo Criativo na vida real?](projetos/08-modo-criativo/) traz história original com voo, construção por peças, rig próprio, quatro blocos Puck na mesma sessão e limite máximo10min. Consulte README/QA para o estado real de render e entrega.

## Série curta — nove temas em 30 segundos

[Índice dos episódios 29–37](series/09-temas-30-segundos/README.md): nove histórias originais em vertical 1080p, voz Puck, personagens/skins Minecraft próprios, Foley Python e dois CTAs em vídeo. O índice reúne MP4s, prévias, fontes, capas e os arquivos únicos `YOUTUBE`. As capas finais têm render próprio por código com câmera próxima e luz neon; receita e script de reprodução estão em cada projeto. Consulte a skill local antes de produzir o próximo episódio.
