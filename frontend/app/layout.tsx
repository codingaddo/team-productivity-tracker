export const metadata = {
  title: 'Team Productivity Tracker',
  description: 'Internal time and productivity tracker',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
