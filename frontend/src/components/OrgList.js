import React, { useEffect, useState } from 'react';
import { getOrgs } from '../api/org';

function OrgList() {
  const [orgs, setOrgs] = useState([]);

  useEffect(() => {
    getOrgs().then(setOrgs);
  }, []);

  return (
    <div>
      <h2>Organizations</h2>
      <ul>
        {orgs.map(o => (
          <li key={o.org_id}>{o.org_name} - {o.org_description}</li>
        ))}
      </ul>
    </div>
  );
}

export default OrgList;
