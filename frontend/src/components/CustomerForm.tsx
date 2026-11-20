import { useState, type ChangeEvent, type FormEvent } from 'react';
import { customersApi } from '../api/resources';
import { errorMessage } from '../api/client';
import type { Customer } from '../types';

interface CustomerFormProps {
  customer?: Customer;
  onSaved: () => void;
  onCancel: () => void;
}

export default function CustomerForm({ customer, onSaved, onCancel }: CustomerFormProps) {
  const [form, setForm] = useState({
    full_name: customer?.full_name ?? '',
    email: customer?.email ?? '',
    phone: customer?.phone ?? '',
    address: customer?.address ?? '',
  });
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const update = (field: keyof typeof form) => (e: ChangeEvent<HTMLInputElement>) =>
    setForm((current) => ({ ...current, [field]: e.target.value }));

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (customer) {
        await customersApi.update(customer.id, form);
      } else {
        await customersApi.create(form);
      }
      onSaved();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-grid">
        <label className="field">
          <span>Full name</span>
          <input required value={form.full_name} onChange={update('full_name')} />
        </label>
        <label className="field">
          <span>Email</span>
          <input type="email" required value={form.email} onChange={update('email')} />
        </label>
        <label className="field">
          <span>Phone</span>
          <input required value={form.phone} onChange={update('phone')} />
        </label>
        <label className="field">
          <span>Address</span>
          <input value={form.address} onChange={update('address')} />
        </label>
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="form-actions">
        <button type="button" className="btn" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? 'Saving…' : 'Save customer'}
        </button>
      </div>
    </form>
  );
}
