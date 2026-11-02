# Executar a parte 01 pelo agente do Flow

O comando mestre contém as instruções da parte inteira, mas não é uma integração remota já executada. Este chat não controla o Flow. O agente dentro da conta do usuário precisa realizar as gerações e pode exigir confirmações ou continuação. O comportamento do agente com este comando ainda não foi testado ao vivo.

## Resultado relatado na conta

O usuário informou que o comando produziu somente um vídeo. Portanto, a execução em lote NÃO foi validada. Não repetir o comando inteiro para tentar forçar o lote: primeiro conferir quantas imagens existem e qual cena corresponde ao vídeo novo. Usar [DIAGNOSTICO-FLOW.txt](DIAGNOSTICO-FLOW.txt) para pedir ao agente apenas inventário e motivo observável da interrupção, sem nova geração. Um único resultado não comprova um limite de um vídeo por conta, plano ou ferramenta.

## Primeiro envio

1. Abra o mesmo projeto do Flow onde fez o primeiro clipe. Manter o projeto ajuda a conservar as referências e os resultados.
2. Baixe [a referência visual existente](../partes/01%20-%20O%20medo%20no%20berco/imagens/001-referencia-final.png) e anexe-a ao painel de conversa do agente. Ela mostra o Lameque e o acabamento desejado.
3. Abra [COMANDO-PARTE-01.txt](COMANDO-PARTE-01.txt), copie o conteúdo inteiro e cole na conversa do agente do Flow.
4. O agente deve procurar as referências já existentes. Para Lameque, reutilizar o homem à direita da imagem anexada. Para Enoque, procurar uma referência existente e, somente se não houver, criar uma ficha fixa antes das cenas que a utilizam.
5. A cena `ENQ-01-01` já existe. O trabalho pendente são 14 imagens, caso ainda não existam no Flow, e 14 animações. A ficha de Enoque é uma tarefa adicional apenas se ainda não existir. Não gerar outra voz.
6. Atender às confirmações que o Flow realmente mostrar. Se o agente pausar, usar [RETOMAR-PARTE-01.txt](RETOMAR-PARTE-01.txt), que manda conferir o que já existe e continuar dos IDs pendentes.
7. Ao concluir, baixar os vídeos e a referência de Enoque. Pedir nomes como `ENQ-01-02.mp4` até `ENQ-01-15.mp4` quando a plataforma permitir. Se os nomes forem diferentes, guardar a tabela ID → nome do arquivo fornecida pelo agente.
8. Colocar os arquivos na pasta compartilhada do Drive, podendo usar um ZIP, e informar aqui o nome do pacote. Com os arquivos disponíveis, o Codex pode recebê-los, conferir identidade e movimento, corrigir a temporização quando necessário e montar o minuto com a Algenib existente e Foley Python.

Não presumir que tudo será concluído em uma única interação: limites de contexto, geração, créditos, confirmações e recursos do agente podem interromper o processo. Não há garantia de persistência automática do estado; manter o mesmo projeto, as referências e a tabela de resultados permite retomar sem reconstruir tudo.

## Consistência dos personagens

- `LAMEQUE_01` é o homem à direita na referência já aprovada, não as figuras laterais.
- `ENOQUE_01` usa uma única ficha com aparência distinta: cabelo e barba prateados, rosto alongado, túnica e manto simples.
- Matusalém e o vigilante simbólico têm IDs reservados, mas suas referências só precisam ser criadas quando entrarem na produção.
- Reutilizar o mesmo recorte é mais confiável do que pedir um rosto novo a cada composição. Para poses novas, anexar a mesma referência de identidade e conferir o resultado antes de animar.
- Um prompt e uma referência reduzem variação, mas não garantem rostos idênticos em toda geração. A conferência visual dos resultados continua necessária; não foi implementado nem alegado um verificador automático infalível de identidade.

A biblioteca de personagens é própria desta série e não redefine o Nico dos outros vídeos. A escolha da Algenib original também permanece intacta.

## Estado local e novos comandos

`progresso-parte-01.json` descreve apenas arquivos efetivamente recebidos neste repositório. Não acessa a conta Flow nem sabe quais assets existem lá e ainda não foram baixados. Por isso o comando manda o agente procurar assets existentes antes de gerar novamente.

O exportador não chama APIs nem gera mídia:

```bash
python3 export_flow.py --part 1
```

Ele lê o plano, exclui clipes já recebidos e escreve o comando e o estado local. O exportador só aceita partes que já tenham um plano escrito; as outras 24 partes ainda não possuem seus prompts completos. Após a revisão do primeiro minuto, o mesmo método pode ser aplicado a elas, conservando as referências.

A montagem local está em `../../tutorial-flow/assemble.py`. Ela exige os 15 clipes, descarta o áudio de origem e usa os WAVs aprovados. Foley e revisão final de som entram na etapa de vídeo; não regenerar a voz para corrigir a montagem.

## Se o agente parou depois das imagens

Usar [ANIMAR-PARTE-01-FLOW.txt](ANIMAR-PARTE-01-FLOW.txt), um comando menor exclusivamente para executar a animação das imagens prontas em lotes de até cinco. Ele não regenera imagens, personagens ou narração. O comando exige arquivos reais e uma tabela de resultados, mas sua execução ainda depende das ferramentas e permissões disponíveis no Flow. Apenas salvar instruções ou receber uma resposta de planejamento não comprova que os vídeos foram gerados.

Atualização: o usuário confirmou que as outras 14 imagens existem no Flow. Não pedir nova geração de imagens. Falta receber a resposta do agente após o vídeo único e identificar o vídeo/cena concluído e eventuais confirmações pendentes. O mapeamento dos nomes reais dos assets ainda não foi recebido.
