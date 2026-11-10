"""Public video statistics only. No arbitrary URLs, media downloads or user data."""
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import urlsplit,parse_qs
from collections import defaultdict,deque
import datetime,json,re,subprocess,sys,threading,time
ORIGIN='https://ohmaetdol.github.io'
CACHE={};LOCK=threading.Lock();SLOTS=threading.BoundedSemaphore(2);REQUESTS=defaultdict(deque);GLOBAL=deque()

def extract(video_id):
    result=subprocess.run([sys.executable,'-m','yt_dlp','--skip-download','--ignore-no-formats-error','--no-warnings','--socket-timeout','8','--retries','0','--extractor-retries','0','--no-playlist','--extractor-args','youtube:skip=hls,dash','--print','%(view_count)s\t%(comment_count)s','https://www.youtube.com/watch?v='+video_id],capture_output=True,text=True,timeout=30)
    parts=result.stdout.strip().split('\t')
    def count(s):return int(s) if s.isdigit() else None
    if len(parts)!=2 or count(parts[0]) is None:raise ValueError('public statistics unavailable')
    return {'id':video_id,'viewCount':count(parts[0]),'commentCount':count(parts[1]),'checkedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'YouTube 공개 통계 자동 조회'}
class Handler(BaseHTTPRequestHandler):
    server_version='VideoStats/1'
    def log_message(self,*args):pass
    def reply(self,code,data):
        body=json.dumps(data,ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('Access-Control-Allow-Origin',ORIGIN)
        self.send_header('Vary','Origin')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers();self.wfile.write(body)
    def do_OPTIONS(self):
        self.send_response(204);self.send_header('Access-Control-Allow-Origin',ORIGIN);self.send_header('Access-Control-Allow-Methods','GET, OPTIONS');self.end_headers()
    def do_GET(self):
        u=urlsplit(self.path)
        if u.path=='/health':return self.reply(200,{'ok':True})
        if u.path!='/api/stats':return self.reply(404,{'error':'not found'})
        origin=self.headers.get('Origin')
        if origin and origin!=ORIGIN:return self.reply(403,{'error':'origin not allowed'})
        ids=parse_qs(u.query).get('id',[])
        if len(ids)!=1 or not re.fullmatch(r'[A-Za-z0-9_-]{11}',ids[0]):return self.reply(400,{'error':'valid video ID required'})
        video_id=ids[0];now=time.monotonic()
        with LOCK:
            cached=CACHE.get(video_id)
            if cached and now-cached[0]<3600:return self.reply(200,{**cached[1],'cached':True})
            ip=self.headers.get('X-Forwarded-For',self.client_address[0]).split(',')[0].strip()[:64]
            bucket=REQUESTS[ip]
            for queue in [bucket,GLOBAL]:
                while queue and now-queue[0]>60:queue.popleft()
            if len(bucket)>=15 or len(GLOBAL)>=60:return self.reply(429,{'error':'잠시 후 다시 시도하세요'})
            if len(REQUESTS)>2000:REQUESTS.clear()
            bucket.append(now);GLOBAL.append(now)
        if not SLOTS.acquire(blocking=False):return self.reply(429,{'error':'통계 조회 중입니다. 잠시 후 다시 시도하세요'})
        try:
            data=extract(video_id)
            with LOCK:
                if len(CACHE)>2000:CACHE.clear()
                CACHE[video_id]=(time.monotonic(),data)
            return self.reply(200,data)
        except Exception:
            if cached:return self.reply(200,{**cached[1],'stale':True})
            return self.reply(502,{'error':'YouTube에서 공개 통계를 가져오지 못했어요. 잠시 후 다시 시도하세요'})
        finally:SLOTS.release()
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',8080),Handler).serve_forever()
