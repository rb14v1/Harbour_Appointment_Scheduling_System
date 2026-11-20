import { Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import AppointmentDetailsPage from './pages/AppointmentDetailsPage';
import AppointmentFormPage from './pages/AppointmentFormPage';
import AppointmentsPage from './pages/AppointmentsPage';
import AppointmentTypesPage from './pages/AppointmentTypesPage';
import CustomersPage from './pages/CustomersPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/customers" element={<CustomersPage />} />
        <Route path="/appointments" element={<AppointmentsPage />} />
        <Route path="/appointments/new" element={<AppointmentFormPage />} />
        <Route path="/appointments/:id" element={<AppointmentDetailsPage />} />
        <Route path="/appointments/:id/edit" element={<AppointmentFormPage />} />
        <Route path="/appointment-types" element={<AppointmentTypesPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
