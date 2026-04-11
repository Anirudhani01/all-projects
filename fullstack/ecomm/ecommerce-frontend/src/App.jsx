import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Products from './pages/Products'
import Wishlist from './pages/Wishlist'

function App() {
  console.log('App component loaded at:', new Date().toISOString())
  console.log('App version:', Date.now())
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="pt-16">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/wishlist" element={<Wishlist />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
