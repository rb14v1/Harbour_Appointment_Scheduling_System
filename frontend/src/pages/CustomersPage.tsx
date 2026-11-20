import { useCallback, useEffect, useState } from 'react';
import { customersApi } from '../api/resources';
import { errorMessage } from '../api/client';
import CustomerForm from '../components/CustomerForm';
import Modal from '../components/Modal';
import type { Customer } from '../types';

export default function CustomersPage() {
  const [search, setSearch] = useState('');
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<{ customer?: Customer } | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setCustomers(await customersApi.list(search.trim()));
      setError(null);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => {
    load();
  }, [load]);

  async function handleDelete(customer: Customer) {
    if (!window.confirm(`Delete ${customer.full_name}?`)) return;
    try {
      await customersApi.remove(customer.id);
      load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <section>
      <header className="page-header">
        <h1>Customers</h1>
        <button type="button" className="btn btn-primary" onClick={() => setModal({})}>
          Add customer
        </button>
      </header>

      <div className="toolbar">
        <input
          type="search"
          placeholder="Search by name, email or phone"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search customers"
        />
      </div>

      {error && <p className="form-error">{error}</p>}

      <div className="card table-wrap">
        {loading ? (
          <p className="muted">Loading customers…</p>
        ) : customers.length === 0 ? (
          <p className="muted">No customers found.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Address</th>
                <th aria-label="Actions" />
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.full_name}</td>
                  <td>{customer.email}</td>
                  <td>{customer.phone}</td>
                  <td>{customer.address}</td>
                  <td className="actions">
                    <button type="button" className="btn btn-ghost" onClick={() => setModal({ customer })}>
                      Edit
                    </button>
                    <button type="button" className="btn btn-ghost danger" onClick={() => handleDelete(customer)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {modal && (
        <Modal title={modal.customer ? 'Edit customer' : 'Add customer'} onClose={() => setModal(null)}>
          <CustomerForm
            customer={modal.customer}
            onCancel={() => setModal(null)}
            onSaved={() => {
              setModal(null);
              load();
            }}
          />
        </Modal>
      )}
    </section>
  );
}
