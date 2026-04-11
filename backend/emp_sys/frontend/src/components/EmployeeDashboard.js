import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import './EmployeeDashboard.css';

const initialFormState = {
  Name: '',
  Email: '',
  Education: '',
  JoiningYear: '',
  City: '',
  PaymentTier: '',
  Age: '',
  Gender: '',
  EverBenched: '',
  ExperienceInCurrentDomain: '',
  LeaveOrNot: '',
};

const EmployeeDashboard = () => {
  const { user, logout } = useAuth();
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchTerm, setSearchTerm] = useState('');
  const [stats, setStats] = useState({
    total: 0,
    male: 0,
    female: 0,
    averageAge: 0
  });
  // Modal and form state
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [formData, setFormData] = useState(initialFormState);
  const [editId, setEditId] = useState(null);

  // Fetch employees with pagination
  const fetchEmployees = async (page = 1, limit = 10) => {
    try {
      setLoading(true);
      const skip = (page - 1) * limit;
      const response = await axios.get(`/employees/?skip=${skip}&limit=${limit}`);
      setEmployees(response.data);
      setCurrentPage(page);
      if (response.data.length < limit && page > 1) {
        setTotalPages(page);
      } else if (response.data.length === limit) {
        setTotalPages(page + 1);
      }
    } catch (err) {
      setError('Failed to fetch employees');
      console.error('Error fetching employees:', err);
    } finally {
      setLoading(false);
    }
  };

  // Search employees
  const searchEmployees = async () => {
    if (!searchTerm.trim()) {
      fetchEmployees(1, pageSize);
      return;
    }
    try {
      setLoading(true);
      const response = await axios.get(`/employees/search/?name=${encodeURIComponent(searchTerm)}`);
      setEmployees(response.data);
      setCurrentPage(1);
      setTotalPages(1);
    } catch (err) {
      setError('Failed to search employees');
      console.error('Error searching employees:', err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate stats from current employees
  const calculateStats = (empList) => {
    const total = empList.length;
    const male = empList.filter(emp => emp.Gender === 'Male').length;
    const female = empList.filter(emp => emp.Gender === 'Female').length;
    const ages = empList.map(emp => emp.Age).filter(age => age);
    const averageAge = ages.length > 0 ? Math.round(ages.reduce((a, b) => a + b, 0) / ages.length) : 0;
    return { total, male, female, averageAge };
  };

  // Handle search input change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  // Handle search submit
  const handleSearchSubmit = (e) => {
    e.preventDefault();
    searchEmployees();
  };

  // Handle page change
  const handlePageChange = (page) => {
    if (searchTerm.trim()) {
      setCurrentPage(1);
      searchEmployees();
    } else {
      fetchEmployees(page, pageSize);
    }
  };

  // Handle page size change
  const handlePageSizeChange = (e) => {
    const newSize = parseInt(e.target.value);
    setPageSize(newSize);
    fetchEmployees(1, newSize);
  };

  // Modal form handlers
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Add new employee
  const handleAddEmployee = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/employees/', {
        ...formData,
        Age: formData.Age ? parseInt(formData.Age) : null,
        JoiningYear: formData.JoiningYear ? parseInt(formData.JoiningYear) : null,
        PaymentTier: formData.PaymentTier ? parseInt(formData.PaymentTier) : null,
        ExperienceInCurrentDomain: formData.ExperienceInCurrentDomain ? parseInt(formData.ExperienceInCurrentDomain) : null,
        LeaveOrNot: formData.LeaveOrNot ? parseInt(formData.LeaveOrNot) : 0,
      });
      setShowAddModal(false);
      setFormData(initialFormState);
      fetchEmployees(currentPage, pageSize);
    } catch (err) {
      setError('Failed to add employee');
      console.error('Error adding employee:', err);
    }
  };

  // Open edit modal
  const openEditModal = (employee) => {
    setEditId(employee.emp_id);
    setFormData({
      Name: employee.Name || '',
      Email: employee.Email || '',
      Education: employee.Education || '',
      JoiningYear: employee.JoiningYear || '',
      City: employee.City || '',
      PaymentTier: employee.PaymentTier || '',
      Age: employee.Age || '',
      Gender: employee.Gender || '',
      EverBenched: employee.EverBenched || '',
      ExperienceInCurrentDomain: employee.ExperienceInCurrentDomain || '',
      LeaveOrNot: employee.LeaveOrNot || '',
    });
    setShowEditModal(true);
  };

  // Edit employee
  const handleEditEmployee = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/employees/${editId}`, {
        ...formData,
        Age: formData.Age ? parseInt(formData.Age) : null,
        JoiningYear: formData.JoiningYear ? parseInt(formData.JoiningYear) : null,
        PaymentTier: formData.PaymentTier ? parseInt(formData.PaymentTier) : null,
        ExperienceInCurrentDomain: formData.ExperienceInCurrentDomain ? parseInt(formData.ExperienceInCurrentDomain) : null,
        LeaveOrNot: formData.LeaveOrNot ? parseInt(formData.LeaveOrNot) : 0,
      });
      setShowEditModal(false);
      setFormData(initialFormState);
      setEditId(null);
      fetchEmployees(currentPage, pageSize);
    } catch (err) {
      setError('Failed to edit employee');
      console.error('Error editing employee:', err);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  // Get status badge class
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'Yes':
        return 'badge-warning';
      case 'No':
        return 'badge-success';
      default:
        return 'badge-secondary';
    }
  };

  // Initial load
  useEffect(() => {
    fetchEmployees(1, pageSize);
  }, []);

  // Update stats when employees change
  useEffect(() => {
    setStats(calculateStats(employees));
  }, [employees]);

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="container">
          <div className="dashboard-header-content">
            <h1 className="dashboard-title">Employee Dashboard</h1>
            <div className="user-info">
              <span>Welcome, {user?.name}</span>
              <button className="btn btn-danger logout-btn" onClick={logout}>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="dashboard-content">
        <div className="container">
          {/* New Employee Button */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 16 }}>
            <button className="btn btn-success" onClick={() => { setShowAddModal(true); setFormData(initialFormState); }}>
              + New Employee
            </button>
          </div>

          {/* Stats Grid */}
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Employees</h3>
              <div className="value">{stats.total}</div>
            </div>
            <div className="stat-card">
              <h3>Male Employees</h3>
              <div className="value">{stats.male}</div>
            </div>
            <div className="stat-card">
              <h3>Female Employees</h3>
              <div className="value">{stats.female}</div>
            </div>
            <div className="stat-card">
              <h3>Average Age</h3>
              <div className="value">{stats.averageAge}</div>
            </div>
          </div>

          {/* Controls Section */}
          <div className="controls-section">
            <form onSubmit={handleSearchSubmit} className="controls-row">
              <input
                type="text"
                className="input search-input"
                placeholder="Search by employee name..."
                value={searchTerm}
                onChange={handleSearchChange}
              />
              <button type="submit" className="btn btn-primary">
                Search
              </button>
              {searchTerm && (
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setSearchTerm('');
                    fetchEmployees(1, pageSize);
                  }}
                >
                  Clear
                </button>
              )}
              <select
                className="input"
                value={pageSize}
                onChange={handlePageSizeChange}
                style={{ width: 'auto', minWidth: '100px' }}
              >
                <option value={5}>5 per page</option>
                <option value={10}>10 per page</option>
                <option value={20}>20 per page</option>
                <option value={50}>50 per page</option>
              </select>
            </form>
          </div>

          {/* Error Message */}
          {error && (
            <div className="error">
              {error}
            </div>
          )}

          {/* Table Container */}
          <div className="table-container">
            <div className="table-header">
              <h2 className="table-title">Employee List</h2>
              <div className="table-info">
                Showing {employees.length} employees
                {!searchTerm && totalPages > 1 && ` (Page ${currentPage} of ${totalPages})`}
              </div>
            </div>

            {loading ? (
              <div className="loading">
                <div className="spinner"></div>
                Loading employees...
              </div>
            ) : (
              <>
                <div className="table-wrapper">
                  <table className="table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Education</th>
                        <th>Joining Year</th>
                        <th>City</th>
                        <th>Payment Tier</th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Ever Benched</th>
                        <th>Experience</th>
                        <th>Leave Status</th>
                        <th>Edit</th>
                      </tr>
                    </thead>
                    <tbody>
                      {employees.map((employee) => (
                        <tr key={employee.emp_id}>
                          <td>{employee.emp_id}</td>
                          <td>
                            <strong>{employee.Name}</strong>
                          </td>
                          <td>{employee.Email}</td>
                          <td>{employee.Education || 'N/A'}</td>
                          <td>{employee.JoiningYear || 'N/A'}</td>
                          <td>{employee.City || 'N/A'}</td>
                          <td>
                            <span className={`badge badge-tier-${employee.PaymentTier || 0}`}>
                              Tier {employee.PaymentTier || 'N/A'}
                            </span>
                          </td>
                          <td>{employee.Age || 'N/A'}</td>
                          <td>
                            <span className={`badge badge-gender-${employee.Gender?.toLowerCase() || 'unknown'}`}>
                              {employee.Gender || 'N/A'}
                            </span>
                          </td>
                          <td>
                            <span className={`badge ${getStatusBadgeClass(employee.EverBenched)}`}>
                              {employee.EverBenched || 'N/A'}
                            </span>
                          </td>
                          <td>{employee.ExperienceInCurrentDomain || 0} years</td>
                          <td>
                            <span className={`badge ${employee.LeaveOrNot ? 'badge-danger' : 'badge-success'}`}>
                              {employee.LeaveOrNot ? 'On Leave' : 'Active'}
                            </span>
                          </td>
                          <td>
                            <button className="btn btn-warning btn-sm" onClick={() => openEditModal(employee)}>
                              Edit
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {!searchTerm && totalPages > 1 && (
                  <div className="pagination">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </button>
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      const page = i + 1;
                      return (
                        <button
                          key={page}
                          onClick={() => handlePageChange(page)}
                          className={currentPage === page ? 'active' : ''}
                        >
                          {page}
                        </button>
                      );
                    })}
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </button>
                  </div>
                )}

                {employees.length === 0 && !loading && (
                  <div className="no-data">
                    <p>No employees found.</p>
                    {searchTerm && (
                      <button
                        className="btn btn-primary"
                        onClick={() => {
                          setSearchTerm('');
                          fetchEmployees(1, pageSize);
                        }}
                      >
                        Clear Search
                      </button>
                    )}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>

      {/* Add Employee Modal */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Add New Employee</h2>
            <form onSubmit={handleAddEmployee} className="employee-form">
              {Object.keys(initialFormState).map((key) => (
                <div className="form-group" key={key}>
                  <label>{key}</label>
                  <input
                    type="text"
                    name={key}
                    value={formData[key]}
                    onChange={handleInputChange}
                  />
                </div>
              ))}
              <div className="form-actions">
                <button type="submit" className="btn btn-success">Add</button>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Employee Modal */}
      {showEditModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Edit Employee</h2>
            <form onSubmit={handleEditEmployee} className="employee-form">
              {Object.keys(initialFormState).map((key) => (
                <div className="form-group" key={key}>
                  <label>{key}</label>
                  <input
                    type="text"
                    name={key}
                    value={formData[key]}
                    onChange={handleInputChange}
                  />
                </div>
              ))}
              <div className="form-actions">
                <button type="submit" className="btn btn-warning">Save</button>
                <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeeDashboard;
