import React, { useState } from 'react';
import { createOrg } from '../api/org';

function OrgForm() {
  const [form, setForm] = useState({
    org_name: '',
    org_description: ''
  });
  const [message, setMessage] = useState('');

  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setMessage('');
    try {
      await createOrg(form);
      setMessage('Organization created!');
    } catch (err) {
      setMessage('Error creating organization');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Create Organization</h3>
      <input name="org_name" placeholder="Org Name" value={form.org_name} onChange={handleChange} required />
      <input name="org_description" placeholder="Description" value={form.org_description} onChange={handleChange} required />
      <button type="submit">Create</button>
      {message && <div>{message}</div>}
    </form>
  );
}

export default OrgForm;
