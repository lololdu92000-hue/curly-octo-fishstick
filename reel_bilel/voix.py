import wave,numpy as np,json,sys
w=wave.open('../el2/voice.wav');sr=w.getframerate();x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768
segs=[(0,5.62),(5.80,9.56),(9.70,14.06),(14.20,18.57),(18.75,23.52),(23.92,26.13),(26.36,31.80),(31.95,37.33)]
starts=json.load(open('starts.json'));END=float(sys.argv[1])
out=np.zeros(int(END*sr))
for i,((a,b),s) in enumerate(zip(segs,starts)):
    seg=x[int(a*sr):int(b*sr)].copy();f=int(.02*sr);seg[:f]*=np.linspace(0,1,f);seg[-f:]*=np.linspace(1,0,f)
    st=int((s+(0.15 if i==0 else (0.06 if i==4 else 0.25)))*sr);out[st:st+len(seg)]+=seg[:len(out)-st]
    nxt=starts[i+1] if i+1<len(starts) else END
    print(i,f'voix {b-a:.2f}s -> fin {s+.25+b-a:.2f} / scène suivante {nxt:.2f}')
w=wave.open('voice_bilel.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((np.clip(out,-1,1)*32767).astype(np.int16).tobytes());w.close()
