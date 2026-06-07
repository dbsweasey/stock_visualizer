export default function Controls({ control }) {
  return (
    <div>
      <button onClick={() => control(1)}>1s</button>
      <button onClick={() => control(5)}>5s</button>
      <button onClick={() => control(15)}>15s</button>
      <button onClick={() => control(60)}>1m</button>
    </div>
  );
}
