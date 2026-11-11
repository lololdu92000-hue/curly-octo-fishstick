import subprocess,json,wave,numpy as np,os
M='fr-siwis-medium/fr-siwis-medium.onnx'
starts=[0,3.8,9.0,13.4,18.0,23.0,28.2,32.6,37.0,42.0];END=48.6
L=["Personne t'a jamais raconté l'histoire de ces tours.",
"Années cinquante. Ici, c'était le bidonville de La Folie. Pas d'électricité.",
"Juin soixante et onze : tout est rasé.",
"En soixante-treize, l'architecte Émile Aillaud reçoit la commande.",
"Le chantier va durer jusqu'en mille neuf cent quatre-vingt-un.",
"Son idée : une mosaïque, pour que les tours se fondent dans le ciel.",
"Des fenêtres rondes, carrées… et en goutte d'eau.",
"Dix-huit tours. Leur surnom : les Tours Nuages.",
"Aujourd'hui, elles sont labellisées, et en rénovation depuis deux mille vingt-trois.",
"Alors… on fait quelle ville maintenant ? Dis-le en commentaire !"]
def dur(p):
    w=wave.open(p);return w.getnframes()/w.getframerate()
os.makedirs('lines',exist_ok=True)
SR=44100;out=np.zeros(int(END*SR))
# pitch: asetrate .93 (timbre plus jeune/masculin) + rubberband .905 => ~0.84
for i,txt in enumerate(L):
    raw=f'lines/raw{i}.wav'
    subprocess.run(['python3','-m','piper','-m',M,'-f',raw,'--length-scale','0.92','--noise-scale','0.7','--noise-w-scale','0.85','--sentence-silence','0.15'],input=txt.encode(),check=True,capture_output=True)
    d=dur(raw)/0.93
    win=(starts[i+1] if i+1<len(starts) else END-0.6)-starts[i]-0.45
    tempo=max(1.0,d/win)
    fx=f"asetrate={22050*0.93},aresample=44100,rubberband=pitch=0.905:tempo={tempo:.3f}:formant=preserved,highpass=f=90,equalizer=f=3500:t=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,aecho=0.8:0.5:28:0.12,loudnorm=I=-16:TP=-1.5"
    pr=f'lines/vo{i}.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',raw,'-af',fx,'-ac','1','-ar','44100',pr],check=True)
    w=wave.open(pr);x=np.frombuffer(w.readframes(w.getnframes()),np.int16)/32768
    s=int((starts[i]+0.25)*SR);e=min(len(out),s+len(x));out[s:e]+=x[:e-s]
    print(i,f'{d:.2f}s win {win:.2f} tempo {tempo:.2f}')
out=np.clip(out,-1,1)
w=wave.open('voice_full.wav','wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
