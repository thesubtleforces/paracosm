export default function Landing() {
  const bot = process.env.NEXT_PUBLIC_BOT_USERNAME;
  return (
    <main className="landing">
      <div>
        <h1>PARACOSM</h1>
        <p>
          This page opens scenes from a game in progress. Walk links arrive inside the
          story, from the Game Master, and expire after half an hour.
        </p>
        {bot ? (
          <p>
            <a href={`https://t.me/${bot}`}>Back to the table</a>
          </p>
        ) : null}
      </div>
    </main>
  );
}
