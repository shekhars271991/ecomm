'use client'

import { QueryClient, QueryClientProvider } from 'react-query'
import { useState } from 'react'
import { Toaster } from 'react-hot-toast'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5, // 5 minutes
        cacheTime: 1000 * 60 * 10, // 10 minutes
        retry: 3,
        refetchOnWindowFocus: false,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster
        position="top-center"
        reverseOrder={false}
        gutter={8}
        containerClassName=""
        containerStyle={{}}
        toastOptions={{
          // Default options for all toasts
          className: '',
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
            borderRadius: '12px',
            fontSize: '14px',
            fontWeight: '500',
            padding: '12px 16px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.12)',
          },
          // Success toast styling
          success: {
            duration: 3000,
            style: {
              background: '#22c55e',
              color: '#fff',
            },
            iconTheme: {
              primary: '#fff',
              secondary: '#22c55e',
            },
          },
          // Error toast styling
          error: {
            duration: 5000,
            style: {
              background: '#ef4444',
              color: '#fff',
            },
            iconTheme: {
              primary: '#fff',
              secondary: '#ef4444',
            },
          },
          // Loading toast styling
          loading: {
            style: {
              background: '#f97316',
              color: '#fff',
            },
            iconTheme: {
              primary: '#fff',
              secondary: '#f97316',
            },
          },
        }}
      />
    </QueryClientProvider>
  )
} 