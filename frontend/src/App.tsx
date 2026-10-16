import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Warehouse from './pages/Warehouse'
import Buyers from './pages/Buyers'
import Vehicles from './pages/Vehicles'
import RoutesPage from './pages/Routes'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Warehouse />} />
          <Route path="warehouse" element={<Warehouse />} />
          <Route path="buyers" element={<Buyers />} />
          <Route path="vehicles" element={<Vehicles />} />
          <Route path="routes" element={<RoutesPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
