import { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, VolumeX } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Navbar, BottomNav } from '../components/Navbar'
import '../components/components.css'
import './ChatPage.css'

const API = '/api'

const LANG_NAMES = {
    hi: 'Hindi', en: 'English', bn: 'Bengali', ta: 'Tamil',
    te: 'Telugu', kn: 'Kannada', mr: 'Marathi', gu: 'Gujarati', pa: 'Punjabi'
}

/* Custom Sathi AI Avatar SVG */
const SathiAvatar = () => (
    <svg viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg" width="28" height="28">
        <circle cx="30" cy="22" r="10" fill="rgba(232,141,10,0.9)" />
        <circle cx="30" cy="22" r="6" fill="#0d0e1c" />
        <circle cx="27" cy="20" r="2" fill="#e88d0a" />
        <circle cx="33" cy="20" r="2" fill="#e88d0a" />
        <rect x="18" y="35" width="24" height="16" rx="4" fill="rgba(232,141,10,0.8)" />
        <rect x="22" y="40" width="4" height="6" rx="1" fill="#0d0e1c" />
        <rect x="34" y="40" width="4" height="6" rx="1" fill="#0d0e1c" />
        <line x1="30" y1="32" x2="30" y2="35" stroke="rgba(232,141,10,0.8)" strokeWidth="2" />
    </svg>
)

export default function ChatPage() {
    const navigate = useNavigate()
    const [messages, setMessages] = useState([
        {
            role: 'assistant',
            text: 'Namaste! 🙏 Main Sathi hoon — aapka AI saathi for government schemes.\n\n🎤 Mic button dabake voice mein bolein (Hindi, Tamil, Bengali — koi bhi bhasha), ya text likhein.',
            schemes: []
        }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [recording, setRecording] = useState(false)
    const [voiceMode, setVoiceMode] = useState(false)
    const [sessionId, setSessionId] = useState(null)
    const [audioPlaying, setAudioPlaying] = useState(false)
    const [dbSessionId, setDbSessionId] = useState(null)
    const [detectedLang, setDetectedLang] = useState('hi')

    // keep ref in sync so playAudio closure can read current voiceMode
    useEffect(() => { voiceModeRef.current = voiceMode }, [voiceMode])

    const bottomRef = useRef()
    const mediaRecRef = useRef(null)
    const chunksRef = useRef([])

    // Create/load session on mount
    useEffect(() => {
        initDbSession()
    }, [])

    const initDbSession = async () => {
        try {
            // First check if user is logged in
            const localUser = JSON.parse(localStorage.getItem('yojna_user'))
            if (!localUser) return

            // To keep things simple, generate a deterministic session 
            // ID based on user ID or email so they always resume their main thread
            const sid = `session-${localUser.email || 'guest'}`
            setDbSessionId(sid)

            // Chat history is kept in React state for the session.
            // (Backend /chat/session only supports DELETE to clear memory, no GET history endpoint)
        } catch (e) { console.error("Could not load history", e) }
    }

    // Notice we do NOT need to save messages individually anymore.
    // The AI Hub chat POST endpoint automatically saves user and assistant messages to SQLite.
    // We can remove saveMessage calls on the frontend to avoid duplicate data!
    // eslint-disable-next-line no-unused-vars
    const saveMessage = async (role, text) => {
        // Obsolete: Handled by backend `/api/chat` router now.
    }
    const audioRef = useRef(null)
    const voiceModeRef = useRef(false) // track voiceMode in closures

    const scrollBottom = () => bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    useEffect(scrollBottom, [messages, loading])

    const playAudio = async (blob) => {
        if (audioRef.current) { audioRef.current.pause(); audioRef.current = null }
        const url = URL.createObjectURL(blob)
        const audio = new Audio(url)
        audioRef.current = audio
        setAudioPlaying(true)
        audio.onended = async () => {
            setAudioPlaying(false)
            URL.revokeObjectURL(url)
            // Auto-listen: start mic again after each response if still in voice mode
            if (voiceModeRef.current) {
                await startRecordingAuto()
            }
        }
        audio.onerror = () => { setAudioPlaying(false); URL.revokeObjectURL(url) }
        await audio.play()
    }

    const stopAudio = () => {
        if (audioRef.current) { audioRef.current.pause(); audioRef.current = null }
        setAudioPlaying(false)
    }

    const addMsg = (role, text, extra = {}) =>
        setMessages(m => [...m, { role, text, schemes: [], ...extra }])

    const startVoiceSession = async () => {
        setLoading(true)
        try {
            const form = new FormData()
            form.append('language', 'hi')
            const res = await fetch(`${API}/voice/conversation/start`, { method: 'POST', body: form })
            if (!res.ok) throw new Error(`${res.status}`)
            const sid = res.headers.get('X-Session-Id')
            const qText = decodeURIComponent(res.headers.get('X-Question-En') || '')
            const blob = await res.blob()
            setSessionId(sid)
            setVoiceMode(true)
            addMsg('assistant', qText, { voice: true })
            await playAudio(blob)
        } catch (err) {
            addMsg('assistant', `\u26A0\uFE0F Voice session shuru nahi ho saka: ${err.message}`)
        } finally {
            setLoading(false)
        }
    }

    // Internal: starts mic without checking recording state — used by auto-listen
    const startRecordingAuto = async () => {
        try {
            // Brief pause so user knows Sathi finished before we listen
            await new Promise(r => setTimeout(r, 600))
            if (!voiceModeRef.current) return  // session ended while waiting
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
            const mr = new MediaRecorder(stream, { mimeType: 'audio/webm' })
            chunksRef.current = []
            mr.ondataavailable = (e) => { if (e.data.size > 0) chunksRef.current.push(e.data) }
            mr.onstop = () => stream.getTracks().forEach(t => t.stop())
            mr.start()
            mediaRecRef.current = mr
            setRecording(true)
        } catch {
            // silently fail — user can tap mic manually
        }
    }

    const startRecording = async () => {
        if (recording) return
        await startRecordingAuto()
    }

    const stopRecordingAndSend = () => {
        if (!mediaRecRef.current || !recording) return
        const mr = mediaRecRef.current
        mr.onstop = async () => {
            mr.stream?.getTracks().forEach(t => t.stop())
            setRecording(false)

            const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
            if (blob.size < 1000) {
                addMsg('assistant', '\u26A0\uFE0F Recording bahut choti thi. Thoda zyada bolein.')
                return
            }

            setMessages(m => [...m, { role: 'user', text: '\uD83C\uDFA4 [Voice message]', schemes: [] }])
            setLoading(true)

            try {
                const form = new FormData()
                form.append('audio', blob, 'answer.webm')
                form.append('session_id', sessionId)
                form.append('language', detectedLang)   // language hint → prevents STT misdetection
                const res = await fetch(`${API}/voice/conversation/answer`, { method: 'POST', body: form })
                if (!res.ok) throw new Error(`${res.status}`)

                const transcript = decodeURIComponent(res.headers.get('X-Transcript') || '')
                const reply = decodeURIComponent(res.headers.get('X-Reply') || '')
                const isDone = res.headers.get('X-Done') === 'true'
                const detLang = res.headers.get('X-Detected-Language') || 'hi'
                setDetectedLang(detLang)

                const audioBlob = await res.blob()

                if (transcript) {
                    setMessages(m => {
                        const updated = [...m]
                        updated[updated.length - 1] = { role: 'user', text: `\uD83C\uDFA4 "${transcript}"`, schemes: [] }
                        return updated
                    })
                }
                addMsg('assistant', reply, { voice: true })
                await playAudio(audioBlob)

                if (isDone) {
                    setVoiceMode(false)
                    setSessionId(null)
                    addMsg('assistant', '\u2705 Interview complete! Upar diye gaye schemes dekhein ya text mein aur puchhen.')
                }
            } catch (err) {
                addMsg('assistant', `\u26A0\uFE0F Voice error: ${err.message}`)
            } finally {
                setLoading(false)
            }
        }
        mr.stop()
    }

    const handleMicClick = async () => {
        if (recording) {
            stopRecordingAndSend()
        } else if (!voiceMode) {
            await startVoiceSession()
            await startRecording()
        } else {
            await startRecording()
        }
    }

    const sendMessage = async () => {
        if (!input.trim()) return
        const text = input.trim()
        addMsg('user', text)
        saveMessage('user', text)
        setInput('')
        setLoading(true)
        try {
            const res = await fetch(`${API}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, session_id: dbSessionId || 'frontend-demo' })
            })
            if (res.ok) {
                const data = await res.json()
                const reply = data.response || data.reply || data.message || 'Samajh gaya!'
                setMessages(m => [...m, {
                    role: 'assistant',
                    text: reply,
                    schemes: data.matched_schemes || []
                }])
            } else {
                const reply = 'Backend se connect nahi ho pa raha. /schemes pe jaakar schemes browse karein.'
                addMsg('assistant', reply)
            }
        } catch {
            const reply = 'Backend offline lag raha hai. Schemes browse karne ke liye "Schemes" click karein.'
            addMsg('assistant', reply)
        } finally {
            setLoading(false)
        }
    }

    const handleKey = e => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            if (recording) {
                stopRecordingAndSend()  // Enter = stop & send voice
            } else {
                sendMessage()
            }
        }
    }

    return (
        <div className="page-wrapper chat-wrapper">
            <Navbar />

            {voiceMode && (
                <div className="voice-mode-banner">
                    <span className="voice-pulse-dot" />
                    <span>
                        🌐 Detected: <strong>{LANG_NAMES[detectedLang] || detectedLang.toUpperCase()}</strong>
                        &nbsp;&bull; Tap 🎤 to speak
                    </span>
                    <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => { setVoiceMode(false); setSessionId(null); stopAudio() }}
                    >
                        End
                    </button>
                </div>
            )}

            <div className="chat-messages">
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-bubble-row ${msg.role}`}>
                        {msg.role === 'assistant' && (
                            <div className="chat-avatar sathi-avatar-custom"><SathiAvatar /></div>
                        )}
                        <div className={`chat-bubble glass-card ${msg.role}`}>
                            {msg.voice && <span className="chat-voice-tag">🔊 Voice</span>}
                            <p className="chat-text" style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</p>
                            {msg.schemes && msg.schemes.length > 0 && (
                                <div className="chat-schemes">
                                    {msg.schemes.map(s => (
                                        <div
                                            key={s.id || s.name}
                                            className="chat-scheme-card"
                                            onClick={() => navigate(`/schemes/${s.id || 'scheme'}`, { state: s })}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <p className="scheme-card-title">{s.name}</p>
                                            <p className="scheme-card-benefit">{s.benefit}</p>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="chat-bubble-row assistant">
                        <div className="chat-avatar sathi-avatar-custom"><SathiAvatar /></div>
                        <div className="chat-bubble glass-card assistant">
                            <div className="typing-indicator">
                                <div className="typing-dot" />
                                <div className="typing-dot" />
                                <div className="typing-dot" />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            <div className="chat-input-bar glass-card">
                <button
                    className={`chat-mic-btn ${recording ? 'recording' : voiceMode ? 'active' : ''}`}
                    onClick={handleMicClick}
                    title={recording ? 'Tap to stop & send' : voiceMode ? 'Tap to speak' : 'Start voice session'}
                    disabled={loading}
                >
                    {recording ? <MicOff size={18} /> : <Mic size={18} />}
                </button>

                {audioPlaying && (
                    <button className="chat-mic-btn active" onClick={stopAudio} title="Stop audio">
                        <VolumeX size={18} />
                    </button>
                )}

                <textarea
                    className="chat-input"
                    placeholder={recording ? '🔴 Recording… press Enter or tap 🎤 to send' : 'Yojana ke baare mein puchho…'}
                    value={input}
                    onChange={e => { if (!recording) setInput(e.target.value) }}
                    onKeyDown={handleKey}
                    rows={1}
                />
                <button
                    className="chat-send-btn btn btn-primary btn-sm"
                    onClick={recording ? stopRecordingAndSend : sendMessage}
                    disabled={loading || (!recording && !input.trim())}
                >
                    <Send size={16} />
                </button>
            </div>

            <BottomNav />
        </div>
    )
}
