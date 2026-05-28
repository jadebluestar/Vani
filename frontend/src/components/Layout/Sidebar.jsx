import React from 'react'
import { NavLink } from 'react-router-dom'
import { 
  LayoutDashboard, 
  MessageSquare, 
  Mic, 
  Users, 
  UserPlus, 
  TrendingUp, 
  Award, 
  Settings
} from 'lucide-react'

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/practice', icon: MessageSquare, label: 'Practice' },
  { path: '/interview', icon: Mic, label: 'Interview' },
  { path: '/tutors', icon: Users, label: 'Tutors' },
  { path: '/group', icon: UserPlus, label: 'Group Session' },
  { path: '/progress', icon: TrendingUp, label: 'Progress' },
  { path: '/credentials', icon: Award, label: 'Credentials' },
  { path: '/settings', icon: Settings, label: 'Settings' },
]

export default function Sidebar({ open, setOpen }) {
  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div 
          className="fixed inset-0 z-30 bg-gray-900/50 lg:hidden"
          onClick={() => setOpen(false)}
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-40 w-64 h-screen pt-16 transition-transform bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 ${
          open ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
      >
        <div className="h-full px-3 pb-4 overflow-y-auto">
          <ul className="space-y-1 font-medium">
            {navItems.map((item) => (
              <li key={item.path}>
                <NavLink
                  to={item.path}
                  onClick={() => setOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center p-2 text-gray-900 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 group transition-colors ${
                      isActive ? 'bg-gray-100 dark:bg-gray-700 text-primary-600 dark:text-primary-400' : ''
                    }`
                  }
                >
                  <item.icon className="w-5 h-5 transition duration-75" />
                  <span className="ml-3 text-sm">{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </>
  )
}