import { useNavigate } from 'react-router-dom';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{ background: '#0f1117', color: '#e2e8f0', fontFamily: 'Inter, sans-serif', minHeight: '100vh' }}>

      {/* NAV */}
      <nav style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 60px', borderBottom: '1px solid #1e2433' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ background: '#3b82f6', borderRadius: 8, width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>⚡</div>
          <span style={{ fontWeight: 700, fontSize: 20, color: '#fff' }}>Qhunu</span>
        </div>
        <div style={{ display: 'flex', gap: 16 }}>
          <button onClick={() => navigate('/login')} style={{ background: 'transparent', border: '1px solid #334155', color: '#94a3b8', padding: '8px 20px', borderRadius: 8, cursor: 'pointer' }}>
            Iniciar sesión
          </button>
          <button onClick={() => navigate('/signup')} style={{ background: '#3b82f6', border: 'none', color: '#fff', padding: '8px 20px', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
            Empezar gratis
          </button>
        </div>
      </nav>

      {/* HERO */}
      <section style={{ textAlign: 'center', padding: '100px 60px 60px' }}>
        <div style={{ display: 'inline-block', background: '#1e2433', border: '1px solid #334155', borderRadius: 20, padding: '6px 16px', fontSize: 13, color: '#60a5fa', marginBottom: 24 }}>
          ✦ Diagnóstico automático con IA — 500ms por alerta
        </div>
        <h1 style={{ fontSize: 56, fontWeight: 800, lineHeight: 1.15, marginBottom: 24, color: '#fff' }}>
          Tu equipo recibe 100 alertas.<br />
          <span style={{ color: '#3b82f6' }}>Qhunu diagnostica todas.</span>
        </h1>
        <p style={{ fontSize: 20, color: '#94a3b8', maxWidth: 600, margin: '0 auto 40px', lineHeight: 1.7 }}>
          Automatiza el diagnóstico de alertas cloud con IA. 
          Reduce el tiempo de investigación de 45 minutos a 5. 
          Sin contratar más operadores NOC.
        </p>
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
          <button onClick={() => navigate('/signup')} style={{ background: '#3b82f6', border: 'none', color: '#fff', padding: '14px 32px', borderRadius: 10, cursor: 'pointer', fontWeight: 700, fontSize: 16 }}>
            Empezar gratis →
          </button>
          <button onClick={() => navigate('/login')} style={{ background: '#1e2433', border: '1px solid #334155', color: '#e2e8f0', padding: '14px 32px', borderRadius: 10, cursor: 'pointer', fontSize: 16 }}>
            Ver demo
          </button>
        </div>
      </section>

      {/* METRICAS */}
      <section style={{ display: 'flex', justifyContent: 'center', gap: 40, padding: '40px 60px', borderTop: '1px solid #1e2433', borderBottom: '1px solid #1e2433' }}>
        {[
          { value: '~500ms', label: 'Latencia por alerta' },
          { value: '99%', label: 'Precisión clasificación' },
          { value: '$0.0003', label: 'Costo por alerta' },
          { value: '7', label: 'Categorías NOC' },
        ].map((m) => (
          <div key={m.label} style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 36, fontWeight: 800, color: '#3b82f6' }}>{m.value}</div>
            <div style={{ fontSize: 14, color: '#64748b', marginTop: 4 }}>{m.label}</div>
          </div>
        ))}
      </section>

      {/* PROBLEMA */}
      <section style={{ padding: '80px 60px', maxWidth: 900, margin: '0 auto' }}>
        <h2 style={{ fontSize: 36, fontWeight: 700, textAlign: 'center', marginBottom: 16, color: '#fff' }}>
          El problema que todos ignoran
        </h2>
        <p style={{ textAlign: 'center', color: '#94a3b8', fontSize: 18, marginBottom: 48 }}>
          Tu equipo NOC recibe cientos de alertas por día. La mayoría son ruido. Pero una puede ser crítica.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 24 }}>
          {[
            { icon: '⏱', title: '45 min promedio', desc: 'Tiempo que tarda un operador en investigar una alerta crítica manualmente' },
            { icon: '😩', title: '67% son ignoradas', desc: 'Las alertas se acumulan y los equipos desarrollan "alert fatigue"' },
            { icon: '💸', title: '$35,000/año', desc: 'Costo mínimo de herramientas como PagerDuty para empresas medianas' },
          ].map((p) => (
            <div key={p.title} style={{ background: '#1e2433', border: '1px solid #334155', borderRadius: 12, padding: 24 }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>{p.icon}</div>
              <div style={{ fontWeight: 700, fontSize: 18, color: '#f1f5f9', marginBottom: 8 }}>{p.title}</div>
              <div style={{ color: '#64748b', lineHeight: 1.6 }}>{p.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* COMO FUNCIONA */}
      <section style={{ padding: '80px 60px', background: '#0a0d14' }}>
        <h2 style={{ fontSize: 36, fontWeight: 700, textAlign: 'center', marginBottom: 48, color: '#fff' }}>
          Cómo funciona Qhunu
        </h2>
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 0, maxWidth: 800, margin: '0 auto' }}>
          {[
            { step: '1', title: 'Alerta llega', desc: 'Azure Monitor envía webhook a Qhunu' },
            { step: '2', title: 'IA clasifica', desc: 'Claude Haiku categoriza en 500ms' },
            { step: '3', title: 'Diagnóstico', desc: 'Root cause + acción sugerida' },
            { step: '4', title: 'Dashboard', desc: 'Tu equipo ve todo en un lugar' },
          ].map((s, i) => (
            <div key={s.step} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{ textAlign: 'center', width: 160 }}>
                <div style={{ background: '#3b82f6', borderRadius: '50%', width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px', fontWeight: 800, fontSize: 20, color: '#fff' }}>{s.step}</div>
                <div style={{ fontWeight: 700, color: '#f1f5f9', marginBottom: 6 }}>{s.title}</div>
                <div style={{ color: '#64748b', fontSize: 13 }}>{s.desc}</div>
              </div>
              {i < 3 && <div style={{ color: '#334155', fontSize: 24, margin: '0 8px', marginBottom: 32 }}>→</div>}
            </div>
          ))}
        </div>
      </section>

      {/* FEATURES */}
      <section style={{ padding: '80px 60px', maxWidth: 900, margin: '0 auto' }}>
        <h2 style={{ fontSize: 36, fontWeight: 700, textAlign: 'center', marginBottom: 48, color: '#fff' }}>
          Todo lo que necesita tu equipo NOC
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {[
            { icon: '🧠', title: 'Diagnóstico con IA', desc: 'Root cause automático con evidencia y acción sugerida para cada alerta crítica' },
            { icon: '☁️', title: 'Multicloud nativo', desc: 'Conecta Azure Monitor hoy. AWS CloudWatch y GCP Monitoring próximamente' },
            { icon: '📊', title: 'Dashboard en tiempo real', desc: 'Visualiza tendencias, distribución por categoría y alertas activas en un solo lugar' },
            { icon: '🔔', title: 'Notificaciones Slack', desc: 'Alertas críticas llegan directo a tu canal #ops con diagnóstico incluido' },
            { icon: '📦', title: 'Inventario exportable', desc: 'Descarga tu inventario de recursos Azure en CSV/Excel por subscription o RG' },
            { icon: '🔒', title: 'Multi-tenant seguro', desc: 'Aislamiento completo de datos entre clientes. Tu infraestructura, tus datos' },
          ].map((f) => (
            <div key={f.title} style={{ background: '#1e2433', border: '1px solid #334155', borderRadius: 12, padding: 24, display: 'flex', gap: 16 }}>
              <div style={{ fontSize: 28 }}>{f.icon}</div>
              <div>
                <div style={{ fontWeight: 700, color: '#f1f5f9', marginBottom: 6 }}>{f.title}</div>
                <div style={{ color: '#64748b', lineHeight: 1.6, fontSize: 14 }}>{f.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* PRICING */}
      <section style={{ padding: '80px 60px', background: '#0a0d14' }}>
        <h2 style={{ fontSize: 36, fontWeight: 700, textAlign: 'center', marginBottom: 16, color: '#fff' }}>
          Precios pensados para LATAM
        </h2>
        <p style={{ textAlign: 'center', color: '#94a3b8', marginBottom: 48 }}>90% más barato que PagerDuty. Sin contratos anuales.</p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: 24, flexWrap: 'wrap' }}>
          {[
            { plan: 'Starter', price: '$99', period: '/mes', alerts: '1,000 alertas/mes', features: ['Dashboard completo', 'Clasificación IA', 'Soporte email'], cta: 'Empezar gratis', highlight: false },
            { plan: 'Growth', price: '$299', period: '/mes', alerts: '10,000 alertas/mes', features: ['Todo Starter', 'Diagnóstico IA', 'Slack + Jira', 'Inventario exportable'], cta: 'Empezar gratis', highlight: true },
            { plan: 'Enterprise', price: '$799', period: '/mes', alerts: 'Ilimitado', features: ['Todo Growth', 'Multi-tenant', 'SLA 99.9%', 'Soporte dedicado'], cta: 'Contactar', highlight: false },
          ].map((p) => (
            <div key={p.plan} style={{ background: p.highlight ? '#1d3a6e' : '#1e2433', border: `1px solid ${p.highlight ? '#3b82f6' : '#334155'}`, borderRadius: 16, padding: 32, width: 260, position: 'relative' }}>
              {p.highlight && <div style={{ position: 'absolute', top: -12, left: '50%', transform: 'translateX(-50%)', background: '#3b82f6', color: '#fff', fontSize: 12, fontWeight: 700, padding: '4px 12px', borderRadius: 20 }}>MÁS POPULAR</div>}
              <div style={{ fontWeight: 700, fontSize: 20, color: '#fff', marginBottom: 8 }}>{p.plan}</div>
              <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 4 }}>
                <span style={{ fontSize: 40, fontWeight: 800, color: p.highlight ? '#60a5fa' : '#f1f5f9' }}>{p.price}</span>
                <span style={{ color: '#64748b' }}>{p.period}</span>
              </div>
              <div style={{ color: '#64748b', fontSize: 13, marginBottom: 24 }}>{p.alerts}</div>
              <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 24px', display: 'flex', flexDirection: 'column', gap: 8 }}>
                {p.features.map((f) => (
                  <li key={f} style={{ color: '#94a3b8', fontSize: 14, display: 'flex', gap: 8 }}>
                    <span style={{ color: '#22c55e' }}>✓</span> {f}
                  </li>
                ))}
              </ul>
              <button onClick={() => navigate('/signup')} style={{ width: '100%', background: p.highlight ? '#3b82f6' : 'transparent', border: `1px solid ${p.highlight ? '#3b82f6' : '#334155'}`, color: '#fff', padding: '10px 0', borderRadius: 8, cursor: 'pointer', fontWeight: 600 }}>
                {p.cta}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* CTA FINAL */}
      <section style={{ textAlign: 'center', padding: '80px 60px' }}>
        <h2 style={{ fontSize: 40, fontWeight: 800, color: '#fff', marginBottom: 16 }}>
          Empieza a diagnosticar alertas hoy
        </h2>
        <p style={{ color: '#94a3b8', fontSize: 18, marginBottom: 40 }}>
          Gratis para empezar. Sin tarjeta de crédito. Setup en 5 minutos.
        </p>
        <button onClick={() => navigate('/signup')} style={{ background: '#3b82f6', border: 'none', color: '#fff', padding: '16px 48px', borderRadius: 12, cursor: 'pointer', fontWeight: 700, fontSize: 18 }}>
          Crear cuenta gratis →
        </button>
      </section>

      {/* FOOTER */}
      <footer style={{ borderTop: '1px solid #1e2433', padding: '32px 60px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ background: '#3b82f6', borderRadius: 6, width: 24, height: 24, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>⚡</div>
          <span style={{ fontWeight: 700, color: '#fff' }}>Qhunu</span>
        </div>
        <div style={{ color: '#475569', fontSize: 13 }}>
          © 2026 Qhunu · Diagnósticos automáticos de infraestructura · Lima, Perú
        </div>
        <div style={{ display: 'flex', gap: 20 }}>
          <a href="https://app.qhunu.com" style={{ color: '#64748b', fontSize: 13, textDecoration: 'none' }}>Dashboard</a>
          <a href="mailto:hola@qhunu.com" style={{ color: '#64748b', fontSize: 13, textDecoration: 'none' }}>Contacto</a>
        </div>
      </footer>

    </div>
  );
}
