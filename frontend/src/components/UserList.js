import React, { useEffect, useState } from 'react';
import { getUsers } from '../api/user';

function UserList() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    getUsers().then(setUsers);
  }, []);

  return (
    <div>
      <h2>Users</h2>
      <ul>
        {users.map(u => (
          <li key={u.user_id}>{u.first_name} {u.last_name} ({u.user_email})</li>
        ))}
      </ul>
    </div>
  );
}

export default UserList;
