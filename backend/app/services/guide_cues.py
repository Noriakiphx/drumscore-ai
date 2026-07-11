from app.models.score import GuideCue
_DEFAULTS=[
 GuideCue(id="intro",time_sec=0,bar=1,label="Intro",color="#49B6FF"),
 GuideCue(id="verse-a",time_sec=16,bar=9,label="Verse A",color="#7B4DFF"),
 GuideCue(id="chorus",time_sec=48,bar=25,label="Chorus",color="#FF7A59"),
 GuideCue(id="bridge",time_sec=80,bar=41,label="Bridge",color="#34D399"),
 GuideCue(id="ending",time_sec=112,bar=57,label="Ending",color="#FBBF24")]
class Store:
 def __init__(self): self.items=list(_DEFAULTS)
 def list(self): return self.items
 def add(self,c): self.items.append(c); self.items.sort(key=lambda x:x.time_sec); return c
 def reset(self): self.items=list(_DEFAULTS); return self.items
guide_cue_store=Store()
