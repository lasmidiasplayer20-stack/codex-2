from pathlib import Path
import runpy,sys
P=Path(__file__).resolve().parents[1]
sys.argv[1:1]=['--project',str(P)]
runpy.run_path(str(P.parents[1]/'skill/scripts/facts45_audio.py'),run_name='__main__')
