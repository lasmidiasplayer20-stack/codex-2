# Análise da referência — God of War Ragnarök animado

## Acesso e material examinado

O download direto da pasta compartilhada do Google Drive funcionou após a publicação das regras de rede. O arquivo foi baixado inteiro, sem a ferramenta de anexos limitada a 32 MiB e sem utilizar o plugin do Drive.

| Propriedade | Resultado verificado |
| --- | --- |
| Duração | 764,725986 segundos — 12min44,726s |
| Arquivo | 81.788.154 bytes, aproximadamente 78 MiB |
| Vídeo | H.264, 1920×1080, 24 fps |
| Áudio | AAC, 44,1 kHz, estéreo |
| Crédito visível | PIZOHED; aparece na abertura e em cartões/créditos |
| Idioma detectado no áudio | Inglês; transcrição automática ElevenLabs Scribe v1 |
| Identificação técnica | SHA-256 `34a1961ad40ed7b855435dee57e68d32584646986b83daf1eda90a5ce0948ca1` |

Método: decodificação do vídeo para obter **153 amostras visuais a intervalos de cinco segundos**, cobrindo de 00:00 a 12:40; revisão das oito pranchas resultantes; inspeção adicional de quadros selecionados por mudança de cena; e transcrição automática da faixa de áudio inteira. Os intervalos narrativos abaixo são aproximados, não uma lista de cortes validada quadro a quadro.

Isso permite avaliar estrutura, personagens, cenários e linguagem visual. A transcrição automática não equivale a uma revisão humana de cada fala: nomes, gritos, referências e vozes sobrepostas podem conter erros. O áudio não foi ouvido manualmente através de um player; as observações sonoras abaixo se apoiam nos eventos e falas reconhecidos.

O MP4, o áudio extraído, as pranchas de referência e a transcrição integral permaneceram fora do GitHub, em `/workspace/reference/ragnarok/`. O repositório recebe a análise e os materiais novos do projeto.

## O que a referência é

Uma **paródia 2D que condensa a história de Ragnarök**, combinando diálogos curtos, encenação caricata, ação muito rápida, narração de montagens e piadas de metalinguagem. Apesar do título do arquivo conter “Full Movie”, não é a história inteira do jogo apresentada com todas as cenas: vários arcos são resumidos em segundos, cartões ou gags.

O começo encadeia inverno, Fenrir/urso, visita de Thor e Odin, confronto e descoberta das profecias. O desenvolvimento alterna Kratos, as aventuras de Atreus, o falso Týr e a preparação para o confronto. A parte final passa pela traição, Surtr, guerra, Thor/Odin, a escolha sobre a máscara e a despedida. Há um epílogo visual e créditos.

## Desenho e encenação observáveis

- **Silhueta primeiro:** Kratos tem tronco muito largo, pernas pequenas, barba como massa escura e tatuagem de leitura imediata. Atreus é estreito, leve, com cabeça/olhos grandes. Thor ganha uma massa corporal distinta; Odin é fino e curvado. Essas diferenças continuam legíveis em planos abertos.
- **Rosto e gesto carregam a atuação:** olhos, sobrancelhas, boca, inclinação da cabeça e uma mão indicando algo frequentemente mudam enquanto o corpo mantém a pose base.
- **Fundos funcionam como palcos:** casa, interior da casa de Sindri, floresta e salões reaparecem em vários planos. A câmera em geral preserva o espaço da ação, sem percorrer continuamente cenários complexos.
- **Animação seletiva:** conversas longas aproveitam enquadramentos e poses semelhantes; ações-chave recebem desenhos mais exagerados e maior mudança de silhueta. Isso é compatível com um fluxo de rigs/recortes e animação desenhada de apoio, mas o arquivo renderizado não revela qual programa ou técnica exata o autor usou.
- **Acabamento simples nos personagens:** grandes áreas de cor e contorno claro, com sombreamento contido; cenários recebem mais variação e atmosfera. Rostos não dependem de microtextura.
- **Ação abreviada:** golpes, quedas, trajetos e transições às vezes resolvem em um corte, borrão, explosão gráfica, quadro de impacto ou mudança brusca de pose.

Não há evidência de que seja apenas uma sequência de imagens com zoom. Existem trocas de poses e expressões, gestos, articulação de membros e deformações desenhadas.

## Montagem e ritmo

| Faixa aproximada | Construção observada | Aplicação para a nova versão |
| --- | --- | --- |
| 00:00–01:15 | Introdução rápida; acontecimentos e combate condensados entre conversas curtas. | Começar com uma ação ou relação clara e economizar exposição. |
| 01:15–03:05 | Profecias, viagem e encontro com o falso Týr; espaços mantidos por mais tempo para diálogo. | Planejar poses de escuta, respostas e gestos reutilizáveis. |
| 03:05–04:55 | Conversa Atreus/Sindri e sequência de pequenas aventuras com cartões recorrentes. | Montagens podem cobrir deslocamentos sem animar cada passo da viagem. |
| 04:55–06:55 | Narração resume Ironwood, Asgard e atividades paralelas de Kratos. | Definir onde uma voz narrativa ajuda e onde a cena precisa respirar. |
| 06:55–08:55 | Reencontros, combate e retorno ao núcleo do falso Týr/Brok. | Alternar escala e duração dos planos para a revelação ter peso. |
| 08:55–11:30 | Preparação final, guerra e confronto; depois uma conversa sustentada sobre a máscara. | Reservar os efeitos mais fortes à guerra; simplificar o quadro na decisão emocional. |
| 11:30–12:15 | Despedida e reação final de Kratos; o ritmo desacelera. | Priorizar olhos, pausa e mudança de expressão no encerramento. |
| 12:15–12:44 | Cartões finais e créditos. | Reservar tempo próprio para encerramento e créditos. |

Há repetição intencional de cartões, retornos a cenários conhecidos e contraste entre falas extensas e ações curtíssimas. Tempos de produção não podem ser inferidos da duração do vídeo; a preparação de personagens e poses é parte relevante do trabalho.

## Personagens, criaturas e objetos

O núcleo visual inclui Kratos, Atreus, Mimir, Thor, Odin, Týr/disfarce, Brok, Sindri, Freya, Angrboda, Heimdall e Thrúd. Também há gigantes/criaturas e participações muito breves. A lista de trabalho em `ELENCO_E_ASSETS.csv` separa identificação visual segura, identificação provável e inserções paródicas que não precisam integrar a nossa adaptação.

Itens recorrentes: machado, arco/flechas, Mjölnir, cabeça de Mimir, máscara, lança Draupnir, pedras/esferas de almas, correntes, Gjallarhorn, portais e objetos domésticos. Cenários com maior potencial de reutilização: floresta/casa em Midgard, casa de Sindri, sala de Odin e arena do confronto final.

## Som e voz

A transcrição identifica diálogo, trechos narrados e eventos como passos, fogo, vento, impactos, metal, rugidos e música. Isso sugere três trilhas de trabalho separadas: **fala/narração**, **ambiente/foley** e **acentos de ação**.

Para o projeto:

1. Escrever as falas novas e o texto narrativo antes de gerar os takes.
2. Definir uma voz de catálogo por personagem na ElevenLabs; guardar ID, parâmetros e identificação de take, sem guardar credenciais no código.
3. Separar fala por cena e intenção; gerar pequenas variações de ritmo e emoção quando necessário.
4. Criar uma biblioteca de passos na neve, couro, metal, gelo, trovão, magia, vento e criaturas. Os três áudios atuais são apenas amostras iniciais.
5. Montar o animatic com vozes provisórias antes de finalizar bocas e movimentos.
6. Fazer a mixagem com diálogos legíveis; efeitos e música não devem encobrir palavras importantes.

## Como aplicar o estilo novo já criado

A arte de Kratos entregue é muito mais detalhada que os personagens da referência. Ela funciona como direção de arte e referência de acabamento. Para animá-la com consistência, é necessário um **modelo limpo para animação**, com menos linhas em couro, barba, fivelas e placas pequenas.

| Elemento | Manter da nossa arte | Preparar para animação |
| --- | --- | --- |
| Kratos | Identidade, massa corporal, tatuagem, barba, ombro de armadura, paleta. | Contornos limpos e separação de cabeça, tronco, braço/antebraço/mão, pernas, tecido e arma. |
| Expressões | Contenção, raiva, luto e decisão. | Biblioteca de olhos/sobrancelhas, viradas de cabeça e bocas para fala. |
| Textura | Pintura seca e gravura nórdica. | Aplicação estável, evitando que a textura “ferva” ou mude a cada quadro. |
| Cenários | Profundidade, neve, pedra e madeira. | Camadas reais, áreas de chão para contatos e versões por enquadramento. |
| Armas e FX | Ciano do gelo, ferro/bronze, contraste com fogo âmbar. | Artes isoladas, pivôs, poses de empunhadura e sequências separadas de partículas/impactos. |
| Movimento | Peso de Kratos e silhueta forte. | Rig 2D com poses desenhadas de apoio para rotações e ação; composição e montagem depois. |

Um programa de rig 2D, como Blender/Grease Pencil, OpenToonz, Moho ou Harmony, pode organizar a animação conforme o fluxo escolhido. FFmpeg/Python podem ajudar em montagem, áudio e validação; não substituem a atuação, os desenhos intermediários ou o rig.

## Próxima entrega de produção

O acesso ao vídeo está resolvido. Depois da análise foram criados quatro quadros-chave separados de Kratos assumindo guarda no mesmo enquadramento, acompanhados de uma prévia de quatro segundos com vento e gelo. Ver `QUADROS_PILOTO.md`. A prévia segura poses; ela ainda não contém desenhos intermediários ou movimento contínuo de personagem.

O próximo trabalho é limpar a continuidade, simplificar o personagem para animação e produzir intermediários ou rig para um teste curto com movimento. Em paralelo, a decupagem macro pode virar storyboard plano a plano de toda a adaptação, com diálogos e duração próprios.

Ainda não foram entregues: storyboard final do filme inteiro, sheets dos demais personagens, rigs, animação de personagens ou filme finalizado. Os arquivos atuais são pré-produção e referências estáticas, mais as amostras de áudio.
