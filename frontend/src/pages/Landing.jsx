import { useNavigate } from 'react-router-dom';
import { ArrowRight, AlertCircle, Zap, TrendingUp, CheckCircle2, Clock, DollarSign } from 'lucide-react';
import '../styles/Landing.css';

export default function Landing() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <AlertCircle className="w-8 h-8" />,
      title: 'Clasificación Inteligente',
      description: 'Agrupa alertas caóticas en 7 categorías. Ruido → acción en segundos.',
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: 'Diagnóstico Automático',
      description: 'Identifica raíces causas sin intervención humana. Pruebas y evidencia incluidas.',
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'Remediación Guiada',
      description: 'Sugiere acciones antes de ejecutar. Tu equipo aprueba, el sistema actúa.',
    },
  ];

  const metrics = [
    {
      icon: <Clock className="w-6 h-6" />,
      value: '~500ms',
      label: 'Latencia por alerta',
    },
    {
      icon: <DollarSign className="w-6 h-6" />,
      value: '$0.0003',
      label: 'Costo por alerta',
    },
    {
      icon: <CheckCircle2 className="w-6 h-6" />,
      value: '99%',
      label: 'Precisión en diagnóstico',
    },
  ];

  return (
    <div className="landing-page">
      {/* Navbar */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-text">Qhunu</span>
            <span className="logo-subtitle">CloudOps AI</span>
          </div>
          <button 
            className="nav-cta"
            onClick={() => navigate('/dashboard')}
          >
            Ingresar
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Autonomía en tus operaciones cloud
          </h1>
          <p className="hero-subtitle">
            Tu equipo recibe 100 alertas/día. Casi ninguna es importante.
            <br />
            <strong>Qhunu clasifica, diagnostica y remedia. Tú apruebas.</strong>
          </p>
          <div className="hero-cta-group">
            <button 
              className="cta-primary"
              onClick={() => navigate('/dashboard')}
            >
              Empezar gratis <ArrowRight className="w-4 h-4" />
            </button>
            <button className="cta-secondary">
              Ver demo en vivo
            </button>
          </div>
          <p className="hero-footnote">
            No requiere tarjeta de crédito. Conexión con Azure Monitor en 2 minutos.
          </p>
        </div>
        <div className="hero-visual">
          <div className="alert-stack">
            <div className="alert-card alert-1">⚠️ CPU > 90%</div>
            <div className="alert-card alert-2">🔴 Pod crashlooping</div>
            <div className="alert-card alert-3">💾 Disco lleno en 4h</div>
          </div>
        </div>
      </section>

      {/* Problem Section */}
      <section className="problem">
        <div className="problem-content">
          <h2>El problema que soluciona Qhunu</h2>
          <div className="problem-grid">
            <div className="problem-card">
              <h3>Ruido constante</h3>
              <p>Azure Monitor dispara alertas por todo. Tu equipo no sabe cuáles son críticas.</p>
            </div>
            <div className="problem-card">
              <h3>Diagnóstico manual</h3>
              <p>Los engineers pierden horas investigando qué causó cada alert. Pura receta.</p>
            </div>
            <div className="problem-card">
              <h3>Burnout en on-call</h3>
              <p>MTTR larga. Poca automatización. Los mismos patrones se repiten cada semana.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="solution">
        <h2>Nuestra solución</h2>
        <div className="features-grid">
          {features.map((feature, idx) => (
            <div key={idx} className="feature-card">
              <div className="feature-icon">
                {feature.icon}
              </div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Metrics Section */}
      <section className="metrics">
        <h2>Números que hablan</h2>
        <div className="metrics-grid">
          {metrics.map((metric, idx) => (
            <div key={idx} className="metric-card">
              <div className="metric-icon">
                {metric.icon}
              </div>
              <div className="metric-value">{metric.value}</div>
              <div className="metric-label">{metric.label}</div>
            </div>
          ))}
        </div>
        <p className="metrics-note">
          Procesa reales alertas de Azure Monitor en producción desde 2026-04-07.
        </p>
      </section>

      {/* CTA Section */}
      <section className="cta-final">
        <div className="cta-box">
          <h2>¿Tu equipo maneja alertas a mano?</h2>
          <p>Qhunu reduce MTTR en 80% y costo operativo hasta 70%.</p>
          <button 
            className="cta-primary large"
            onClick={() => navigate('/dashboard')}
          >
            Empieza gratis hoy <ArrowRight className="w-5 h-5" />
          </button>
          <p className="cta-footnote">
            2 minutos setup. Sin tarjeta. Alertas reales desde tu suscripción Azure.
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <p>&copy; 2026 Qhunu. CloudOps autonomía.</p>
          <div className="footer-links">
            <a href="#docs">Docs</a>
            <a href="#status">Status</a>
            <a href="#contact">Contacto</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
