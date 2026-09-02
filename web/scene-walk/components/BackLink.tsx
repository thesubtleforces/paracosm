export function BackLink() {
  const bot = process.env.NEXT_PUBLIC_BOT_USERNAME;
  if (!bot) return null;
  return (
    <a className="btn" href={`https://t.me/${bot}`}>
      Back to the table
    </a>
  );
}
