import { useState, useRef } from 'react'
import { Camera, Upload, CheckCircle, XCircle, HelpCircle, RefreshCw } from 'lucide-react'
import { Navbar, BottomNav } from '../components/Navbar'
import '../components/components.css'
import './ScannerPage.css'

const SAMPLE_RESULT = {
    doc_type: 'Aadhaar Card',
    fields: { Name: 'Rajesh Kumar', 'Date of Birth': '15/08/1985', Address: 'Village Rampur, Dist. Pune, Maharashtra — 412010' },
    missing: ['Income Certificate', 'Bank Statement'],
    validity: { is_valid: true, has_seal: true }
}

export default function ScannerPage() {
    const [state, setState] = useState('idle') // idle | scanning | result
    const [result, setResult] = useState(null)
    const fileRef = useRef()

    const handleFile = (e) => {
        const file = e.target.files[0]
        if (!file) return
        setState('scanning')
        setTimeout(() => { setState('result'); setResult(SAMPLE_RESULT) }, 2200)
    }

    const reset = () => { setState('idle'); setResult(null) }

    return (
        <div className="page-wrapper">
            <Navbar />
            <main className="page-content">

                <div className="scanner-header">
                    <h1 className="scanner-title">Jan-Sahayak Lens 📷</h1>
                    <p className="text-muted scanner-sub">Apna document scan karein — fields auto-extract honge</p>
                </div>

                {state === 'idle' && (
                    <>
                        {/* Viewfinder */}
                        <div className="glass-card scanner-viewfinder">
                            <div className="scanner-frame">
                                <div className="scanner-corner tl" />
                                <div className="scanner-corner tr" />
                                <div className="scanner-corner bl" />
                                <div className="scanner-corner br" />
                                <div className="scan-line" />
                                <div className="scanner-placeholder">
                                    <Camera size={48} className="text-muted" />
                                    <p className="text-muted scanner-placeholder-text">Document yahan rakhein</p>
                                </div>
                            </div>
                        </div>

                        <div className="scanner-actions">
                            <button className="btn btn-primary btn-lg scanner-upload-btn" onClick={() => fileRef.current.click()}>
                                <Upload size={18} /> Document Upload Karein
                            </button>
                            <input ref={fileRef} type="file" accept="image/*,.pdf" hidden onChange={handleFile} />
                            <p className="text-subtle scanner-note">Aadhaar, Ration Card, Income Certificate, Land Records. Camera access requires HTTPS.</p>
                        </div>

                        <div className="scanner-supported">
                            {['📄 Aadhaar', '📑 PAN', '🌾 Khasra', '📋 Income Cert.', '🏥 Health Card'].map(d => (
                                <span key={d} className="badge badge-muted">{d}</span>
                            ))}
                        </div>
                    </>
                )}

                {state === 'scanning' && (
                    <div className="scanner-loading glass-card">
                        <div className="scanner-spinner">
                            <RefreshCw size={36} className="text-saffron spin" />
                        </div>
                        <p className="scanner-loading-text">Document scan ho raha hai…</p>
                        <p className="text-subtle" style={{ fontSize: 13 }}>PaddleOCR + AI field extraction</p>
                        <div className="shimmer shimmer-line wide" style={{ margin: '8px auto', maxWidth: 240 }} />
                        <div className="shimmer shimmer-line medium" style={{ margin: '4px auto', maxWidth: 180 }} />
                    </div>
                )}

                {state === 'result' && result && (
                    <>
                        {/* Doc Type */}
                        <div className="glass-card glass-card-glow scanner-result-header">
                            <div className="scanner-result-badge">
                                <CheckCircle size={20} className="text-green" />
                                <span className="badge badge-green">Valid Document</span>
                            </div>
                            <h2 className="scanner-doc-type">{result.doc_type}</h2>
                        </div>

                        {/* Extracted Fields */}
                        <div className="glass-card scanner-fields">
                            <h3 className="scanner-fields-title">Extracted Fields ✅</h3>
                            {Object.entries(result.fields).map(([key, val]) => (
                                <div key={key} className="scanner-field-row">
                                    <span className="scanner-field-key text-muted">{key}</span>
                                    <span className="scanner-field-val">{val}</span>
                                </div>
                            ))}
                        </div>

                        {/* Missing Fields */}
                        {result.missing.length > 0 && (
                            <div className="glass-card scanner-missing">
                                <h3 className="scanner-fields-title"><XCircle size={16} className="text-red" /> Missing Documents</h3>
                                {result.missing.map((m, i) => (
                                    <div key={i} className="scanner-missing-row">
                                        <XCircle size={14} className="text-red" />
                                        <span className="text-muted">{m}</span>
                                        <button className="btn btn-ghost btn-sm scanner-guide-btn">
                                            <HelpCircle size={12} /> Kaise Prapt Karein?
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <button className="btn btn-ghost scanner-reset-btn" onClick={reset}>
                            <RefreshCw size={16} /> Dobara Scan Karein
                        </button>
                    </>
                )}

            </main>
            <BottomNav />
        </div>
    )
}
