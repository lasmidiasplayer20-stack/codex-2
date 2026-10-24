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

## Limites

After Effects não roda neste Linux: use o renderizador Python. JSX e servidor desktop originais estão incluídos, mas não ativados nem validados no After Effects real. O MP4 de exemplo aiTrends é um teste visual de 3 segundos sem áudio; o Stick usa mixagem procedural com SFX, sem narração humana. Transcrição está instalada, mas nenhum modelo Whisper foi baixado ou testado. Serviços ElevenLabs/Kie e outras APIs pagas não foram acionados. O renderizador aiTrends pode apenas avisar sobre cenas ausentes: inspecione a folha de quadros/logs antes de afirmar que um vídeo está completo.

As fontes originais continuam com suas licenças: Stick declara uso pelo proprietário do plugin, ícones Fluent são MIT e Anton é OFL. A adaptação não amplia direitos de redistribuição. Referências visuais originais foram preservadas como material do pacote fornecido pelo usuário.

Veja `VALIDATION.json` para evidências dos testes desta instância. O ZIP portátil contém fontes/locks/instruções e demonstrações; dependências binárias, caches e ambientes virtuais são reinstalados por `setup`.
