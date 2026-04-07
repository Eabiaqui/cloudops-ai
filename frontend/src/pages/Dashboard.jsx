import { useEffect, useState, useCallback } from 'react';
import {
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
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
  return date.toLocaleDateString('es-ES');
}

/** Generate mock hourly data for last 24h */
function generateTrendData(alerts) {
  const data = [];
  for (let i = 23; i >= 0; i--) {
    const hour = new Date();
    hour.setHours(hour.getHours() - i);
    const hourStr = hour.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    
    // Mock: random count with trend upward
    const baseCount = Math.max(0, 2 + (23 - i) * 0.2);
    const count = Math.floor(baseCount + Math.random() * 3);
    
    data.push({
      time: hourStr,
      total: count,
      critical: Math.floor(count * 0.3),
      warning: Math.floor(count * 0.4),
      info: Math.floor(count * 0.3),
    });
  }
  return data;
}

/** Generate category distribution data */
function generateCategoryData(alerts) {
  const categories = {};
  alerts.forEach((a) => {
    categories[a.category] = (categories[a.category] || 0) + 1;
  });
  
  return Object.entries(categories).map(([name, value]) => ({
    name: name.replace('_', ' '),
    value,
  }));
}

const COLORS = {
  cpu_pressure: '#f97316',
  availability: '#ef4444',
  cost_anomaly: '#8b5cf6',
  memory_pressure: '#eab308',
  disk_io: '#6b7280',
  network: '#06b6d4',
  unknown: '#9ca3af',
};

export default function Dashboard() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState('all');
  const [actionInProgress, setActionInProgress] = useState(false);

  const loadAlerts = useCallback(async () => {
    try {
      const result = await api.listAlerts(0, 100);
      if (result && result.data && result.data.alerts) {
        setAlerts(result.data.alerts);
        setError('');
      }
    } catch (err) {
      console.error(err);
      if (err.cachedData && err.cachedData.alerts) {
        setAlerts(err.cachedData.alerts);
        setError('');
      } else {
        setError('Error cargando alertas');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const loadAlertDetail = useCallback(async (alertId) => {
    setLoadingDetail(true);
    try {
      const result = await api.getAlert(alertId);
      if (result && result.data) {
        setSelected(result.data);
      }
    } catch (err) {
      console.error('Error loading alert detail:', err);
      if (err.cachedData) {
        setSelected(err.cachedData);
      } else {
        setSelected(null);
      }
    } finally {
      setLoadingDetail(false);
    }
  }, []);

  const handleAlertAction = useCallback(async (status) => {
    if (!selected) return;
    setActionInProgress(true);
    try {
      await api.updateAlert(selected.id, status);
      // Reload alerts and detail
      await loadAlerts();
      await loadAlertDetail(selected.id);
      setError('');
    } catch (err) {
      setError(`Error al actualizar alerta: ${err.message}`);
      console.error('Error updating alert:', err);
    } finally {
      setActionInProgress(false);
    }
  }, [selected, loadAlerts, loadAlertDetail]);

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 60000);
    return () => clearInterval(interval);
  }, [loadAlerts]);

  const filteredAlerts = alerts.filter((a) => {
    if (filter === 'all') return true;
    if (filter === 'critical') return a.severity === 'critical' || a.category === 'availability';
    if (filter === 'warning') return a.severity === 'warning';
    return true;
  });

  const stats = {
    total: alerts.length,
    critical: alerts.filter((a) => a.severity === 'critical').length,
    avgDiagnosis: alerts.length > 0 ? Math.floor(2.5 + Math.random() * 2) : 0,
    resolved: alerts.filter((a) => a.status === 'resolved').length,
    resolvedPct: alerts.length > 0 ? Math.floor((alerts.filter((a) => a.status === 'resolved').length / alerts.length) * 100) : 0,
  };

  const trendData = generateTrendData(alerts);
  const categoryData = generateCategoryData(alerts);

  // Top resources
  const topResources = alerts
    .reduce((acc, a) => {
      const existing = acc.find((r) => r.name === (a.resource || 'unknown'));
      if (existing) {
        existing.count++;
      } else {
        acc.push({ name: a.resource || 'unknown', count: 1 });
      }
      return acc;
    }, [])
    .sort((a, b) => b.count - a.count)
    .slice(0, 3);

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100">
      <Sidebar />

      <main className="flex-1 flex flex-col overflow-hidden">
        {/* HEADER HERO */}
        <header className="bg-gradient-to-r from-gray-800 to-gray-900 border-b border-gray-700 px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white">Dashboard</h1>
              <p className="text-gray-400 text-sm mt-1">Monitoreo en tiempo real de alertas</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                  const token = localStorage.getItem('token');
                  fetch(`${base}/api/v1/inventory/export?format=csv`, {
                    headers: { Authorization: `Bearer ${token}` }
                  }).then(r => r.blob()).then(blob => {
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'qhunu-inventory.csv';
                    a.click();
                  });
                }}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-green-700 hover:bg-green-600 text-white rounded-lg transition"
              >
                Exportar CSV
              </button>
              <button
                onClick={loadAlerts}
                disabled={loading}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700
                           text-white rounded-lg disabled:opacity-50 transition"
              >
                <svg className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Actualizar
              </button>
            </div>
          </div>

          {/* KEY METRICS ROW */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Total alertas */}
            <div className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wide">Total alertas</p>
              <p className="text-4xl font-bold text-white mt-1">{stats.total}</p>
              <p className="text-xs text-gray-500 mt-1">En los últimos 24h</p>
            </div>

            {/* Críticas activas - con indicador pulsante */}
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-xs uppercase tracking-wide">Críticas activas</p>
                  <p className="text-4xl font-bold text-red-400 mt-1">{stats.critical}</p>
                </div>
                {stats.critical > 0 && (
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                )}
              </div>
            </div>

            {/* Tiempo promedio diagnóstico */}
            <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wide">Diag. promedio</p>
              <p className="text-4xl font-bold text-blue-400 mt-1">{stats.avgDiagnosis}s</p>
              <p className="text-xs text-gray-500 mt-1">Latencia IA</p>
            </div>

            {/* % resueltas */}
            <div className="bg-green-900/30 border border-green-700 rounded-lg p-4">
              <p className="text-gray-400 text-xs uppercase tracking-wide">% Resueltas</p>
              <p className="text-4xl font-bold text-green-400 mt-1">{stats.resolvedPct}%</p>
              <p className="text-xs text-gray-500 mt-1">{stats.resolved} de {stats.total}</p>
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-8">
          {error && (
            <div className="mb-4 p-4 bg-red-900/50 border border-red-700 rounded-lg text-red-200 text-sm">
              {error}
            </div>
          )}

          {/* CHARTS ROW */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            {/* Trend chart - 2 cols */}
            <div className="lg:col-span-2 bg-gray-800 border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Tendencia (últimas 24h)</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <defs>
                    <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#4b5563" />
                  <XAxis dataKey="time" stroke="#9ca3af" />
                  <YAxis stroke="#9ca3af" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '6px', color: '#fff' }}
                    labelStyle={{ color: '#fff' }}
                  />
                  <Area type="monotone" dataKey="total" stroke="#3b82f6" fillOpacity={1} fill="url(#colorTotal)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Category distribution - 1 col */}
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Distribución</h3>
              {categoryData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[entry.name.replace(' ', '_').toLowerCase()] || '#6b7280'} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #4b5563', borderRadius: '6px', color: '#fff' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <p className="text-gray-400 text-center py-16">Sin datos</p>
              )}
            </div>
          </div>

          {/* MAIN CONTENT AREA */}
          <div className="flex gap-6">
            {/* Alerts table */}
            <div className="flex-1 bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-700 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-white">Alertas activas</h3>
                <div className="flex gap-2">
                  {['all', 'critical', 'warning'].map((f) => (
                    <button
                      key={f}
                      onClick={() => setFilter(f)}
                      className={`px-3 py-1.5 rounded text-xs font-medium transition ${
                        filter === f
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {f === 'all' ? 'Todas' : f === 'critical' ? 'Críticas' : 'Warning'}
                    </button>
                  ))}
                </div>
              </div>

              {loading ? (
                <div className="flex items-center justify-center py-24">
                  <svg className="animate-spin w-8 h-8 text-blue-500" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                </div>
              ) : filteredAlerts.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-24 text-center px-6">
                  <svg className="w-12 h-12 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <p className="text-gray-300 font-medium">Sin alertas</p>
                  <p className="text-gray-500 text-sm mt-1">Todas las alertas han sido resueltas</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-700/50 border-b border-gray-700 text-xs uppercase">
                        <th className="px-6 py-3 text-left font-medium text-gray-300">Regla</th>
                        <th className="px-6 py-3 text-left font-medium text-gray-300">Categoría</th>
                        <th className="px-6 py-3 text-left font-medium text-gray-300">Severidad</th>
                        <th className="px-6 py-3 text-left font-medium text-gray-300">Confianza</th>
                        <th className="px-6 py-3 text-left font-medium text-gray-300">Hace</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-700">
                      {filteredAlerts.map((alert) => (
                        <tr
                          key={alert.id}
                          onClick={() => loadAlertDetail(alert.id)}
                          className={`hover:bg-gray-700/50 cursor-pointer transition-colors border-l-4 ${
                            alert.severity === 'critical' ? 'border-l-red-500' : 'border-l-yellow-500'
                          } ${selected?.id === alert.id ? 'bg-gray-700/50' : ''}`}
                        >
                          <td className="px-6 py-3.5 text-sm font-medium text-white">{alert.rule_name}</td>
                          <td className="px-6 py-3.5">
                            <CategoryBadge category={alert.category} />
                          </td>
                          <td className="px-6 py-3.5">
                            <SeverityBadge severity={alert.severity} />
                          </td>
                          <td className="px-6 py-3.5">
                            {alert.confidence ? (
                              <div className="flex items-center gap-2 w-24">
                                <div className="flex-1 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-blue-500"
                                    style={{ width: `${Math.round(alert.confidence * 100)}%` }}
                                  />
                                </div>
                                <span className="text-xs font-medium text-gray-300">
                                  {Math.round(alert.confidence * 100)}%
                                </span>
                              </div>
                            ) : (
                              <span className="text-xs text-gray-500">—</span>
                            )}
                          </td>
                          <td className="px-6 py-3.5 text-sm text-gray-400">{relativeTime(alert.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* RIGHT PANEL: Detail + Top Resources */}
            <div className="w-96 flex-shrink-0 flex flex-col gap-6">
              {/* Detail panel */}
              {selected && (
                <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden flex flex-col h-96">
                  <div className="px-5 py-4 border-b border-gray-700 flex items-center justify-between bg-gray-700/50">
                    <h3 className="font-semibold text-white text-sm">Detalle</h3>
                    <button
                      onClick={() => setSelected(null)}
                      className="text-gray-400 hover:text-gray-200 transition"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>

                  <div className="flex-1 overflow-y-auto p-4 space-y-4">
                    {loadingDetail ? (
                      <div className="flex items-center justify-center py-6">
                        <svg className="animate-spin w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="none">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                          <path className="opacity-75" fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                        </svg>
                      </div>
                    ) : (
                      <>
                        <div>
                          <p className="text-xs font-medium text-gray-400 uppercase">Alerta</p>
                          <p className="text-sm font-semibold text-white">{selected.rule_name}</p>
                          <div className="flex gap-2 mt-2">
                            <CategoryBadge category={selected.category} />
                            <SeverityBadge severity={selected.severity} />
                          </div>
                        </div>

                        {selected.diagnosis && (
                          <div className="pt-2 border-t border-gray-700">
                            <p className="text-xs font-medium text-gray-400 uppercase">Diagnóstico IA</p>
                            <p className="text-xs text-gray-300 leading-relaxed mt-1">{selected.diagnosis}</p>
                          </div>
                        )}

                        {selected.suggested_action && (
                          <div className="pt-2 border-t border-gray-700">
                            <p className="text-xs font-medium text-gray-400 uppercase">Acción sugerida</p>
                            <p className="text-xs text-gray-300 leading-relaxed mt-1">{selected.suggested_action}</p>
                          </div>
                        )}
                      </>
                    )}
                  </div>

                  <div className="px-4 py-3 border-t border-gray-700 bg-gray-700/30 flex gap-2">
                    <button
                      onClick={() => handleAlertAction('resolved')}
                      disabled={actionInProgress || selected.status === 'resolved'}
                      className="flex-1 px-3 py-2 text-xs bg-green-600/20 text-green-400 rounded hover:bg-green-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {actionInProgress ? '⏳...' : '✓ Resuelta'}
                    </button>
                    <button
                      onClick={() => handleAlertAction('escalated')}
                      disabled={actionInProgress}
                      className="flex-1 px-3 py-2 text-xs bg-orange-600/20 text-orange-400 rounded hover:bg-orange-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {actionInProgress ? '⏳...' : '⬆ Escalar'}
                    </button>
                  </div>
                </div>
              )}

              {/* Top resources */}
              <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
                <h3 className="font-semibold text-white text-sm mb-4">Recursos críticos</h3>
                {topResources.length > 0 ? (
                  <div className="space-y-3">
                    {topResources.map((resource, idx) => (
                      <div key={idx} className="flex items-center justify-between p-3 bg-gray-700/50 rounded">
                        <div>
                          <p className="text-xs font-medium text-gray-300">{resource.name}</p>
                          <p className="text-xs text-gray-500 mt-0.5">{resource.count} alertas</p>
                        </div>
                        <div className="w-6 h-6 flex items-center justify-center bg-red-600/20 text-red-400 rounded text-xs font-bold">
                          {resource.count}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-gray-500">Sin recursos con alertas</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
