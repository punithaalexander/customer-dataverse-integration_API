import { useEffect, useState } from 'react'
import { useAuth } from 'react-oidc-context'
import './App.css'

function App() {
  const auth = useAuth()

  const [customers, setCustomers] = useState([])
  const [loadingCustomers, setLoadingCustomers] = useState(false)
  const [customerError, setCustomerError] = useState('')
  const [newCustomer, setNewCustomer] = useState({
  firstName: '',
  lastName: '',
  email: '',
  phone: ''
})

  const [creatingCustomer, setCreatingCustomer] = useState(false)
  const [createMessage, setCreateMessage] = useState('')
  const [editingCustomer, setEditingCustomer] = useState(null)

  useEffect(() => {
  if (!auth.isAuthenticated) {
    return
  }
  }, [auth.isAuthenticated])

  const loadCustomers = async () => {
    setLoadingCustomers(true)
    setCustomerError('')

    try {
      const accessToken = auth.user?.access_token

      const response = await fetch(
        'https://7atkmrcbs5.execute-api.ap-southeast-2.amazonaws.com/customers',
        {
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        }
      )

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`)
      }

      const data = await response.json()

      console.log('Customer API response:', data)

      setCustomers(data.customers || [])
    } catch (error) {
      console.error(error)
      setCustomerError(error.message)
    } finally {
      setLoadingCustomers(false)
    }
  }

  useEffect(() => {
    if (auth.isAuthenticated && auth.user?.access_token) {
      loadCustomers()
    }
  }, [auth.isAuthenticated, auth.user?.access_token])

  const createCustomer = async () => {
  setCreatingCustomer(true)
  setCreateMessage('')

  try {
    const accessToken = auth.user?.access_token

    const response = await fetch(
      'https://7atkmrcbs5.execute-api.ap-southeast-2.amazonaws.com/customers',
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newCustomer)
      }
    )

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`)
    }

    const data = await response.json()

    console.log('Created customer:', data)

    setCreateMessage('Customer created successfully')

    setNewCustomer({
      firstName: '',
      lastName: '',
      email: '',
      phone: ''
    })

    if (data.customer) {
      setCustomers((currentCustomers) => [
        ...currentCustomers,
        data.customer
      ])
    }
  } catch (error) {
    console.error(error)
    setCreateMessage(`Unable to create customer: ${error.message}`)
  } finally {
    setCreatingCustomer(false)
  }
}
  
const updateCustomer = async () => {
    if (!editingCustomer) {
      return
    }

    try {
      const accessToken = auth.user?.access_token

      const response = await fetch(
        `https://7atkmrcbs5.execute-api.ap-southeast-2.amazonaws.com/customers/${editingCustomer.id}`,
        {
          method: 'PUT',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            firstName: editingCustomer.firstName,
            lastName: editingCustomer.lastName,
            email: editingCustomer.email,
            phone: editingCustomer.phone,
          }),
        }
      )

      if (!response.ok) {
        throw new Error(`Update failed: ${response.status}`)
      }

      setEditingCustomer(null)

      // Refresh customers from Dataverse
      await loadCustomers()

    } catch (error) {
      console.error('Update customer error:', error)
      setCustomerError(error.message)
    }
  }

  const deleteCustomer = async (customerId) => {
  const confirmed = window.confirm(
    'Are you sure you want to delete this customer?'
  )

  if (!confirmed) {
    return
  }

  try {
    const accessToken = auth.user?.access_token

    const response = await fetch(
      `https://7atkmrcbs5.execute-api.ap-southeast-2.amazonaws.com/customers/${customerId}`,
      {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    )

    if (!response.ok) {
      throw new Error(`Delete failed: ${response.status}`)
    }

    // Refresh the table from Dataverse
    await loadCustomers()

  } catch (error) {
    console.error('Delete customer error:', error)
    setCustomerError(error.message)
  }
}

  if (auth.isLoading) {
    return <p>Loading...</p>
  }

  if (auth.error) {
    return <p>Authentication error: {auth.error.message}</p>
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Customer Management</h1>
          <p>Dataverse Customer Portal</p>
        </div>

        <div className="auth-section">
          {!auth.isAuthenticated && (
            <button
              className="primary-button"
              onClick={() =>
                auth.signinRedirect({
                  extraQueryParams: {
                    prompt: 'login',
                  },
                })
              }
            >
              Sign in
            </button>
          )}

          {auth.isAuthenticated && (
            <>
              <span className="signed-in-status">
                Signed in
              </span>

              <button
                className="signout-button"
                onClick={() => auth.removeUser()}
              >
                Sign out
              </button>
            </>
          )}
        </div>
      </header>

      <main>
        <h2>Customers</h2>
        {auth.isAuthenticated && (
        <form className="customer-form">
          <h3>Add Customer</h3>
          <div className="form-group">
            <label>
              First Name
              <input
                type="text"
                value={newCustomer.firstName}
                onChange={(e) =>
                  setNewCustomer({
                    ...newCustomer,
                    firstName: e.target.value
                  })
                }
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              Last Name
              <input
                type="text"
                value={newCustomer.lastName}
                onChange={(e) =>
                  setNewCustomer({
                    ...newCustomer,
                    lastName: e.target.value
                  })
                }
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              Email
              <input
                type="email"
                value={newCustomer.email}
                onChange={(e) =>
                  setNewCustomer({
                    ...newCustomer,
                    email: e.target.value
                  })
                }
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              Phone
              <input
                type="text"
                value={newCustomer.phone}
                onChange={(e) =>
                  setNewCustomer({
                    ...newCustomer,
                    phone: e.target.value
                  })
                }
              />
            </label>
          </div>

          <button
            type="button"
            className="primary-button"
            onClick={createCustomer}
            disabled={creatingCustomer}
          >
            {creatingCustomer ? 'Adding...' : 'Add Customer'}
          </button>
          {createMessage && <p>{createMessage}</p>}
        </form>
        )}
        {auth.isAuthenticated ? (
  <>
        {loadingCustomers && <p>Loading customers...</p>}

        {customerError && (
         <p>Unable to load customers: {customerError}</p>
        )}

        {!loadingCustomers && !customerError && (
      <>
        <p className="customer-count">
          Customers loaded: {customers.length}
        </p>

        {editingCustomer && (
          <div className="edit-customer-form">
            <h3>Edit Customer</h3>

            <div className="form-group">
              <label>
                First Name
                <input
                  type="text"
                  value={editingCustomer.firstName || ''}
                  onChange={(e) =>
                    setEditingCustomer({
                      ...editingCustomer,
                      firstName: e.target.value
                    })
                  }
                />
              </label>
            </div>

            <div className="form-group">
              <label>
                Last Name
                <input
                  type="text"
                  value={editingCustomer.lastName || ''}
                  onChange={(e) =>
                    setEditingCustomer({
                      ...editingCustomer,
                      lastName: e.target.value
                    })
                  }
                />
              </label>
            </div>

            <div className="form-group">
              <label>
                Email
                <input
                  type="email"
                  value={editingCustomer.email || ''}
                  onChange={(e) =>
                    setEditingCustomer({
                      ...editingCustomer,
                      email: e.target.value
                    })
                  }
                />
              </label>
            </div>

            <div className="form-group">
              <label>
                Phone
                <input
                  type="text"
                  value={editingCustomer.phone || ''}
                  onChange={(e) =>
                    setEditingCustomer({
                      ...editingCustomer,
                      phone: e.target.value
                    })
                  }
                />
              </label>
            </div>

            <button
              type="button"
              className="primary-button"
              onClick={updateCustomer}
            >
              Save Changes
            </button>

            <button
              type="button"
              className="cancel-button"
              onClick={() => setEditingCustomer(null)}
            >
              Cancel
            </button>
          </div>
        )}

        {customers.length > 0 ? (
          <div className="customer-table-container">
            <table className="customer-table">
              <thead>
                <tr>
                  <th>First Name</th>
                  <th>Last Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {customers.map((customer) => (
                  <tr key={customer.id}>
                    <td>{customer.firstName}</td>
                    <td>{customer.lastName}</td>
                    <td>{customer.email}</td>
                    <td>{customer.phone}</td>
                    <td>
                      <button
                        type="button"
                        className="edit-button"
                        onClick={() => setEditingCustomer({ ...customer })}
                      >
                        Edit
                      </button>
                      <button
                        type="button"
                        className="delete-button"
                        onClick={() => deleteCustomer(customer.id)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No customers found.</p>
        )}
      </>
    )}
  </>
   ) : (
        <p>Please sign in to view customer data.</p>
       )}
      </main>
    </div>
  )
}

export default App