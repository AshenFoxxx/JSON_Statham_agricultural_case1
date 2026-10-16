import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Suppliers from './pages/Suppliers'
import Drivers from './pages/Drivers'
import Warehouse from './pages/Warehouse'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Suppliers />} />
          <Route path="suppliers" element={<Suppliers />} />
          <Route path="drivers" element={<Drivers />} />
          <Route path="warehouse" element={<Warehouse />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
