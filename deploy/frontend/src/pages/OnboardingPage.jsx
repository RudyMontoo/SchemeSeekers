import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, ArrowLeft, Check } from 'lucide-react'

import './OnboardingPage.css'

const STEPS = [
    { id: 1, title: 'Aapka Parichay', subtitle: 'Tell us about yourself' },
    { id: 2, title: 'Aapka Sthan', subtitle: 'Where are you from?' },
    { id: 3, title: 'Aapki Zaroorat', subtitle: 'What help do you need?' },
]

const STATES = [
    'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat', 'Haryana',
    'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra',
    'Manipur', 'Meghalaya', 'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu', 'Telangana',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
]

const CATEGORIES = [
    { emoji: '🌾', label: 'Agriculture' },
    { emoji: '🏠', label: 'Housing' },
    { emoji: '❤️', label: 'Health' },
    { emoji: '🎓', label: 'Education' },
    { emoji: '👩', label: 'Women' },
    { emoji: '🛠️', label: 'Skill Dev' },
    { emoji: '👴', label: 'Pension' },
    { emoji: '💼', label: 'Business' },
]

export default function OnboardingPage() {
    const navigate = useNavigate()
    const [step, setStep] = useState(1)
    const [saving, setSaving] = useState(false)
    const [form, setForm] = useState({
        name: localStorage.getItem('pending_name') || '',
        dob: '', occupation: 'farmer', state: '', district: '', income: '', categories: []
    })

    const update = (field, val) => setForm(f => ({ ...f, [field]: val }))
    const toggleCat = (cat) => {
        setForm(f => ({
            ...f,
            categories: f.categories.includes(cat)
                ? f.categories.filter(c => c !== cat)
                : [...f.categories, cat]
        }))
    }

    const handleNext = async () => {
        if (step < 3) { setStep(s => s + 1); return }

        // Step 3 complete — save profile to localStorage
        setSaving(true)
        const age = form.dob ? Math.floor((Date.now() - new Date(form.dob)) / (365.25 * 24 * 3600 * 1000)) : null
        const profile = {
            name: form.name,
            dob: form.dob,
            age,
            occupation: form.occupation,
            income: form.income,
            state: form.state,
            district: form.district,
            categories: form.categories,
        }
        localStorage.setItem('yojna_profile', JSON.stringify(profile))

        const token = localStorage.getItem('yojna_token')
        if (token) {
            try {
                fetch('http://localhost:8080/api/profile', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                    body: JSON.stringify(profile)
                }).catch(() => { })
            } catch (e) { console.error("Could not save initial profile to API", e) }
        }

        localStorage.removeItem('pending_name')
        setSaving(false)
        navigate('/home')
    }

    const canProceed = () => {
        if (step === 1) return form.name.trim() && form.dob
        if (step === 2) return form.state
        return form.categories.length > 0
    }

    return (
        <div className="onboard-wrapper">
            <div className="onboard-bg-glow" />

            <div className="onboard-container">
                {/* Progress */}
                <div className="onboard-progress-row">
                    {STEPS.map((s, i) => (
                        <div key={s.id} className={`onboard-step-dot ${step > i ? 'done' : ''} ${step === i + 1 ? 'active' : ''}`}>
                            {step > i + 1 ? <Check size={12} /> : s.id}
                        </div>
                    ))}
                </div>
                <div className="onboard-progress-bar">
                    <div className="onboard-progress-fill" style={{ width: `${((step - 1) / (STEPS.length - 1)) * 100}%` }} />
                </div>

                {/* Card */}
                <div className="glass-card onboard-card">
                    <div className="onboard-header">
                        <h2 className="onboard-title">{STEPS[step - 1].title}</h2>
                        <p className="onboard-subtitle text-muted">{STEPS[step - 1].subtitle}</p>
                    </div>

                    {step === 1 && (
                        <div className="onboard-fields">
                            <div className="field-group">
                                <label className="field-label">Aapka Naam (Full Name)</label>
                                <input className="input-glass" placeholder="जैसे: Rajesh Kumar" value={form.name} onChange={e => update('name', e.target.value)} />
                            </div>
                            <div className="field-group">
                                <label className="field-label">Janm Tithi (Date of Birth)</label>
                                <input className="input-glass" type="date" value={form.dob}
                                    onChange={e => update('dob', e.target.value)}
                                    max={new Date().toISOString().split('T')[0]} />
                                {form.dob && (
                                    <p style={{ fontSize: 12, color: 'var(--saffron)', marginTop: 4 }}>
                                        Age: {form.dob ? Math.floor((new Date().getFullYear() - new Date(form.dob).getFullYear())) : ''} years
                                    </p>
                                )}
                            </div>
                            <div className="field-group">
                                <label className="field-label">Vyavsay (Occupation)</label>
                                <select className="input-glass" value={form.occupation} onChange={e => update('occupation', e.target.value)}>
                                    <option value="farmer">Kisan (Farmer)</option>
                                    <option value="labour">Majdoor (Daily Labour)</option>
                                    <option value="student">Vidyarthi (Student)</option>
                                    <option value="business">Vyapar (Business)</option>
                                    <option value="government">Sarkari Karmchari</option>
                                    <option value="homemaker">Gruhasth / Griha Nirmata</option>
                                    <option value="other">Anya (Other)</option>
                                </select>
                            </div>
                            <div className="field-group">
                                <label className="field-label">Varshik Aay (Annual Income)</label>
                                <select className="input-glass" value={form.income} onChange={e => update('income', e.target.value)}>
                                    <option value="">Select range</option>
                                    <option value="0-50k">Below ₹50,000</option>
                                    <option value="50k-1l">₹50,000 – ₹1 Lakh</option>
                                    <option value="1l-2.5l">₹1 Lakh – ₹2.5 Lakh</option>
                                    <option value="2.5l-5l">₹2.5 Lakh – ₹5 Lakh</option>
                                    <option value="5l+">Above ₹5 Lakh</option>
                                </select>
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="onboard-fields">
                            <div className="field-group">
                                <label className="field-label">Rajya (State)</label>
                                <select className="input-glass" value={form.state} onChange={e => update('state', e.target.value)}>
                                    <option value="">Apna rajya chunein</option>
                                    {STATES.map(s => <option key={s} value={s}>{s}</option>)}
                                </select>
                            </div>
                            <div className="field-group">
                                <label className="field-label">Zila (District) <span className="text-subtle">(optional)</span></label>
                                <input className="input-glass" placeholder="जैसे: Pune" value={form.district} onChange={e => update('district', e.target.value)} />
                            </div>
                            <div className="onboard-map-hint">
                                <span>📍</span>
                                <span className="text-muted text-sm">Aapke rajya ke anusar schemes filter honge</span>
                            </div>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="onboard-fields">
                            <p className="text-muted" style={{ fontSize: 13, marginBottom: 12 }}>
                                Ek ya adhik category chunein:
                            </p>
                            <div className="onboard-cat-grid">
                                {CATEGORIES.map(c => (
                                    <button
                                        key={c.label}
                                        type="button"
                                        onClick={() => toggleCat(c.label)}
                                        className={`onboard-cat-btn ${form.categories.includes(c.label) ? 'selected' : ''}`}
                                    >
                                        <span className="cat-emoji">{c.emoji}</span>
                                        <span>{c.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Footer Buttons */}
                    <div className="onboard-footer">
                        {step > 1 && (
                            <button className="btn btn-ghost" onClick={() => setStep(s => s - 1)}>
                                <ArrowLeft size={16} /> Back
                            </button>
                        )}
                        <button
                            className="btn btn-primary"
                            onClick={handleNext}
                            disabled={!canProceed() || saving}
                            style={{ marginLeft: 'auto' }}
                        >
                            {saving ? <span className="btn-spinner" /> : step === 3 ? 'Shuru Karein 🚀' : <><span>Aage Badhein</span> <ArrowRight size={16} /></>}
                        </button>
                    </div>
                </div>

                <p className="onboard-skip" onClick={() => navigate('/home')}>
                    Skip karo, baad mein setup karo →
                </p>
            </div>
        </div>
    )
}
