"""Build a self-contained Flow-agent command from local plans; no remote execution."""
from pathlib import Path
import argparse,json,hashlib,re
A=Path(__file__).resolve().parent;V=A.parent

def write(path,text):
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(text,encoding='utf-8');temp.replace(path)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--part',type=int,required=True);args=parser.parse_args();matches=sorted((V/'partes').glob(f'{args.part:02} - */plano-*.json'))
 if len(matches)!=1:raise SystemExit('Exactly one written plan is required; no prompts invented for unwritten parts.')
 path=matches[0];base=path.parent;plan=json.loads(path.read_text());characters=json.loads((A/'characters.json').read_text());style=json.loads((A/'style-lock.json').read_text());states=[]
 for shot in plan['shots']:
  clip=base/shot['clip'];image=base/shot.get('reference_final_frame',shot['image']);qa=base/shot.get('qa',f"QA-{shot['id'][-2:]}.json");exists=clip.exists();states.append({'id':shot['id'],'image_received':image.exists(),'video_received':exists,'video_sha256':hashlib.sha256(clip.read_bytes()).hexdigest()if exists else None,'local_qa_exists':qa.exists(),'status':'video_received'if exists else'image_received'if image.exists()else'not_received','character_ids':shot.get('character_ids',[])})
 pending=[s for s,st in zip(plan['shots'],states)if not st['video_received']];needed=sorted({k for s in pending for k in s.get('character_ids',[])});missing=[k for k in needed if not characters['characters'][k].get('reference_file')];done=[s['id']for s,st in zip(plan['shots'],states)if st['video_received']]
 intro=f'''PROJETO ENOQUE — PARTE {args.part:02} — COMANDO MESTRE PARA O AGENTE DO FLOW

Este texto é uma instrução a executar no projeto Flow do usuário, NÃO uma conexão ao ChatGPT e NÃO um programa já executado. Trabalhar somente nesta parte. A imagem de referência visual deve estar anexada à conversa. Não iniciar se não conseguir acessar essa referência; informar o que falta.

OBJETIVO
Produzir as imagens e animações faltantes desta parte, em colagem documental original. São 15 cenas de quatro segundos úteis cada, 60 segundos no total. A narração Algenib já existe e será colocada na montagem externa; não criar voz, fala, música, efeitos ou novo roteiro. Imagens: Nano Banana 2 disponível na conta. Vídeo: Omni disponível na conta. Não substituir modelos silenciosamente. Se um recurso não estiver disponível, informar a limitação real.

JÁ CONCLUÍDO — NÃO REFAZER
{', '.join(done)or'Nenhum clipe recebido ainda.'}

CONSISTÊNCIA GLOBAL
Usar a imagem anexada como referência de materiais, gravura, papel, sombras e acabamento. Paleta: {', '.join(style['palette'])}. A mesma pessoa deve manter o rosto, cabelo, barba, corpo, roupa e sandálias. Sempre reutilizar as referências de identidade; uma descrição textual isolada não garante consistência. Preferir reutilizar o mesmo recorte de personagem e mudar a composição ao redor dele. Novas poses não podem reinventar a identidade. Figuras decorativas secundárias devem ser silhuetas discretas, sem novos protagonistas. Preservar as mesmas identidades durante a animação; mover peças de papel, não transformar rostos. Não inserir menores na imagem: passagens de nascimento serão representadas por adultos e objetos simbólicos.

BIBLIOTECA DE PERSONAGENS NECESSÁRIOS NESTA PARTE
'''
 style_prefix=plan['shots'][0]['image_prompt'].split('Não copiar composições de outro canal.',1)[0]+'Não copiar composições de outro canal.'
 animation_common=pending[0]['animation_prompt'].split(' Movimento específico:',1)[0]if pending else''
 lines=[intro,'ESTILO COMUM A TODAS AS IMAGENS',style_prefix,'','CONTINUIDADE DE REFERÊNCIAS','Antes de criar qualquer ficha, procurar no projeto e no histórico uma referência já existente com o ID do personagem. Reutilizá-la se existir. Ausência de arquivo local não prova ausência no Flow. Gerar uma referência nova somente se ela realmente não existir. Rotular como REF-ID-v1 quando a ferramenta permitir e registrar o nome real para futuras partes.','']
 for key in needed:
  c=characters['characters'][key];lines.extend([key+' — '+c['display_name'],c['identity_instruction']])
  if c.get('reference_file'):lines.append('Referência já existente: a imagem anexada. O homem em primeiro plano à direita é LAMEQUE_01; ignorar as figuras laterais para essa identidade.')
  else:lines.extend(['Criar UMA referência visual fixa antes das cenas que usam este personagem. Guardá-la no projeto, registrar o nome real do asset e reutilizá-la nas próximas solicitações. Não criar uma versão diferente por cena.',c['new_reference_prompt']])
  lines.append('')
 lines+=['EXECUÇÃO','1. Preparar apenas as referências de personagem faltantes listadas acima.','2. Gerar imagens faltantes em lotes de no máximo dez, com referência de estilo e identidade em cada solicitação. Uma imagem por cena, nunca uma prancha com várias cenas. Pedir uma única saída por cena quando esse controle existir; não gerar variações extras automaticamente.','3. Conferir a continuidade das referências nos resultados. Se um rosto ou roupa mudou, revisar somente aquela imagem antes de animá-la. Não afirmar que a verificação ocorreu se não conseguir comparar os assets.','4. Animar as imagens prontas em lotes de no máximo cinco. A imagem é o quadro FINAL: os recortes entram e se encaixam até formar a composição.','5. Solicitar quatro segundos quando o modelo oferecer essa duração. Não fingir suporte a uma duração indisponível. Se exportar mais, construir a composição principal nos primeiros quatro segundos e prolongar apenas sua leitura final. O corte útil será conferido na edição.','6. Evitar o problema do teste 001: não exibir a composição pronta em um quadro isolado e depois voltar ao papel vazio. Começar no fundo e iniciar a entrada dos recortes prontamente.','7. Não gerar novamente cenas prontas ao retomar. Manter IDs, nomes reais dos assets e estado por cena. Se precisar de outra interação, parar em um ponto identificável e informar de onde continuar.','8. Se uma solicitação falhar por política, cota ou outro erro, registrar o ID e o aviso. Não repetir indefinidamente, comprar créditos, mudar de conta ou contornar a recusa. Prosseguir apenas nas etapas que a plataforma permitir.','9. Respeitar as confirmações nativas que a plataforma exigir. Não declarar que um download/exportação foi concluído sem arquivo real.','','IMAGENS PENDENTES']
 for s,st in zip(plan['shots'],states):
  if st['video_received']or st['image_received']:continue
  lines.extend(['',s['id']+' — '+s['title'],'PERSONAGENS: '+(', '.join(s.get('character_ids',[]))or'Objetos; nenhum protagonista novo.'),re.sub(r'Figuras humanas adultas com.*?não mostrar bebês ou crianças\.\s*','',s['image_prompt'].replace(style_prefix,'',1),flags=re.S).strip()])
 lines+=['','REGRA DE ANIMAÇÃO COMUM',animation_common,'','ANIMAÇÕES PENDENTES']
 for s in pending:lines.extend(['',s['id']+' — '+s['title'],s['animation_prompt'].split(' Movimento específico: ',1)[-1].split(' Não mostrar a composição inteira')[0]])
 lines+=['','ENTREGA E RETOMADA','Rotular cada asset com seu ID de cena quando o Flow permitir. Exportar os MP4s individuais; os nomes desejados são ENQ-PP-CC.mp4, com PP=parte e CC=cena. Se a ferramenta exportar nomes diferentes, entregar uma tabela ID da cena → nome real do arquivo. Não presumir que há ZIP ou renomeação automática: usar apenas os recursos reais disponíveis.','Ao encerrar, informar em tabela: ID, referência de personagem usada, nome da imagem, nome do vídeo, duração real e estado (pronto/falhou/pendente). Não confundir imagem gerada com vídeo concluído.','Não montar uma nova voz nem inserir a narração dentro de clipes separados. A montagem local juntará os clipes à faixa Algenib contínua, com som procedural discreto.']
 text='\n'.join(lines).strip()+'\n';out=A/f'COMANDO-PARTE-{args.part:02}.txt';write(out,text)
 progress={'part':args.part,'flow_control_available_in_this_chat':False,'command_exported_not_executed':True,'plan_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'style_reference':characters['style_reference'],'character_references_not_received_locally_find_or_create_in_flow':missing,'scenes':states,'videos_received':sum(s['video_received']for s in states),'images_received':sum(s['image_received']for s in states),'videos_pending':len(pending),'output_command':out.name};write(A/f'progresso-parte-{args.part:02}.json',json.dumps(progress,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'part':args.part,'videos_received':progress['videos_received'],'videos_pending':len(pending),'character_references_to_find_or_create_in_flow':missing,'command_characters':len(text),'command_file':str(out)},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
