/** Severity and category badge components */

const SEVERITY_STYLES = {
  critical: 'bg-red-100 text-red-700 border border-red-200',
  error:    'bg-orange-100 text-orange-700 border border-orange-200',
  warning:  'bg-yellow-100 text-yellow-700 border border-yellow-200',
  info:     'bg-blue-100 text-blue-700 border border-blue-200',
};

const CATEGORY_STYLES = {
  cpu_pressure:  'bg-orange-50 text-orange-700',
  availability:  'bg-red-50 text-red-700',
  cost_anomaly:  'bg-purple-50 text-purple-700',
  memory:        'bg-yellow-50 text-yellow-700',
  disk:          'bg-gray-100 text-gray-700',
  network:       'bg-cyan-50 text-cyan-700',
  unknown:       'bg-gray-100 text-gray-500',
};

export function SeverityBadge({ severity }) {
  const style = SEVERITY_STYLES[severity] || SEVERITY_STYLES.info;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style}`}>
      {severity}
    </span>
  );
}

export function CategoryBadge({ category }) {
  const style = CATEGORY_STYLES[category] || CATEGORY_STYLES.unknown;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style}`}>
      {category?.replace('_', ' ') || 'unknown'}
    </span>
  );
}

export function ConfidenceBadge({ confidence }) {
  if (!confidence && confidence !== 0) return null;
  const pct = Math.round(confidence * 100);
  const color = pct >= 80 ? 'text-green-600' : pct >= 60 ? 'text-yellow-600' : 'text-gray-500';
  return (
    <span className={`text-xs font-medium ${color}`}>{pct}%</span>
  );
}
