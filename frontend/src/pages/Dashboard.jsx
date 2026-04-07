import { useEffect, useState, useCallback } from 'react';
import Sidebar from '../components/Sidebar';
import { SeverityBadge, CategoryBadge, ConfidenceBadge } from '../components/AlertBadge';
import api from '../api';

/** Format ISO date to a readable relative string */
function relativeTime(isoString) {
  if (!isoString) return '—';
  const date = new Date(isoString);
  const diff = Date.now() - date.getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'hace un momento';
  if (mins < 60) return `hace ${mins}m`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `hace ${hrs}h`;
  return date.toLocaleDateString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

export default function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null); // selected alert for detail panel
  const [filter, setFilter] = useState('all'); // all | critical | warning

  const loadAlerts = useCallback(async () => {
    try {
      const result = await api.listAlerts(0, 100);
      setAlerts(result.data.alerts || []);
      setError('');
    } catch (err) {
      setError('Error cargando alertas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load alert detail with diagnosis
  const loadAlertDetail = useCallback(async (alertId) => {
    setLoadingDetail(true);
    try {
      const result = await api.getAlert(alertId);
      setSelected(result.data);
    } catch (err) {
      console.error('Error loading alert detail:', err);
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  useEffect(() => {
    loadAlerts();
    // Poll every 15s for real-time feel
    const interval = setInterval(loadAlerts, 15000);
    return () => clearInterval(interval);
  }, [loadAlerts]);

  const filteredAlerts = alerts.filter((a) => {
    if (filter === 'all') return true;
    if (filter === 'critical') return a.severity === 'critical' || a.category === 'availability';
    if (filter === 'warning') return a.severity === 'warning';
    return true;
  });

  // Stats for header cards
  const stats = {
    total: alerts.length,
    critical: alerts.filter((a) => a.severity === 'critical').length,
    diagnosed: alerts.filter((a) => a.diagnosis || a.summary).length,
    categories: [...new Set(alerts.map((a) => a.category))].length,
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Alertas</h1>
              <p className="text-sm text-gray-500 mt-0.5">
                {loading ? 'Cargando...' : `${alerts.length} alertas procesadas`}
              </p>
            </div>
            <button
              onClick={loadAlerts}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-white border border-gray-300
                         text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 transition"
            >
              <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Actualizar
            </button>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8">
          {/* Stats cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            {[
              { label: 'Total alertas', value: stats.total, color: 'text-gray-900' },
              { label: 'Críticas', value: stats.critical, color: 'text-red-600' },
              { label: 'Diagnosticadas', value: stats.diagnosed, color: 'text-green-600' },
              { label: 'Categorías activas', value: stats.categories, color: 'text-blue-600' },
            ].map((stat) => (
              <div key={stat.label} className="bg-white rounded-xl border border-gray-200 p-5">
                <p className="text-sm text-gray-500">{stat.label}</p>
                <p className={`text-3xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
              </div>
            ))}
          </div>

          {/* Filters */}
          <div className="flex gap-2 mb-4">
            {[
              { key: 'all', label: 'Todas' },
              { key: 'critical', label: 'Críticas' },
              { key: 'warning', label: 'Warning' },
            ].map((f) => (
              <button
                key={f.key}
                onClick={() => setFilter(f.key)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
                  filter === f.key
                    ? 'bg-blue-600 text-white'
                    : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          {/* Error state */}
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Main content area */}
          <div className="flex gap-6">
            {/* Alerts table */}
            <div className={`flex-1 bg-white rounded-xl border border-gray-200 overflow-hidden`}>
              {loading ? (
                <div className="flex items-center justify-center py-24">
                  <div className="flex flex-col items-center gap-3">
                    <svg className="animate-spin w-8 h-8 text-blue-500" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <p className="text-gray-500 text-sm">Cargando alertas...</p>
                  </div>
                </div>
              ) : filteredAlerts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-24 text-center px-6">
                  <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mb-4">
                    <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0018 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                    </svg>
                  </div>
                  <p className="text-gray-900 font-medium">No hay alertas</p>
                  <p className="text-gray-500 text-sm mt-1">
                    Las alertas de Azure Monitor aparecerán aquí automáticamente.
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200 bg-gray-50">
                        <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Regla / Recurso
                        </th>
                        <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Categoría
                        </th>
                        <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Severidad
                        </th>
                        <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Confianza
                        </th>
                        <th className="px-5 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">
                          Recibida
                        </th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {filteredAlerts.map((alert) => (
                        <tr
                          key={alert.id}
                          onClick={() => loadAlertDetail(alert.id)}
                          className={`cursor-pointer hover:bg-blue-50 transition-colors ${
                            selected?.id === alert.id ? 'bg-blue-50' : ''
                          }`}
                        >
                          <td className="px-5 py-3.5">
                            <p className="text-sm font-medium text-gray-900 truncate max-w-xs">
                              {alert.rule_name || 'Alerta sin nombre'}
                            </p>
                          </td>
                          <td className="px-5 py-3.5">
                            <CategoryBadge category={alert.category} />
                          </td>
                          <td className="px-5 py-3.5">
                            <SeverityBadge severity={alert.severity} />
                          </td>
                          <td className="px-5 py-3.5">
                            <ConfidenceBadge confidence={alert.confidence} />
                          </td>
                          <td className="px-5 py-3.5 text-sm text-gray-500">
                            {relativeTime(alert.created_at)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Detail panel */}
            {selected && (
              <div className="w-96 flex-shrink-0 bg-white rounded-xl border border-gray-200 overflow-hidden flex flex-col">
                {/* Panel header */}
                <div className="px-5 py-4 border-b border-gray-200 flex items-center justify-between">
                  <h3 className="font-semibold text-gray-900 text-sm">Detalle de alerta</h3>
                  <button
                    onClick={() => setSelected(null)}
                    className="text-gray-400 hover:text-gray-600 transition"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="flex-1 overflow-y-auto p-5 space-y-5">
                  {loadingDetail ? (
                    <div className="flex items-center justify-center py-8">
                      <svg className="animate-spin w-6 h-6 text-blue-500" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    </div>
                  ) : (
                    <>
                      {/* Alert info */}
                      <div>
                        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Alerta</p>
                        <p className="text-sm font-semibold text-gray-900">
                          {selected.rule_name || 'Sin nombre'}
                        </p>
                        <div className="flex gap-2 mt-3 flex-wrap">
                          <CategoryBadge category={selected.category} />
                          <SeverityBadge severity={selected.severity} />
                        </div>
                      </div>

                      {/* Diagnosis */}
                      {selected.diagnosis && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                            Diagnóstico IA
                          </p>
                          <div className="bg-blue-50 border border-blue-100 rounded-lg p-4">
                            <p className="text-sm text-gray-800 leading-relaxed">
                              {selected.diagnosis}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Evidence */}
                      {selected.evidence?.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                            Evidencia
                          </p>
                          <ul className="space-y-1.5">
                            {selected.evidence.map((ev, i) => (
                              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                                <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-600 flex-shrink-0
                                               flex items-center justify-center text-xs font-bold mt-0.5">
                                  {i + 1}
                                </span>
                                {ev}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Suggested action */}
                      {selected.suggested_action && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                            Acción sugerida
                          </p>
                          <div className="bg-green-50 border border-green-100 rounded-lg p-4">
                            <p className="text-sm text-gray-800 leading-relaxed">
                              {selected.suggested_action}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Confidence */}
                      {selected.diagnosis && selected.confidence != null && (
                        <div>
                          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">
                            Confianza del diagnóstico
                          </p>
                          <div className="flex items-center gap-3">
                            <div className="flex-1 h-2 bg-gray-200 rounded-full">
                              <div
                                className="h-2 bg-blue-500 rounded-full"
                                style={{ width: `${Math.round(selected.confidence * 100)}%` }}
                              />
                            </div>
                            <span className="text-sm font-medium text-gray-700">
                              {Math.round(selected.confidence * 100)}%
                            </span>
                          </div>
                        </div>
                      )}

                      {/* Timestamps */}
                      <div className="text-xs text-gray-400 space-y-1 pt-2 border-t border-gray-100">
                        <p>Recibida: {relativeTime(selected.created_at)}</p>
                        {selected.id && <p>ID: {selected.id}</p>}
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
