import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => (
  <nav style={{ padding: '1rem', background: '#eee' }}>
    <Link to="/" style={{ marginRight: '1rem' }}>Dashboard</Link>
    <Link to="/sales">Sales Forecast</Link>
  </nav>
);

export default Navbar;
