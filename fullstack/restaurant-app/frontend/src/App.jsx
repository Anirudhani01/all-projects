// src/App.jsx
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Login from './Login';
import OwnerDashboard from './OwnerDashboard';

const menuItems = [
  { id: 1, name: 'VEG BIRYANI', price: 99, pieces: '1-Pc' },
  { id: 2, name: 'VEG BIRYANI', price: 199, pieces: '2-Pc' },
  { id: 3, name: 'VEG BIRYANI', price: 389, pieces: '4-Pc' },
  { id: 4, name: 'VEG BIRYANI', price: 479, pieces: '6-Pc' },
  { id: 5, name: 'EGG FRIED RICE', price: 120, pieces: '1-Pc' },
  { id: 6, name: 'EGG FRIED RICE', price: 220, pieces: '2-Pc' },
  { id: 7, name: 'EGG OMELETTE', price: 50, pieces: '1-Pc' },
  { id: 8, name: 'EGG CURRY', price: 150, pieces: '1-Pc' },
];

function App() {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [tables, setTables] = useState(
    Array(12).fill().map((_, i) => ({
      tableNumber: i + 1,
      items: [],
      totalBill: 0,
      orderId: null,
    }))
  );
  const [searchTerms, setSearchTerms] = useState(Array(12).fill(''));
  const [selectedItems, setSelectedItems] = useState(Array(12).fill().map(() => []));

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const updateTableState = async (tableIndex, newItems, newTotal) => {
    const newTables = [...tables];
    newTables[tableIndex].items = [...newItems];
    newTables[tableIndex].totalBill = newTotal;

    const response = await fetch(`http://localhost:8000/orders/${newTables[tableIndex].orderId || ''}`, {
      method: newTables[tableIndex].orderId ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        table_number: newTables[tableIndex].tableNumber,
        items: newTables[tableIndex].items,
        total_bill: newTables[tableIndex].totalBill,
      }),
    });

    const order = await response.json();
    newTables[tableIndex].orderId = order.id || newTables[tableIndex].orderId;
    setTables(newTables);
  };

  const markPaid = async (tableIndex) => {
    const table = tables[tableIndex];
    if (table.orderId) {
      await fetch(`http://localhost:8000/orders/${table.orderId}/paid`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
      });
      const newTables = [...tables];
      newTables[tableIndex] = {
        tableNumber: table.tableNumber,
        items: [],
        totalBill: 0,
        orderId: null,
      };
      setTables(newTables);
    }
  };

  const handleSearchChange = (e, tableIndex) => {
    const newSearchTerms = [...searchTerms];
    newSearchTerms[tableIndex] = e.target.value;
    setSearchTerms(newSearchTerms);
  };

  const handleCheckboxChange = (tableIndex, item) => {
    const newSelectedItems = [...selectedItems];
    const currentSelected = newSelectedItems[tableIndex];
    if (currentSelected.some((selected) => selected.id === item.id)) {
      newSelectedItems[tableIndex] = currentSelected.filter((selected) => selected.id !== item.id);
    } else {
      newSelectedItems[tableIndex] = [...currentSelected, item];
    }
    setSelectedItems(newSelectedItems);

    // Update table state in real-time
    const newTotal = newSelectedItems[tableIndex].reduce((sum, selected) => sum + selected.price, 0);
    updateTableState(tableIndex, newSelectedItems[tableIndex], newTotal);
  };

  const Home = () => (
    <div style={{ minHeight: '100vh', backgroundColor: '#e0e7ff', padding: '1.5rem', transition: 'background-color 0.5s ease' }}>
      <div className="time-display" style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <p style={{ fontSize: '1.2rem', color: '#1e40af', transition: 'color 0.3s ease' }}>
          Date: {currentTime.toLocaleDateString()} | Time: {currentTime.toLocaleTimeString()}
        </p>
      </div>
      <Link
        to="/login"
        style={{
          position: 'fixed',
          top: '1rem',
          right: '1rem',
          backgroundColor: '#8b5cf6',
          color: 'white',
          padding: '0.5rem 1rem',
          borderRadius: '0.25rem',
          textDecoration: 'none',
          transition: 'all 0.3s ease',
        }}
        onMouseOver={(e) => {
          e.target.style.backgroundColor = '#6b21a8';
          e.target.style.transform = 'scale(1.05)';
        }}
        onMouseOut={(e) => {
          e.target.style.backgroundColor = '#8b5cf6';
          e.target.style.transform = 'scale(1)';
        }}
      >
        Owner Login
      </Link>
      <h1 className="highlighted">INDUR FOODIES</h1>
      <div className="table-grid">
        {tables.map((table, index) => {
          const tableIndex = index;
          const filteredItems = menuItems.filter((item) =>
            item.name.toLowerCase().includes(searchTerms[tableIndex].toLowerCase())
          );

          return (
            <div
              key={table.tableNumber}
              className="table-box"
              style={{ padding: '1rem', transition: 'all 0.3s ease' }}
            >
              <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.5rem', color: '#1e3a8a' }}>Table {table.tableNumber}</h2>
              <input
                type="text"
                placeholder="Search items (e.g., egg)..."
                value={searchTerms[tableIndex]}
                onChange={(e) => handleSearchChange(e, tableIndex)}
                style={{
                  padding: '0.5rem',
                  border: '1px solid #93c5fd',
                  borderRadius: '0.25rem',
                  width: '100%',
                  marginBottom: '0.5rem',
                  transition: 'border-color 0.3s ease',
                }}
              />
              {searchTerms[tableIndex] && (
                <div
                  style={{
                    marginBottom: '0.5rem',
                    backgroundColor: '#ffffff',
                    border: '1px solid #93c5fd',
                    borderRadius: '0.25rem',
                    maxHeight: '150px',
                    overflowY: 'auto',
                    padding: '0.5rem',
                  }}
                >
                  {filteredItems.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        padding: '0.25rem',
                        backgroundColor: '#f1f5f9',
                        marginBottom: '0.25rem',
                        borderRadius: '0.25rem',
                      }}
                    >
                      <input
                        type="checkbox"
                        checked={selectedItems[tableIndex].some((selected) => selected.id === item.id)}
                        onChange={() => handleCheckboxChange(tableIndex, item)}
                        style={{ marginRight: '0.5rem' }}
                      />
                      <span>{item.name} - ₹{item.price}/-</span>
                    </div>
                  ))}
                </div>
              )}
              {/* New box for selected items only */}
              {selectedItems[tableIndex].length > 0 && (
                <div
                  style={{
                    marginBottom: '0.5rem',
                    backgroundColor: '#ffffff',
                    border: '1px solid #93c5fd',
                    borderRadius: '0.25rem',
                    padding: '0.5rem',
                  }}
                >
                  <ul style={{ margin: 0 }}>
                    {selectedItems[tableIndex].map((item, i) => (
                      <li key={i} style={{ listStyle: 'none', color: '#374151' }}>
                        {item.name} ({item.pieces || '1-Pc'}) - ₹{item.price}/-
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <p style={{ fontWeight: 'bold', marginBottom: '0.5rem', color: '#1e40af' }}>
                Total: ₹{tables[tableIndex].totalBill}/-
              </p>
              <label style={{ display: 'flex', alignItems: 'center' }}>
                <input
                  type="checkbox"
                  onChange={() => markPaid(index)}
                  disabled={!table.items.length}
                  style={{ marginRight: '0.5rem', accentColor: '#8b5cf6' }}
                />
                <span style={{ color: '#374151' }}>Paid</span>
              </label>
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<OwnerDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;