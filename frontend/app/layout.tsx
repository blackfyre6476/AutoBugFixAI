import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AutoFix AI - Autonomous AI Bug Fixing Assistant',
  description: 'Autonomous software engineering assistant that analyzes repositories, identifies root causes, executes fixes in Docker sandboxes, and verifies regression tests.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d16] text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
