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
