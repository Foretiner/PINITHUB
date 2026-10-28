import { useEffect, useRef, useState } from 'react';

type CaptureSession = { sessionId: string; nonce: string; challenge: string; expiresAt: string };
const apiBase = (import.meta as ImportMeta & { env: { VITE_API_URL?: string } }).env.VITE_API_URL ?? 'http://localhost:3000';

export function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [consented, setConsented] = useState(false);
  const [session, setSession] = useState<CaptureSession | null>(null);
  const [message, setMessage] = useState('This development prototype cannot make identity decisions yet.');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (session && videoRef.current && streamRef.current) videoRef.current.srcObject = streamRef.current;
  }, [session]);

  useEffect(() => () => streamRef.current?.getTracks().forEach(track => track.stop()), []);

  async function begin() {
    setBusy(true);
    try {
      const response = await fetch(`${apiBase}/v1/bio/register/sessions`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ consent: true, noticeVersion: 'prototype-1' }),
      });
      if (!response.ok) throw new Error('The registration service is unavailable.');
      const created = await response.json() as CaptureSession;
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } }, audio: false });
      streamRef.current = stream;
      if (videoRef.current) videoRef.current.srcObject = stream;
      setSession(created);
      setMessage('When you press capture, keep a neutral face for the first 3 frames, then perform the displayed movement and blink sequence. 10 frames are captured over about 2.5 seconds and sent to the local API; this page does not save them.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to start camera capture.');
    } finally { setBusy(false); }
  }

  async function submitFrames() {
    if (!session || !videoRef.current) return;
    setBusy(true);
    try {
      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      if (!context) throw new Error('Camera capture is unavailable.');
      canvas.width = videoRef.current.videoWidth; canvas.height = videoRef.current.videoHeight;
      if (!canvas.width || !canvas.height) throw new Error('Wait for the camera image to load, then try again.');
      const form = new FormData();
      for (let i = 0; i < 10; i += 1) {
        context.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
        const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.85));
        if (!blob) throw new Error('Unable to capture an image.');
        form.append('frames', blob, `frame-${i}.jpg`);
        await new Promise(resolve => window.setTimeout(resolve, 250));
      }
      const response = await fetch(`${apiBase}/v1/bio/register/sessions/${session.sessionId}/frames`, {
        method: 'POST', headers: { 'X-Registration-Nonce': session.nonce }, body: form,
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.message ?? 'Biometric enrollment is not ready. No account was created.');
      setMessage('Capture submitted.');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Capture failed.');
    } finally {
      streamRef.current?.getTracks().forEach(track => track.stop()); streamRef.current = null; setSession(null); setBusy(false);
    }
  }

  return <main>
    <section className="card">
      <div className="eyebrow">PINITHUB · DEVELOPMENT PROTOTYPE</div>
      <h1>One person, one account</h1>
      <p className="intro">This is a local development preview. Biometric recognition, liveness checks, duplicate search, and account creation are not enabled.</p>
      <div className="notice"><strong>Privacy notice</strong><p>Camera frames are captured only after you start, sent to the local API, and analysed in memory by the research face service. The app does not save them or create an account. Do not use biometric data without an approved, consented research protocol.</p></div>
      <label className="consent"><input type="checkbox" checked={consented} onChange={event => setConsented(event.target.checked)} /> I understand this is a non-production prototype and consent to a temporary camera capture for local development.</label>
      <button disabled={!consented || busy} onClick={begin}>{busy ? 'Starting…' : 'Start camera'}</button>
      {session && <div className="capture"><p>Challenge: <strong>{session.challenge.replaceAll('_', ' ')}</strong></p><video ref={videoRef} autoPlay muted playsInline /><button disabled={busy} onClick={submitFrames}>Capture challenge (10 frames)</button></div>}
      <p className="status" role="status">{message}</p>
    </section>
  </main>;
}

