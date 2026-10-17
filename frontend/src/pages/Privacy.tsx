import { useState } from 'react'

export default function Privacy() {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    collection: true,
    usage: false,
    storage: false,
    cookies: false,
    contacts: false,
  })

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }))
  }

  const sections = [
    {
      id: 'collection',
      title: '1. Какие данные хранит приложение',
      content: (
        <>
          <p className="mb-3">
            Приложение работает с данными логистики, которые пользователь вводит сам. Учётных записей нет.
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>
              <strong>Хозяйство:</strong> название и координаты.
            </li>
            <li>
              <strong>Культуры:</strong> название, запас в килограммах, предельное время доставки в часах.
            </li>
            <li>
              <strong>Покупатели и заказы:</strong> название, координаты, спрос и закупочная цена по культурам.
            </li>
            <li>
              <strong>Транспорт:</strong> название, грузоподъёмность, расход топлива, цена топлива, число остановок, доступность.
            </li>
            <li>
              <strong>Результаты расчёта:</strong> рейсы, отгрузки, выручка, затраты и прибыль — считаются на сервере и не хранятся как отдельная сущность, пока пользователь не сохранит исходные данные склада.
            </li>
          </ul>
        </>
      ),
    },
    {
      id: 'usage',
      title: '2. Для чего используются данные',
      content: (
        <ul className="list-disc list-inside space-y-2 ml-4">
          <li>учёт запасов, покупателей и машин;</li>
          <li>расчёт плана поставок: прибыль = выручка минус топливо, с учётом срока доставки и разгрузки;</li>
          <li>
            построение маршрутов по дорогам: координаты отправляются в публичный сервис OSRM, чтобы получить километры, время и линию пути.
          </li>
        </ul>
      ),
    },
    {
      id: 'storage',
      title: '3. Где хранятся данные',
      content: (
        <>
          <p className="mb-3">
            Складские данные сохраняются в локальной базе SQLite на компьютере, где запущен сервер API. Отдельного облачного аккаунта нет.
          </p>
          <p>
            Тема оформления хранится в браузере (localStorage). Логинов, паролей и рассылки на электронную почту приложение не использует.
          </p>
        </>
      ),
    },
    {
      id: 'cookies',
      title: '4. Файлы cookie',
      content: (
        <p>
          Рекламные и аналитические cookie не используются. В браузере может сохраняться только выбранная тема интерфейса.
        </p>
      ),
    },
    {
      id: 'contacts',
      title: '5. Контактная информация',
      content: (
        <ul className="list-disc list-inside space-y-2 ml-4">
          <li>
            <strong>Оператор:</strong> ООО «Команда JSON Statham»
          </li>
          <li>
            <strong>Электронная почта:</strong> domni3174@gmail.com
          </li>
        </ul>
      ),
    },
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          Политика конфиденциальности
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Дата последнего обновления: 17 октября 2026 г.
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 sm:p-8 mb-6">
        <p className="text-gray-700 dark:text-gray-300">
          Документ описывает, какие сведения приложение «АгроЛогистика» действительно сохраняет
          и зачем они нужны. Используя приложение, вы соглашаетесь с этим порядком.
        </p>
      </div>

      <div className="space-y-3">
        {sections.map((section) => (
          <div
            key={section.id}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden"
          >
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full flex items-center justify-between p-5 sm:p-6 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              <span className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white pr-4">
                {section.title}
              </span>
              <svg
                className={`w-5 h-5 text-gray-500 dark:text-gray-400 flex-shrink-0 transition-transform duration-200 ${
                  expandedSections[section.id] ? 'rotate-180' : ''
                }`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSections[section.id] && (
              <div className="px-5 sm:px-6 pb-5 sm:pb-6 text-gray-700 dark:text-gray-300 leading-relaxed border-t border-gray-100 dark:border-gray-700 pt-4">
                {section.content}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
