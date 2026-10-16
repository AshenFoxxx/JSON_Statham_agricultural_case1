import type { ReactNode } from 'react'

interface DataTableProps {
  columns: { key: string; label: string; render?: (value: any, row: any) => ReactNode }[]
  data: any[]
  actions?: (row: any) => ReactNode
}

export default function DataTable({ columns, data, actions }: DataTableProps) {
  if (data.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500 dark:text-gray-400">
        Нет данных
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead className="bg-gray-50 dark:bg-gray-800/50">
          <tr>
            {columns.map((col) => (
              <th key={col.key} className="table-header">
                {col.label}
              </th>
            ))}
            {actions && <th className="table-header">Действия</th>}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
          {data.map((row, rowIndex) => (
            <tr key={row.id || rowIndex} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
              {columns.map((col) => (
                <td key={col.key} className="table-cell">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
              {actions && <td className="table-cell">{actions(row)}</td>}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
