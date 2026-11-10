"""공개 영상의 통계 메타데이터만 수집. 미디어·댓글 본문은 다운로드하지 않음."""
import concurrent.futures, datetime, json, pathlib, subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1]
IDS=['Eir2GhnFJdc','QWYnZG7LfEs','xxrfVnnouhE','SAZnEJQhtnQ','1mDLxn3j4Hw','hd4djS203y0','LeNe13HbEBw']
path=ROOT/'stats.json'
previous=json.loads(path.read_text()) if path.exists() else {'videos':{}}
def collect(video_id):
 try:
  result=subprocess.run(['yt-dlp','--skip-download','--no-warnings','--socket-timeout','10','--retries','0','--extractor-retries','0','--no-playlist','--print','%(view_count)s\t%(comment_count)s\t%(upload_date)s','https://www.youtube.com/watch?v='+video_id],capture_output=True,text=True,timeout=55,check=True)
  parts=result.stdout.strip().split('\t')
  def count(s): return int(s) if s.isdigit() else None
  views,comments=count(parts[0]),count(parts[1])
  if views is None and comments is None: raise ValueError('통계 없음')
  return video_id,{'viewCount':views,'commentCount':comments,'publishedAt':parts[2] if parts[2].isdigit() else None,'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'YouTube 공개 영상 메타데이터'}
 except Exception:
  print(video_id+': 조회 실패, 기존 확인값 보존')
  return video_id,None
success=0
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for video_id,data in pool.map(collect,IDS):
  if data:
   previous['videos'][video_id]=data;success+=1;print(video_id+': 통계 확인')
if success:
 previous['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 path.write_text(json.dumps(previous,ensure_ascii=False,indent=2)+'\n')
print(f'{success}/{len(IDS)} 확인 완료')
if not success: raise SystemExit(1)
