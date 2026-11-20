import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { dashboardApi } from '../api/resources';
import { errorMessage } from '../api/client';
import StatCard from '../components/StatCard';
import StatusBadge from '../components/StatusBadge';
import type { DashboardData } from '../types';
import { formatDateTime } from '../utils/datetime';

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    dashboardApi
      .get()
      .then((result) => active && setData(result))
      .catch((err) => active && setError(errorMessage(err)));
    return () => {
      active = false;
    };
  }, []);

  if (error) return <p className="form-error">{error}</p>;
  if (!data) return <p className="muted">Loading dashboard…</p>;

  return (
    <section>
      <header className="page-header">
        <h1>Dashboard</h1>
        <Link to="/appointments/new" className="btn btn-primary">
          New appointment
        </Link>
      </header>

      <div className="stat-grid">
        <StatCard label="Total" value={data.total} />
        <StatCard label="Today" value={data.today} />
        <StatCard label="Upcoming" value={data.upcoming} />
        <StatCard label="Completed" value={data.completed} />
        <StatCard label="Cancelled" value={data.cancelled} />
      </div>

      <div className="two-column">
        <div className="card">
          <h2>Recent appointments</h2>
          {data.recent.length === 0 ? (
            <p className="muted">No appointments yet.</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Start</th>
                    <th>Customer</th>
                    <th>Type</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.recent.map((appointment) => (
                    <tr key={appointment.id}>
                      <td>
                        <Link to={`/appointments/${appointment.id}`}>{formatDateTime(appointment.start_at)}</Link>
                      </td>
                      <td>{appointment.customer_name}</td>
                      <td>{appointment.appointment_type_name}</td>
                      <td>
                        <StatusBadge status={appointment.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="card">
          <h2>By appointment type</h2>
          {data.by_type.length === 0 ? (
            <p className="muted">No data yet.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Type</th>
                  <th className="num">Count</th>
                </tr>
              </thead>
              <tbody>
                {data.by_type.map((row) => (
                  <tr key={row.type_id}>
                    <td>{row.type_name}</td>
                    <td className="num">{row.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </section>
  );
}
