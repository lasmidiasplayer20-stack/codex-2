# Tutorial — análise e adaptação

Fonte fornecida pelo usuário: `Tutorial.mp4`, na pasta compartilhada do Drive, ID `1xedG4mU6VHRge1KF4yIAuIibwQ1gv_d1`. Duração: 405,745 s (6min46s), 1280×720. Foram inspecionados 40 quadros distribuídos pelo vídeo e quadros adicionais em resolução original. A fala inteira passou por transcrição/análise automática em três trechos. Não houve escuta humana integral nem teste na conta Google Flow do usuário. O vídeo e a transcrição de terceiros permanecem privados.

## O que o vídeo demonstra

| Trecho aproximado | Etapa observada |
|---|---|
| 00:00–01:30 | Demonstração de personagens desenhados sobre cenários ilustrados; história em cenas, com imagem correspondente à fala. |
| 01:40–02:10 | Requisitos citados pelo autor: Claude Desktop/Code com navegador, conta Google e plano com acesso ao Flow. Login feito pelo usuário. |
| 02:10–03:20 | Um comando informa tema e quantidade de cenas. O Claude escreve a história, escolhe a voz e preenche a ferramenta personalizada. |
| 03:20–03:50 | O autor atribui falas repetidas ao reaproveitamento de gravações e mostra nomes exclusivos por cena. A interface exibe Charon; algumas transcrições automáticas reconhecem o nome como Sharon. |
| 03:50–04:30 | Estados por cena, retomada após recarregar e transferência do trabalho de geração à ferramenta. |
| 04:30–05:10 | Clipes ajustados à duração da fala, junção e download de um MP4. |
| 05:10–05:50 | Escala por número de cenas e consumo de créditos. O autor menciona cerca de 25 minutos para gerar um exemplo de aproximadamente um minuto. Isso não foi medido aqui. |
| 05:50–06:35 | Menu Tools/Create tool, criação por instrução, Done e Pin. O prompt completo do autor e o código interno não são disponibilizados integralmente pela fala do tutorial. |

Em 01:05, a interface mostra uma alocação com clipe de 8 s e continuação de 4 s para uma fala maior. Em 06:15, aparece um modo rotulado UPLOAD; o vídeo não demonstra importar um master externo de 25 minutos. Não se pode prometer esse suporte sem testar a conta/ferramenta real.

## Arquitetura aproveitável

1. Roteiro e plano de cenas fora do gerador.
2. Personagem de referência e aparência constantes.
3. Um prompt de ação/câmera por cena, com ID único e estado de geração.
4. Geração de clipes pelo Flow.
5. Ajuste dos clipes à linha do tempo da narração.
6. Montagem, validação e exportação.

O Claude atua como operador e planejador; o Flow e a ferramenta personalizada realizam a geração. Não é apresentado um plugin universal de animação que transforme o modelo de conversa em um renderizador.

## Nossa adaptação

A Algenib original está aprovada e os 25 WAVs de um minuto estão prontos. Usar esse material como fonte definitiva. Não passar pela geração de voz do tutorial, não trocar para Charon e não criar novamente 25 minutos de fala. O áudio que vier nos clipes deve ser descartado.

O plano visual deve seguir o texto existente. Se uma frase aborda transmissão de manuscritos, mostrar leitura, cópia ou preservação; se descreve uma visão de Enoque, usar ilustração narrativa dessa passagem. Não preencher explicações históricas com ações desconexas. As imagens devem manter clara a natureza ilustrativa dos relatos religiosos, sem alegar reconstrução arqueológica precisa.

O caminho que independe de suporte a áudio externo no Flow é: gerar os clipes visuais, baixá-los e usar o montador local para juntar os clipes com os WAVs. Há um piloto de 8 tomadas/60 s e um índice das 25 partes. O orçamento inicial de 200 clipes corresponde a uma média de 7,5 s por tomada, não a uma contagem final nem a uma estimativa de preço. Frases e movimentos podem exigir mais cortes ou continuações.

## Acesso e custo

O tutorial usa créditos do Flow. O consumo citado por seu autor não determina o custo do nosso projeto. A chave da API Gemini usada para voz não autentica uma sessão no site Google Flow nem comprova acesso ao Tool Builder. Não há sessão autenticada do Flow disponível neste ambiente. Nenhum crédito de geração de vídeo foi acionado e nenhuma ferramenta foi instalada na conta do usuário.

`FLOW-PROMPT.txt` é uma especificação nossa para tentar construir uma ferramenta equivalente. Não é o prompt privado do autor nem uma integração Flow já testada. A montagem Python local, por outro lado, tem teste técnico separado e não depende de conta ou API.
