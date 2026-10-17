import { Outlet, NavLink } from 'react-router-dom'
import { useTheme } from '../contexts/ThemeContext'

const navItems = [
  { path: '/warehouse', label: 'Склад', icon: '🏭' },
  { path: '/farm', label: 'Хозяйство', icon: '🌾' },
  { path: '/buyers', label: 'Покупатели', icon: '🛒' },
  { path: '/vehicles', label: 'Машины', icon: '🚛' },
  { path: '/routes', label: 'Маршруты', icon: '🗺️' },
]

export default function Layout() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🌾</span>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white">
                АгроЛогистика
              </h1>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                title={theme === 'light' ? 'Тёмная тема' : 'Светлая тема'}
              >
                {theme === 'light' ? '🌙' : '☀️'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-1 -mb-px">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                end
                className={({ isActive }) =>
                  `flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    isActive
                      ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
                  }`
                }
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500 dark:text-gray-400">
            <p>
              © {new Date().getFullYear()} АгроЛогистика. Все права защищены. ООО "Команда JSON Statham".
            </p>
            <div className="flex items-center gap-4">
              <a
                href="/privacy"
                className="text-primary-600 dark:text-primary-400 hover:underline"
              >
                Политика конфиденциальности
              </a>
              <a
                href="/doc/"
                className="text-primary-600 dark:text-primary-400 hover:underline"
              >
                Документация
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
