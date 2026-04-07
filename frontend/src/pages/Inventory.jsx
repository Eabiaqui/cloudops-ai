import { useEffect, useState } from 'react';
import Sidebar from '../components/Sidebar';
import api from '../api';

export default function Inventory() {
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    setLoading(true);
    try {
      const result = await api.getInventory();
      if (result && result.data && result.data.resources) {
        setResources(result.data.resources);
        setError('');
      }
    } catch (err) {
      console.error('Error loading inventory:', err);
      setError('Error cargando inventario');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    setExporting(true);
    try {
      const response = await api.exportInventory(format);
      if (response && response.data) {
        if (format === 'csv') {
          const blob = new Blob([response.data.data], { type: 'text/csv' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'inventory.csv';
          a.click();
          window.URL.revokeObjectURL(url);
        } else {
          const blob = new Blob([JSON.stringify(response.data.resources, null, 2)], { type: 'application/json' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'inventory.json';
          a.click();
          window.URL.revokeObjectURL(url);
        }
      }
    } catch (err) {
      console.error('Error exporting inventory:', err);
      setError('Error exportando inventario');
    } finally {
      setExporting(false);
    }
  };

  const filteredResources = filterType === 'all' 
    ? resources 
    : resources.filter(r => r.type === filterType);

  const resourceTypes = [...new Set(resources.map(r => r.type))];

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Inventario Azure</h1>
            <p className="text-gray-400">Recursos y capacidades en tus suscripciones</p>
          </div>

          {/* Controls */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex gap-3">
              <button
                onClick={() => setFilterType('all')}
                className={`px-4 py-2 rounded text-sm font-medium transition ${
                  filterType === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Todos ({resources.length})
              </button>
              {resourceTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => setFilterType(type)}
                  className={`px-4 py-2 rounded text-sm font-medium transition ${
                    filterType === type
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {type} ({resources.filter(r => r.type === type).length})
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => handleExport('json')}
                disabled={exporting || resources.length === 0}
                className="px-4 py-2 bg-green-600/20 text-green-400 rounded hover:bg-green-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {exporting ? '⏳ Exportando...' : '📥 JSON'}
              </button>
              <button
                onClick={() => handleExport('csv')}
                disabled={exporting || resources.length === 0}
                className="px-4 py-2 bg-green-600/20 text-green-400 rounded hover:bg-green-600/30 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium"
              >
                {exporting ? '⏳ Exportando...' : '📥 CSV'}
              </button>
            </div>
          </div>

          {/* Resources Table */}
          <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center py-24">
                <svg className="animate-spin w-8 h-8 text-blue-500" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
              </div>
            ) : filteredResources.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-24 text-center px-6">
                <svg className="w-12 h-12 text-gray-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                    d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
                <p className="text-gray-300 font-medium">Sin recursos</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-700/50 border-b border-gray-700 text-xs uppercase">
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Nombre</th>
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Tipo</th>
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Suscripción</th>
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Grupo de Recursos</th>
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Estado</th>
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Ubicación</th>
                      <th className="px-6 py-3 text-left font-medium text-gray-300">Alertas</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {filteredResources.map((resource, idx) => (
                      <tr key={idx} className="hover:bg-gray-700/50 transition-colors">
                        <td className="px-6 py-3.5 text-sm font-medium text-white">{resource.name}</td>
                        <td className="px-6 py-3.5">
                          <span className="inline-block px-2 py-1 bg-blue-900/30 text-blue-300 text-xs rounded">
                            {resource.type}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-sm text-gray-400">{resource.subscription_id}</td>
                        <td className="px-6 py-3.5 text-sm text-gray-400">{resource.resource_group}</td>
                        <td className="px-6 py-3.5">
                          <span className={`inline-block px-2 py-1 text-xs rounded ${
                            resource.status === 'Running' || resource.status === 'Ready' || resource.status === 'Succeeded'
                              ? 'bg-green-900/30 text-green-300'
                              : resource.status === 'Stopped'
                              ? 'bg-gray-900/30 text-gray-400'
                              : 'bg-yellow-900/30 text-yellow-300'
                          }`}>
                            {resource.status}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-sm text-gray-400">{resource.location}</td>
                        <td className="px-6 py-3.5">
                          {resource.alert_count > 0 ? (
                            <span className="inline-block w-6 h-6 flex items-center justify-center bg-red-600/20 text-red-400 rounded text-xs font-bold">
                              {resource.alert_count}
                            </span>
                          ) : (
                            <span className="text-xs text-gray-500">—</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Stats footer */}
          <div className="mt-6 grid grid-cols-4 gap-4">
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <p className="text-xs text-gray-400 uppercase font-semibold">Total recursos</p>
              <p className="text-2xl font-bold text-white mt-2">{resources.length}</p>
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <p className="text-xs text-gray-400 uppercase font-semibold">Tipos únicos</p>
              <p className="text-2xl font-bold text-white mt-2">{resourceTypes.length}</p>
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <p className="text-xs text-gray-400 uppercase font-semibold">Suscripciones</p>
              <p className="text-2xl font-bold text-white mt-2">{[...new Set(resources.map(r => r.subscription_id))].length}</p>
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <p className="text-xs text-gray-400 uppercase font-semibold">Con alertas</p>
              <p className="text-2xl font-bold text-white mt-2">{resources.filter(r => r.alert_count > 0).length}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
