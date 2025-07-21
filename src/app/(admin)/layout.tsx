import { ReactNode } from 'react';

export default function AdminLayout({ children }: { children: ReactNode }) {
  // Add admin-specific layout components here, e.g., a sidebar
  return <div>{children}</div>;
}