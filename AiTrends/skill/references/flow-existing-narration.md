# Flow com narração já aprovada

Caso de referência: [Enoque — adaptação do tutorial](../../Apocalipse/01%20-%20Enoque%20-%20Alem%20do%20mundo%20visivel/video/tutorial-flow/README.md). O usuário forneceu `Tutorial.mp4` no Drive e pediu uma forma de aplicar o método aos 25 minutos de Algenib já entregues.

O tutorial apresenta Claude como planejador/operador de uma ferramenta personalizada no Google Flow. A geração e montagem não são capacidades exclusivas de um plugin do Claude. Distinguir o que foi observado no vídeo, o que foi construído localmente e o que está testado na conta real do Flow.

- Reutilizar os WAVs aprovados. Não gerar voz no Flow, trocar narrador nem pedir novamente a aprovação dessa mesma configuração.
- Planejar ações e câmera segundo a fala já existente. Um plano com durações estimadas não equivale a alinhamento de palavras; conferir os cortes com reprodução antes de tratá-los como finais.
- Preservar identidade visual dos personagens por referência constante, sem transformar cada tomada em um novo personagem.
- A chave Gemini API não autentica uma sessão no site Flow. Não prometer acesso ao Tool Builder, automação por navegador, custo, créditos ou importação de áudio longo sem verificar os recursos realmente disponíveis.
- Se necessário, gerar/receber clipes visuais e montar localmente com Python/FFmpeg. Descartar o áudio dos clipes. Não congelar, repetir nem acelerar automaticamente cenas curtas.
- Guardar IDs e estado por cena para retomar falhas sem regenerar cenas prontas. Testar um trecho pequeno em movimento antes de ampliar a produção.
- Contabilizar geração de clipes separadamente da voz já pronta. Não acionar geração paga por causa de um documento de referência. Prosseguir dentro da autorização real do usuário e do acesso disponível, sem criar novas etapas de aprovação para ações já autorizadas.

O kit contém uma especificação original para o Tool Builder, storyboard provisório de um minuto, referências das 25 partes e montador local testado em 2 s com fontes sintéticas. O teste valida montagem e preservação do áudio, não geração Flow nem aparência da série. Nenhum clipe real do Flow foi gerado nesta etapa. No vídeo final, aplicar também os cuidados de articulações, estabilidade temporal e Foley Python já documentados no estúdio.

## Referência posterior — tutorial_2

O usuário esclareceu o visual com `tutorial_2.mp4`: colagem documental de papel, mapas e recortes, não a proposta anterior de personagens ilustrados. A tela mostra Nano Banana 2 nas imagens, Omni Flash na animação e uma alternativa Qwen3.8-Max com Criar Vídeo. O prompt de animação visível trata a imagem como quadro final da composição. Ver [análise e prompts de teste](../../Apocalipse/01%20-%20Enoque%20-%20Alem%20do%20mundo%20visivel/video/tutorial-02-vox/README.md). Não chamar a imagem de Lameque gerada no chat ou o storyboard anterior de amostra desse novo visual. Preservar a Algenib; não repetir a etapa ElevenLabs/realce de voz do tutorial. Limites e disponibilidade dos geradores permanecem dependentes da conta e não foram testados aqui.

### Duração definida depois pelo usuário

Enoque passa a ter 25 partes de um minuto, com 15 cenas de quatro segundos cada: 375 cenas. Imagens no Nano Banana 2 e animações no Omni dentro do Flow. O usuário informou conta paga; isso não estabelece acesso conectado ao chat. Não afirmar que o modelo aceita quatro segundos nativos sem verificar na conta: a edição pode aproveitar uma janela de quatro segundos de uma origem maior, preservando a construção e a composição final, sem acelerar. A especificação está em `video/tutorial-02-vox/production-spec.json`; os 15 prompts da parte 01 foram preparados, sem gerar assets ou gastar créditos de vídeo.

### Primeiro clipe recebido do usuário

`enoque-01.mp4` (Drive `1Rzpo1KztzFYc-xDLG50QL1erDTD3cAQG`) é o teste curto da colagem, distinto da referência longa `Enoque_01.mp4`. Recebido em 1080p/24 fps, 94 quadros de vídeo. Um quadro isolado na abertura mostrava a composição completa antes de retornar ao papel vazio; ele foi removido. A composição final já estável ganhou três quadros de leitura, resultando em 96 quadros/4 s, sem acelerar a animação. Original preservado; versão de montagem em `video/tutorial-02-vox/partes/01 - O medo no berco/clips/001.mp4`, sem áudio do gerador. Não regenerar essa cena automaticamente. O Google havia bloqueado uma imagem anterior com aviso de conteúdo relacionado a menores; os prompts seguintes passaram a usar adultos com roupas antigas e objetos simbólicos, sem mostrar menores. Isso altera o conteúdo visual e não garante aprovação futura pelo serviço.

### Automação por comando mestre e consistência

O usuário pediu execução por partes com consistência dos personagens e perguntou sobre um único prompt. Preparado `video/tutorial-02-vox/automation/COMANDO-PARTE-01.txt`: texto autocontido para colar no agente do Flow, com referência anexada. Este chat não tem acesso direto à conta. O comando pede 14 imagens e 14 animações faltantes e exclui a cena 001. `characters.json` fixa LAMEQUE_01 pelo homem à direita na referência e reserva identidades distintas de Enoque e Matusalém; as referências faltantes devem ser procuradas no projeto antes de criar novas. Reutilizar referências e recortes, sem prometer identidade perfeita só por prompt. Manter a mesma conversa/projeto e registrar nomes reais dos assets. `export_flow.py` lê apenas arquivos locais e produz o comando e estado local, sem chamar APIs. O estado não prova o que foi gerado no Flow e ainda não foi baixado. Não prometer 25 minutos ou sequer um bloco concluído em uma única interação: podem existir confirmações, pausas e limites. O exportador foi conferido para excluir a cena concluída e produzir saída repetível; a execução do comando no Flow não foi testada.

Se o agente responder com planejamento ou parar após gerar imagens, o comando específico `automation/ANIMAR-PARTE-01-FLOW.txt` pede execução dos vídeos em lotes, usando apenas imagens prontas. Não chamar um arquivo de instruções de automação já funcionando: é necessário observar a invocação das ferramentas e os vídeos retornados na conta real. Salvar instruções em Concluir não inicia por si só a execução.

### Resultado real do comando no Flow

O usuário relatou que a tentativa gerou apenas um vídeo. Não tratar o prompt mestre como automação em lote validada. Primeiro conferir se as outras 14 imagens existem, qual cena foi animada e o que o agente informou sobre a interrupção. Usar o pedido de inventário em `automation/DIAGNOSTICO-FLOW.txt`, sem nova geração. Não atribuir a causa a um limite da plataforma, cota ou falha de prompt sem evidência. Não repetir o lote inteiro nem afirmar que um texto maior resolverá. Automação garantida exigiria uma integração/controlador executável e testado, indisponível neste chat para a conta Flow.
