"""Create an empty numbered episode; never overwrite, generate speech or call APIs."""
from pathlib import Path
import argparse,json,re,unicodedata,shutil
BASE=Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('title');p.add_argument('--seconds',type=float,default=510);p.add_argument('--slug');p.add_argument('--copy-cast',action='store_true');a=p.parse_args()
 if not 5<=a.seconds<=3600:raise SystemExit('Choose 5–3600 seconds.')
 slug=a.slug or re.sub('[^a-z0-9]+','-',unicodedata.normalize('NFKD',a.title).encode('ascii','ignore').decode().lower()).strip('-')
 if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug):raise SystemExit('Use a simple lowercase hyphenated slug.')
 directory=BASE/'projetos';directory.mkdir(exist_ok=True);numbers=[int(m.group(1))for f in directory.iterdir()if(m:=re.match(r'^(\d+)-',f.name))];number=max(numbers,default=0)+1;root=directory/f'{number:02}-{slug}';root.mkdir(exist_ok=False)
 for sub in ['input','story','scenes','scripts','audio','timeline','exports','qa']:(root/sub).mkdir()
 cfg={'title':f'{number:02} - {a.title}','aspect':'16:9','resolution':'1080p','fps':24,'style':'entaoSpeed','duration':a.seconds,'voiceover':'audio/narracao.mp3','script':'input/narracao.txt','captions':False,'bars':'none','fadeIn':.25,'fadeOut':.9,'fast3D':True}
 for name,obj in [('config.json',cfg),('runtime-style.json',{'contrast':1,'sat':1,'lift':[0,0,0],'gamma':[1,1,1],'gain':[1,1,1],'vignette':.23,'grain':0,'bloom':0}),('story/beats.json',[]),('story/shots.json',{'title':a.title,'duration':a.seconds,'shots':[]})]:(root/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
 (root/'input/narracao.txt').write_text('');(root/'.gitignore').write_text('build/\nreferencias/\naudio/*.wav\n*.log\n__pycache__/\n');(root/'README.md').write_text(f'# {cfg["title"]}\n\nProjeto vazio; leia `../../skill/SKILL.md`, escreva roteiro e cenas próprios antes de renderizar. Nenhuma voz ou imagem foi gerada.\n')
 if a.copy_cast:
  example=BASE/'projetos/03-10x-mais-rapido/scenes'
  for f in ['rig.js','world.js']:shutil.copyfile(example/f,root/'scenes'/f)
 youtube=BASE/'youtube'/cfg['title'];youtube.mkdir(parents=True,exist_ok=False)
 for name in ['titulo.txt','descricao.txt','tags.txt']:(youtube/name).write_text('')
 print(root);print(youtube)
if __name__=='__main__':main()
