# RAGNAROK — desenvolvimento visual

Primeira entrega para uma adaptação animada de **God of War Ragnarök**, mantendo Kratos e a história do jogo, conforme solicitado. Direção visual: gravura nórdica pintada, couro e metal escuros, vermelho queimado e gelo ciano.

## Ver agora

- [NOVO — quatro quadros-chave numerados do Kratos](imagens/animacoes/cena_001_kratos_guarda/quadros/)
- [NOVO — prévia MP4 de quatro segundos com vento e gelo](videos/testes/kratos_guarda_animatic_4s.mp4)
- [Como usar os quadros e o que falta para animar](documentacao/QUADROS_PILOTO.md)
- [Kratos — arte principal](imagens/personagens/kratos/kratos_conceito.png)
- [Kratos — model sheet: frente, perfil, costas e expressões](imagens/personagens/kratos/kratos_model_sheet.png)
- [Kratos — seis poses de ação](imagens/personagens/kratos/kratos_poses.png)
- [Armas e desenvolvimento de efeitos de gelo](imagens/assets/armas/armas_e_fx_conceito.png)
- [Cenário — Midgard no Fimbulwinter](imagens/cenarios/midgard/midgard_fimbulwinter.png)
- [Storyboard visual — teste de abertura, oito quadros](imagens/storyboards/abertura_fimbulwinter_01.png)
- [Voz provisória de Kratos em português](audios/vozes/kratos/kratos_teste_ptbr.mp3)
- [Efeito — machado e gelo](audios/efeitos_sonoros/machado_gelo.mp3)
- [Ambiente — vento em Midgard](audios/efeitos_sonoros/vento_midgard.mp3)

![Kratos — conceito](imagens/personagens/kratos/kratos_conceito.png)

![Kratos — model sheet](imagens/personagens/kratos/kratos_model_sheet.png)

## Organização

```text
RAGNAROK/
  imagens/
    personagens/kratos/       conceito, model sheet e poses
    assets/armas/             prancha de armas e FX
    assets/itens/             reservado para objetos de cena
    cenarios/midgard/         cenário do Fimbulwinter
    efeitos/                 reservado para elementos VFX separados
    storyboards/             prancha visual da abertura
    animacoes/               quadros-chave separados e seus manifestos
  audios/
    vozes/kratos/             fala de teste
    efeitos_sonoros/          machado/gelo, vento e despertar do gelo
    manifesto.json           modelos, voz e prompts utilizados
  documentacao/              direção visual, storyboard e planejamento
  scripts/                  cliente ElevenLabs sem credenciais no código
  videos/testes/             prévia MP4 do animatic de quatro poses
```

## O que esta entrega contém

A primeira entrega contém seis imagens novas e três áudios gerados para este projeto. A atualização acrescenta **quatro PNGs separados de poses-chave, um efeito de gelo e um MP4 de quatro segundos para testar a ordem e os tempos das poses**. A prévia é um animatic com poses mantidas, sem animação intermediária.

Os desenhos são interpretações visuais novas; Kratos, os personagens e a história de God of War Ragnarök são preexistentes. A voz usa uma voz de catálogo da ElevenLabs: não é a voz oficial nem uma clonagem do ator. A fala é um texto de teste, não uma transcrição do jogo. A prévia de quatro segundos usa apenas ambiente e efeito, sem fala ou lip sync.

As pranchas são imagens achatadas de desenvolvimento visual. O model sheet não é um modelo 3D nem um rig. As poses são referências estáticas, não animações exportadas ou um ciclo de caminhada completo. A prancha de armas inclui estudos de FX; os elementos ainda não estão separados em transparência.

O storyboard desta entrega cobre somente um **teste de abertura de 30 segundos**. A animação completa, o storyboard do filme inteiro e os sheets dos demais personagens ainda não foram produzidos.

## Referência em vídeo

**Acesso resolvido pelo Google Drive.** O vídeo foi baixado integralmente e analisado visualmente por amostragem ao longo de toda a duração, com transcrição automática do áudio pela ElevenLabs. A ferramenta original de anexos continua limitada a 32 MiB, mas o download HTTP direto do Drive funcionou após a atualização da rede. O plugin do Drive não foi usado.

O arquivo tem **12min44,726s, 1920×1080, 24 fps e 81.788.154 bytes**. Trata-se de uma paródia animada 2D de Ragnarök, creditada a PIZOHED no próprio vídeo, com montagem condensada e humor visual. A análise é uma referência para criar materiais novos, mantendo os personagens e a história do jogo conforme solicitado.

O vídeo e a transcrição integral ficaram fora do repositório. Os desenhos e áudios novos deste pacote não foram extraídos da referência.

- [Análise do vídeo e linguagem de animação](documentacao/ANALISE_VIDEO.md)
- [Dados técnicos e método da análise](documentacao/fonte_video.json)
- [Decupagem de toda a referência por sequências](documentacao/DECUPAGEM_REFERENCIA.csv)
- [Elenco e assets identificados na referência](documentacao/ELENCO_E_ASSETS.csv)
- [Direção visual e continuidade](documentacao/DIRECAO_VISUAL.md)
- [Storyboard do teste de abertura](documentacao/STORYBOARD_ABERTURA.md)
- [Estrutura da adaptação e pendências](documentacao/PLANO_DE_PRODUCAO.md)
- [Inventário técnico e verificações](documentacao/manifesto_assets.json)

## Gerar mais áudio

Requer Python 3, acesso a `api.elevenlabs.io` e a variável segura `ELEVENLABS_API_KEY`. Não cole a chave no repositório. A geração utiliza os créditos da conta ElevenLabs.

Execute a partir da raiz do repositório, usando um ID de voz disponível na conta (o usado neste pacote está no manifesto de áudio):

```bash
python3 RAGNAROK/scripts/gerar_audio.py voz "Texto em português." RAGNAROK/audios/vozes/kratos/nova_fala.mp3 --voz ID_DA_VOZ
python3 RAGNAROK/scripts/gerar_audio.py efeito "Heavy ice crack, no music, no voices" RAGNAROK/audios/efeitos_sonoros/novo_gelo.mp3 --segundos 3
```

O script não sobrescreve arquivos existentes. Ele foi usado para gerar as amostras de voz e efeitos deste pacote. Não há dependências Python externas.

Para remontar a prévia a partir dos PNGs e MP3s existentes, requer FFmpeg e não consome créditos de API:

```bash
python3 RAGNAROK/scripts/montar_animatic_guarda.py --saida /tmp/kratos_guarda.mp4
```
